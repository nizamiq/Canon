"""
Canon API v1 Module

Contains all v1 API routers and endpoints.
"""

from fastapi import APIRouter

from canon.api.v1.endpoints import health, prompts

api_router = APIRouter(prefix="/v1")

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(prompts.router, prefix="/prompts", tags=["prompts"])

__all__ = ["api_router"]
