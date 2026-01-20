"""
Pydantic schemas for Celery task status and responses.
"""
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class TaskStatus(str, Enum):
    """Celery task status enum."""
    PENDING = "PENDING"
    STARTED = "STARTED"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    RETRY = "RETRY"
    REVOKED = "REVOKED"


class TaskStatusResponse(BaseModel):
    """Response schema for task status check."""

    task_id: str = Field(..., description="Task ID")
    status: TaskStatus = Field(..., description="Current task status")
    result: Optional[Dict[str, Any]] = Field(None, description="Task result if completed")
    error: Optional[str] = Field(None, description="Error message if failed")
    progress: Optional[Dict[str, Any]] = Field(None, description="Task progress information")
