"""
Canon - NizamIQ Prompt Registry

A centralized, version-controlled registry for all AI agent prompts
used in the NizamIQ ecosystem.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from canon.api.v1.endpoints import health, prompts
from canon.core.config import settings
from canon.core.database import engine
from canon.models.base import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown events:
    - Startup: Initialize database connections
    - Shutdown: Clean up resources
    """
    # Startup
    # TODO: Create tables if they don't exist (for development)
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # Shutdown
    await engine.dispose()


def create_application() -> FastAPI:
    """
    Application factory.
    
    Creates and configures the FastAPI application with:
    - Lifespan management
    - CORS middleware
    - API routers
    - Health checks
    
    Returns:
        Configured FastAPI application instance.
    """
    app = FastAPI(
        title="Canon - NizamIQ Prompt Registry",
        description="""
        A centralized, version-controlled registry for all AI agent prompts
        used in the NizamIQ ecosystem.
        
        ## Features
        
        - **Prompt Versioning**: Immutable version history for all prompts
        - **Tag Management**: Mutable tags (production, staging, etc.)
        - **Access Control**: Aegis RBAC integration
        - **Audit Logging**: Complete change history
        - **Search**: Full-text search across prompts
        """,
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # TODO: Restrict in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(
        health.router,
        prefix="/health",
        tags=["Health"],
    )
    app.include_router(
        prompts.router,
        prefix="/v1/prompts",
        tags=["Prompts"],
    )
    
    return app


# Create the application instance
app = create_application()


@app.get("/healthz", status_code=200, tags=["Health"])
async def health_check():
    """
    Kubernetes-style health check endpoint.
    
    Returns:
        Simple health status for load balancer health checks.
    """
    return {"status": "ok"}
