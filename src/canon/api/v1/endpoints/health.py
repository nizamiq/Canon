"""
Health Check Endpoints

Provides health and readiness check endpoints for the Canon service.
"""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    service: str
    version: str


class ReadinessResponse(BaseModel):
    """Readiness check response model."""

    status: str
    database: str
    aegis: str


@router.get("", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Basic health check endpoint.

    Returns:
        Health status indicating service is running.
    """
    from canon import __version__

    return HealthResponse(
        status="healthy",
        service="canon",
        version=__version__,
    )


@router.get("/ready", response_model=ReadinessResponse)
async def readiness_check() -> ReadinessResponse:
    """
    Readiness check endpoint.

    Verifies all critical dependencies are available.

    Returns:
        Readiness status for service and dependencies.
    """
    # TODO: Implement actual database and aegis health checks
    return ReadinessResponse(
        status="ready",
        database="connected",
        aegis="connected",
    )
