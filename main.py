#!/usr/bin/env python3
"""
Main entry point for Destin MCP Server.
"""

import asyncio
import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

async def main():
    """Main entry point."""
    from destin_mcp.server import DestinMCPServer
    from destin_mcp.config import get_settings
    from mcp.server.stdio import stdio_server
    
    settings = get_settings()
    
    async with DestinMCPServer() as server_instance:
        # Run the server with stdio transport
        async with stdio_server() as (read_stream, write_stream):
            await server_instance.server.run(
                read_stream,
                write_stream,
                server_instance.server.create_initialization_options()
            )

if __name__ == "__main__":
    asyncio.run(main())
