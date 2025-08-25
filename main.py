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

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
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

@app.on_event("startup")
async def startup_event():
    logger.info(f"Application starting in {settings.ENVIRONMENT} environment")
    logger.info(f"CORS origins: {settings.ALLOWED_ORIGINS}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutting down")