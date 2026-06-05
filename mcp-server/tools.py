"""
Tool implementations for MCP Nmap Server.
Contains the actual logic for tools that can be imported by both Python and Node servers.
"""

import json
import subprocess
import os
from threading import Lock
from pathlib import Path

# Shared state for scan management (if needed by Python server)
_active_scan_process = None
_cancel_requested = False
_process_lock = Lock()


def scan_local_machine(scan_type: str = "quick") -> str:
    """
    Scans the local machine (localhost/127.0.0.1) safely using Nmap.
    
    :param scan_type: 'quick' (Top 100 ports), 'intense' (OS & service version details), or 'ping' (Host discovery)
    :return: JSON string with scan results or error
    """
    target = "127.0.0.1"
    
    # Strictly define allowed configurations to enforce programmatic validation
    if scan_type == "quick":
        args = ["nmap", "-F", target]
    elif scan_type == "intense":
        args = ["nmap", "-T4", "-A", "-v", target]
    elif scan_type == "ping":
        args = ["nmap", "-sn", target]
    else:
        return json.dumps({"status": "error", "message": f"Unknown or unauthorized scan type: {scan_type}"})

    global _active_scan_process, _cancel_requested
    with _process_lock:
        _cancel_requested = False

    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    with _process_lock:
        _active_scan_process = process

    try:
        stdout, stderr = process.communicate(timeout=60)

        if _cancel_requested:
            return json.dumps({
                "status": "error",
                "message": "Scan was cancelled by the user.",
            })

        if process.returncode != 0:
            return json.dumps({
                "status": "error",
                "message": "Nmap command execution failed.",
                "stderr": stderr,
            })

        return json.dumps({
            "status": "success",
            "scan_type": scan_type,
            "raw_output": stdout,
        })
    except subprocess.TimeoutExpired:
        process.kill()
        process.communicate()
        return json.dumps({
            "status": "error",
            "message": "The network scan timed out before completion.",
        })
    except FileNotFoundError:
        return json.dumps({
            "status": "error",
            "message": "Nmap binary not found on your system PATH. Verify installation.",
        })
    finally:
        with _process_lock:
            _active_scan_process = None


def file_creator(path: str, content: str) -> str:
    """
    Resolves directories recursively and writes the specified content into the target file path.
    
    :param path: Target file path (can be relative or absolute)
    :param content: Content to write to the file
    :return: JSON string with success status or error message
    """
    try:
        # Convert to Path object for easier handling
        file_path = Path(path)
        
        # Resolve the path (making it absolute and resolving any '..' or '.')
        resolved_path = file_path.resolve()
        
        # Ensure parent directory exists
        resolved_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write content to file
        resolved_path.write_text(content, encoding='utf-8')
        
        return json.dumps({
            "status": "success",
            "message": f"File created successfully at {resolved_path}",
            "path": str(resolved_path),
            "bytes_written": len(content.encode('utf-8'))
        })
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Failed to create file: {str(e)}",
            "path": path
        })


# For backward compatibility or direct use
cancel_scan_func = None  # Will be set by server if needed

def cancel_scan() -> bool:
    """Terminate an active scan process if one is running."""
    global _cancel_requested
    with _process_lock:
        process = _active_scan_process
        _cancel_requested = True

    if not process:
        return False

    try:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
        return True
    except Exception:
        return False
