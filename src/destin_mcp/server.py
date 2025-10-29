"""Main MCP server implementation for Destin Travel Tech."""

import asyncio
from typing import Any, Dict

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import ServerCapabilities
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    GetPromptRequest,
    GetPromptResult,
    ListPromptsRequest,
    ListPromptsResult,
    ListResourcesRequest,
    ListResourcesResult,
    ListToolsRequest,
    ListToolsResult,
    ReadResourceRequest,
    ReadResourceResult,
    TextContent,
)

from .config import get_settings
from .prompts import TravelPrompts
from .resources import TravelResources
from .tools import HotelTools
from .utils import HTTPClient, setup_logger

logger = setup_logger(__name__)


class DestinMCPServer:
    """Production-level MCP server for Destin travel tech APIs."""
    
    def __init__(self):
        self.settings = get_settings()
        self.server = Server(self.settings.server_name)
        self.http_client = None
        
        # Initialize components
        self.travel_prompts = TravelPrompts()
        self.travel_resources = TravelResources()
        self.hotel_tools = None  # Will be initialized with http_client
        
        self.setup_handlers()
    
    @property
    def tools(self):
        """Get list of available tools."""
        tools = []
        if self.hotel_tools:
            tools.extend(self.hotel_tools.get_tool_definitions())
        return tools
    
    @property
    def resources(self):
        """Get list of available resources."""
        return self.travel_resources.get_resource_list()
    
    @property
    def prompts(self):
        """Get list of available prompts."""
        return self.travel_prompts.get_prompt_list()
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.http_client = HTTPClient()
        await self.http_client.__aenter__()
        
        # Initialize tools with http_client
        self.hotel_tools = HotelTools(self.http_client)
        
        logger.info(f"Destin MCP Server {self.settings.server_version} initialized")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.http_client:
            await self.http_client.__aexit__(exc_type, exc_val, exc_tb)
        logger.info("Destin MCP Server shutdown complete")
    
    def setup_handlers(self):
        """Set up MCP request handlers."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            """List available tools."""
            logger.debug("Listing available tools")
            tools = []
            
            if self.hotel_tools:
                tools.extend(self.hotel_tools.get_tool_definitions())
            
            logger.info(f"Returning {len(tools)} tools")
            return ListToolsResult(tools=tools)
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict = None) -> CallToolResult:
            """Handle tool execution requests."""
            arguments = arguments or {}
            
            logger.info(f"Executing tool: {name} with arguments: {arguments}")
            
            try:
                # Route to appropriate tool handler
                if name in ["search_hotels", "book_hotel", "get_hotel_info", "get_booking_details", "list_suppliers"]:
                    return await self.hotel_tools.execute_tool(name, arguments)
                else:
                    return CallToolResult(
                        content=[TextContent(type="text", text=f"Unknown tool: {name}")]
                    )
            except Exception as e:
                logger.error(f"Error executing tool {name}: {str(e)}")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error executing tool {name}: {str(e)}")]
                )
    
    async def call_tool_direct(self, name: str, arguments: dict = None) -> CallToolResult:
        """Direct method to call tools (for HTTP API)."""
        arguments = arguments or {}
        
        logger.info(f"Direct tool call: {name} with arguments: {arguments}")
        
        try:
            # Route to appropriate tool handler
            if name in ["search_hotels", "book_hotel", "get_hotel_info", "get_booking_details", "list_suppliers"]:
                return await self.hotel_tools.execute_tool(name, arguments)
            else:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Unknown tool: {name}")]
                )
        except Exception as e:
            logger.error(f"Error executing tool {name}: {str(e)}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error executing tool {name}: {str(e)}")]
            )
        
        @self.server.list_resources()
        async def handle_list_resources() -> ListResourcesResult:
            """List available resources."""
            logger.debug("Listing available resources")
            resources = self.travel_resources.get_resource_list()
            logger.info(f"Returning {len(resources)} resources")
            return ListResourcesResult(resources=resources)
        
        @self.server.read_resource()
        async def handle_read_resource(request: ReadResourceRequest) -> ReadResourceResult:
            """Read a specific resource."""
            uri = request.params.uri
            logger.info(f"Reading resource: {uri}")
            
            try:
                contents = await self.travel_resources.get_resource_contents(uri)
                return ReadResourceResult(contents=[contents])
            except Exception as e:
                logger.error(f"Failed to read resource {uri}: {str(e)}")
                raise
        
        @self.server.list_prompts()
        async def handle_list_prompts() -> ListPromptsResult:
            """List available prompts."""
            logger.debug("Listing available prompts")
            prompts = self.travel_prompts.get_prompt_list()
            logger.info(f"Returning {len(prompts)} prompts")
            return ListPromptsResult(prompts=prompts)
        
        @self.server.get_prompt()
        async def handle_get_prompt(request: GetPromptRequest) -> GetPromptResult:
            """Get a specific prompt."""
            name = request.params.name
            arguments = request.params.arguments or {}
            
            logger.info(f"Getting prompt: {name}")
            logger.debug(f"Prompt arguments: {arguments}")
            
            try:
                return await self.travel_prompts.get_prompt(name, arguments)
            except Exception as e:
                logger.error(f"Failed to get prompt {name}: {str(e)}")
                raise


# Main function removed - use main.py as entry point
