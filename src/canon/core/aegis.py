"""
Canon Aegis Integration

Provides Aegis SDK integration for RBAC enforcement.
"""

from typing import Any

import httpx

from canon.core.config import settings
from canon.core.logging import get_logger

logger = get_logger(__name__)


class AegisClient:
    """
    Client for interacting with the Aegis governance service.

    Aegis provides centralized RBAC enforcement for all NizamIQ services.
    """

    # Canon resource types for Aegis
    RESOURCE_PROMPT = "canon:prompt"
    RESOURCE_VERSION = "canon:version"
    RESOURCE_TAG = "canon:tag"

    # Canon actions for Aegis
    ACTION_CREATE = "create"
    ACTION_READ = "read"
    ACTION_UPDATE = "update"
    ACTION_DELETE = "delete"
    ACTION_APPROVE = "approve"
    ACTION_PUBLISH = "publish"

    def __init__(self, base_url: str | None = None, timeout: int = 30):
        """
        Initialize Aegis client.

        Args:
            base_url: Aegis service URL. Falls back to settings.
            timeout: Request timeout in seconds.
        """
        self.base_url = base_url or settings.aegis_url
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def check_permission(
        self,
        user_id: str,
        resource: str,
        action: str,
        resource_id: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> bool:
        """
        Check if a user has permission to perform an action.

        Args:
            user_id: User identifier.
            resource: Resource type (e.g., "canon:prompt").
            action: Action to perform (e.g., "create").
            resource_id: Optional specific resource ID.
            context: Optional additional context.

        Returns:
            bool: True if permitted, False otherwise.
        """
        if not self.base_url:
            logger.warning("Aegis URL not configured - allowing all operations")
            return True

        try:
            client = await self._get_client()

            payload = {
                "user_id": user_id,
                "resource": resource,
                "action": action,
                "resource_id": resource_id,
                "context": context or {},
            }

            response = await client.post(
                f"{self.base_url}/api/v1/permissions/check",
                json=payload,
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("allowed", False)

            logger.warning(
                f"Aegis permission check failed: {response.status_code}"
            )
            return False

        except Exception as e:
            logger.error(f"Aegis client error: {e}")
            # Fail closed in production, fail open in development
            return settings.environment == "development"

    async def check_prompt_permission(
        self,
        user_id: str,
        action: str,
        prompt_id: str | None = None,
    ) -> bool:
        """
        Check permission for prompt operations.

        Args:
            user_id: User identifier.
            action: Action to perform.
            prompt_id: Optional prompt ID for resource-specific checks.

        Returns:
            bool: True if permitted.
        """
        return await self.check_permission(
            user_id=user_id,
            resource=self.RESOURCE_PROMPT,
            action=action,
            resource_id=prompt_id,
        )

    async def check_version_permission(
        self,
        user_id: str,
        action: str,
        prompt_id: str,
        version: int | None = None,
    ) -> bool:
        """
        Check permission for version operations.

        Args:
            user_id: User identifier.
            action: Action to perform.
            prompt_id: Prompt ID.
            version: Optional version number.

        Returns:
            bool: True if permitted.
        """
        resource_id = f"{prompt_id}:v{version}" if version else prompt_id
        return await self.check_permission(
            user_id=user_id,
            resource=self.RESOURCE_VERSION,
            action=action,
            resource_id=resource_id,
        )

    async def log_action(
        self,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: str,
        details: dict[str, Any] | None = None,
    ) -> bool:
        """
        Log an action to Aegis for audit purposes.

        Args:
            user_id: User who performed the action.
            action: Action performed.
            resource_type: Type of resource.
            resource_id: Resource identifier.
            details: Additional details.

        Returns:
            bool: True if logged successfully.
        """
        if not self.base_url:
            return True

        try:
            client = await self._get_client()

            payload = {
                "user_id": user_id,
                "action": action,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "details": details or {},
            }

            response = await client.post(
                f"{self.base_url}/api/v1/audit/log",
                json=payload,
            )

            return response.status_code == 200

        except Exception as e:
            logger.error(f"Aegis audit log error: {e}")
            return False


# Global Aegis client instance
_aegis_client: AegisClient | None = None


def get_aegis_client() -> AegisClient:
    """Get or create global Aegis client."""
    global _aegis_client
    if _aegis_client is None:
        _aegis_client = AegisClient()
    return _aegis_client


async def close_aegis_client() -> None:
    """Close global Aegis client."""
    global _aegis_client
    if _aegis_client:
        await _aegis_client.close()
        _aegis_client = None
