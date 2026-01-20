"""
Celery tasks for document processing.
"""
import logging
from typing import Optional
from pathlib import Path

from app.core.celery_app import celery_app
from app.services.document_service import DocumentService
from app.services.vectordb_service import VectorDBService

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="app.tasks.document_tasks.process_pdf_task")
def process_pdf_task(
    self,
    pdf_path_or_url: str,
    category: str,
    subcategory: Optional[str] = None
):
    """
    Process a PDF document and store in vector database.

    Args:
        pdf_path_or_url: Path or URL to PDF
        category: Document category
        subcategory: Document subcategory

    Returns:
        dict: Processing results
    """
    try:
        # Update task state
        self.update_state(
            state="STARTED",
            meta={"stage": "initializing", "progress": 0}
        )
       
        logger.info(f"Processing PDF: {pdf_path_or_url}")

        # Initialize services
        doc_service = DocumentService()
        vectordb_service = VectorDBService()

        # Process PDF
        self.update_state(
            state="STARTED",
            meta={"stage": "processing_pdf", "progress": 20}
        )

        texts, metadatas, ids = doc_service.process_pdf(
            pdf_path_or_url,
            category,
            subcategory
        )

        logger.info(f"Processed {len(texts)} chunks from PDF")

        # Store in vector database
        self.update_state(
            state="STARTED",
            meta={"stage": "storing_embeddings", "progress": 60}
        )

        vectordb_service.add_documents(texts, metadatas, ids)

        logger.info(f"Stored {len(ids)} chunks in vector database")

        # Complete
        self.update_state(
            state="STARTED",
            meta={"stage": "completed", "progress": 100}
        )

        return {
            "status": "success",
            "chunks_processed": len(texts),
            "document_id": metadatas[0]["document_id"] if metadatas else None,
            "filename": metadatas[0]["filename"] if metadatas else None
        }

    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}", exc_info=True)
        self.update_state(
            state="FAILURE",
            meta={"error": str(e)}
        )
        raise
