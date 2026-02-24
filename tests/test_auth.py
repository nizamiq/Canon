"""
Tests for Canon Authentication

Unit tests for JWT authentication and authorization.
"""

import base64
import json
import time
import pytest

from canon.core.auth import (
    verify_jwt,
    get_current_user,
    CurrentUser,
    JWTPayload,
)


def create_test_token(
    sub: str = "user-123",
    exp: int | None = None,
    iss: str = "https://auth.nizamiq.com",
    aud: str = "canon",
    roles: list[str] | None = None,
    expired: bool = False,
) -> str:
    """Helper to create test JWT tokens."""
    header = {"alg": "RS256", "typ": "JWT"}
    
    if exp is None:
        exp = int(time.time()) + (0 if expired else 3600)
    
    payload = {
        "sub": sub,
        "iss": iss,
        "aud": aud,
        "exp": exp,
        "iat": int(time.time()),
        "email": f"{sub}@test.com",
        "name": f"Test {sub}",
        "roles": roles or ["viewer"],
    }
    
    header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
    payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    signature_b64 = "fakesignature"
    
    return f"{header_b64}.{payload_b64}.{signature_b64}"


class TestJWTVerification:
    """Tests for JWT verification."""

    @pytest.mark.asyncio
    async def test_verify_valid_token(self):
        """Test verifying a valid token."""
        token = create_test_token(sub="user-1", roles=["admin"])
        
        payload = await verify_jwt(token)
        
        assert payload.sub == "user-1"
        assert payload.roles == ["admin"]
        assert payload.email == "user-1@test.com"

    @pytest.mark.asyncio
    async def test_verify_expired_token_fails(self):
        """Test that expired tokens are rejected."""
        token = create_test_token(expired=True)
        
        with pytest.raises(Exception):  # HTTPException
            await verify_jwt(token)

    @pytest.mark.asyncio
    async def test_verify_invalid_format_fails(self):
        """Test that malformed tokens are rejected."""
        with pytest.raises(Exception):
            await verify_jwt("invalid.token.format")

    @pytest.mark.asyncio
    async def test_verify_missing_parts_fails(self):
        """Test that tokens with missing parts are rejected."""
        with pytest.raises(Exception):
            await verify_jwt("only.two")


class TestCurrentUser:
    """Tests for CurrentUser model."""

    def test_current_user_creation(self):
        """Test creating a current user."""
        user = CurrentUser(
            user_id="user-123",
            email="user@test.com",
            name="Test User",
            roles=["admin", "editor"],
            org_id="org-1",
        )
        
        assert user.user_id == "user-123"
        assert user.email == "user@test.com"
        assert user.roles == ["admin", "editor"]

    def test_current_user_minimal(self):
        """Test creating minimal current user."""
        user = CurrentUser(user_id="user-1")
        
        assert user.user_id == "user-1"
        assert user.email is None
        assert user.roles == []
