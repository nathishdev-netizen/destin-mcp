#!/bin/bash

# Entrypoint script for Destin MCP Server
set -e

echo "🚀 Starting Destin MCP Server..."
echo "Environment: $(python --version)"
echo "Working directory: $(pwd)"
echo "Python path: $PYTHONPATH"

# Check which mode to run in
if [ "${MCP_MODE:-stdio}" = "http" ]; then
    echo "📡 Starting in HTTP REST API mode on port ${PORT:-8000}..."
    echo "🌐 HTTP API will be available at http://0.0.0.0:${PORT:-8000}"
    echo "📋 Available endpoints:"
    echo "  - GET  /           - Server info"
    echo "  - GET  /health     - Health check"
    echo "  - GET  /tools      - List tools"
    echo "  - POST /call_tool  - Call MCP tool"
    echo "  - POST /hotels/search - Search hotels"
    echo "  - POST /hotels/book   - Book hotel"
    
    # Run the HTTP REST API server
    python -c "
import asyncio
import sys
sys.path.append('src')
from destin_mcp.http_server import run_http_server

asyncio.run(run_http_server())
"
elif [ "${MCP_MODE:-stdio}" = "mcp-http" ]; then
    echo "🚀 Starting in MCP-over-HTTP mode on port ${PORT:-8000}..."
    echo "🌐 MCP Protocol over HTTP available at http://0.0.0.0:${PORT:-8000}"
    echo "📡 Ready for Claude Desktop Pro Custom Connectors"
    echo "📋 MCP endpoints:"
    echo "  - GET  /           - Server info"
    echo "  - POST /mcp        - MCP JSON-RPC requests"
    echo "  - GET  /sse/{id}   - Server-Sent Events"
    echo "  - GET  /health     - Health check"
    
    # Run the MCP-over-HTTP transport server
    python -c "
import asyncio
import sys
sys.path.append('src')
from destin_mcp.transports.http_transport import run_mcp_http_transport

asyncio.run(run_mcp_http_transport())
"
else
    echo "📨 Starting in STDIO mode..."
    echo "💡 This mode is for MCP protocol communication"
    echo "🔗 Connect via MCP client (Claude Desktop local, MCP Inspector, etc.)"
    
    # Run the actual MCP server
    python main.py
fi
