"""
Canon Core Module

Contains configuration, logging, and core business logic.
"""

from canon.core.config import settings
from canon.core.logging import get_logger

__all__ = ["settings", "get_logger"]
