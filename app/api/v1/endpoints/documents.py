"""
Document processing API endpoints with file upload support.
"""
from fastapi import APIRouter, HTTPException
from celery.result import AsyncResult
from typing import List, Optional

from app.schemas.document import (
    DocumentProcessRequest,
    DocumentProcessResponse,
    SearchRequest,
    SearchResponse,
    ChunksListResponse
)
from app.schemas.task import TaskStatusResponse
from app.tasks.document_tasks import process_pdf_task
from app.core.celery_app import celery_app
from app.services.vectordb_service import VectorDBService

router = APIRouter()
vectordb_service = VectorDBService()


@router.post("/process", response_model=DocumentProcessResponse)
async def process_document(request: DocumentProcessRequest):
    """
    Submit a PDF document for processing.

    The document will be processed asynchronously using Celery.
    Returns a task_id that can be used to check the status.
    """
    try:
        # Submit task to Celery
        task = process_pdf_task.apply_async(
            args=[
                request.pdf_path_or_url,
                request.category,
                request.subcategory
            ]
        )

        return DocumentProcessResponse(
            task_id=task.id,
            status="PENDING",
            message="Document processing task submitted successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit processing task: {str(e)}"
        )


@router.get("/task/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """
    Get the status of a document processing task.
    """
    try:
        task_result = AsyncResult(task_id, app=celery_app)

        response = {
            "task_id": task_id,
            "status": task_result.state,
            "result": None,
            "error": None,
            "progress": None
        }

        if task_result.state == "PENDING":
            response["result"] = {"message": "Task is waiting to be processed"}
        elif task_result.state == "STARTED":
            response["progress"] = task_result.info if task_result.info else {}
        elif task_result.state == "SUCCESS":
            response["result"] = task_result.result
        elif task_result.state == "FAILURE":
            response["error"] = str(task_result.info)

        return TaskStatusResponse(**response)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve task status: {str(e)}"
        )


@router.post("/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """
    Perform semantic search on processed documents.
    """
    try:
        results = vectordb_service.semantic_search(
            query_text=request.query_text,
            n_results=request.n_results,
            category_filter=request.category_filter,
            subcategory_filter=request.subcategory_filter,
            images_only=request.images_only,
            tables_only=request.tables_only
        )

        return SearchResponse(
            query=request.query_text,
            results=results,
            count=len(results)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )


@router.get("/chunks", response_model=ChunksListResponse)
async def list_chunks(
    document_id: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """
    List all chunks or chunks for a specific document.
    """
    try:
        chunks = vectordb_service.list_chunks(
            document_id=document_id,
            limit=limit,
            offset=offset
        )
        return ChunksListResponse(
            chunks=chunks,
            count=len(chunks),
            limit=limit,
            offset=offset
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list chunks: {str(e)}"
        )


@router.get("/list")
async def list_documents():
    """
    List all documents in the vector database.
    """
    try:
        documents = vectordb_service.list_available_documents()
        return {"documents": documents, "count": len(documents)}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list documents: {str(e)}"
        )


@router.delete("/task/{task_id}")
async def revoke_task(task_id: str):
    """
    Revoke a running or pending task.
    """
    try:
        celery_app.control.revoke(task_id, terminate=True)
        return {"message": f"Task {task_id} has been revoked", "task_id": task_id}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to revoke task: {str(e)}"
        )
