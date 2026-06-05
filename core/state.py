import streamlit as st
from config.defaults import (
    LLAMA_CPP_DEFAULT_URL, GGUF_MODELS_DIR,
    MCP_SCRIPT_PATH, DEFAULT_CONTEXT_SIZE,
    LLAMA_SERVER_BIN,
)
from config.scenarios import SCENARIOS, DEFAULT_SCENARIO


_SCENARIO = SCENARIOS[DEFAULT_SCENARIO]

_DEFAULTS: dict = {
    # Model / backend
    "backend_type":          "llama.cpp",
    "llm_url":               LLAMA_CPP_DEFAULT_URL,
    "model_dir":             GGUF_MODELS_DIR,
    "llm_models":            [],
    "selected_model":        None,
    "selected_model_path":   None,
    "context_size":          DEFAULT_CONTEXT_SIZE,

    # llama-server management
    "llama_server_bin":      LLAMA_SERVER_BIN,  # editable from UI (fix #29)
    "llama_server_running":  False,

    # MCP
    "mcp_url":       MCP_SCRIPT_PATH,
    "mcp_tools":     {},
    "mcp_running":   False,

    # Metrics setup
    "active_scenario":    DEFAULT_SCENARIO,
    "validation_command": _SCENARIO["validation_command"],
    "fail_patterns":      list(_SCENARIO["fail_patterns"]),
    "metrics_matrix":     list(_SCENARIO["default_metrics"]),

    # Execute
    "sys_prompt":        _SCENARIO["system_prompt"],
    "user_prompt":       _SCENARIO["user_prompt"],
    "run_logs":          [],
    "run_completed":     False,
    "cancel_requested":  False,   # set True by Cancel button (fix #16)

    # Telemetry (current run)
    "telemetry": {},

    # Run history — list of past telemetry dicts (fix #26)
    "run_history": [],

    # Internal trackers
    "_last_backend":       "llama.cpp",
    "_last_exec_scenario": DEFAULT_SCENARIO,
    # Prompt edit tracking for scenario-change warning (fix #10)
    "_prompts_user_edited": False,
}


def init_state() -> None:
    for key, default in _DEFAULTS.items():
        st.session_state.setdefault(key, default)
