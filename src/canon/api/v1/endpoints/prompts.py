"""
Prompt Management Endpoints

Provides CRUD operations for prompts in the Canon registry.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from canon.core.aegis import AegisClient, get_aegis_client
from canon.core.auth import CurrentUser, get_current_user, require_roles
from canon.core.database import get_db_session
from canon.models.prompt import Prompt, PromptVersion, VersionTag
from canon.services.audit import AuditService
from canon.services.prompt import PromptService

router = APIRouter()


# Request/Response Models
class PromptBase(BaseModel):
    """Base model for prompt data."""

    name: str = Field(..., description="Unique prompt identifier", min_length=1, max_length=255)
    description: str | None = Field(None, description="Prompt description", max_length=1000)


class PromptCreate(PromptBase):
    """Model for creating a new prompt."""

    content: str = Field(..., description="Prompt content/text", min_length=1)
    tags: list[str] = Field(default_factory=lambda: ["draft"], description="Initial tags")


class PromptUpdate(BaseModel):
    """Model for updating prompt metadata."""

    description: str | None = Field(None, description="Prompt description")


class VersionCreate(BaseModel):
    """Model for creating a new version."""

    content: str = Field(..., description="New version content", min_length=1)


class TagUpdate(BaseModel):
    """Model for updating a tag."""

    version: int = Field(..., description="Target version number", ge=1)


class PromptVersionResponse(BaseModel):
    """Model for a prompt version."""

    id: str
    version: int
    content: str
    created_at: str
    created_by: str

    class Config:
        from_attributes = True

    @classmethod
    def from_model(cls, v: PromptVersion) -> "PromptVersionResponse":
        return cls(
            id=v.id,
            version=v.version,
            content=v.content,
            created_at=v.created_at.isoformat(),
            created_by=v.created_by,
        )


class TagResponse(BaseModel):
    """Model for a tag."""

    tag_name: str
    version: int
    created_at: str
    updated_at: str

    @classmethod
    def from_model(cls, t: VersionTag) -> "TagResponse":
        return cls(
            tag_name=t.tag_name,
            version=0,  # Will be populated from version relationship
            created_at=t.created_at.isoformat(),
            updated_at=t.updated_at.isoformat(),
        )


class PromptResponse(PromptBase):
    """Model for prompt response."""

    id: str
    current_version: int
    tags: list[str]
    created_at: str
    updated_at: str
    versions: list[PromptVersionResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True

    @classmethod
    def from_model(cls, p: Prompt) -> "PromptResponse":
        return cls(
            id=p.id,
            name=p.name,
            description=p.description,
            current_version=p.current_version,
            tags=[t.tag_name for t in p.tags],
            created_at=p.created_at.isoformat(),
            updated_at=p.updated_at.isoformat(),
            versions=[PromptVersionResponse.from_model(v) for v in p.versions],
        )


class PromptListResponse(BaseModel):
    """Model for paginated prompt list response."""

    prompts: list[PromptResponse]
    total: int
    page: int
    page_size: int


class TagListResponse(BaseModel):
    """Model for tag list response."""

    tags: list[TagResponse]


# Dependencies
def get_prompt_service(
    db: AsyncSession = Depends(get_db_session),
    aegis: AegisClient = Depends(lambda: get_aegis_client()),
) -> PromptService:
    """Get prompt service with dependencies."""
    audit = AuditService(db)
    return PromptService(db, audit, aegis)


# Endpoints
@router.get("", response_model=PromptListResponse)
async def list_prompts(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    tag: str | None = Query(None, description="Filter by tag"),
    service: PromptService = Depends(get_prompt_service),
    _: CurrentUser = Depends(get_current_user),
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
    prompts, total = await service.list_prompts(page=page, page_size=page_size, tag=tag)

    return PromptListResponse(
        prompts=[PromptResponse.from_model(p) for p in prompts],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=PromptResponse, status_code=status.HTTP_201_CREATED)
async def create_prompt(
    prompt: PromptCreate,
    service: PromptService = Depends(get_prompt_service),
    user: CurrentUser = Depends(require_roles("editor", "admin")),
) -> PromptResponse:
    """
    Create a new prompt.

    Args:
        prompt: Prompt creation data.

    Returns:
        Created prompt with initial version.

    Raises:
        HTTPException: If prompt with name already exists.
    """
    try:
        created = await service.create_prompt(
            name=prompt.name,
            content=prompt.content,
            description=prompt.description,
            tags=prompt.tags,
            actor=user.user_id,
        )
        return PromptResponse.from_model(created)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e


@router.get("/{name}", response_model=PromptResponse)
async def get_prompt(
    name: str,
    service: PromptService = Depends(get_prompt_service),
    _: CurrentUser = Depends(get_current_user),
) -> PromptResponse:
    """
    Get a specific prompt by name.

    Args:
        name: Prompt name/identifier.

    Returns:
        Prompt details with all versions.

    Raises:
        HTTPException: If prompt not found.
    """
    prompt = await service.get_prompt(name)
    if not prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found")

    return PromptResponse.from_model(prompt)


@router.post("/{name}/versions", response_model=PromptVersionResponse, status_code=status.HTTP_201_CREATED)
async def create_version(
    name: str,
    version: VersionCreate,
    service: PromptService = Depends(get_prompt_service),
    user: CurrentUser = Depends(require_roles("editor", "admin")),
) -> PromptVersionResponse:
    """
    Create a new version of an existing prompt.

    Args:
        name: Prompt name.
        version: Version creation data.

    Returns:
        Created version.

    Raises:
        HTTPException: If prompt not found.
    """
    try:
        created = await service.create_version(
            prompt_name=name,
            content=version.content,
            actor=user.user_id,
        )
        return PromptVersionResponse.from_model(created)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.get("/{name}/versions/{version}", response_model=PromptVersionResponse)
async def get_prompt_version(
    name: str,
    version: int,
    service: PromptService = Depends(get_prompt_service),
    _: CurrentUser = Depends(get_current_user),
) -> PromptVersionResponse:
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
    version_obj = await service.get_version(name, version)
    if not version_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Version not found")

    return PromptVersionResponse.from_model(version_obj)


@router.get("/{name}/tags", response_model=TagListResponse)
async def list_tags(
    name: str,
    service: PromptService = Depends(get_prompt_service),
    _: CurrentUser = Depends(get_current_user),
) -> TagListResponse:
    """
    List all tags for a prompt.

    Args:
        name: Prompt name.

    Returns:
        List of tags.

    Raises:
        HTTPException: If prompt not found.
    """
    try:
        tags = await service.list_tags(name)
        return TagListResponse(
            tags=[TagResponse.from_model(t) for t in tags]
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.put("/{name}/tags/{tag_name}", response_model=TagResponse)
async def update_tag(
    name: str,
    tag_name: str,
    tag_update: TagUpdate,
    service: PromptService = Depends(get_prompt_service),
    user: CurrentUser = Depends(require_roles("editor", "admin")),
) -> TagResponse:
    """
    Create or move a tag to a specific version.

    Args:
        name: Prompt name.
        tag_name: Tag name (e.g., 'production', 'staging').
        tag_update: Tag update data.

    Returns:
        Updated tag.

    Raises:
        HTTPException: If prompt or version not found.
    """
    try:
        tag = await service.get_or_create_tag(
            prompt_name=name,
            tag_name=tag_name,
            target_version=tag_update.version,
            actor=user.user_id,
        )
        return TagResponse.from_model(tag)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.delete("/{name}/tags/{tag_name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    name: str,
    tag_name: str,
    service: PromptService = Depends(get_prompt_service),
    user: CurrentUser = Depends(require_roles("admin")),
) -> None:
    """
    Delete a tag from a prompt.

    Args:
        name: Prompt name.
        tag_name: Tag name.

    Raises:
        HTTPException: If prompt not found.
    """
    deleted = await service.delete_tag(name, tag_name, user.user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")


@router.get("/{name}/tag/{tag_name}", response_model=PromptVersionResponse)
async def get_by_tag(
    name: str,
    tag_name: str,
    service: PromptService = Depends(get_prompt_service),
    _: CurrentUser = Depends(get_current_user),
) -> PromptVersionResponse:
    """
    Get the version of a prompt pointed to by a tag.

    This is the canonical endpoint for production consumers.
    Consumers should use stable tag names (e.g., 'production') rather than
    version numbers to ensure they always get the approved content.

    Args:
        name: Prompt name.
        tag_name: Tag name.

    Returns:
        Version pointed to by the tag.

    Raises:
        HTTPException: If prompt or tag not found.
    """
    result = await service.get_prompt_by_tag(name, tag_name)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prompt '{name}' with tag '{tag_name}' not found",
        )

    _, version = result
    return PromptVersionResponse.from_model(version)
