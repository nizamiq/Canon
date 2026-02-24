"""
Canon Core Module

Provides core functionality: configuration, database, authentication, and logging.
"""

from canon.core.config import settings, get_settings
from canon.core.database import get_db_session, init_db, close_db
from canon.core.auth import get_current_user, require_roles, CurrentUser
from canon.core.aegis import get_aegis_client, AegisClient

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
