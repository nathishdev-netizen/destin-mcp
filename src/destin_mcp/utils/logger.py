"""Logging utilities for Destin MCP Server."""

import logging
import sys
from typing import Optional

from ..config import get_settings


def setup_logger(name: Optional[str] = None) -> logging.Logger:
    """Set up and configure logger."""
    settings = get_settings()
    
    logger = logging.getLogger(name or __name__)
    
    # Avoid adding multiple handlers
    if logger.handlers:
        return logger
    
    # Set log level
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Create console handler (use stderr to avoid interfering with MCP protocol)
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(log_level)
    
    # Create formatter
    if settings.debug:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger
