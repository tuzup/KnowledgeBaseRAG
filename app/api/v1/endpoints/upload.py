"""
File upload endpoint.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import shutil
import uuid
from datetime import datetime

from app.core.config import settings

router = APIRouter()


@router.post("/file")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a PDF file.

    Returns the file path where the file is stored.
    """
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    # Validate file size
    contents = await file.read()
    if len(contents) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE / (1024*1024)}MB"
        )

    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    safe_filename = f"{timestamp}_{unique_id}_{file.filename}"
    file_path = Path(settings.UPLOAD_DIR) / safe_filename

    # Save file
    try:
        with open(file_path, "wb") as f:
            f.write(contents)

        return {
            "filename": safe_filename,
            "original_filename": file.filename,
            "file_path": str(file_path),
            "file_size": len(contents),
            "upload_time": timestamp
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save file: {str(e)}"
        )
