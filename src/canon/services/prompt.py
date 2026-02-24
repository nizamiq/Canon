"""
Canon Prompt Service

Business logic for prompt management with database integration.
"""

import uuid
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from canon.core.aegis import AegisClient
from canon.core.logging import get_logger
from canon.models.prompt import Prompt, PromptVersion, VersionTag
from canon.services.audit import AuditService

logger = get_logger(__name__)


class PromptService:
    """
    Service for managing prompts with full database integration.

    Handles CRUD operations, versioning, tagging, and audit logging.
    """

    def __init__(
        self,
        db: AsyncSession,
        audit: AuditService,
        aegis: AegisClient | None = None,
    ):
        """
        Initialize prompt service.

        Args:
            db: Database session.
            audit: Audit service for logging.
            aegis: Optional Aegis client for RBAC.
        """
        self.db = db
        self.audit = audit
        self.aegis = aegis

    async def list_prompts(
        self,
        page: int = 1,
        page_size: int = 20,
        tag: str | None = None,
    ) -> tuple[list[Prompt], int]:
        """
        List prompts with optional filtering.

        Args:
            page: Page number (1-indexed).
            page_size: Items per page.
            tag: Optional tag filter.

        Returns:
            Tuple of (prompts list, total count).
        """
        # Base query
        query = select(Prompt).options(selectinload(Prompt.tags))

        # Apply tag filter
        if tag:
            query = query.join(VersionTag).where(VersionTag.tag_name == tag)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size).order_by(Prompt.created_at.desc())

        result = await self.db.execute(query)
        prompts = list(result.scalars().all())

        return prompts, total

    async def get_prompt(self, name: str) -> Prompt | None:
        """
        Get a prompt by name with versions and tags.

        Args:
            name: Prompt name.

        Returns:
            Prompt or None if not found.
        """
        query = (
            select(Prompt)
            .where(Prompt.name == name)
            .options(
                selectinload(Prompt.versions),
                selectinload(Prompt.tags),
            )
        )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_prompt(
        self,
        name: str,
        content: str,
        description: str | None = None,
        tags: list[str] | None = None,
        actor: str = "system",
    ) -> Prompt:
        """
        Create a new prompt with initial version.

        Args:
            name: Unique prompt name.
            content: Initial prompt content.
            description: Optional description.
            tags: Optional list of initial tags.
            actor: User ID of the creator.

        Returns:
            Created prompt.

        Raises:
            ValueError: If prompt name already exists.
        """
        # Check if prompt already exists
        existing = await self.get_prompt(name)
        if existing:
            raise ValueError(f"Prompt '{name}' already exists")

        prompt_id = str(uuid.uuid4())
        version_id = str(uuid.uuid4())
        now = datetime.utcnow()

        # Create prompt
        prompt = Prompt(
            id=prompt_id,
            name=name,
            description=description,
            current_version=1,
            created_at=now,
            updated_at=now,
        )
        self.db.add(prompt)

        # Create initial version
        version = PromptVersion(
            id=version_id,
            prompt_id=prompt_id,
            version=1,
            content=content,
            created_at=now,
            created_by=actor,
        )
        self.db.add(version)

        # Create initial tags
        tag_objects = []
        if tags:
            for tag_name in tags:
                tag = VersionTag(
                    id=str(uuid.uuid4()),
                    prompt_id=prompt_id,
                    tag_name=tag_name,
                    version_id=version_id,
                    created_at=now,
                    updated_at=now,
                )
                self.db.add(tag)
                tag_objects.append(tag)

        # Flush to get IDs
        await self.db.flush()

        # Log audit
        await self.audit.log_prompt_create(
            prompt_id=prompt_id,
            prompt_name=name,
            actor=actor,
            initial_content=content,
        )

        # Refresh to load relationships
        await self.db.refresh(prompt, ["versions", "tags"])

        logger.info(f"Created prompt '{name}' with version 1 by {actor}")

        return prompt

    async def create_version(
        self,
        prompt_name: str,
        content: str,
        actor: str = "system",
    ) -> PromptVersion:
        """
        Create a new version of an existing prompt.

        Args:
            prompt_name: Prompt name.
            content: New version content.
            actor: User ID of the creator.

        Returns:
            Created version.

        Raises:
            ValueError: If prompt not found.
        """
        prompt = await self.get_prompt(prompt_name)
        if not prompt:
            raise ValueError(f"Prompt '{prompt_name}' not found")

        new_version_number = prompt.current_version + 1
        version_id = str(uuid.uuid4())
        now = datetime.utcnow()

        # Create new version
        version = PromptVersion(
            id=version_id,
            prompt_id=prompt.id,
            version=new_version_number,
            content=content,
            created_at=now,
            created_by=actor,
        )
        self.db.add(version)

        # Update prompt current version
        prompt.current_version = new_version_number
        prompt.updated_at = now

        # Flush to persist
        await self.db.flush()

        # Log audit
        await self.audit.log_version_create(
            prompt_id=prompt.id,
            version=new_version_number,
            actor=actor,
            content_length=len(content),
        )

        logger.info(f"Created version {new_version_number} for prompt '{prompt_name}' by {actor}")

        return version

    async def get_version(
        self,
        prompt_name: str,
        version: int,
    ) -> PromptVersion | None:
        """
        Get a specific version of a prompt.

        Args:
            prompt_name: Prompt name.
            version: Version number.

        Returns:
            PromptVersion or None if not found.
        """
        prompt = await self.get_prompt(prompt_name)
        if not prompt:
            return None

        query = (
            select(PromptVersion)
            .where(PromptVersion.prompt_id == prompt.id)
            .where(PromptVersion.version == version)
        )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_or_create_tag(
        self,
        prompt_name: str,
        tag_name: str,
        target_version: int | None = None,
        actor: str = "system",
    ) -> VersionTag:
        """
        Get or create a tag, optionally moving it to a specific version.

        Args:
            prompt_name: Prompt name.
            tag_name: Tag name (e.g., 'production', 'staging').
            target_version: Version to point tag to. Defaults to current.
            actor: User ID performing the action.

        Returns:
            VersionTag instance.

        Raises:
            ValueError: If prompt or target version not found.
        """
        prompt = await self.get_prompt(prompt_name)
        if not prompt:
            raise ValueError(f"Prompt '{prompt_name}' not found")

        target_ver = target_version or prompt.current_version

        # Get target version
        version = await self.get_version(prompt_name, target_ver)
        if not version:
            raise ValueError(f"Version {target_ver} not found for prompt '{prompt_name}'")

        now = datetime.utcnow()

        # Check if tag already exists
        query = (
            select(VersionTag)
            .where(VersionTag.prompt_id == prompt.id)
            .where(VersionTag.tag_name == tag_name)
        )
        result = await self.db.execute(query)
        tag = result.scalar_one_or_none()

        old_version = None

        if tag:
            # Update existing tag
            old_version = tag.version_id
            tag.version_id = version.id
            tag.updated_at = now
        else:
            # Create new tag
            tag = VersionTag(
                id=str(uuid.uuid4()),
                prompt_id=prompt.id,
                tag_name=tag_name,
                version_id=version.id,
                created_at=now,
                updated_at=now,
            )
            self.db.add(tag)

        await self.db.flush()

        # Log audit
        await self.audit.log_tag_update(
            prompt_id=prompt.id,
            tag_name=tag_name,
            old_version=old_version,
            new_version=target_ver,
            actor=actor,
        )

        logger.info(f"Tag '{tag_name}' -> version {target_ver} for prompt '{prompt_name}' by {actor}")

        return tag

    async def list_tags(self, prompt_name: str) -> list[VersionTag]:
        """
        List all tags for a prompt.

        Args:
            prompt_name: Prompt name.

        Returns:
            List of VersionTag instances.

        Raises:
            ValueError: If prompt not found.
        """
        prompt = await self.get_prompt(prompt_name)
        if not prompt:
            raise ValueError(f"Prompt '{prompt_name}' not found")

        query = (
            select(VersionTag)
            .where(VersionTag.prompt_id == prompt.id)
            .order_by(VersionTag.tag_name)
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def delete_tag(
        self,
        prompt_name: str,
        tag_name: str,
        actor: str = "system",
    ) -> bool:
        """
        Delete a tag from a prompt.

        Args:
            prompt_name: Prompt name.
            tag_name: Tag name.
            actor: User ID performing the action.

        Returns:
            True if deleted, False if not found.
        """
        prompt = await self.get_prompt(prompt_name)
        if not prompt:
            return False

        query = (
            select(VersionTag)
            .where(VersionTag.prompt_id == prompt.id)
            .where(VersionTag.tag_name == tag_name)
        )
        result = await self.db.execute(query)
        tag = result.scalar_one_or_none()

        if not tag:
            return False

        await self.db.delete(tag)

        logger.info(f"Deleted tag '{tag_name}' from prompt '{prompt_name}' by {actor}")

        return True

    async def get_prompt_by_tag(
        self,
        name: str,
        tag: str,
    ) -> tuple[Prompt, PromptVersion] | None:
        """
        Get a prompt and the version pointed to by a tag.

        Args:
            name: Prompt name.
            tag: Tag name.

        Returns:
            Tuple of (prompt, version) or None if not found.
        """
        prompt = await self.get_prompt(name)
        if not prompt:
            return None

        # Find the tag
        tag_obj = next((t for t in prompt.tags if t.tag_name == tag), None)
        if not tag_obj:
            return None

        # Get the version
        query = (
            select(PromptVersion)
            .where(PromptVersion.id == tag_obj.version_id)
        )
        result = await self.db.execute(query)
        version = result.scalar_one_or_none()

        if not version:
            return None

        return prompt, version
