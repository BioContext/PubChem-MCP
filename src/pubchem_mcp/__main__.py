"""
Main entry point for the PubChem MCP server.
"""

from pubchem_mcp_server import mcp

if __name__ == "__main__":
    mcp.run(transport='stdio') 