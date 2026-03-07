"""
Tests for Canon SDK Client

Comprehensive unit tests for the CanonClient class with mocked API responses.
"""

import pytest
import respx
from httpx import Response

from canon_sdk import CanonClient
from canon_sdk.exceptions import (
    CanonAuthError,
    CanonNotFoundError,
    CanonValidationError,
)
from canon_sdk.models import Prompt, PromptList


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def client():
    """Create a CanonClient instance for testing."""
    return CanonClient(
        base_url="https://canon.nizamiq.com",
        api_token="test-token",
        enable_caching=False,  # Disable caching for tests
    )


@pytest.fixture
def sample_prompt_data():
    """Sample prompt data for mocking API responses."""
    return {
        "name": "test-prompt",
        "description": "A test prompt",
        "current_version": 2,
        "versions": [
            {
                "version": 1,
                "content": "Version 1 content",
                "created_at": "2026-01-01T00:00:00",
                "created_by": "user1",
                "tags": ["draft"],
                "metadata": {},
            },
            {
                "version": 2,
                "content": "Version 2 content",
                "created_at": "2026-01-02T00:00:00",
                "created_by": "user1",
                "tags": ["production"],
                "metadata": {},
            },
        ],
        "created_at": "2026-01-01T00:00:00",
        "updated_at": "2026-01-02T00:00:00",
        "owner": "user1",
        "metadata": {},
    }


# =============================================================================
# Client Initialization Tests
# =============================================================================

class TestClientInitialization:
    """Tests for CanonClient initialization."""
    
    def test_client_initialization(self):
        """Test that client can be initialized with all parameters."""
        client = CanonClient(
            base_url="https://canon.nizamiq.com",
            api_token="secret-token",
            timeout=60.0,
            max_retries=5,
            enable_caching=True,
            cache_ttl=600.0,
        )
        
        assert client.base_url == "https://canon.nizamiq.com"
        assert client.api_token == "secret-token"
        assert client.timeout == 60.0
        assert client.max_retries == 5
        assert client.enable_caching is True
        assert client.cache_ttl == 600.0
    
    def test_client_without_token(self):
        """Test that client can be initialized without token."""
        client = CanonClient(base_url="https://canon.nizamiq.com")
        
        assert client.api_token is None
    
    def test_client_context_manager(self):
        """Test that client works as context manager."""
        with CanonClient("https://canon.nizamiq.com") as client:
            assert isinstance(client, CanonClient)


# =============================================================================
# Prompt Retrieval Tests
# =============================================================================

class TestPromptRetrieval:
    """Tests for prompt retrieval methods."""
    
    @respx.mock
    def test_get_prompt_success(self, client, sample_prompt_data):
        """Test successful prompt retrieval."""
        route = respx.get("https://canon.nizamiq.com/v1/prompts/test-prompt").mock(
            return_value=Response(200, json=sample_prompt_data)
        )
        
        prompt = client.get_prompt("test-prompt")
        
        assert isinstance(prompt, Prompt)
        assert prompt.name == "test-prompt"
        assert prompt.current_version == 2
        assert len(prompt.versions) == 2
        assert route.called
    
    @respx.mock
    def test_get_prompt_not_found(self, client):
        """Test 404 response handling."""
        respx.get("https://canon.nizamiq.com/v1/prompts/nonexistent").mock(
            return_value=Response(404, json={"detail": "Prompt not found"})
        )
        
        with pytest.raises(CanonNotFoundError):
            client.get_prompt("nonexistent")
    
    @respx.mock
    def test_get_prompt_auth_error(self, client):
        """Test 401 response handling."""
        respx.get("https://canon.nizamiq.com/v1/prompts/test-prompt").mock(
            return_value=Response(401, json={"detail": "Unauthorized"})
        )
        
        with pytest.raises(CanonAuthError):
            client.get_prompt("test-prompt")
    
    @respx.mock
    def test_list_prompts_success(self, client):
        """Test successful prompt listing."""
        response_data = {
            "items": [{
                "name": "prompt-1",
                "description": "First prompt",
                "current_version": 1,
                "versions": [],
                "created_at": "2026-01-01T00:00:00",
                "updated_at": "2026-01-01T00:00:00",
                "owner": "user1",
                "metadata": {},
            }],
            "total": 1,
            "page": 1,
            "page_size": 20,
        }
        
        route = respx.get("https://canon.nizamiq.com/v1/prompts").mock(
            return_value=Response(200, json=response_data)
        )
        
        result = client.list_prompts()
        
        assert isinstance(result, PromptList)
        assert result.total == 1
        assert len(result.items) == 1
        assert result.items[0].name == "prompt-1"
        assert route.called
    
    @respx.mock
    def test_list_prompts_with_search(self, client):
        """Test prompt listing with search parameter."""
        response_data = {"items": [], "total": 0, "page": 1, "page_size": 20}
        
        route = respx.get(
            "https://canon.nizamiq.com/v1/prompts",
        ).mock(return_value=Response(200, json=response_data))
        
        client.list_prompts(search="email")
        
        assert route.called
        request = route.calls[0].request
        assert "search=email" in str(request.url)


# =============================================================================
# Prompt Management Tests
# =============================================================================

class TestPromptManagement:
    """Tests for prompt management methods."""
    
    @respx.mock
    def test_create_prompt_success(self, client, sample_prompt_data):
        """Test successful prompt creation."""
        route = respx.post("https://canon.nizamiq.com/v1/prompts").mock(
            return_value=Response(201, json=sample_prompt_data)
        )
        
        prompt = client.create_prompt(
            name="test-prompt",
            content="Test content",
            description="A test prompt",
        )
        
        assert isinstance(prompt, Prompt)
        assert prompt.name == "test-prompt"
        assert route.called
    
    @respx.mock
    def test_create_prompt_validation_error(self, client):
        """Test validation error handling."""
        respx.post("https://canon.nizamiq.com/v1/prompts").mock(
            return_value=Response(422, json={"detail": "Invalid prompt name"})
        )
        
        with pytest.raises(CanonValidationError):
            client.create_prompt(name="", content="Test")
    
    @respx.mock
    def test_create_version_success(self, client, sample_prompt_data):
        """Test successful version creation."""
        route = respx.post("https://canon.nizamiq.com/v1/prompts/test-prompt/versions").mock(
            return_value=Response(201, json=sample_prompt_data)
        )
        
        prompt = client.create_version("test-prompt", "New version content")
        
        assert isinstance(prompt, Prompt)
        assert route.called
    
    @respx.mock
    def test_update_tags_success(self, client, sample_prompt_data):
        """Test successful tag update."""
        route = respx.put("https://canon.nizamiq.com/v1/prompts/test-prompt/tags").mock(
            return_value=Response(200, json=sample_prompt_data)
        )
        
        prompt = client.update_tags("test-prompt", 2, ["production", "stable"])
        
        assert isinstance(prompt, Prompt)
        assert route.called
    
    @respx.mock
    def test_delete_prompt_success(self, client):
        """Test successful prompt deletion."""
        route = respx.delete("https://canon.nizamiq.com/v1/prompts/test-prompt").mock(
            return_value=Response(204)
        )
        
        client.delete_prompt("test-prompt")
        
        assert route.called


# =============================================================================
# Cache Tests
# =============================================================================

class TestCaching:
    """Tests for client caching functionality."""
    
    @respx.mock
    def test_caching_enabled(self, sample_prompt_data):
        """Test that caching works when enabled."""
        client = CanonClient(
            "https://canon.nizamiq.com",
            enable_caching=True,
        )
        
        route = respx.get("https://canon.nizamiq.com/v1/prompts/test-prompt").mock(
            return_value=Response(200, json=sample_prompt_data)
        )
        
        # First call should hit the API
        prompt1 = client.get_prompt("test-prompt")
        assert route.call_count == 1
        
        # Second call should use cache
        prompt2 = client.get_prompt("test-prompt")
        assert route.call_count == 1  # No additional API call
        
        assert prompt1.name == prompt2.name
    
    @respx.mock
    def test_cache_bypass(self, client, sample_prompt_data):
        """Test that cache can be bypassed."""
        route = respx.get("https://canon.nizamiq.com/v1/prompts/test-prompt").mock(
            return_value=Response(200, json=sample_prompt_data)
        )
        
        # First call
        client.get_prompt("test-prompt", use_cache=False)
        
        # Second call without cache
        client.get_prompt("test-prompt", use_cache=False)
        
        assert route.call_count == 2
    
    def test_clear_cache(self):
        """Test cache clearing."""
        client = CanonClient(
            "https://canon.nizamiq.com",
            enable_caching=True,
        )
        
        # Add something to cache manually
        client._set_cache("test-key", "test-value")
        assert client.get_cache_stats()["size"] == 1
        
        # Clear cache
        client.clear_cache()
        assert client.get_cache_stats()["size"] == 0
    
    def test_cache_stats(self):
        """Test cache statistics."""
        client = CanonClient(
            "https://canon.nizamiq.com",
            enable_caching=True,
        )
        
        stats = client.get_cache_stats()
        assert "size" in stats
        assert "max_size" in stats


# =============================================================================
# Retry Logic Tests
# =============================================================================

class TestRetryLogic:
    """Tests for retry behavior."""
    
    @respx.mock
    def test_retry_on_connection_error(self, client):
        """Test that connection errors trigger retries."""
        # First two calls fail, third succeeds
        route = respx.get("https://canon.nizamiq.com/v1/prompts/test").mock(
            side_effect=[
                Response(500, json={"error": "Server error"}),
                Response(500, json={"error": "Server error"}),
                Response(200, json={
                    "name": "test",
                    "current_version": 1,
                    "versions": [],
                    "created_at": "2026-01-01T00:00:00",
                    "updated_at": "2026-01-01T00:00:00",
                    "owner": "user1",
                    "metadata": {},
                }),
            ]
        )
        
        # Should retry and eventually succeed
        prompt = client.get_prompt("test")
        
        assert prompt.name == "test"
        assert route.call_count == 3


# =============================================================================
# Edge Cases
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and error conditions."""
    
    def test_base_url_trailing_slash(self):
        """Test that trailing slashes are handled correctly."""
        client = CanonClient("https://canon.nizamiq.com/")
        assert client.base_url == "https://canon.nizamiq.com"
    
    @respx.mock
    def test_empty_list_response(self, client):
        """Test handling of empty list response."""
        respx.get("https://canon.nizamiq.com/v1/prompts").mock(
            return_value=Response(200, json={
                "items": [],
                "total": 0,
                "page": 1,
                "page_size": 20,
            })
        )
        
        result = client.list_prompts()
        
        assert result.total == 0
        assert len(result.items) == 0
        assert result.has_next is False
        assert result.has_prev is False
