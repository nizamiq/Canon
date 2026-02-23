"""Tests for Canon core configuration."""

import pytest
from canon.core.config import Settings, get_settings


def test_settings_defaults():
    """Test default settings values."""
    settings = Settings()
    
    assert settings.app_name == "Canon"
    assert settings.app_version == "1.0.0"
    assert settings.debug is False
    assert settings.environment == "development"


def test_settings_database_url():
    """Test database URL configuration."""
    settings = Settings()
    
    assert "postgresql" in settings.database_url
    assert "canon" in settings.database_url


def test_get_settings_caching():
    """Test that get_settings returns cached instance."""
    settings1 = get_settings()
    settings2 = get_settings()
    
    assert settings1 is settings2


def test_settings_from_environment():
    """Test settings can be overridden from environment."""
    import os
    
    original = os.environ.get("CANON_DEBUG")
    os.environ["CANON_DEBUG"] = "true"
    
    settings = Settings()
    assert settings.debug is True
    
    if original is not None:
        os.environ["CANON_DEBUG"] = original
    else:
        os.environ.pop("CANON_DEBUG", None)
