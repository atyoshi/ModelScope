import streamlit as st
from config.defaults import GGUF_MODELS_DIR, DEFAULT_CONTEXT_SIZE
from config.scenarios import SCENARIOS, DEFAULT_SCENARIO
from core.state import init_state
from core.models import scan_gguf_models
from core import llama_server
from ui.styles import inject
from ui import config_tab, execute_tab, dashboard_tab

st.set_page_config(
    page_title="SPARK Evaluator",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject()
init_state()

# ── Scenario state sync — runs BEFORE any widgets are created ─────────────────
# Syncs prompts, validation, fail_patterns, and metrics when scenario changes.
# Guards against overwriting user-edited prompts (fix #10).
_active = st.session_state.get("active_scenario", DEFAULT_SCENARIO)
if st.session_state.get("_last_exec_scenario") != _active:
    _s = SCENARIOS.get(_active, SCENARIOS[DEFAULT_SCENARIO])
    _edited = st.session_state.get("_prompts_user_edited", False)
    if not _edited:
        st.session_state["sys_prompt"]  = _s["system_prompt"]
        st.session_state["user_prompt"] = _s["user_prompt"]
    # Always sync validation / metrics (these aren't free-text authored by user)
    st.session_state["validation_command"] = _s["validation_command"]
    st.session_state["fail_patterns"]      = list(_s["fail_patterns"])
    st.session_state["metrics_matrix"]     = list(_s["default_metrics"])
    st.session_state["_last_exec_scenario"] = _active
    st.session_state["_prompts_user_edited"] = False

# ── No automatic model loading ──────────────────────────────────────────────
# User must explicitly choose a model before any server starts.
# Poll running server only (fix #7: don't auto-start, just check if already running).
llama_server.poll_ready(st.session_state.get("llm_url", ""))

st.markdown("<h1 class='spark-title'>SPARK EVAL</h1>", unsafe_allow_html=True)
st.caption("LLM & MCP Tool Evaluation Platform")

tab_cfg, tab_exec, tab_dash = st.tabs([
    "⚙  Configuration",
    "▶  Execute Evaluation",
    "📊  Analytical Dashboard",
])

with tab_cfg:
    config_tab.render()

with tab_exec:
    execute_tab.render()

with tab_dash:
    dashboard_tab.render()
