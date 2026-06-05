"""
FastMCP Server for Nmap scanning with separated tool logic.
"""

import json
from mcp.server.fastmcp import FastMCP
from tools import scan_local_machine, file_creator

# Initialize the FastMCP Server
mcp = FastMCP("Local Nmap Scanner")


@mcp.tool()
def scan_local_machine_wrapper(scan_type: str = "quick") -> str:
    """
    Wrapper for scan_local_machine tool.
    
    :param scan_type: 'quick' (Top 100 ports), 'intense' (OS & service version details), or 'ping' (Host discovery)
    """
    return scan_local_machine(scan_type)


@mcp.tool()
def file_creator_wrapper(path: str, content: str) -> str:
    """
    Wrapper for file_creator tool.
    
    :param path: Target file path (can be relative or absolute)
    :param content: Content to write to the file
    """
    return file_creator(path, content)


if __name__ == "__main__":
    # Runs the server using standard input/output (Stdio) transport by default
    mcp.run()
