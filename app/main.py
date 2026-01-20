"""
FastAPI main application module with CORS and file upload support.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from app.core.config import settings
from app.api.v1.endpoints import documents, health, upload


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup - Create directories
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
    os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
    print(f"Starting {settings.PROJECT_NAME}")
    yield
    # Shutdown
    print(f"Shutting down {settings.PROJECT_NAME}")


# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="PDF processing service with Docling, Celery, and Vector DB",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware configuration
allowed_origins = settings.CORS_ORIGINS.split(",") if hasattr(settings, 'CORS_ORIGINS') else ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for serving uploaded files
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")
app.mount("/outputs", StaticFiles(directory=settings.OUTPUT_DIR), name="outputs")

# Include routers
app.include_router(
    health.router,
    prefix=f"{settings.API_V1_PREFIX}/health",
    tags=["health"]
)

app.include_router(
    upload.router,
    prefix=f"{settings.API_V1_PREFIX}/upload",
    tags=["upload"]
)

app.include_router(
    documents.router,
    prefix=f"{settings.API_V1_PREFIX}/documents",
    tags=["documents"]
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "FastAPI Docling Service with React Frontend",
        "version": "1.0.0",
        "docs": "/docs",
        "frontend": "http://localhost:3000"
    }
