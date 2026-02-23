"""Canon Python SDK Client."""

import httpx
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class PromptVersion(BaseModel):
    version: int
    content: str
    created_at: str
    created_by: str


class PromptResponse(BaseModel):
    name: str
    description: Optional[str]
    current_version: int
    tags: List[str]
    versions: List[PromptVersion]


class PromptListResponse(BaseModel):
    prompts: List[PromptResponse]
    total: int
    page: int
    page_size: int


class CanonClient:
    """Client for interacting with the Canon prompt registry."""

    def __init__(self, base_url: str, timeout: float = 10.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def get_prompt(self, name: str) -> PromptResponse:
        """Fetch a prompt by name."""
        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(f"{self.base_url}/v1/prompts/{name}")
            response.raise_for_status()
            return PromptResponse(**response.json())

    def list_prompts(self, page: int = 1, page_size: int = 20, tag: Optional[str] = None) -> PromptListResponse:
        """List all prompts."""
        params: dict[str, Any] = {"page": page, "page_size": page_size}
        if tag:
            params["tag"] = tag
        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(f"{self.base_url}/v1/prompts", params=params)
            response.raise_for_status()
            return PromptListResponse(**response.json())

    def get_prompt_version(self, name: str, version: int) -> PromptVersion:
        """Fetch a specific version of a prompt."""
        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(f"{self.base_url}/v1/prompts/{name}/versions/{version}")
            response.raise_for_status()
            return PromptVersion(**response.json())

    def create_prompt(
        self, name: str, content: str, description: Optional[str] = None, tags: Optional[List[str]] = None
    ) -> PromptResponse:
        """Create a new prompt."""
        payload = {
            "name": name,
            "content": content,
            "description": description,
            "tags": tags or []
        }
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(f"{self.base_url}/v1/prompts", json=payload)
            response.raise_for_status()
            return PromptResponse(**response.json())
