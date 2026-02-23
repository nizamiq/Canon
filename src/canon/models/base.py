"""
Canon Base Models

Provides base model classes and mixins for SQLAlchemy models.
"""

from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, String
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class AuditMixin:
    """Mixin for audit fields."""

    created_by = Column(String(255), nullable=False)
    updated_by = Column(String(255), nullable=False)
