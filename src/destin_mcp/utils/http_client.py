"""HTTP client utilities for API communication."""

import json
from typing import Any, Dict, Optional
from urllib.parse import urljoin

import httpx

from ..config import get_settings
from .logger import setup_logger

logger = setup_logger(__name__)


class HTTPClient:
    """HTTP client for travel tech APIs."""
    
    def __init__(self):
        self.settings = get_settings()
        self.client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.settings.timeout_seconds),
            headers={
                "Content-Type": "application/json",
                "User-Agent": self.settings.user_agent
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.client:
            await self.client.aclose()
    
    async def make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        supplier: Optional[str] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to travel API with error handling."""
        if not self.client:
            raise Exception("HTTP client not initialized")
        
        url = urljoin(self.settings.base_url, endpoint)
        supplier = supplier or self.settings.default_supplier
        
        # Replace supplier placeholder in URL
        url = url.replace("{supplier}", supplier)
        
        try:
            logger.info(f"Making {method} request to {url}")
            if data and self.settings.debug:
                logger.debug(f"Request data: {json.dumps(data, indent=2)}")
            
            if method.upper() == "GET":
                response = await self.client.get(url)
            elif method.upper() == "POST":
                response = await self.client.post(url, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"Request successful. Status: {response.status_code}")
            return result
            
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except httpx.RequestError as e:
            error_msg = f"Request failed: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
