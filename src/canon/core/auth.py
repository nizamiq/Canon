"""
Canon Authentication Module

Provides JWT authentication middleware for Zitadel integration.
"""

import base64
import json
import time
from typing import Any

import httpx
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from canon.core.config import settings
from canon.core.logging import get_logger

logger = get_logger(__name__)

security = HTTPBearer(auto_error=False)


class JWTPayload(BaseModel):
    """Decoded JWT payload structure."""

    sub: str
    iss: str | None = None
    aud: str | None = None
    exp: int | None = None
    iat: int | None = None
    email: str | None = None
    name: str | None = None
    roles: list[str] = []
    org_id: str | None = None
    raw: dict[str, Any] = {}


class CurrentUser(BaseModel):
    """Authenticated user information."""

    user_id: str
    email: str | None = None
    name: str | None = None
    roles: list[str] = []
    org_id: str | None = None


# Cache for Zitadel OIDC keys
_oidc_keys_cache: dict = {}
_oidc_keys_expiry: float = 0


async def get_oidc_keys() -> dict:
    """
    Fetch OIDC keys from Zitadel for JWT verification.

    Returns:
        dict: OIDC configuration with keys.
    """
    global _oidc_keys_cache, _oidc_keys_expiry

    # Return cached keys if still valid (cache for 1 hour)
    if _oidc_keys_cache and time.time() < _oidc_keys_expiry:
        return _oidc_keys_cache

    if not settings.zitadel_issuer_url:
        logger.warning("Zitadel issuer URL not configured - skipping JWT verification")
        return {}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Fetch OIDC configuration
            oidc_url = f"{settings.zitadel_issuer_url.rstrip('/')}/.well-known/openid-configuration"
            response = await client.get(oidc_url)
            response.raise_for_status()
            oidc_config = response.json()

            # Fetch JWKS
            jwks_url = oidc_config.get("jwks_uri")
            if jwks_url:
                response = await client.get(jwks_url)
                response.raise_for_status()
                _oidc_keys_cache = response.json()
                _oidc_keys_expiry = time.time() + 3600  # 1 hour cache

            return _oidc_keys_cache
    except Exception as e:
        logger.error(f"Failed to fetch OIDC keys: {e}")
        return {}


async def verify_jwt(token: str) -> JWTPayload:
    """
    Verify and decode a JWT token.

    Args:
        token: JWT token string.

    Returns:
        JWTPayload: Decoded token payload.

    Raises:
        HTTPException: If token is invalid or expired.
    """
    try:
        # Decode token without verification for development
        # In production, this should use proper JWT verification with JWKS
        parts = token.split(".")
        if len(parts) != 3:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token format",
            )

        # Decode payload
        payload_bytes = base64.urlsafe_b64decode(parts[1] + "==")
        payload_dict = json.loads(payload_bytes)

        # Check expiration
        if payload_dict.get("exp") and payload_dict["exp"] < time.time():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
            )

        # Validate issuer if configured
        if settings.jwt_issuer and payload_dict.get("iss") != settings.jwt_issuer:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token issuer",
            )

        # Validate audience if configured
        if settings.jwt_audience:
            aud = payload_dict.get("aud", [])
            if isinstance(aud, str):
                aud = [aud]
            if settings.jwt_audience not in aud:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token audience",
                )

        return JWTPayload(
            sub=payload_dict.get("sub", ""),
            iss=payload_dict.get("iss"),
            aud=payload_dict.get("aud"),
            exp=payload_dict.get("exp"),
            iat=payload_dict.get("iat"),
            email=payload_dict.get("email"),
            name=payload_dict.get("name"),
            roles=payload_dict.get("roles", []),
            org_id=payload_dict.get("urn:zitadel:iam:org:project:roles", {}).keys().__iter__().__last__() if payload_dict.get("urn:zitadel:iam:org:project:roles") else None,
            raw=payload_dict,
        )
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token encoding",
        ) from None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"JWT verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token verification failed",
        ) from e


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> CurrentUser | None:
    """
    Dependency that extracts and validates the current user from JWT.

    Args:
        request: FastAPI request object.
        credentials: HTTP Bearer credentials.

    Returns:
        CurrentUser: Authenticated user information or None if no auth.

    Raises:
        HTTPException: If token is invalid (when auth is required).
    """
    # Allow anonymous access in development mode
    if not credentials:
        if settings.environment == "development":
            return CurrentUser(
                user_id="dev-user",
                email="dev@nizamiq.local",
                name="Development User",
                roles=["admin", "editor", "viewer"],
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    payload = await verify_jwt(credentials.credentials)

    return CurrentUser(
        user_id=payload.sub,
        email=payload.email,
        name=payload.name,
        roles=payload.roles,
        org_id=payload.org_id,
    )


def require_roles(*required_roles: str):
    """
    Dependency factory that requires specific roles.

    Args:
        *required_roles: Roles required to access the endpoint.

    Returns:
        Dependency function.
    """
    async def role_checker(
        user: CurrentUser = Depends(get_current_user),
    ) -> CurrentUser:
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
            )

        # Check if user has any of the required roles
        user_roles = set(user.roles)
        required = set(required_roles)

        if not required.intersection(user_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required roles: {', '.join(required_roles)}",
            )

        return user

    return role_checker
