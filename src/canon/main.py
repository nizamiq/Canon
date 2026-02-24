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
from canon.core.database import init_db, close_db
from canon.core.aegis import close_aegis_client
from canon.core.logging import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager for startup/shutdown events."""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")

    # Initialize database connection pool
    try:
        await init_db()
        logger.info("Database connection pool initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

    yield

    # Cleanup
    logger.info(f"Shutting down {settings.app_name}")
    await close_db()
    await close_aegis_client()
    logger.info("Cleanup complete")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        description="Centralized AI Agent Prompt Registry for the NizamIQ ecosystem.",
        version=__version__,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Configure CORS based on environment
    allowed_origins = ["*"] if settings.environment == "development" else [
        "https://nizamiq.com",
        "https://*.nizamiq.com",
        "https://portal.nizamiq.com",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
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
