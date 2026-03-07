"""
Canon SDK Models

Pydantic models for Canon API request/response types.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class PromptVersion(BaseModel):
    """Represents a version of a prompt."""
    
    version: int = Field(..., description="Version number")
    content: str = Field(..., description="Prompt content")
    created_at: datetime = Field(..., description="Creation timestamp")
    created_by: str = Field(..., description="User who created this version")
    tags: list[str] = Field(default_factory=list, description="Tags applied to this version")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class Prompt(BaseModel):
    """Represents a prompt in the Canon registry."""
    
    name: str = Field(..., description="Unique prompt identifier")
    description: str | None = Field(None, description="Prompt description")
    current_version: int = Field(..., description="Latest version number")
    versions: list[PromptVersion] = Field(default_factory=list, description="All versions")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    owner: str = Field(..., description="Prompt owner")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    def get_version(self, version: int | None = None) -> PromptVersion:
        """Get a specific version or the current version."""
        if version is None:
            version = self.current_version
        for v in self.versions:
            if v.version == version:
                return v
        raise ValueError(f"Version {version} not found for prompt {self.name}")
    
    def get_tagged_version(self, tag: str) -> PromptVersion | None:
        """Get the version with a specific tag."""
        for v in self.versions:
            if tag in v.tags:
                return v
        return None


class PromptList(BaseModel):
    """List of prompts with pagination info."""
    
    items: list[Prompt] = Field(default_factory=list, description="Prompt items")
    total: int = Field(..., description="Total number of prompts")
    page: int = Field(default=1, description="Current page number")
    page_size: int = Field(default=20, description="Items per page")
    
    @property
    def has_next(self) -> bool:
        """Check if there are more pages."""
        return self.page * self.page_size < self.total
    
    @property
    def has_prev(self) -> bool:
        """Check if there are previous pages."""
        return self.page > 1


class PromptCreateRequest(BaseModel):
    """Request model for creating a new prompt."""
    
    name: str = Field(..., description="Unique prompt identifier", min_length=1, max_length=255)
    description: str | None = Field(None, description="Prompt description", max_length=1000)
    content: str = Field(..., description="Initial prompt content", min_length=1)
    tags: list[str] = Field(default_factory=lambda: ["draft"], description="Initial tags")


class PromptUpdateRequest(BaseModel):
    """Request model for updating prompt metadata."""
    
    description: str | None = Field(None, description="Updated description")


class VersionCreateRequest(BaseModel):
    """Request model for creating a new version."""
    
    content: str = Field(..., description="New version content", min_length=1)


class TagUpdateRequest(BaseModel):
    """Request model for updating tags."""
    
    version: int = Field(..., description="Version number to tag")
    tags: list[str] = Field(..., description="Tags to apply")
