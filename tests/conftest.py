"""
Canon Test Configuration

Pytest fixtures for testing the Canon application.
"""

import asyncio
import os
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from canon.main import create_app
from canon.models.base import Base
from canon.core.database import async_session_factory, engine


# Test database URL
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "sqlite+aiosqlite:///:memory:"
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_engine():
    """Create a test database engine."""
    # Use SQLite in-memory for testing
    test_engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
    )
    
    # Create all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield test_engine
    
    # Cleanup
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await test_engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    test_session_factory = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    
    async with test_session_factory() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(db_session) -> AsyncGenerator[AsyncClient, None]:
    """Create a test HTTP client."""
    # Override the database session dependency
    from canon.core.database import get_db_session
    
    async def override_get_db():
        yield db_session
    
    app = create_app()
    app.dependency_overrides[get_db_session] = override_get_db
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
def mock_jwt_payload():
    """Create a mock JWT payload for testing."""
    import base64
    import json
    import time
    
    header = {"alg": "RS256", "typ": "JWT"}
    payload = {
        "sub": "test-user-123",
        "iss": "https://auth.nizamiq.com",
        "aud": "canon",
        "exp": int(time.time()) + 3600,
        "iat": int(time.time()),
        "email": "test@nizamiq.com",
        "name": "Test User",
        "roles": ["admin", "editor"],
    }
    
    # Encode header and payload
    header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
    payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    
    # Create a fake signature (won't be verified in tests)
    signature_b64 = "fakesignature123"
    
    return f"{header_b64}.{payload_b64}.{signature_b64}"


@pytest.fixture
def auth_headers(mock_jwt_payload) -> dict:
    """Create authorization headers for testing."""
    return {"Authorization": f"Bearer {mock_jwt_payload}"}
