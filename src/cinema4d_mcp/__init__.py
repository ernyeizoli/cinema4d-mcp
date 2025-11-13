"""Cinema 4D MCP Server - Connect Claude to Cinema 4D"""

__version__ = "0.1.0"

import os

from . import server

mcp_app = server.mcp_app


def main() -> None:
    """Main entry point for the package."""
    transport = os.environ.get("C4D_MCP_TRANSPORT", "stdio")
    server.run_mcp_server(transport)


def main_wrapper():
    """Entry point for the wrapper script."""
    main()