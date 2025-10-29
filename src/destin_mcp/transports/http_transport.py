"""HTTP transport implementation for MCP protocol."""

import asyncio
import json
import logging
from typing import Any, Dict, Optional, List
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from mcp.types import (
    JSONRPCRequest,
    JSONRPCResponse,
    JSONRPCNotification,
    JSONRPCError,
    InitializeRequest,
    InitializeResult,
    ListToolsRequest,
    ListToolsResult,
    CallToolRequest,
    CallToolResult,
    ListResourcesRequest,
    ListResourcesResult,
    ListPromptsRequest,
    ListPromptsResult,
)

from ..server import DestinMCPServer

logger = logging.getLogger(__name__)


class MCPHTTPTransport:
    """HTTP transport for MCP protocol using Server-Sent Events."""
    
    def __init__(self, mcp_server: DestinMCPServer):
        self.mcp_server = mcp_server
        self.app = FastAPI(
            title="Destin MCP Server - HTTP Transport",
            description="MCP protocol over HTTP with SSE support for Claude Desktop Pro",
            version="1.0.0"
        )
        self._setup_middleware()
        self._setup_routes()
        self._client_connections: Dict[str, asyncio.Queue] = {}
    
    def _setup_middleware(self):
        """Setup CORS and other middleware."""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["https://claude.ai", "https://claude.com", "*"],
            allow_credentials=True,
            allow_methods=["GET", "POST", "OPTIONS"],
            allow_headers=["*"],
        )
    
    def _setup_routes(self):
        """Setup MCP protocol routes."""
        
        @self.app.get("/")
        async def root():
            """MCP server info endpoint."""
            return {
                "name": "Destin MCP Server",
                "version": "1.0.0",
                "protocol_version": "2024-11-05",
                "description": "Travel booking MCP server with hotel search and booking capabilities",
                "transport": "http+sse",
                "capabilities": {
                    "tools": True,
                    "resources": True,
                    "prompts": True,
                    "logging": False
                },
                "endpoints": {
                    "mcp": "/mcp",
                    "sse": "/sse/{client_id}"
                }
            }
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            return {"status": "healthy", "transport": "mcp-http"}
        
        @self.app.post("/mcp")
        async def handle_mcp_request(request: Request):
            """Handle MCP JSON-RPC requests."""
            try:
                body = await request.json()
                logger.info(f"Received MCP request: {body.get('method', 'unknown')}")
                
                # Handle different MCP methods
                method = body.get("method")
                params = body.get("params", {})
                request_id = body.get("id")
                
                if method == "initialize":
                    result = await self._handle_initialize(params)
                elif method == "tools/list":
                    result = await self._handle_list_tools(params)
                elif method == "tools/call":
                    result = await self._handle_call_tool(params)
                elif method == "resources/list":
                    result = await self._handle_list_resources(params)
                elif method == "prompts/list":
                    result = await self._handle_list_prompts(params)
                else:
                    raise HTTPException(status_code=400, detail=f"Unknown method: {method}")
                
                # Return JSON-RPC response
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": result
                }
                
                return response
                
            except Exception as e:
                logger.error(f"Error handling MCP request: {e}")
                error_response = {
                    "jsonrpc": "2.0",
                    "id": body.get("id") if 'body' in locals() else None,
                    "error": {
                        "code": -32603,
                        "message": str(e)
                    }
                }
                return Response(
                    content=json.dumps(error_response),
                    status_code=500,
                    media_type="application/json"
                )
        
        @self.app.get("/sse/{client_id}")
        async def sse_endpoint(client_id: str):
            """Server-Sent Events endpoint for real-time communication."""
            async def event_stream():
                # Create client queue
                client_queue = asyncio.Queue()
                self._client_connections[client_id] = client_queue
                
                try:
                    # Send initial connection event
                    yield f"data: {json.dumps({'type': 'connected', 'client_id': client_id})}\n\n"
                    
                    # Keep connection alive and send events
                    while True:
                        try:
                            # Wait for events with timeout
                            event = await asyncio.wait_for(client_queue.get(), timeout=30.0)
                            yield f"data: {json.dumps(event)}\n\n"
                        except asyncio.TimeoutError:
                            # Send keep-alive ping
                            yield f"data: {json.dumps({'type': 'ping'})}\n\n"
                        
                except asyncio.CancelledError:
                    logger.info(f"SSE connection closed for client {client_id}")
                finally:
                    # Clean up client connection
                    if client_id in self._client_connections:
                        del self._client_connections[client_id]
            
            return StreamingResponse(
                event_stream(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Cache-Control"
                }
            )
    
    async def _handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP initialize request."""
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {
                    "listChanged": True
                },
                "resources": {
                    "listChanged": True,
                    "subscribe": False
                },
                "prompts": {
                    "listChanged": True
                }
            },
            "serverInfo": {
                "name": "Destin MCP Server",
                "version": "1.0.0"
            }
        }
    
    async def _handle_list_tools(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/list request."""
        tools = []
        if hasattr(self.mcp_server, 'tools') and self.mcp_server.tools:
            tools.extend([tool.model_dump() for tool in self.mcp_server.tools])
        
        return {"tools": tools}
    
    async def _handle_call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/call request."""
        name = params.get("name")
        arguments = params.get("arguments", {})
        
        if not name:
            raise ValueError("Tool name is required")
        
        # Call the tool using the MCP server
        result = await self.mcp_server.call_tool_direct(name, arguments)
        
        # Convert to MCP format
        return {
            "content": [
                {
                    "type": content.type,
                    "text": content.text
                } for content in result.content
            ]
        }
    
    async def _handle_list_resources(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resources/list request."""
        resources = []
        if self.mcp_server.travel_resources:
            resources.extend([resource.model_dump() for resource in self.mcp_server.resources])
        
        return {"resources": resources}
    
    async def _handle_list_prompts(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle prompts/list request."""
        prompts = []
        if self.mcp_server.travel_prompts:
            prompts.extend([prompt.model_dump() for prompt in self.mcp_server.prompts])
        
        return {"prompts": prompts}
    
    async def broadcast_to_clients(self, event: Dict[str, Any]):
        """Broadcast event to all connected clients."""
        if not self._client_connections:
            return
        
        disconnected_clients = []
        for client_id, queue in self._client_connections.items():
            try:
                await queue.put(event)
            except Exception as e:
                logger.warning(f"Failed to send event to client {client_id}: {e}")
                disconnected_clients.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            del self._client_connections[client_id]
    
    async def start_server(self, host: str = "0.0.0.0", port: int = 8000):
        """Start the HTTP transport server."""
        logger.info(f"🌐 Starting MCP HTTP Transport on {host}:{port}")
        logger.info("📡 Ready for Claude Desktop Pro Custom Connectors")
        
        config = uvicorn.Config(
            app=self.app,
            host=host,
            port=port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()


async def run_mcp_http_transport():
    """Run the MCP HTTP transport server."""
    # Initialize MCP server
    mcp_server = DestinMCPServer()
    await mcp_server.__aenter__()
    
    # Create and start HTTP transport
    transport = MCPHTTPTransport(mcp_server)
    await transport.start_server(
        host="0.0.0.0",
        port=8000
    )
