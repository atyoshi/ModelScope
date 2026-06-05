import re
import streamlit as st
from config.defaults import (
    LLAMA_CPP_DEFAULT_URL, OLLAMA_DEFAULT_URL,
    GGUF_MODELS_DIR, MIN_CONTEXT_SIZE, MAX_CONTEXT_SIZE, CONTEXT_STEP,
)
from config.metrics import METRIC_TYPES, CATEGORIES, format_criterion
from core.models import scan_gguf_models, fetch_ollama_models, detect_backend
from core.mcp_manager import start_mcp, stop_mcp, discover_tools
from core import llama_server


def render() -> None:
    st.header("Configuration")
    sub_model, sub_metrics = st.tabs(["Model Setup", "Metrics Setup"])
    with sub_model:
        _model_setup()
    with sub_metrics:
        _metrics_setup()


# ── Model Setup ────────────────────────────────────────────────────────────────

def _model_setup() -> None:
    # Apply any pending backend detection BEFORE the selectbox is created.
    if "_pending_backend" in st.session_state:
        pending = st.session_state.pop("_pending_backend")
        st.session_state["backend_type"] = pending
        st.session_state["_last_backend"] = pending
        st.session_state["llm_models"]    = []
        st.session_state["selected_model"] = None

    # ── Backend & URL ──────────────────────────────────────────────────────────
    st.subheader("Backend & URL")
    col_be, col_url, col_detect = st.columns([2, 6, 1])

    with col_be:
        backend = st.selectbox(
            "Backend",
            options=["llama.cpp", "ollama"],
            index=0 if st.session_state["backend_type"] == "llama.cpp" else 1,
            key="backend_type",
        )

    with col_url:
        if st.session_state.get("_last_backend") != backend:
            st.session_state["llm_url"] = (
                LLAMA_CPP_DEFAULT_URL if backend == "llama.cpp" else OLLAMA_DEFAULT_URL
            )
            st.session_state["_last_backend"] = backend
            st.session_state["llm_models"]    = []
            st.session_state["selected_model"] = None
        elif not (st.session_state.get("llm_url") or "").strip():
            st.session_state["llm_url"] = (
                LLAMA_CPP_DEFAULT_URL if backend == "llama.cpp" else OLLAMA_DEFAULT_URL
            )
        st.text_input("Server URL", key="llm_url")

    with col_detect:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        if st.button("Detect", use_container_width=True, help="Auto-detect backend from URL"):
            found = detect_backend(st.session_state["llm_url"])
            if found:
                st.session_state["_pending_backend"] = found
                st.rerun()
            else:
                st.warning("No server found at that URL")

    # ── llama-server management (llama.cpp only) ──────────────────────────────
    if backend == "llama.cpp":
        with st.expander("🖥  llama-server", expanded=True):
            _llama_server_controls()

    # ── Model selection ────────────────────────────────────────────────────────
    st.subheader("Model")
    if backend == "llama.cpp":
        _gguf_model_selector()
    else:
        _ollama_model_selector()

    # ── Context Window ─────────────────────────────────────────────────────────
    st.subheader("Context Window")
    ctx = st.slider(
        "Size (tokens)",
        min_value=MIN_CONTEXT_SIZE,
        max_value=MAX_CONTEXT_SIZE,
        step=CONTEXT_STEP,
        key="context_size",
        help="Number of tokens in the model's context window. Restart the server to apply changes.",
    )
    # Warn if slider differs from running server's n_ctx (fix #5)
    if backend == "llama.cpp":
        url = st.session_state.get("llm_url", "")
        info = llama_server.get_server_info(url)
        if info and info["n_ctx"] is not None and info["n_ctx"] != ctx:
            st.warning(
                f"⚠️  Running server n_ctx = **{info['n_ctx']}** but slider is set to **{ctx}**. "
                f"Click **Restart** in the llama-server section to apply the new size."
            )

    # ── MCP Server ─────────────────────────────────────────────────────────────
    with st.expander("🔌  SecOps MCP Server", expanded=False):
        _mcp_server_section()


def _llama_server_controls() -> None:
    """Status, server info, and Start/Stop/Restart for the local llama-server."""
    # Auto-start message (fix #6: info for starting, success for ready)
    msg_pair = st.session_state.pop("_autostart_msg", None)
    if msg_pair:
        level, msg = msg_pair
        if level == "ok":
            st.success(f"Auto-start: {msg}")
        elif level == "info":
            st.info(f"Auto-start: {msg}")
        else:
            st.error(f"Auto-start: {msg}")

    url   = st.session_state.get("llm_url", "")
    ready = llama_server.poll_ready(url)   # single poll per render (fix #4)
    proc  = st.session_state.get("llama_server_process")
    model_chosen = bool(st.session_state.get("selected_model_path"))

    if ready:
        st.success("🟢 Running and ready")
        # Show server info (fix #28)
        info = llama_server.get_server_info(url)
        if info:
            model_name = (info.get("model_path") or "").split("/")[-1] or "?"
            st.caption(f"Model: `{model_name}`  |  n_ctx: `{info.get('n_ctx', '?')}`")
    elif proc and model_chosen:
        st.info("🟡 Starting — loading model into memory…")
    elif not model_chosen:
        st.warning("🔴 Model not chosen — select a GGUF model first")
    else:
        st.warning("🔴 Not running")

    col_start, col_stop, col_restart = st.columns(3)
    with col_start:
        if st.button("Start", use_container_width=True, key="btn_ls_start"):
            path = st.session_state.get("selected_model_path")
            if not path:
                st.error("Select a GGUF model first")
            else:
                ok, msg = llama_server.start(
                    path,
                    context_size=st.session_state.get("context_size", 4096),
                )
                st.success(msg) if ok else st.error(msg)

    with col_stop:
        if st.button("Stop", use_container_width=True, key="btn_ls_stop"):
            ok, msg = llama_server.stop()
            st.success(msg) if ok else st.info(msg)

    with col_restart:
        if st.button("Restart", use_container_width=True, key="btn_ls_restart"):
            llama_server.stop()
            path = st.session_state.get("selected_model_path")
            if path:
                ok, msg = llama_server.start(
                    path,
                    context_size=st.session_state.get("context_size", 4096),
                )
                st.success(msg) if ok else st.error(msg)
            else:
                st.error("Select a GGUF model first")

    # Editable binary path (fix #29)
    st.text_input(
        "llama-server binary path",
        key="llama_server_bin",
        help="Path to the llama-server executable. Edit here if installed in a non-default location.",
    )


def _mcp_server_section() -> None:
    """MCP server path, Start/Stop, and tool discovery."""
    col_path, col_start, col_stop = st.columns([6, 1, 1])
    with col_path:
        st.text_input("Node.js Script Path", key="mcp_url")
    with col_start:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        if st.button("Start MCP", use_container_width=True, key="btn_start_mcp"):
            ok, msg = start_mcp(st.session_state["mcp_url"])
            st.success(msg) if ok else st.error(msg)
    with col_stop:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        if st.button("Stop MCP", use_container_width=True, key="btn_stop_mcp"):
            ok, msg = stop_mcp()
            st.success(msg) if ok else st.info(msg)

    running = st.session_state.get("mcp_running", False)
    st.caption("Status: " + ("🟢 Running" if running else "🔴 Stopped"))

    col_ft, _ = st.columns([2, 5])
    with col_ft:
        if st.button("Fetch Tools", use_container_width=True):
            if not st.session_state.get("mcp_running", False):
                st.error("MCP server is not running — start it first.")
            else:
                tools = discover_tools(st.session_state["mcp_url"])
                if tools:
                    # Clean up orphaned tool_chk_* keys from previous fetch (fix #9)
                    prev = st.session_state.get("mcp_tools", {})
                    old_keys = set(prev.keys()) - {t["name"] for t in tools}
                    for old in old_keys:
                        st.session_state.pop(f"tool_chk_{old}", None)
                    # Preserve existing checked/unchecked choices for tools that persist
                    st.session_state["mcp_tools"] = {
                        t["name"]: prev.get(t["name"], True)
                        for t in tools
                    }
                    st.success(f"Found: {', '.join(t['name'] for t in tools)}")
                else:
                    st.warning("No tools found — is the MCP server running?")

    # Tool toggles with descriptions as tooltips (fix #25)
    tools_dict = st.session_state.get("mcp_tools", {})
    if tools_dict:
        st.write("**Available MCP Tools**")
        # Reload descriptions for tooltips
        from core.mcp_manager import load_tools_from_json
        import os
        mcp_dir     = os.path.dirname(st.session_state.get("mcp_url", ""))
        desc_lookup = {
            t["name"]: t.get("description", "")
            for t in load_tools_from_json(mcp_dir)
        }

        ncols   = min(4, len(tools_dict))
        cols    = st.columns(ncols)
        updated = {}
        for idx, (name, enabled) in enumerate(tools_dict.items()):
            with cols[idx % ncols]:
                updated[name] = st.checkbox(
                    name,
                    value=enabled,
                    key=f"tool_chk_{name}",
                    help=desc_lookup.get(name) or None,
                )
        st.session_state["mcp_tools"] = updated
    else:
        st.info("Click **Fetch Tools** to discover tools from the MCP server.")


def _gguf_model_selector() -> None:
    col_dir, col_scan = st.columns([6, 1])
    with col_dir:
        st.text_input(
            "GGUF Models Directory", key="model_dir",
            help="Root directory scanned recursively — vocab-only files are excluded automatically",
        )
    with col_scan:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        if st.button("Scan", use_container_width=True, key="btn_scan_gguf"):
            found = scan_gguf_models(st.session_state["model_dir"])
            st.session_state["llm_models"] = found
            st.success(f"{len(found)} model(s) found") if found else st.warning("No inference GGUF models found")

    models = st.session_state.get("llm_models", [])
    if models:
        labels = [
            f"{m['name']}  ({m.get('size_gb', '?')} GB)"
            for m in models
        ]
        names  = [m["name"] for m in models]
        cur    = st.session_state.get("selected_model")
        idx    = names.index(cur) if cur in names else 0
        sel_label = st.selectbox(
            "Select GGUF Model", options=labels, index=idx,
            help="Vocab-only files are filtered out automatically. Size shown next to each model.",
        )
        sel = names[labels.index(sel_label)]
        st.session_state["selected_model"]      = sel
        sel_model = next(m for m in models if m["name"] == sel)
        st.session_state["selected_model_path"] = sel_model["path"]
        st.caption(f"Path: `{sel_model['path']}`  |  Size: `{sel_model.get('size_gb', '?')} GB`")

        # Warn if the running server is loaded with a different model
        url = st.session_state.get("llm_url", "")
        info = llama_server.get_server_info(url) if llama_server.is_running(url) else None
        if info and info.get("model_path"):
            import os as _os
            running_base  = _os.path.basename(info["model_path"])
            selected_base = _os.path.basename(sel_model["path"])
            if running_base != selected_base:
                st.warning(
                    f"⚠️  Running server has **{running_base}** loaded, "
                    f"but **{selected_base}** is selected. "
                    f"Click **Restart** to switch models."
                )
    else:
        st.info("Click **Scan** to discover GGUF models.")


def _ollama_model_selector() -> None:
    col_btn, _ = st.columns([2, 5])
    with col_btn:
        if st.button("Fetch Ollama Models", use_container_width=True):
            found = fetch_ollama_models(st.session_state["llm_url"])
            if found:
                st.session_state["llm_models"] = [
                    {"name": m["name"], "path": m["name"], "size_gb": m["size_gb"]}
                    for m in found
                ]
                st.success(f"{len(found)} model(s)")
            else:
                st.warning("No models — is Ollama running?")

    models = st.session_state.get("llm_models", [])
    if models:
        labels    = [f"{m['name']}  ({m.get('size_gb', '?')} GB)" for m in models]
        raw_names = [m["name"] for m in models]
        cur       = st.session_state.get("selected_model")
        idx       = raw_names.index(cur) if cur in raw_names else 0
        sel_label = st.selectbox("Select Ollama Model", options=labels, index=idx)
        sel_name  = raw_names[labels.index(sel_label)]
        st.session_state["selected_model"] = sel_name
    else:
        st.info("Click **Fetch Ollama Models** to list available models.")


# ── Metrics Setup ──────────────────────────────────────────────────────────────

_CAT_COLOUR = {
    "Validation":  "#6366f1",
    "Tool":        "#f59e0b",
    "Content":     "#06b6d4",
    "Performance": "#10b981",
    "Path":        "#8b5cf6",
    "Judge":       "#f43f5e",
}


def _cat_badge(cat: str) -> str:
    colour = _CAT_COLOUR.get(cat, "#64748b")
    return (
        f'<span style="background:{colour};color:#fff;padding:1px 7px;'
        f'border-radius:4px;font-size:0.7rem;font-weight:700">{cat}</span>'
    )


def _metrics_setup() -> None:
    # ── Validation command ─────────────────────────────────────────────────────
    st.subheader("Validation")
    st.text_input(
        "Validation Command",
        key="validation_command",
        help="Shell command run after evaluation to verify the task was completed",
        placeholder="e.g. cat /tmp/test",
    )

    st.write("**Fail Patterns**")
    st.caption("Strings that mark the run as failed even when exit code = 0")
    patterns: list = st.session_state.get("fail_patterns", [])
    col_inp, col_add = st.columns([5, 1])
    with col_inp:
        new_p = st.text_input(
            "New pattern", placeholder='e.g. "file not found"',
            label_visibility="collapsed", key="_new_fail_pattern",
        )
    with col_add:
        if st.button("Add", use_container_width=True, key="btn_add_pattern"):
            p = new_p.strip()
            if p and p not in patterns:
                st.session_state["fail_patterns"] = patterns + [p]
                st.rerun()

    if patterns:
        to_remove = None
        for i, p in enumerate(patterns):
            pc, pd = st.columns([8, 1])
            pc.code(p)
            if pd.button("✕", key=f"del_fp_{i}"):
                to_remove = i
        if to_remove is not None:
            del patterns[to_remove]
            st.session_state["fail_patterns"] = patterns
            st.rerun()

        # Confirmation for Clear All (fix #21)
        if st.session_state.get("_confirm_clear_patterns"):
            st.warning("Clear all fail patterns? This cannot be undone.")
            cc1, cc2, _ = st.columns([1, 1, 5])
            if cc1.button("Yes, clear", key="btn_confirm_clear_yes"):
                st.session_state["fail_patterns"] = []
                st.session_state["_confirm_clear_patterns"] = False
                st.rerun()
            if cc2.button("Cancel", key="btn_confirm_clear_no"):
                st.session_state["_confirm_clear_patterns"] = False
                st.rerun()
        else:
            if st.button("Clear All", key="btn_clear_patterns"):
                st.session_state["_confirm_clear_patterns"] = True
                st.rerun()

    st.divider()

    # ── Metrics matrix ─────────────────────────────────────────────────────────
    st.subheader("Metrics Matrix")
    st.caption(
        "Each metric is evaluated against run telemetry after execution. "
        "Inspired by [mcp-eval](https://github.com/lastmile-ai/mcp-eval) "
        "and [MCPEval](https://github.com/SalesforceAIResearch/MCPEval)."
    )

    matrix: list = st.session_state.get("metrics_matrix", [])

    # Reset with confirmation (fix #20)
    if st.session_state.get("_confirm_reset_metrics"):
        st.warning("Reset metrics to scenario defaults? All custom metrics will be lost.")
        cr1, cr2, _ = st.columns([1, 1, 5])
        if cr1.button("Yes, reset", key="btn_confirm_reset_yes"):
            from config.scenarios import SCENARIOS
            active   = st.session_state.get("active_scenario", "")
            defaults = SCENARIOS.get(active, {}).get("default_metrics", [])
            st.session_state["metrics_matrix"] = list(defaults)
            st.session_state["_confirm_reset_metrics"] = False
            st.rerun()
        if cr2.button("Cancel", key="btn_confirm_reset_no"):
            st.session_state["_confirm_reset_metrics"] = False
            st.rerun()
    else:
        col_rst, _ = st.columns([2, 5])
        with col_rst:
            if st.button("Reset to scenario defaults", key="btn_reset_metrics"):
                st.session_state["_confirm_reset_metrics"] = True
                st.rerun()

    # ── Add metric expander ────────────────────────────────────────────────────
    with st.expander("＋  Add metric"):
        type_options: list[str] = []
        for cat in CATEGORIES:
            for key, info in METRIC_TYPES.items():
                if info["category"] == cat:
                    type_options.append(f"{cat}: {info['label']}")

        # Auto-suggest next available ID (fix #22)
        existing_ids = {m.get("id", "") for m in matrix}
        suggested_id = next(
            f"M-{i:03d}" for i in range(1, 999)
            if f"M-{i:03d}" not in existing_ids
        )

        c1, c2, c3 = st.columns([2, 3, 4])
        new_id     = c1.text_input("ID",   value=suggested_id, key="_nm_id")
        new_name   = c2.text_input("Name", placeholder="My Check", key="_nm_name")
        type_label = c3.selectbox("Type",  options=type_options, key="_nm_type")

        selected_type_key = ""
        for key, info in METRIC_TYPES.items():
            if f"{info['category']}: {info['label']}" == type_label:
                selected_type_key = key
                break

        param_values: dict = {}
        if selected_type_key:
            type_info = METRIC_TYPES[selected_type_key]
            if type_info["params"]:
                st.caption(f"*{type_info['description']}*")
                pcols = st.columns(min(3, len(type_info["params"])))
                for i, param in enumerate(type_info["params"]):
                    with pcols[i % 3]:
                        pkey = f"_nm_p_{param['name']}"
                        if param["type"] == "int":
                            param_values[param["name"]] = st.number_input(
                                param["label"], value=int(param.get("default", 0)),
                                step=1, key=pkey,
                            )
                        elif param["type"] == "float":
                            param_values[param["name"]] = st.number_input(
                                param["label"], value=float(param.get("default", 0.0)),
                                step=0.1, format="%.1f", key=pkey,
                            )
                        elif param["type"] == "bool":
                            param_values[param["name"]] = st.checkbox(
                                param["label"],
                                value=bool(param.get("default", True)), key=pkey,
                            )
                        else:
                            param_values[param["name"]] = st.text_input(
                                param["label"],
                                value=str(param.get("default", "")), key=pkey,
                            )

        if st.button("Add Metric", key="btn_add_metric"):
            _errors = []
            _id   = new_id.strip()
            _name = new_name.strip()
            if not _name:
                _errors.append("Name is required.")
            if not _id:
                _errors.append("ID is required.")
            elif not re.match(r"^M-\d{3}$", _id):
                _errors.append("ID must match format M-NNN (e.g. M-001, M-042).")
            elif _id in existing_ids:
                _errors.append(f"ID **{_id}** is already used by another metric.")
            if selected_type_key:
                for param in METRIC_TYPES[selected_type_key]["params"]:
                    if param["type"] == "str":
                        val = str(param_values.get(param["name"], "")).strip()
                        if not val:
                            _errors.append(f"Parameter **{param['label']}** is required.")
            if _errors:
                for err in _errors:
                    st.error(err)
            else:
                matrix.append({
                    "id":      _id,
                    "name":    _name,
                    "type":    selected_type_key,
                    "enabled": True,
                    "params":  dict(param_values),
                })
                st.session_state["metrics_matrix"] = matrix
                st.rerun()

    # ── Matrix table ──────────────────────────────────────────────────────────
    if matrix:
        hcols = st.columns([1, 2, 3, 2, 4, 1])
        # Fix #23: use text not emoji for last header
        for lbl, col in zip(["✓", "ID", "Name", "Type", "Criterion", "Del"], hcols):
            col.markdown(f"**{lbl}**")
        st.divider()

        to_delete = None
        for i, m in enumerate(matrix):
            rc      = st.columns([1, 2, 3, 2, 4, 1])
            enabled = rc[0].checkbox(
                "Include", value=m.get("enabled", True),
                key=f"me_{i}_{m['id']}", label_visibility="collapsed",
            )
            matrix[i]["enabled"] = enabled
            rc[1].code(m["id"])
            rc[2].write(m["name"])
            cat = METRIC_TYPES.get(m.get("type", ""), {}).get("category", "—")
            rc[3].markdown(_cat_badge(cat), unsafe_allow_html=True)
            rc[4].caption(format_criterion(m))
            if rc[5].button("🗑", key=f"md_{i}"):
                to_delete = i

        if to_delete is not None:
            del matrix[to_delete]
            st.session_state["metrics_matrix"] = matrix
            st.rerun()

        st.session_state["metrics_matrix"] = matrix
    else:
        st.info("No metrics configured. Click **Reset to scenario defaults** or add one above.")
