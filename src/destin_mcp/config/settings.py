"""Configuration settings for Destin MCP Server."""

import os
from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # API Configuration
    base_url: str = Field(
        default="https://supplier-apis-for-travel-tech.vercel.app",
        description="Base URL for travel tech APIs"
    )
    default_supplier: str = Field(
        default="dida",
        description="Default hotel supplier"
    )
    timeout_seconds: int = Field(
        default=30,
        description="HTTP request timeout in seconds"
    )
    
    # Server Configuration
    server_name: str = Field(
        default="destin-travel-server",
        description="MCP server name"
    )
    server_version: str = Field(
        default="1.0.0",
        description="MCP server version"
    )
    
    # Logging Configuration
    log_level: str = Field(
        default="INFO",
        description="Logging level"
    )
    debug: bool = Field(
        default=False,
        description="Enable debug mode"
    )
    
    # HTTP Client Configuration
    user_agent: str = Field(
        default="Destin-MCP-Server/1.0",
        description="User agent for HTTP requests"
    )
    max_retries: int = Field(
        default=3,
        description="Maximum number of HTTP retries"
    )
    
    # Rate Limiting
    rate_limit_requests: int = Field(
        default=100,
        description="Requests per minute limit"
    )
    rate_limit_window: int = Field(
        default=60,
        description="Rate limit window in seconds"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()
