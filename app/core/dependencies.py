"""
FastAPI dependency injection functions.
"""
from app.services.vectordb_service import VectorDBService
from app.services.embedding_service import EmbeddingService
from app.services.document_service import DocumentService

def get_vectordb_service() -> VectorDBService:
    """Get VectorDB service instance."""
    return VectorDBService()

def get_embedding_service() -> EmbeddingService:
    """Get Embedding service instance."""
    return EmbeddingService()

def get_document_service() -> DocumentService:
    """Get Document service instance."""
    return DocumentService()
