"""
Pydantic schemas for document-related requests and responses.
"""
from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field


class DocumentProcessRequest(BaseModel):
    """Request schema for processing a PDF document."""

    pdf_path_or_url: str = Field(..., description="Local path or URL to PDF")
    category: str = Field(..., description="Document category")
    subcategory: Optional[str] = Field(None, description="Document subcategory")


class DocumentMetadata(BaseModel):
    """Metadata for a processed document chunk."""

    filename: str
    document_id: str
    category: str
    subcategory: str = ""
    page_numbers: str = ""
    title: str = ""
    source_path: str
    has_images: bool = False
    image_count: int = 0
    table_count: int = 0
    image_references: str = ""
    image_descriptions: str = ""
    figure_captions: str = ""


class DocumentChunk(BaseModel):
    """Processed document chunk with text and metadata."""

    chunk_id: str
    text: str
    metadata: Dict[str, Any]


class DocumentProcessResponse(BaseModel):
    """Response schema for document processing task."""

    task_id: str = Field(..., description="Celery task ID")
    status: str = Field(..., description="Task status")
    message: str = Field(..., description="Response message")


class SearchRequest(BaseModel):
    """Request schema for semantic search."""

    query_text: str = Field(..., description="Search query")
    n_results: int = Field(5, ge=1, le=100, description="Number of results")
    category_filter: Optional[str] = Field(None, description="Filter by category")
    subcategory_filter: Optional[str] = Field(None, description="Filter by subcategory")
    images_only: bool = Field(False, description="Search only chunks with images")
    tables_only: bool = Field(False, description="Search only chunks with tables")


class SearchResult(BaseModel):
    """Single search result."""

    chunk_id: str
    document_text: str
    metadata: Dict
    distance: float


class SearchResponse(BaseModel):
    """Response schema for search results."""

    query: str
    results: List[SearchResult]
    count: int


class ChunksListResponse(BaseModel):
    """Response schema for listing chunks."""

    chunks: List[DocumentChunk]
    count: int
    limit: int
    offset: int
