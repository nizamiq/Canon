"""
Canon Configuration Module

Provides application settings via Pydantic BaseSettings.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = {"env_prefix": "CANON_", "env_file": ".env", "case_sensitive": False}

    # Application
    app_name: str = "Canon"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/canon"
    database_pool_size: int = 10
    database_max_overflow: int = 20

    # Security
    jwt_issuer: str | None = None
    jwt_audience: str | None = None
    zitadel_issuer_url: str | None = None

    # Aegis Integration
    aegis_url: str | None = None
    aegis_timeout: int = 30

    # Redis (optional caching)
    redis_url: str | None = None


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()
