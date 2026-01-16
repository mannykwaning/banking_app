"""
Main FastAPI application for the Banking App.
Production-ready structure with repository and service layer pattern.
"""

from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import time
import logging
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.config import settings
from app.core.database import create_tables, get_db
from app.core.logging import setup_logging, get_logger
from app.api.v1 import router as api_v1_router
from app.core.error_handlers import register_exception_handlers


# Initialize logging
setup_logging(
    log_level=settings.log_level,
    log_dir=settings.log_dir,
    app_name=settings.app_name.lower().replace(" ", "_"),
    log_format=settings.log_format,
    date_format=settings.log_date_format,
    message_format=settings.log_message_format,
)

logger = get_logger(__name__)


# Lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database tables on startup and cleanup on shutdown."""
    logger.info(
        "Starting application",
        extra={
            "app_name": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment,
            "debug": settings.debug,
        },
    )
    create_tables()
    logger.info("Database tables created successfully")
    logger.info("Application startup complete")

    yield

    # Graceful shutdown - cleanup resources
    logger.info("Initiating graceful shutdown")
    try:
        # Close database connections
        from app.core.database import engine

        engine.dispose()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error during shutdown cleanup: {str(e)}")
    finally:
        logger.info("Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="A production-ready banking application backend API with FastAPI and SQLite",
    docs_url="/docs" if settings.debug else None,  # Disable docs in production
    redoc_url="/redoc" if settings.debug else None,  # Disable redoc in production
    lifespan=lifespan,
)


# Register error handlers
register_exception_handlers(app)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests and responses."""
    start_time = time.time()

    # Log request
    logger.info(
        "Incoming request",
        extra={
            "method": request.method,
            "path": request.url.path,
            "client_host": request.client.host if request.client else None,
            "query_params": str(request.query_params),
        },
    )

    # Process request
    response = await call_next(request)

    # Calculate processing time
    process_time = time.time() - start_time

    # Log response
    logger.info(
        "Request completed",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "process_time_ms": round(process_time * 1000, 2),
        },
    )

    # Add processing time header
    response.headers["X-Process-Time"] = str(process_time)

    return response


@app.get("/health", tags=["Health"])
def health_check():
    """Basic liveness check - returns healthy if service is running."""
    logger.debug("Health check endpoint accessed")
    return {"status": "healthy", "service": settings.app_name}


@app.get("/health/ready", tags=["Health"])
def health_ready(db: Session = Depends(get_db)):
    """Readiness check - verifies database connectivity."""
    try:
        # Ping the database by executing a simple query
        db.execute(text("SELECT 1"))
        logger.debug("Health ready check passed")
        return {
            "status": "ready",
            "service": settings.app_name,
            "database": "connected",
        }
    except Exception as e:
        logger.error(f"Health ready check failed: {str(e)}")
        return {
            "status": "not_ready",
            "service": settings.app_name,
            "database": "disconnected",
            "error": str(e),
        }


# Include API v1 router
app.include_router(api_v1_router, prefix=settings.api_v1_prefix)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
