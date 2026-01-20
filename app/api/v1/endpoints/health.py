"""
Health check endpoints.
"""
from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()

@router.get("")
async def health_check():
    """Simple health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": "1.0.0"
    }

@router.get("/ready")
async def readiness_check():
    """Readiness check for kubernetes/orchestration."""
    return {"status": "ready"}
