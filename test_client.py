#!/usr/bin/env python3
"""
Test client for PubChem MCP server.
"""

import asyncio
import sys
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters


async def main():
    """Run a test of the PubChem MCP server."""
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "mcp_server"]
    )
    
    print("Starting client...")
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            print("Initializing session...")
            await session.initialize()
            print("Session initialized!")
            
            # List available tools
            tools = await session.list_tools()
            print(f"Available tools: {[tool.name for tool in tools]}")
            
            # Test search_compound tool
            print("\nSearching for aspirin...")
            result = await session.call_tool("search_compound", {"query": "aspirin", "max_results": 2})
            print(f"Search result: {result}")
            
            # Test get_compound_properties tool if available
            if "get_compound_properties" in [tool.name for tool in tools]:
                print("\nGetting properties for aspirin (CID 2244)...")
                properties = await session.call_tool("get_compound_properties", {"cid": 2244})
                print(f"Properties: {properties}")


if __name__ == "__main__":
    asyncio.run(main()) 