"""Tests for Canon Python SDK."""

import pytest
from httpx import Response
from canon.sdk.client import CanonClient
from canon.main import app
from fastapi.testclient import TestClient

# Create a mock transport that uses FastAPI TestClient
# Since we are using an in-memory store in endpoints, we can test seamlessly.

@pytest.fixture
def test_client():
    return TestClient(app)

class MockHttpxClient:
    def __init__(self, test_client):
        self.client = test_client

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def get(self, url, **kwargs):
        res = self.client.get(url.replace("http://test", ""))
        # wrap the httpx response minimally
        class FakeResponse:
            def __init__(self, r):
                self.status_code = r.status_code
                self._json = r.json()
            def json(self):
                return self._json
            def raise_for_status(self):
                if self.status_code >= 400:
                    raise Exception(f"HTTP Error {self.status_code}")
        return FakeResponse(res)

    def post(self, url, json=None, **kwargs):
        res = self.client.post(url.replace("http://test", ""), json=json)
        class FakeResponse:
            def __init__(self, r):
                self.status_code = r.status_code
                self._json = r.json()
            def json(self):
                return self._json
            def raise_for_status(self):
                if self.status_code >= 400:
                    raise Exception(f"HTTP Error {self.status_code}")
        return FakeResponse(res)

@pytest.fixture
def canon_client(test_client, monkeypatch):
    """Fixture that returns a CanonClient patched to use the TestClient."""
    import httpx
    
    # Patch httpx.Client to return our MockHttpxClient
    monkeypatch.setattr(httpx, "Client", lambda timeout=None: MockHttpxClient(test_client))
    
    return CanonClient(base_url="http://test")

def test_sdk_create_and_get_prompt(canon_client):
    """Test SDK can create and retrieve a prompt."""
    
    # 1. Create prompt
    new_prompt = canon_client.create_prompt(
        name="atlas-sys-prompt",
        description="System prompt for Atlas solution generation",
        content="You are an expert AI architect...",
        tags=["production", "atlas"]
    )
    
    assert new_prompt.name == "atlas-sys-prompt"
    assert new_prompt.current_version == 1
    
    # 2. Get prompt
    fetched_prompt = canon_client.get_prompt("atlas-sys-prompt")
    
    assert fetched_prompt.name == "atlas-sys-prompt"
    assert fetched_prompt.tags == ["production", "atlas"]
    assert len(fetched_prompt.versions) == 1
    assert fetched_prompt.versions[0].version == 1
    assert fetched_prompt.versions[0].content == "You are an expert AI architect..."

def test_sdk_get_prompt_version(canon_client):
    """Test SDK can fetch a specific version."""
    # The prompt was created in the previous test? 
    # No, fixtures are per-test. So we recreate it.
    canon_client.create_prompt(
        name="recce-sys-prompt",
        content="You are an OSINT agent...",
    )
    
    version_data = canon_client.get_prompt_version("recce-sys-prompt", 1)
    assert version_data.version == 1
    assert version_data.content == "You are an OSINT agent..."
