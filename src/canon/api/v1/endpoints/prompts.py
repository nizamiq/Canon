"""
Prompt Management Endpoints

Provides CRUD operations for prompts in the Canon registry.
"""

from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

router = APIRouter()


class PromptBase(BaseModel):
    """Base model for prompt data."""

    name: str = Field(..., description="Unique prompt identifier")
    description: str | None = Field(None, description="Prompt description")


class PromptCreate(PromptBase):
    """Model for creating a new prompt."""

    content: str = Field(..., description="Prompt content/text")
    tags: list[str] = Field(default_factory=list, description="Initial tags")


class PromptVersion(BaseModel):
    """Model for a prompt version."""

    version: int
    content: str
    created_at: datetime
    created_by: str


class PromptResponse(PromptBase):
    """Model for prompt response."""

    id: str
    current_version: int
    tags: list[str]
    created_at: datetime
    updated_at: datetime
    versions: list[PromptVersion] = Field(default_factory=list)


class PromptListResponse(BaseModel):
    """Model for paginated prompt list response."""

    prompts: list[PromptResponse]
    total: int
    page: int
    page_size: int


# In-memory store for Phase 01 scaffolding (will be replaced with database)
_PROMPTS_STORE: dict = {}


@router.get("", response_model=PromptListResponse)
async def list_prompts(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    tag: str | None = Query(None, description="Filter by tag"),
) -> PromptListResponse:
    """
    List all prompts with optional filtering.

    Args:
        page: Page number for pagination.
        page_size: Number of items per page.
        tag: Optional tag filter.

    Returns:
        Paginated list of prompts.
    """
    prompts = list(_PROMPTS_STORE.values())

    if tag:
        prompts = [p for p in prompts if tag in p.get("tags", [])]

    start = (page - 1) * page_size
    end = start + page_size

    return PromptListResponse(
        prompts=prompts[start:end],
        total=len(prompts),
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=PromptResponse, status_code=201)
async def create_prompt(prompt: PromptCreate) -> PromptResponse:
    """
    Create a new prompt.

    Args:
        prompt: Prompt creation data.

    Returns:
        Created prompt with initial version.

    Raises:
        HTTPException: If prompt with name already exists.
    """
    if prompt.name in _PROMPTS_STORE:
        raise HTTPException(
            status_code=409, detail="Prompt with this name already exists"
        )

    now = datetime.now(datetime.UTC).replace(tzinfo=None)

    prompt_data = {
        "id": prompt.name,  # Using name as ID for simplicity
        "name": prompt.name,
        "description": prompt.description,
        "current_version": 1,
        "tags": prompt.tags or [],
        "created_at": now,
        "updated_at": now,
        "versions": [
            {
                "version": 1,
                "content": prompt.content,
                "created_at": now,
                "created_by": "system",  # TODO: Get from JWT
            }
        ],
    }

    _PROMPTS_STORE[prompt.name] = prompt_data

    return PromptResponse(**prompt_data)


@router.get("/{name}", response_model=PromptResponse)
async def get_prompt(name: str) -> PromptResponse:
    """
    Get a specific prompt by name.

    Args:
        name: Prompt name/identifier.

    Returns:
        Prompt details with all versions.

    Raises:
        HTTPException: If prompt not found.
    """
    if name not in _PROMPTS_STORE:
        raise HTTPException(status_code=404, detail="Prompt not found")

    return PromptResponse(**_PROMPTS_STORE[name])


@router.get("/{name}/versions/{version}", response_model=PromptVersion)
async def get_prompt_version(name: str, version: int) -> PromptVersion:
    """
    Get a specific version of a prompt.

    Args:
        name: Prompt name/identifier.
        version: Version number.

    Returns:
        Specific prompt version.

    Raises:
        HTTPException: If prompt or version not found.
    """
    if name not in _PROMPTS_STORE:
        raise HTTPException(status_code=404, detail="Prompt not found")

    prompt = _PROMPTS_STORE[name]
    for v in prompt["versions"]:
        if v["version"] == version:
            return PromptVersion(**v)

    raise HTTPException(status_code=404, detail="Version not found")
