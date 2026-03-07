"""
Canon SDK - Python client for the Canon Prompt Registry.

This package provides a Python SDK for interacting with the Canon
prompt registry service, including prompt retrieval, versioning,
and caching capabilities.

Example:
    >>> from canon_sdk import CanonClient
    >>> client = CanonClient("https://canon.nizamiq.com")
    >>> prompt = client.get_prompt("my-prompt")
    >>> print(prompt.content)
"""

from canon_sdk.client import CanonClient
from canon_sdk.models import Prompt, PromptVersion, PromptList
from canon_sdk.exceptions import (
    CanonError,
    CanonAPIError,
    CanonAuthError,
    CanonNotFoundError,
    CanonValidationError,
)

__version__ = "0.1.0"
__all__ = [
    "CanonClient",
    "Prompt",
    "PromptVersion",
    "PromptList",
    "CanonError",
    "CanonAPIError",
    "CanonAuthError",
    "CanonNotFoundError",
    "CanonValidationError",
]
