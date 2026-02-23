"""Tests for Canon API endpoints."""

import pytest
from fastapi.testclient import TestClient

from canon.main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


class TestHealthEndpoints:
    """Tests for health check endpoints."""

    def test_health_check(self, client):
        """Test health check returns ok status."""
        response = client.get("/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "canon"

    def test_health_ready(self, client):
        """Test readiness check endpoint."""
        response = client.get("/v1/health/ready")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data


class TestPromptEndpoints:
    """Tests for prompt management endpoints."""

    def test_list_prompts_empty(self, client):
        """Test listing prompts when empty."""
        response = client.get("/v1/prompts")
        
        assert response.status_code == 200
        data = response.json()
        assert "prompts" in data
        assert "total" in data
        assert data["total"] >= 0

    def test_create_prompt(self, client):
        """Test creating a new prompt."""
        prompt_data = {
            "name": "test-prompt",
            "description": "A test prompt",
            "content": "This is test prompt content",
            "tags": ["test", "example"]
        }
        
        response = client.post("/v1/prompts", json=prompt_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "test-prompt"
        assert data["current_version"] == 1

    def test_create_duplicate_prompt(self, client):
        """Test creating a duplicate prompt fails."""
        prompt_data = {
            "name": "duplicate-test",
            "content": "First prompt"
        }
        
        # First creation should succeed
        response1 = client.post("/v1/prompts", json=prompt_data)
        assert response1.status_code == 201
        
        # Second creation should fail
        response2 = client.post("/v1/prompts", json=prompt_data)
        assert response2.status_code == 409

    def test_get_prompt(self, client):
        """Test getting a specific prompt."""
        # First create a prompt
        prompt_data = {
            "name": "get-test-prompt",
            "content": "Test content"
        }
        client.post("/v1/prompts", json=prompt_data)
        
        # Then get it
        response = client.get("/v1/prompts/get-test-prompt")
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "get-test-prompt"

    def test_get_nonexistent_prompt(self, client):
        """Test getting a nonexistent prompt returns 404."""
        response = client.get("/v1/prompts/nonexistent-prompt")
        
        assert response.status_code == 404

    def test_get_prompt_version(self, client):
        """Test getting a specific prompt version."""
        # First create a prompt
        prompt_data = {
            "name": "version-test-prompt",
            "content": "Version 1 content"
        }
        client.post("/v1/prompts", json=prompt_data)
        
        # Get version 1
        response = client.get("/v1/prompts/version-test-prompt/versions/1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["version"] == 1

    def test_list_prompts_with_pagination(self, client):
        """Test listing prompts with pagination."""
        response = client.get("/v1/prompts?page=1&page_size=10")
        
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 10
