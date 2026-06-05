import json
import os
import subprocess
import streamlit as st
import requests
from config.defaults import MCP_SERVER_BASE_URL


def start_mcp(script_path: str) -> tuple[bool, str]:
    if not os.path.exists(script_path):
        return False, f"Script not found: {script_path}"
    try:
        proc = subprocess.Popen(
            ["node", script_path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        st.session_state["mcp_process"] = proc
        st.session_state["mcp_running"] = True
        return True, f"Started (pid {proc.pid})"
    except FileNotFoundError:
        return False, "node not found — is Node.js installed?"
    except Exception as e:
        return False, str(e)


def stop_mcp() -> tuple[bool, str]:
    proc = st.session_state.get("mcp_process")
    if not proc:
        return False, "No MCP server running"
    try:
        proc.terminate()
        st.session_state.pop("mcp_process", None)
        st.session_state["mcp_running"] = False
        return True, "Stopped"
    except Exception as e:
        return False, str(e)


def load_tools_from_json(mcp_dir: str) -> list[dict]:
    """
    Read tools from tools.json.  Returns list of {name, description} dicts. (fix #25)
    """
    path = os.path.join(mcp_dir, "tools.json")
    if not os.path.exists(path):
        return []
    try:
        with open(path) as fh:
            data = json.load(fh)
        if isinstance(data, list):
            return [
                {"name": t["name"], "description": t.get("description", "")}
                for t in data if isinstance(t, dict) and "name" in t
            ]
        if isinstance(data, dict):
            return [{"name": k, "description": ""} for k in data]
    except Exception:
        pass
    return []


def fetch_tools_from_json(mcp_dir: str) -> list[str]:
    """Return just tool names (backwards compat)."""
    return [t["name"] for t in load_tools_from_json(mcp_dir)]


def fetch_tools_from_server(base_url: str = MCP_SERVER_BASE_URL) -> list[str]:
    """
    Ask the running MCP server for its tool list via JSON-RPC.
    Uses a short 1 s timeout so Fetch Tools doesn't hang when MCP is down. (fix #3)
    """
    try:
        init_resp = requests.post(
            f"{base_url}/sse",
            json={
                "jsonrpc": "2.0", "id": 1, "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "spark-eval", "version": "1.0"},
                },
            },
            timeout=1,   # was 5 s — reduced to 1 s (fix #3)
        )
        if not init_resp.ok:
            return []
        session_id = init_resp.headers.get("mcp-session-id", "")
        headers    = {"mcp-session-id": session_id} if session_id else {}

        list_resp = requests.post(
            f"{base_url}/sse",
            json={"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
            headers=headers,
            timeout=1,
        )
        if not list_resp.ok:
            return []
        result = list_resp.json().get("result", {})
        return [t["name"] for t in result.get("tools", []) if isinstance(t, dict)]
    except Exception:
        return []


def discover_tools(mcp_script_path: str) -> list[dict]:
    """
    Try live server first (1 s timeout), fall back to tools.json.
    Returns list of {name, description} dicts. (fix #25)
    """
    live_names = fetch_tools_from_server()
    if live_names:
        # Got live names — try to enrich with descriptions from tools.json
        mcp_dir   = os.path.dirname(mcp_script_path)
        json_tools = {t["name"]: t.get("description", "") for t in load_tools_from_json(mcp_dir)}
        return [
            {"name": n, "description": json_tools.get(n, "")}
            for n in live_names
        ]
    # Fall back to tools.json entirely
    return load_tools_from_json(os.path.dirname(mcp_script_path))


def call_mcp_tool(
    tool_name: str,
    tool_args: dict,
    base_url: str = MCP_SERVER_BASE_URL,
) -> dict:
    """Call a tool on the MCP server and return its result dict."""
    try:
        init_resp = requests.post(
            f"{base_url}/sse",
            json={
                "jsonrpc": "2.0", "id": 1, "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "spark-eval", "version": "1.0"},
                },
            },
            timeout=3,
        )
        session_id = init_resp.headers.get("mcp-session-id", "")
        headers    = {"mcp-session-id": session_id} if session_id else {}

        call_resp = requests.post(
            f"{base_url}/sse",
            json={
                "jsonrpc": "2.0", "id": 3,
                "method": "tools/call",
                "params": {"name": tool_name, "arguments": tool_args},
            },
            headers=headers,
            timeout=30,
        )
        data = call_resp.json()
        if "error" in data:
            return {"error": data["error"].get("message", str(data["error"]))}
        return data.get("result", {})
    except Exception as e:
        return {"error": str(e)}
