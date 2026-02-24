"""
Canon Core Module

Provides core functionality: configuration, database, authentication, and logging.
"""

from canon.core.aegis import AegisClient, get_aegis_client
from canon.core.auth import CurrentUser, get_current_user, require_roles
from canon.core.config import get_settings, settings
from canon.core.database import close_db, get_db_session, init_db

__all__ = [
    "settings",
    "get_settings",
    "get_db_session",
    "init_db",
    "close_db",
    "get_current_user",
    "require_roles",
    "CurrentUser",
    "get_aegis_client",
    "AegisClient",
]
