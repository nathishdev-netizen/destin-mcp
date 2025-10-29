"""HTTP server wrapper for MCP server."""

import asyncio
import json
import logging
from typing import Any, Dict, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from .server import DestinMCPServer
from .config import get_settings

logger = logging.getLogger(__name__)

class MCPHTTPServer:
    """HTTP wrapper for MCP server."""
    
    def __init__(self):
        self.settings = get_settings()
        self.mcp_server = None  # Will be initialized in start_server
        self.app = FastAPI(
            title="Destin MCP Server",
            description="HTTP API for Destin MCP Server",
            version="1.0.0"
        )
        self._setup_middleware()
        self._setup_routes()
    
    def _setup_middleware(self):
        """Setup CORS and other middleware."""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def _setup_routes(self):
        """Setup HTTP routes."""
        
        @self.app.get("/")
        async def root():
            """Root endpoint with server info."""
            return {
                "name": "Destin MCP Server",
                "version": "1.0.0",
                "description": "Travel booking MCP server with hotel search and booking capabilities",
                "endpoints": {
                    "tools": "/tools",
                    "call_tool": "/call_tool",
                    "resources": "/resources",
                    "prompts": "/prompts",
                    "health": "/health"
                },
                "available_tools": [
                    "search_hotels",
                    "book_hotel", 
                    "get_hotel_info",
                    "get_booking_details",
                    "list_suppliers"
                ]
            }
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            return {"status": "healthy", "server": "running"}
        
        @self.app.get("/tools")
        async def list_tools():
            """List available tools."""
            try:
                # Get tools from the server's tools list
                tools_list = []
                for tool in self.mcp_server.tools:
                    tools_list.append({
                        "name": tool.name,
                        "description": tool.description,
                        "inputSchema": tool.inputSchema
                    })
                return {"tools": tools_list}
            except Exception as e:
                logger.error(f"Error listing tools: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/call_tool")
        async def call_tool(request: Request):
            """Call a tool via HTTP."""
            try:
                body = await request.json()
                tool_name = body.get("name")
                arguments = body.get("arguments", {})
                
                if not tool_name:
                    raise HTTPException(status_code=400, detail="Tool name is required")
                
                # Call the MCP server tool using direct method
                result = await self.mcp_server.call_tool_direct(tool_name, arguments)
                
                # Convert result to JSON-serializable format
                return {
                    "success": True,
                    "result": {
                        "content": [
                            {
                                "type": content.type,
                                "text": content.text
                            } for content in result.content
                        ]
                    }
                }
                
            except Exception as e:
                logger.error(f"Error calling tool {tool_name}: {e}")
                return JSONResponse(
                    status_code=500,
                    content={
                        "success": False,
                        "error": str(e),
                        "tool_name": tool_name
                    }
                )
        
        @self.app.get("/resources")
        async def list_resources():
            """List available resources."""
            try:
                # Get resources from the server's resources list
                resources_list = []
                for resource in self.mcp_server.resources:
                    resources_list.append({
                        "uri": resource.uri,
                        "name": resource.name,
                        "description": resource.description,
                        "mimeType": resource.mimeType
                    })
                return {"resources": resources_list}
            except Exception as e:
                logger.error(f"Error listing resources: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/prompts")
        async def list_prompts():
            """List available prompts."""
            try:
                # Get prompts from the server's prompts list
                prompts_list = []
                for prompt in self.mcp_server.prompts:
                    prompts_list.append({
                        "name": prompt.name,
                        "description": prompt.description,
                        "arguments": prompt.arguments
                    })
                return {"prompts": prompts_list}
            except Exception as e:
                logger.error(f"Error listing prompts: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # Hotel-specific convenience endpoints
        @self.app.post("/hotels/search")
        async def search_hotels(request: Request):
            """Search hotels endpoint."""
            try:
                body = await request.json()
                result = await self.mcp_server.call_tool_direct("search_hotels", body)
                return {"success": True, "data": result.content[0].text}
            except Exception as e:
                logger.error(f"Error searching hotels: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/hotels/book")
        async def book_hotel(request: Request):
            """Book hotel endpoint."""
            try:
                body = await request.json()
                result = await self.mcp_server.call_tool_direct("book_hotel", body)
                return {"success": True, "data": result.content[0].text}
            except Exception as e:
                logger.error(f"Error booking hotel: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/hotels/{hotel_id}")
        async def get_hotel_info(hotel_id: str, supplier: str = "dida"):
            """Get hotel information."""
            try:
                result = await self.mcp_server.call_tool_direct("get_hotel_info", {
                    "hotelId": hotel_id,
                    "supplier": supplier
                })
                return {"success": True, "data": result.content[0].text}
            except Exception as e:
                logger.error(f"Error getting hotel info: {e}")
                raise HTTPException(status_code=500, detail=str(e))

    async def start_server(self, host: str = "0.0.0.0", port: int = 8000):
        """Start the HTTP server."""
        # Initialize MCP server
        self.mcp_server = DestinMCPServer()
        await self.mcp_server.__aenter__()
        
        logger.info(f"🌐 Starting MCP HTTP Server on {host}:{port}")
        config = uvicorn.Config(
            app=self.app,
            host=host,
            port=port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()


async def run_http_server():
    """Run the HTTP server."""
    settings = get_settings()
    server = MCPHTTPServer()
    await server.start_server(
        host="0.0.0.0",
        port=int(settings.port) if hasattr(settings, 'port') else 8000
    )
