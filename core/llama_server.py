import os
import subprocess
import time
import requests
import streamlit as st
from config.defaults import LLAMA_SERVER_BIN, LLAMA_CPP_DEFAULT_URL


def is_running(url: str = LLAMA_CPP_DEFAULT_URL, timeout: float = 2.0) -> bool:
    """Return True if llama-server is responding at url/health."""
    try:
        r = requests.get(url.rstrip("/") + "/health", timeout=timeout)
        return r.ok
    except Exception:
        return False


def get_server_info(url: str = LLAMA_CPP_DEFAULT_URL) -> dict | None:
    """
    Return {n_ctx, model_path} from the running server, or None. (fix #28)
    Reads /props endpoint: default_generation_settings.n_ctx + model_path.
    """
    try:
        r = requests.get(url.rstrip("/") + "/props", timeout=3)
        if not r.ok:
            return None
        d = r.json()
        return {
            "n_ctx":      d.get("default_generation_settings", {}).get("n_ctx"),
            "model_path": d.get("model_path", ""),
        }
    except Exception:
        return None


def get_n_ctx(url: str = LLAMA_CPP_DEFAULT_URL) -> int | None:
    """Return the actual n_ctx of the running server, or None."""
    info = get_server_info(url)
    return info["n_ctx"] if info else None


def _kill_port(port: int) -> None:
    """Kill any process currently listening on the given TCP port."""
    try:
        subprocess.run(["fuser", "-k", f"{port}/tcp"],
                       capture_output=True, timeout=5)
        time.sleep(0.8)
    except Exception:
        pass


def start(
    model_path:   str,
    context_size: int = 4096,
    host:         str = "127.0.0.1",
    port:         int = 8080,
    binary:       str | None = None,
) -> tuple[bool, str]:
    """
    Launch llama-server as a background subprocess.

    Checks the running server's n_ctx if one is already up:
    - n_ctx >= context_size → reuse
    - n_ctx <  context_size → kill and restart with correct size

    binary defaults to LLAMA_SERVER_BIN but can be overridden (fix #29).
    """
    url = f"http://{host}:{port}"
    bin_path = binary or st.session_state.get("llama_server_bin", LLAMA_SERVER_BIN)

    if is_running(url):
        info        = get_server_info(url)
        current_ctx = info["n_ctx"] if info else None
        running_model = (info or {}).get("model_path", "")
        # Compare by basename so absolute-path differences don't matter
        model_matches = (
            not model_path
            or os.path.basename(running_model) == os.path.basename(model_path)
        )
        if current_ctx is not None and current_ctx >= context_size and model_matches:
            st.session_state["llama_server_running"] = True
            return True, f"Already running at {url} (n_ctx={current_ctx}, model matches)"
        if not model_matches:
            action = (
                f"Restarting: loaded model is '{os.path.basename(running_model)}', "
                f"requested '{os.path.basename(model_path)}'"
            )
        else:
            action = (
                f"Restarting: n_ctx={current_ctx} < requested {context_size}"
                if current_ctx else "Restarting (could not read n_ctx)"
            )
        proc = st.session_state.get("llama_server_process")
        if proc:
            try:
                proc.terminate()
            except Exception:
                pass
            st.session_state.pop("llama_server_process", None)
        _kill_port(port)
    else:
        action = "Starting"

    try:
        proc = subprocess.Popen(
            [
                bin_path,
                "--model",    model_path,
                "--ctx-size", str(context_size),
                "--host",     host,
                "--port",     str(port),
                "--jinja",
                "--parallel", "1",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        st.session_state["llama_server_process"] = proc
        st.session_state["llama_server_running"] = False
        st.session_state["llama_server_url"]     = url
        return True, f"{action} (pid {proc.pid}) — loading model…"
    except FileNotFoundError:
        return False, f"llama-server not found: {bin_path}"
    except Exception as e:
        return False, str(e)


def stop(host: str = "127.0.0.1", port: int = 8080) -> tuple[bool, str]:
    """Terminate the tracked process and kill the port so orphaned servers are removed too."""
    url  = f"http://{host}:{port}"
    proc = st.session_state.get("llama_server_process")
    if proc:
        try:
            proc.terminate()
            proc.wait(timeout=3)
        except Exception:
            pass
        st.session_state.pop("llama_server_process", None)
    # Kill the port regardless — handles externally-started or orphaned servers
    _kill_port(port)
    st.session_state["llama_server_running"] = False
    return True, "Server stopped"


def poll_ready(url: str = LLAMA_CPP_DEFAULT_URL) -> bool:
    """
    Non-blocking readiness check.
    Updates llama_server_running in session_state and returns True when healthy.
    Always polls regardless of whether we have a tracked process (fix #12).
    """
    ready = is_running(url)
    st.session_state["llama_server_running"] = ready
    return ready
