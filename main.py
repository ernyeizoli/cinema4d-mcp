#!/usr/bin/env python3
"""
Cinema 4D MCP Server - Main entry point script

This script starts the Cinema 4D MCP server either directly or through
package imports, allowing it to be run both as a script and as a module.
"""

import argparse
import sys
import os
import socket
import logging
import traceback

# Configure logging to stderr
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)

logger = logging.getLogger("cinema4d-mcp")

# Add the src directory to the Python path
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
if os.path.exists(src_path):
    sys.path.insert(0, src_path)

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def log_to_stderr(message):
    """Log a message to stderr for Claude Desktop to capture."""
    print(message, file=sys.stderr, flush=True)


def main():
    """Main entry point function."""
    parser = argparse.ArgumentParser(description="Start the Cinema 4D MCP server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "streamable-http"],
        help="MCP transport to use (overrides C4D_MCP_TRANSPORT if provided)",
    )
    args = parser.parse_args()

    log_to_stderr("========== CINEMA 4D MCP SERVER STARTING ==========")
    log_to_stderr(f"Python version: {sys.version}")
    log_to_stderr(f"Current directory: {os.getcwd()}")
    log_to_stderr(f"Python path: {sys.path}")

    # Check if Cinema 4D socket is available
    c4d_host = os.environ.get("C4D_HOST", "127.0.0.1")
    c4d_port = int(os.environ.get("C4D_PORT", 5555))

    log_to_stderr(f"Checking connection to Cinema 4D on {c4d_host}:{c4d_port}")
    try:
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_socket.settimeout(5)  # Set 5 second timeout
        test_socket.connect((c4d_host, c4d_port))
        test_socket.close()
        log_to_stderr("✅ Successfully connected to Cinema 4D socket!")
    except Exception as e:
        log_to_stderr(f"❌ Could not connect to Cinema 4D socket: {e}")
        log_to_stderr(
            "   The server will still start, but Cinema 4D integration won't work!"
        )

    try:
        log_to_stderr("Importing cinema4d_mcp...")
        import cinema4d_mcp  # type: ignore[import]

        log_to_stderr("🚀 Starting Cinema 4D MCP Server...")

        # Provide connection details based on configured transport
        transport = (args.transport or os.environ.get("C4D_MCP_TRANSPORT", "stdio")).lower()
        os.environ["C4D_MCP_TRANSPORT"] = transport  # ensure package sees the chosen transport
        settings = cinema4d_mcp.mcp_app.settings

        if transport == "streamable-http":
            base_url = f"http://{settings.host}:{settings.port}{settings.streamable_http_path}"
            log_to_stderr(f"MCP Streamable HTTP endpoint: {base_url}")
            if settings.json_response:
                log_to_stderr("Clients POST JSON-RPC (initialize/call_tool) here and receive JSON responses.")
            else:
                log_to_stderr(
                    "Clients POST JSON-RPC here and must accept Server-Sent Events (text/event-stream) responses."
                )
            if settings.stateless_http:
                log_to_stderr("Stateless HTTP mode: each request creates an independent MCP session.")
            else:
                log_to_stderr("Stateful HTTP mode: reuse the returned mcp-session-id header on subsequent requests.")
        elif transport == "sse":
            sse_url = f"http://{settings.host}:{settings.port}{settings.sse_path}"
            post_url = f"http://{settings.host}:{settings.port}{settings.message_path}"
            log_to_stderr(f"MCP SSE endpoint (GET): {sse_url}")
            log_to_stderr(f"MCP message POST endpoint: {post_url}")
            log_to_stderr("Clients connect via SSE for server pushes and POST JSON-RPC to the message endpoint.")
        else:
            log_to_stderr("MCP STDIO transport active: connect using a client that launches this process (e.g. Claude Desktop).")

        cinema4d_mcp.main()
    except Exception as e:
        log_to_stderr(f"❌ Error starting server: {e}")
        log_to_stderr(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
