"""
Canon FastAPI Application Entry Point

The main entry point for running the Canon prompt registry service.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from canon import __version__
from canon.api.v1 import api_router
from canon.core.config import settings
from canon.core.logging import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager for startup/shutdown events."""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    # TODO: Initialize database connection pool
    # TODO: Initialize Aegis client
    yield
    logger.info(f"Shutting down {settings.app_name}")
    # TODO: Close database connection pool


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        description="Centralized AI Agent Prompt Registry for the NizamIQ ecosystem.",
        version=__version__,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # TODO: Configure based on environment
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API routers
    app.include_router(api_router)

    return app


# Create the application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "canon.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
