"""Base class for MCP tools."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from mcp.types import CallToolResult, Tool

from ..utils import HTTPClient


class BaseTool(ABC):
    """Base class for all MCP tools."""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    @abstractmethod
    def get_tool_definitions(self) -> List[Tool]:
        """Return tool definitions for this tool class."""
        pass
    
    @abstractmethod
    async def execute_tool(self, name: str, arguments: Dict[str, Any]) -> CallToolResult:
        """Execute a specific tool by name."""
        pass
