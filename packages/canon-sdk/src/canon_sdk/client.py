"""
Canon SDK Client

Main client class for interacting with the Canon Prompt Registry.
"""

from __future__ import annotations

import functools
import time
from typing import Any

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from canon_sdk.exceptions import (
    CanonAPIError,
    CanonAuthError,
    CanonConnectionError,
    CanonNotFoundError,
    CanonTimeoutError,
    CanonValidationError,
)
from canon_sdk.models import (
    Prompt,
    PromptCreateRequest,
    PromptList,
    PromptUpdateRequest,
    TagUpdateRequest,
    VersionCreateRequest,
)


class CanonClient:
    """
    Client for the Canon Prompt Registry API.
    
    This client provides methods for retrieving and managing prompts
    in the Canon registry, with built-in caching, retry logic, and
    comprehensive error handling.
    
    Args:
        base_url: The Canon service URL (e.g., "https://canon.nizamiq.com")
        api_token: Optional API token for authentication
        timeout: Request timeout in seconds (default: 30)
        max_retries: Maximum number of retries for failed requests (default: 3)
        enable_caching: Whether to enable in-memory caching (default: True)
        cache_ttl: Cache time-to-live in seconds (default: 300)
    
    Example:
        >>> client = CanonClient("https://canon.nizamiq.com", api_token="secret")
        >>> prompt = client.get_prompt("my-prompt")
        >>> print(prompt.current_version)
    """
    
    def __init__(
        self,
        base_url: str,
        api_token: str | None = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        enable_caching: bool = True,
        cache_ttl: float = 300.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_token = api_token
        self.timeout = timeout
        self.max_retries = max_retries
        self.enable_caching = enable_caching
        self.cache_ttl = cache_ttl
        
        # Initialize cache
        self._cache: dict[str, tuple[Any, float]] = {}
        
        # Initialize HTTP client
        headers = {"Accept": "application/json"}
        if api_token:
            headers["Authorization"] = f"Bearer {api_token}"
        
        self._client = httpx.Client(
            base_url=self.base_url,
            headers=headers,
            timeout=timeout,
        )
    
    def _get_cache_key(self, method: str, *args: Any, **kwargs: Any) -> str:
        """Generate a cache key for a method call."""
        key_parts = [method] + [str(a) for a in args] + [f"{k}={v}" for k, v in sorted(kwargs.items())]
        return ":".join(key_parts)
    
    def _get_from_cache(self, key: str) -> Any | None:
        """Get a value from cache if it exists and hasn't expired."""
        if not self.enable_caching or key not in self._cache:
            return None
        
        value, timestamp = self._cache[key]
        if time.time() - timestamp > self.cache_ttl:
            del self._cache[key]
            return None
        return value
    
    def _set_cache(self, key: str, value: Any) -> None:
        """Set a value in the cache."""
        if self.enable_caching:
            self._cache[key] = (value, time.time())
    
    def _clear_cache(self, prefix: str | None = None) -> None:
        """Clear cache, optionally only entries matching a prefix."""
        if prefix is None:
            self._cache.clear()
        else:
            keys_to_delete = [k for k in self._cache if k.startswith(prefix)]
            for k in keys_to_delete:
                del self._cache[k]
    
    def _handle_response(self, response: httpx.Response) -> dict[str, Any]:
        """Handle HTTP response and raise appropriate exceptions."""
        if response.status_code == 200 or response.status_code == 201:
            return response.json()
        elif response.status_code == 401 or response.status_code == 403:
            raise CanonAuthError(
                "Authentication failed",
                status_code=response.status_code,
                response_body=response.text,
            )
        elif response.status_code == 404:
            raise CanonNotFoundError(
                "Resource not found",
                status_code=response.status_code,
                response_body=response.text,
            )
        elif response.status_code == 422:
            raise CanonValidationError(
                "Validation failed",
                status_code=response.status_code,
                response_body=response.text,
            )
        else:
            raise CanonAPIError(
                f"API error: {response.status_code}",
                status_code=response.status_code,
                response_body=response.text,
            )
    
    @retry(
        retry=retry_if_exception_type((CanonConnectionError, CanonTimeoutError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
    )
    def _request(
        self,
        method: str,
        path: str,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make an HTTP request with retry logic."""
        try:
            response = self._client.request(method, path, json=json, params=params)
            return self._handle_response(response)
        except httpx.TimeoutException as e:
            raise CanonTimeoutError(f"Request timed out: {e}")
        except httpx.ConnectError as e:
            raise CanonConnectionError(f"Connection failed: {e}")
    
    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()
    
    def __enter__(self) -> CanonClient:
        return self
    
    def __exit__(self, *args: Any) -> None:
        self.close()
    
    # =========================================================================
    # Prompt Retrieval Methods
    # =========================================================================
    
    def get_prompt(self, name: str, use_cache: bool = True) -> Prompt:
        """
        Get a prompt by name.
        
        Args:
            name: The prompt identifier
            use_cache: Whether to use cached result (default: True)
        
        Returns:
            Prompt object
        
        Raises:
            CanonNotFoundError: If prompt doesn't exist
            CanonAuthError: If authentication fails
            CanonAPIError: For other API errors
        
        Example:
            >>> prompt = client.get_prompt("my-prompt")
            >>> print(prompt.description)
        """
        cache_key = self._get_cache_key("get_prompt", name)
        
        if use_cache:
            cached = self._get_from_cache(cache_key)
            if cached:
                return cached
        
        data = self._request("GET", f"/v1/prompts/{name}")
        prompt = Prompt(**data)
        
        if use_cache:
            self._set_cache(cache_key, prompt)
        
        return prompt
    
    def get_prompt_version(self, name: str, version: int) -> Prompt:
        """
        Get a specific version of a prompt.
        
        Args:
            name: The prompt identifier
            version: The version number
        
        Returns:
            Prompt with only the requested version
        
        Raises:
            CanonNotFoundError: If prompt or version doesn't exist
        """
        data = self._request("GET", f"/v1/prompts/{name}/versions/{version}")
        return Prompt(**data)
    
    def get_prompt_by_tag(self, name: str, tag: str) -> Prompt:
        """
        Get a prompt version by tag (e.g., "production", "staging").
        
        Args:
            name: The prompt identifier
            tag: The tag to look up
        
        Returns:
            Prompt with the tagged version
        
        Raises:
            CanonNotFoundError: If prompt or tag doesn't exist
        """
        data = self._request("GET", f"/v1/prompts/{name}/tags/{tag}")
        return Prompt(**data)
    
    def list_prompts(
        self,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
        use_cache: bool = True,
    ) -> PromptList:
        """
        List prompts with pagination and optional search.
        
        Args:
            page: Page number (default: 1)
            page_size: Items per page (default: 20)
            search: Optional search query
            use_cache: Whether to use cached result (default: True)
        
        Returns:
            Paginated list of prompts
        
        Example:
            >>> prompts = client.list_prompts(search="email")
            >>> for prompt in prompts.items:
            ...     print(prompt.name)
        """
        cache_key = self._get_cache_key("list_prompts", page, page_size, search)
        
        if use_cache:
            cached = self._get_from_cache(cache_key)
            if cached:
                return cached
        
        params: dict[str, Any] = {"page": page, "page_size": page_size}
        if search:
            params["search"] = search
        
        data = self._request("GET", "/v1/prompts", params=params)
        result = PromptList(**data)
        
        if use_cache:
            self._set_cache(cache_key, result)
        
        return result
    
    # =========================================================================
    # Prompt Management Methods
    # =========================================================================
    
    def create_prompt(
        self,
        name: str,
        content: str,
        description: str | None = None,
        tags: list[str] | None = None,
    ) -> Prompt:
        """
        Create a new prompt.
        
        Args:
            name: Unique prompt identifier
            content: Initial prompt content
            description: Optional description
            tags: Optional initial tags (default: ["draft"])
        
        Returns:
            Created prompt
        
        Raises:
            CanonValidationError: If validation fails
            CanonAuthError: If not authorized to create prompts
        
        Example:
            >>> prompt = client.create_prompt(
            ...     "welcome-email",
            ...     content="Write a welcome email to {{name}}",
            ...     description="Welcome email template"
            ... )
        """
        request = PromptCreateRequest(
            name=name,
            content=content,
            description=description,
            tags=tags or ["draft"],
        )
        
        data = self._request("POST", "/v1/prompts", json=request.model_dump())
        
        # Clear list cache since we added a new prompt
        self._clear_cache("list_prompts")
        
        return Prompt(**data)
    
    def update_prompt(
        self,
        name: str,
        description: str | None = None,
    ) -> Prompt:
        """
        Update prompt metadata.
        
        Args:
            name: Prompt identifier
            description: New description (optional)
        
        Returns:
            Updated prompt
        """
        request = PromptUpdateRequest(description=description)
        
        data = self._request(
            "PATCH",
            f"/v1/prompts/{name}",
            json=request.model_dump(exclude_unset=True),
        )
        
        # Clear caches for this prompt
        self._clear_cache("get_prompt")
        
        return Prompt(**data)
    
    def create_version(
        self,
        name: str,
        content: str,
    ) -> Prompt:
        """
        Create a new version of an existing prompt.
        
        Args:
            name: Prompt identifier
            content: New version content
        
        Returns:
            Prompt with new version
        
        Example:
            >>> prompt = client.create_version(
            ...     "welcome-email",
            ...     content="Updated welcome email for {{name}}"
            ... )
            >>> print(prompt.current_version)  # Version incremented
        """
        request = VersionCreateRequest(content=content)
        
        data = self._request(
            "POST",
            f"/v1/prompts/{name}/versions",
            json=request.model_dump(),
        )
        
        # Clear caches for this prompt
        self._clear_cache("get_prompt")
        
        return Prompt(**data)
    
    def update_tags(
        self,
        name: str,
        version: int,
        tags: list[str],
    ) -> Prompt:
        """
        Update tags for a specific prompt version.
        
        Args:
            name: Prompt identifier
            version: Version number to tag
            tags: Tags to apply
        
        Returns:
            Updated prompt
        
        Example:
            >>> # Promote version 3 to production
            >>> client.update_tags("welcome-email", 3, ["production"])
        """
        request = TagUpdateRequest(version=version, tags=tags)
        
        data = self._request(
            "PUT",
            f"/v1/prompts/{name}/tags",
            json=request.model_dump(),
        )
        
        # Clear caches
        self._clear_cache("get_prompt")
        
        return Prompt(**data)
    
    def delete_prompt(self, name: str) -> None:
        """
        Delete a prompt.
        
        Args:
            name: Prompt identifier to delete
        
        Raises:
            CanonNotFoundError: If prompt doesn't exist
            CanonAuthError: If not authorized to delete
        """
        self._request("DELETE", f"/v1/prompts/{name}")
        
        # Clear caches
        self._clear_cache("get_prompt")
        self._clear_cache("list_prompts")
    
    # =========================================================================
    # Cache Management
    # =========================================================================
    
    def clear_cache(self) -> None:
        """Clear all cached data."""
        self._cache.clear()
    
    def get_cache_stats(self) -> dict[str, int]:
        """Get cache statistics."""
        return {
            "size": len(self._cache),
            "max_size": 1000,  # Could make this configurable
        }
