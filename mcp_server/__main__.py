"""
Main entry point for the PubChem MCP server.
"""

import asyncio
import argparse
import sys
from mcp_server.server import app

def main():
    """Run the PubChem MCP server."""
    parser = argparse.ArgumentParser(description='PubChem MCP Server')
    parser.add_argument('--port', type=int, default=8000, help='Port to run the server on')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Host to bind the server to')
    parser.add_argument('--stdio', action='store_true', help='Run in stdio mode for MCP')
    
    args = parser.parse_args()
    
    if args.stdio:
        # Run in stdio mode for MCP
        app.run(transport='stdio')
    else:
        # Run as a web server
        import uvicorn
        uvicorn.run(
            "mcp_server.server:app",
            host=args.host,
            port=args.port,
            log_level="info"
        )

if __name__ == "__main__":
    main() 