"""
Canon Audit Service

Provides audit logging for all governance-relevant actions.
"""

import json
import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from canon.core.logging import get_logger
from canon.models.prompt import AuditLog

logger = get_logger(__name__)


class AuditService:
    """
    Service for recording audit log entries.

    All governance-relevant actions are logged immutably for
    compliance and debugging purposes.
    """

    # Audit action types
    ACTION_CREATE = "CREATE"
    ACTION_UPDATE = "UPDATE"
    ACTION_DELETE = "DELETE"
    ACTION_APPROVE = "APPROVE"
    ACTION_REJECT = "REJECT"
    ACTION_TAG = "TAG"
    ACTION_PUBLISH = "PUBLISH"
    ACTION_ROLLBACK = "ROLLBACK"

    # Resource types
    RESOURCE_PROMPT = "PROMPT"
    RESOURCE_VERSION = "VERSION"
    RESOURCE_TAG = "TAG"

    def __init__(self, db: AsyncSession):
        """
        Initialize audit service.

        Args:
            db: Database session.
        """
        self.db = db

    async def log(
        self,
        action: str,
        resource_type: str,
        resource_id: str,
        actor: str,
        details: dict | None = None,
    ) -> AuditLog:
        """
        Create an audit log entry.

        Args:
            action: Action type (CREATE, UPDATE, etc.).
            resource_type: Resource type (PROMPT, VERSION, etc.).
            resource_id: Resource identifier.
            actor: User ID of the actor.
            details: Optional additional details.

        Returns:
            AuditLog: Created audit log entry.
        """
        log_entry = AuditLog(
            id=str(uuid.uuid4()),
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            actor=actor,
            details=json.dumps(details) if details else None,
            created_at=datetime.utcnow(),
        )

        self.db.add(log_entry)
        await self.db.flush()

        logger.info(
            f"Audit log created: {action} {resource_type}:{resource_id} by {actor}"
        )

        return log_entry

    async def log_prompt_create(
        self,
        prompt_id: str,
        prompt_name: str,
        actor: str,
        initial_content: str | None = None,
    ) -> AuditLog:
        """Log prompt creation."""
        return await self.log(
            action=self.ACTION_CREATE,
            resource_type=self.RESOURCE_PROMPT,
            resource_id=prompt_id,
            actor=actor,
            details={
                "prompt_name": prompt_name,
                "initial_content_length": len(initial_content) if initial_content else 0,
            },
        )

    async def log_version_create(
        self,
        prompt_id: str,
        version: int,
        actor: str,
        content_length: int,
    ) -> AuditLog:
        """Log version creation."""
        return await self.log(
            action=self.ACTION_CREATE,
            resource_type=self.RESOURCE_VERSION,
            resource_id=f"{prompt_id}:v{version}",
            actor=actor,
            details={
                "prompt_id": prompt_id,
                "version": version,
                "content_length": content_length,
            },
        )

    async def log_tag_update(
        self,
        prompt_id: str,
        tag_name: str,
        old_version: int | None,
        new_version: int,
        actor: str,
    ) -> AuditLog:
        """Log tag update."""
        return await self.log(
            action=self.ACTION_TAG,
            resource_type=self.RESOURCE_TAG,
            resource_id=f"{prompt_id}:{tag_name}",
            actor=actor,
            details={
                "prompt_id": prompt_id,
                "tag_name": tag_name,
                "old_version": old_version,
                "new_version": new_version,
            },
        )

    async def log_prompt_publish(
        self,
        prompt_id: str,
        version: int,
        actor: str,
    ) -> AuditLog:
        """Log prompt publication to production."""
        return await self.log(
            action=self.ACTION_PUBLISH,
            resource_type=self.RESOURCE_PROMPT,
            resource_id=prompt_id,
            actor=actor,
            details={
                "published_version": version,
            },
        )

    async def get_resource_history(
        self,
        resource_type: str,
        resource_id: str,
        limit: int = 100,
    ) -> list[AuditLog]:
        """
        Get audit history for a resource.

        Args:
            resource_type: Resource type.
            resource_id: Resource identifier.
            limit: Maximum number of entries.

        Returns:
            List of audit log entries.
        """
        stmt = (
            select(AuditLog)
            .where(AuditLog.resource_type == resource_type)
            .where(AuditLog.resource_id == resource_id)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        return list(result.scalars().all())
