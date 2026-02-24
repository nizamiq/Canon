"""
Tests for Canon API Endpoints

Comprehensive tests for prompt management API.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestHealthEndpoint:
    """Tests for health check endpoint."""

    async def test_health_check(self, client: AsyncClient):
        """Test health check returns OK."""
        response = await client.get("/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data


@pytest.mark.asyncio
class TestPromptList:
    """Tests for prompt listing endpoint."""

    async def test_list_prompts_empty(self, client: AsyncClient, auth_headers: dict):
        """Test listing prompts when empty."""
        response = await client.get("/v1/prompts", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["prompts"] == []
        assert data["total"] == 0

    async def test_list_prompts_pagination(self, client: AsyncClient, auth_headers: dict):
        """Test pagination parameters."""
        response = await client.get(
            "/v1/prompts?page=1&page_size=10",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 10

    async def test_list_prompts_unauthenticated(self, client: AsyncClient):
        """Test listing prompts without authentication."""
        response = await client.get("/v1/prompts")
        # In development mode, should still work
        assert response.status_code in [200, 401]


@pytest.mark.asyncio
class TestPromptCreate:
    """Tests for prompt creation endpoint."""

    async def test_create_prompt(self, client: AsyncClient, auth_headers: dict):
        """Test creating a new prompt."""
        response = await client.post(
            "/v1/prompts",
            headers=auth_headers,
            json={
                "name": "test-prompt",
                "description": "A test prompt",
                "content": "This is the prompt content.",
                "tags": ["draft"],
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "test-prompt"
        assert data["description"] == "A test prompt"
        assert data["current_version"] == 1
        assert len(data["versions"]) == 1

    async def test_create_prompt_duplicate(self, client: AsyncClient, auth_headers: dict):
        """Test creating duplicate prompt fails."""
        # Create first prompt
        await client.post(
            "/v1/prompts",
            headers=auth_headers,
            json={
                "name": "duplicate-test",
                "content": "Content 1",
            },
        )
        
        # Try to create duplicate
        response = await client.post(
            "/v1/prompts",
            headers=auth_headers,
            json={
                "name": "duplicate-test",
                "content": "Content 2",
            },
        )
        assert response.status_code == 409

    async def test_create_prompt_missing_content(self, client: AsyncClient, auth_headers: dict):
        """Test creating prompt without content fails."""
        response = await client.post(
            "/v1/prompts",
            headers=auth_headers,
            json={
                "name": "no-content",
                "description": "Missing content",
            },
        )
        assert response.status_code == 422


@pytest.mark.asyncio
class TestPromptGet:
    """Tests for prompt retrieval endpoint."""

    async def test_get_prompt(self, client: AsyncClient, auth_headers: dict):
        """Test getting an existing prompt."""
        # Create prompt
        await client.post(
            "/v1/prompts",
            headers=auth_headers,
            json={
                "name": "get-test",
                "content": "Get test content",
            },
        )
        
        # Get prompt
        response = await client.get("/v1/prompts/get-test", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "get-test"

    async def test_get_prompt_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test getting non-existent prompt."""
        response = await client.get("/v1/prompts/nonexistent", headers=auth_headers)
        assert response.status_code == 404


@pytest.mark.asyncio
class TestVersionManagement:
    """Tests for version management endpoints."""

    async def test_create_version(self, client: AsyncClient, auth_headers: dict):
        """Test creating a new version."""
        # Create prompt
        await client.post(
            "/v1/prompts",
            headers=auth_headers,
            json={
                "name": "version-test",
                "content": "Version 1 content",
            },
        )
        
        # Create new version
        response = await client.post(
            "/v1/prompts/version-test/versions",
            headers=auth_headers,
            json={
                "content": "Version 2 content",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["version"] == 2

    async def test_get_specific_version(self, client: AsyncClient, auth_headers: dict):
        """Test getting a specific version."""
        # Create prompt
        await client.post(
            "/v1/prompts",
            headers=auth_headers,
            json={
                "name": "version-get-test",
                "content": "Version 1",
            },
        )
        
        # Get version 1
        response = await client.get(
            "/v1/prompts/version-get-test/versions/1",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["version"] == 1
        assert data["content"] == "Version 1"


@pytest.mark.asyncio
class TestTagManagement:
    """Tests for tag management endpoints."""

    async def test_list_tags(self, client: AsyncClient, auth_headers: dict):
        """Test listing tags for a prompt."""
        # Create prompt with tags
        await client.post(
            "/v1/prompts",
            headers=auth_headers,
            json={
                "name": "tag-list-test",
                "content": "Content",
                "tags": ["draft", "testing"],
            },
        )
        
        response = await client.get("/v1/prompts/tag-list-test/tags", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["tags"]) >= 2

    async def test_update_tag(self, client: AsyncClient, auth_headers: dict):
        """Test updating a tag to point to specific version."""
        # Create prompt
        await client.post(
            "/v1/prompts",
            headers=auth_headers,
            json={
                "name": "tag-update-test",
                "content": "Version 1",
                "tags": ["draft"],
            },
        )
        
        # Create version 2
        await client.post(
            "/v1/prompts/tag-update-test/versions",
            headers=auth_headers,
            json={"content": "Version 2"},
        )
        
        # Update tag to point to version 2
        response = await client.put(
            "/v1/prompts/tag-update-test/tags/production",
            headers=auth_headers,
            json={"version": 2},
        )
        assert response.status_code == 200

    async def test_delete_tag(self, client: AsyncClient, auth_headers: dict):
        """Test deleting a tag."""
        # Create prompt
        await client.post(
            "/v1/prompts",
            headers=auth_headers,
            json={
                "name": "tag-delete-test",
                "content": "Content",
                "tags": ["to-delete"],
            },
        )
        
        # Delete tag
        response = await client.delete(
            "/v1/prompts/tag-delete-test/tags/to-delete",
            headers=auth_headers,
        )
        assert response.status_code == 204

    async def test_get_by_tag(self, client: AsyncClient, auth_headers: dict):
        """Test getting prompt version by tag."""
        # Create prompt
        await client.post(
            "/v1/prompts",
            headers=auth_headers,
            json={
                "name": "tag-get-test",
                "content": "Version 1",
                "tags": ["production"],
            },
        )
        
        # Get by tag
        response = await client.get(
            "/v1/prompts/tag-get-test/tag/production",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "content" in data

    async def test_get_by_tag_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test getting by non-existent tag."""
        # Create prompt
        await client.post(
            "/v1/prompts",
            headers=auth_headers,
            json={
                "name": "tag-notfound-test",
                "content": "Content",
            },
        )
        
        response = await client.get(
            "/v1/prompts/tag-notfound-test/tag/nonexistent",
            headers=auth_headers,
        )
        assert response.status_code == 404
