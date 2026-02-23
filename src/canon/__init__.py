"""
Canon - Centralized AI Agent Prompt Registry

This package provides the core service for managing AI agent prompts
in the NizamIQ ecosystem.
"""

__version__ = "1.0.0"
__author__ = "NizamIQ Team"

from canon.core.config import settings
from canon.core.logging import get_logger

__all__ = ["settings", "get_logger", "__version__"]
