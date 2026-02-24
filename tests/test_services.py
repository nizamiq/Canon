"""
Tests for Canon Services

Unit tests for service layer business logic.
"""

import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from canon.services.audit import AuditService
from canon.services.prompt import PromptService
from canon.models.prompt import Prompt, PromptVersion, VersionTag


@pytest.mark.asyncio
class TestPromptService:
    """Tests for PromptService."""

    async def test_create_prompt(self, db_session: AsyncSession):
        """Test creating a prompt."""
        audit = AuditService(db_session)
        service = PromptService(db_session, audit)
        
        prompt = await service.create_prompt(
            name="test-prompt",
            content="Test content",
            description="Test description",
            tags=["draft"],
            actor="test-user",
        )
        
        assert prompt.name == "test-prompt"
        assert prompt.description == "Test description"
        assert prompt.current_version == 1
        assert len(prompt.versions) == 1
        assert len(prompt.tags) == 1

    async def test_create_prompt_duplicate_fails(self, db_session: AsyncSession):
        """Test that duplicate prompt names fail."""
        audit = AuditService(db_session)
        service = PromptService(db_session, audit)
        
        await service.create_prompt(
            name="duplicate",
            content="Content 1",
            actor="test-user",
        )
        
        with pytest.raises(ValueError, match="already exists"):
            await service.create_prompt(
                name="duplicate",
                content="Content 2",
                actor="test-user",
            )

    async def test_list_prompts(self, db_session: AsyncSession):
        """Test listing prompts."""
        audit = AuditService(db_session)
        service = PromptService(db_session, audit)
        
        # Create some prompts
        await service.create_prompt("prompt-1", "Content 1", actor="user1")
        await service.create_prompt("prompt-2", "Content 2", actor="user1")
        await service.create_prompt("prompt-3", "Content 3", actor="user1")
        
        prompts, total = await service.list_prompts()
        
        assert total == 3
        assert len(prompts) == 3

    async def test_list_prompts_pagination(self, db_session: AsyncSession):
        """Test paginated prompt listing."""
        audit = AuditService(db_session)
        service = PromptService(db_session, audit)
        
        # Create prompts
        for i in range(5):
            await service.create_prompt(f"page-prompt-{i}", f"Content {i}", actor="user")
        
        # Get first page
        prompts, total = await service.list_prompts(page=1, page_size=2)
        assert total == 5
        assert len(prompts) == 2
        
        # Get second page
        prompts, _ = await service.list_prompts(page=2, page_size=2)
        assert len(prompts) == 2

    async def test_get_prompt(self, db_session: AsyncSession):
        """Test getting a prompt by name."""
        audit = AuditService(db_session)
        service = PromptService(db_session, audit)
        
        await service.create_prompt("get-test", "Content", description="Get desc", actor="user")
        
        prompt = await service.get_prompt("get-test")
        
        assert prompt is not None
        assert prompt.name == "get-test"
        assert prompt.description == "Get desc"

    async def test_get_prompt_not_found(self, db_session: AsyncSession):
        """Test getting non-existent prompt."""
        audit = AuditService(db_session)
        service = PromptService(db_session, audit)
        
        prompt = await service.get_prompt("nonexistent")
        assert prompt is None

    async def test_create_version(self, db_session: AsyncSession):
        """Test creating a new version."""
        audit = AuditService(db_session)
        service = PromptService(db_session, audit)
        
        # Create prompt
        await service.create_prompt("version-test", "Version 1", actor="user")
        
        # Create new version
        version = await service.create_version("version-test", "Version 2", actor="user")
        
        assert version.version == 2
        assert version.content == "Version 2"
        
        # Verify prompt was updated
        prompt = await service.get_prompt("version-test")
        assert prompt.current_version == 2

    async def test_create_version_prompt_not_found(self, db_session: AsyncSession):
        """Test creating version for non-existent prompt."""
        audit = AuditService(db_session)
        service = PromptService(db_session, audit)
        
        with pytest.raises(ValueError, match="not found"):
            await service.create_version("nonexistent", "Content", actor="user")

    async def test_get_version(self, db_session: AsyncSession):
        """Test getting specific version."""
        audit = AuditService(db_session)
        service = PromptService(db_session, audit)
        
        await service.create_prompt("ver-get-test", "Version 1", actor="user")
        await service.create_version("ver-get-test", "Version 2", actor="user")
        
        v1 = await service.get_version("ver-get-test", 1)
        v2 = await service.get_version("ver-get-test", 2)
        
        assert v1.content == "Version 1"
        assert v2.content == "Version 2"

    async def test_tag_management(self, db_session: AsyncSession):
        """Test tag creation and movement."""
        audit = AuditService(db_session)
        service = PromptService(db_session, audit)
        
        # Create prompt
        await service.create_prompt("tag-test", "V1", actor="user")
        await service.create_version("tag-test", "V2", actor="user")
        
        # Create tag pointing to v1
        tag = await service.get_or_create_tag("tag-test", "production", 1, actor="user")
        assert tag.tag_name == "production"
        
        # Move tag to v2
        tag = await service.get_or_create_tag("tag-test", "production", 2, actor="user")
        
        # Get by tag
        result = await service.get_prompt_by_tag("tag-test", "production")
        assert result is not None
        _, version = result
        assert version.version == 2

    async def test_list_tags(self, db_session: AsyncSession):
        """Test listing tags."""
        audit = AuditService(db_session)
        service = PromptService(db_session, audit)
        
        await service.create_prompt(
            "tag-list-test",
            "Content",
            tags=["draft", "review"],
            actor="user",
        )
        
        tags = await service.list_tags("tag-list-test")
        tag_names = [t.tag_name for t in tags]
        
        assert "draft" in tag_names
        assert "review" in tag_names

    async def test_delete_tag(self, db_session: AsyncSession):
        """Test deleting a tag."""
        audit = AuditService(db_session)
        service = PromptService(db_session, audit)
        
        await service.create_prompt("del-tag-test", "Content", tags=["to-delete"], actor="user")
        
        deleted = await service.delete_tag("del-tag-test", "to-delete", actor="user")
        assert deleted is True
        
        # Verify deleted
        tags = await service.list_tags("del-tag-test")
        assert "to-delete" not in [t.tag_name for t in tags]


@pytest.mark.asyncio
class TestAuditService:
    """Tests for AuditService."""

    async def test_log_action(self, db_session: AsyncSession):
        """Test logging an action."""
        audit = AuditService(db_session)
        
        log = await audit.log(
            action="CREATE",
            resource_type="PROMPT",
            resource_id="prompt-123",
            actor="user-1",
            details={"key": "value"},
        )
        
        assert log.action == "CREATE"
        assert log.resource_type == "PROMPT"
        assert log.resource_id == "prompt-123"
        assert log.actor == "user-1"

    async def test_log_prompt_create(self, db_session: AsyncSession):
        """Test logging prompt creation."""
        audit = AuditService(db_session)
        
        log = await audit.log_prompt_create(
            prompt_id="p1",
            prompt_name="test",
            actor="user",
            initial_content="Content",
        )
        
        assert log.action == "CREATE"
        assert log.resource_type == "PROMPT"

    async def test_log_version_create(self, db_session: AsyncSession):
        """Test logging version creation."""
        audit = AuditService(db_session)
        
        log = await audit.log_version_create(
            prompt_id="p1",
            version=2,
            actor="user",
            content_length=100,
        )
        
        assert log.action == "CREATE"
        assert log.resource_type == "VERSION"

    async def test_log_tag_update(self, db_session: AsyncSession):
        """Test logging tag update."""
        audit = AuditService(db_session)
        
        log = await audit.log_tag_update(
            prompt_id="p1",
            tag_name="production",
            old_version=1,
            new_version=2,
            actor="user",
        )
        
        assert log.action == "TAG"
        assert log.resource_type == "TAG"

    async def test_get_resource_history(self, db_session: AsyncSession):
        """Test getting resource history."""
        audit = AuditService(db_session)
        
        # Create some logs
        await audit.log_prompt_create("p1", "test", "user")
        await audit.log_version_create("p1", 2, "user", 100)
        
        history = await audit.get_resource_history("PROMPT", "p1")
        
        assert len(history) >= 1
