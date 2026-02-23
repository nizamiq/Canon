"""
Canon Prompt Models

SQLAlchemy models for prompts, versions, tags, and audit logging.
"""

from datetime import datetime

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from canon.models.base import Base, TimestampMixin


class Prompt(Base, TimestampMixin):
    """
    Logical prompt definition.

    A prompt represents a named, versioned piece of content
    used to instruct AI agents.
    """

    __tablename__ = "canon_prompts"

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[str] = mapped_column(Text, unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    current_version: Mapped[int] = mapped_column(default=1, nullable=False)

    # Relationships
    versions: Mapped[list["PromptVersion"]] = relationship(
        "PromptVersion", back_populates="prompt", cascade="all, delete-orphan"
    )
    tags: Mapped[list["VersionTag"]] = relationship(
        "VersionTag", back_populates="prompt", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Prompt(name={self.name}, current_version={self.current_version})>"


class PromptVersion(Base):
    """
    Immutable content snapshot of a prompt.

    Each version stores the exact content at a point in time
    and cannot be modified after creation.
    """

    __tablename__ = "canon_prompt_versions"

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    prompt_id: Mapped[str] = mapped_column(Text, ForeignKey("canon_prompts.id"), nullable=False)
    version: Mapped[int] = mapped_column(nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    created_by: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    prompt: Mapped["Prompt"] = relationship("Prompt", back_populates="versions")

    def __repr__(self) -> str:
        return f"<PromptVersion(prompt_id={self.prompt_id}, version={self.version})>"


class VersionTag(Base):
    """
    Mutable pointer to a specific prompt version.

    Tags like 'production', 'staging', 'latest' can be
    moved between versions without modifying content.
    """

    __tablename__ = "canon_version_tags"

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    prompt_id: Mapped[str] = mapped_column(Text, ForeignKey("canon_prompts.id"), nullable=False)
    tag_name: Mapped[str] = mapped_column(Text, nullable=False)
    version_id: Mapped[str] = mapped_column(Text, ForeignKey("canon_prompt_versions.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    prompt: Mapped["Prompt"] = relationship("Prompt", back_populates="tags")
    version: Mapped["PromptVersion"] = relationship("PromptVersion")

    def __repr__(self) -> str:
        return f"<VersionTag(prompt_id={self.prompt_id}, tag={self.tag_name})>"


class AuditLog(Base):
    """
    Immutable audit log for all governance-relevant actions.

    Records who did what, when, for compliance and debugging.
    """

    __tablename__ = "canon_audit_log"

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    action: Mapped[str] = mapped_column(Text, nullable=False)  # CREATE, UPDATE, APPROVE, etc.
    resource_type: Mapped[str] = mapped_column(Text, nullable=False)  # PROMPT, VERSION, TAG
    resource_id: Mapped[str] = mapped_column(Text, nullable=False)
    actor: Mapped[str] = mapped_column(Text, nullable=False)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON details
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<AuditLog(action={self.action}, resource={self.resource_type}:{self.resource_id})>"
