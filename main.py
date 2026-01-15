"""
Main FastAPI application for the Banking App.
Production-ready structure with repository and service layer pattern.
"""

from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import create_tables
from app.api.v1 import router as api_v1_router


# Lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database tables on startup."""
    create_tables()
    yield


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="A production-ready banking application backend API with FastAPI and SQLite",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


@app.get("/", tags=["Root"])
def root():
    """Root endpoint - health check."""
    return {
        "message": "Welcome to the Banking App API",
        "version": settings.app_version,
        "status": "operational",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": settings.app_name}


# Include API v1 router
app.include_router(api_v1_router, prefix=settings.api_v1_prefix)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
