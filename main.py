from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routers import auth, contracts, default_texts
from app.services.file_service import ensure_directories
from app.logger import get_logger

# Initialize logging
logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Contract Signing Service",
    description="API for managing contract signatures with PDF generation",
    version="1.0.0"
)

# CORS middleware - dynamic configuration based on environment
from app.config import settings
import os

# Get CORS origins with fallback
def get_cors_origins():
    try:
        # First try to get from settings
        origins = settings.ALLOWED_ORIGINS
        if isinstance(origins, list) and origins:
            logger.info(f"Using settings ALLOWED_ORIGINS: {origins}")
            return origins
        elif origins == "*":
            logger.info("Using wildcard CORS: *")
            return ["*"]
        else:
            logger.info(f"Converting single origin to list: {origins}")
            return [origins]
    except Exception as e:
        logger.warning(f"Error reading ALLOWED_ORIGINS from settings: {e}")
        
        # Fallback: read directly from environment
        env_origins = os.getenv("ALLOWED_ORIGINS")
        if env_origins and env_origins.strip() != "*":
            origins_list = [origin.strip() for origin in env_origins.split(',') if origin.strip()]
            logger.info(f"Using environment ALLOWED_ORIGINS: {origins_list}")
            return origins_list
        
        # Final fallback based on environment
        env = os.getenv("ENVIRONMENT", "development")
        if env == "production":
            fallback_origins = [
                "https://sign.delarueda.es",
                "https://sign.back.delarueda.es",
                "https://delarueda-firmacontratosfront-cl4otx.dokploy.cc"
            ]
            logger.info(f"Using production fallback origins: {fallback_origins}")
            return fallback_origins
        else:
            fallback_origins = ["http://localhost:3000", "http://127.0.0.1:3000"]
            logger.info(f"Using development fallback origins: {fallback_origins}")
            return fallback_origins

cors_origins = get_cors_origins()
logger.info(f"CORS origins configured: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Ensure storage directories exist
ensure_directories()
logger.info("Storage directories initialized")

# Mount static files
app.mount("/storage", StaticFiles(directory="storage"), name="storage")

# Include routers
app.include_router(auth.router)
app.include_router(contracts.router)
app.include_router(default_texts.router)
logger.info("Application routers configured")

# Health check endpoint
@app.get("/")
def read_root():
    logger.info("Health check endpoint accessed")
    return {
        "message": "Contract signing service is running.",
        "version": "1.0.0",
        "status": "healthy",
        "environment": settings.ENVIRONMENT
    }

# Debug endpoint for CORS configuration
@app.get("/debug/cors")
def debug_cors():
    import os
    return {
        "configured_origins": cors_origins,
        "settings_origins": getattr(settings, 'ALLOWED_ORIGINS', 'NOT_SET'),
        "environment_var": os.getenv("ENVIRONMENT", "NOT_SET"),
        "allowed_origins_env": os.getenv("ALLOWED_ORIGINS", "NOT_SET"),
        "settings_environment": getattr(settings, 'ENVIRONMENT', 'NOT_SET'),
        "cors_type": type(cors_origins).__name__,
        "cors_count": len(cors_origins) if cors_origins else 0,
        "cors_origins_raw": str(cors_origins)
    }

@app.on_event("startup")
async def startup_event():
    logger.info(f"Application starting in {settings.ENVIRONMENT} environment")
    logger.info(f"CORS origins: {settings.ALLOWED_ORIGINS}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutting down")