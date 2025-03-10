"""
Main FastAPI application for the OMRA Appliance Repair Business Automation System.
"""
import logging
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from backend.api import api_router
from backend.core.config import settings
from backend.core.logging import setup_logging
from backend.core.audit import setup_audit_logging
from backend.core.middleware import setup_middleware
from backend.db.session import engine, create_tables
from backend.db.mongodb import get_mongodb, close_mongodb_connection

# Setup logging
setup_logging()
logger = logging.getLogger("omra")

# Setup audit logging
setup_audit_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Set up CORS middleware
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Setup application middleware
setup_middleware(app)

# Request middleware for logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log request information."""
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = (time.time() - start_time) * 1000
    logger.info(
        f"Request: {request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Process time: {process_time:.2f}ms"
    )
    
    return response

# Error handlers
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Handle generic exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# MongoDB connection events
@app.on_event("startup")
async def startup_db_client():
    """Initialize database connections on startup."""
    # Create SQL tables
    await create_tables()
    logger.info("SQL database tables initialized")
    
    # Initialize MongoDB connection
    mongodb = await get_mongodb()
    logger.info("MongoDB connection initialized")
    
    # Log application startup
    logger.info(f"Application {settings.PROJECT_NAME} started")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Audit logging: {'enabled' if settings.AUDIT_LOG_ENABLED else 'disabled'}")

@app.on_event("shutdown")
async def shutdown_db_client():
    """Close database connections on shutdown."""
    # Close MongoDB connection
    await close_mongodb_connection()
    logger.info("MongoDB connection closed")
    logger.info(f"Application {settings.PROJECT_NAME} shutdown")

# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"} 