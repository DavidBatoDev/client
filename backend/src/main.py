"""
Social Media OCR Backend API
FastAPI application for handling image uploads, OCR processing, and layout extraction.
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import uvicorn
from loguru import logger

from .config.settings import get_settings
from .database.connection import init_database
from .routers import images, ocr, layouts, auth, users
from .middleware.rate_limiting import RateLimitMiddleware
from .middleware.error_handling import ErrorHandlingMiddleware

# Initialize settings
settings = get_settings()

# Security scheme
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events
    """
    # Startup
    logger.info("Starting Social Media OCR Backend API")
    await init_database()
    logger.info("Database initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Social Media OCR Backend API")

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered Social Media OCR Backend API",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=settings.ALLOWED_METHODS.split(","),
    allow_headers=settings.ALLOWED_HEADERS.split(","),
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.DEBUG else ["localhost", "127.0.0.1"]
)

app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(RateLimitMiddleware)

# Include routers
app.include_router(
    auth.router,
    prefix="/api/v1/auth",
    tags=["Authentication"]
)

app.include_router(
    users.router,
    prefix="/api/v1/users",
    tags=["Users"]
)

app.include_router(
    images.router,
    prefix="/api/v1/images",
    tags=["Images"]
)

app.include_router(
    ocr.router,
    prefix="/api/v1/ocr",
    tags=["OCR Processing"]
)

app.include_router(
    layouts.router,
    prefix="/api/v1/layouts",
    tags=["Layout Management"]
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }

# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint
    """
    return {
        "message": "Welcome to Social Media OCR Backend API",
        "version": settings.APP_VERSION,
        "docs": "/docs" if settings.DEBUG else None
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    ) 