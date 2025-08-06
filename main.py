from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routers import auth, contracts, default_texts
from app.services.file_service import ensure_directories

# Create FastAPI app
app = FastAPI(
    title="Contract Signing Service",
    description="API for managing contract signatures with PDF generation",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure storage directories exist
ensure_directories()

# Mount static files
app.mount("/storage", StaticFiles(directory="storage"), name="storage")

# Include routers
app.include_router(auth.router)
app.include_router(contracts.router)
app.include_router(default_texts.router)

# Health check endpoint
@app.get("/")
def read_root():
    return {
        "message": "Contract signing service is running.",
        "version": "1.0.0",
        "status": "healthy"
    }