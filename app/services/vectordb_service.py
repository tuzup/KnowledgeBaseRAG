"""
Vector database service for ChromaDB operations.
"""
import logging
from typing import List, Optional, Dict

from app.core.database import get_chroma_client, get_collection
from app.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


class VectorDBService:
    """Service for vector database operations."""

    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.client = get_chroma_client()
        self.collection = get_collection()
    
    def add_documents(
        self,
        texts: List[str],
        metadatas: List[dict],
        ids: List[str]
    ):
        """Add documents to the vector database."""
        logger.info(f"Computing embeddings for {len(texts)} documents")
        embeddings = self.embedding_service.get_embeddings(texts)

        logger.info(f"Adding {len(ids)} documents to collection")
        self.collection.add(
            documents=texts,
            metadatas=metadatas,
            embeddings=embeddings,
            ids=ids,
        )

        logger.info("Documents added successfully")

    def semantic_search(
        self,
        query_text: str,
        n_results: int = 5,
        category_filter: Optional[str] = None,
        subcategory_filter: Optional[str] = None,
        images_only: bool = False,
        tables_only: bool = False
    ) -> List[Dict]:
        """Perform semantic search."""
        self.client = get_chroma_client(force_refresh=True)
        self.collection = get_collection()

        # Build where clause
        where_clause = {}
        if category_filter:
            where_clause["category"] = category_filter
        if subcategory_filter:
            where_clause["subcategory"] = subcategory_filter
        if images_only:
            where_clause["has_images"] = True
        if tables_only:
            where_clause["table_count"] = {"$gt": 0}

        # Get query embedding
        q_emb = self.embedding_service.get_embeddings([query_text])[0]

        # Query
        query_params = {
            "query_embeddings": [q_emb],
            "n_results": n_results,
            "include": ["documents", "metadatas", "distances"]
        }
        if where_clause:
            query_params["where"] = where_clause

        print("Query Params:", query_params)  # Debugging line

        results = self.collection.query(**query_params)

        # Format results
        formatted_results = []
        if results["ids"] and results["ids"][0]:
            for i in range(len(results["ids"][0])):
                formatted_results.append({
                    "chunk_id": results["ids"][0][i],
                    "document_text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i]
                })

        return formatted_results

    def list_chunks(
        self,
        document_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict]:
        """List chunks with pagination."""
        query_params = {
            "limit": limit,
            "offset": offset,
            "include": ["documents", "metadatas"]
        }

        if document_id:
            query_params["where"] = {"document_id": document_id}

        results = self.collection.get(**query_params)

        chunks = []
        if results["ids"]:
            for i in range(len(results["ids"])):
                chunks.append({
                    "chunk_id": results["ids"][i],
                    "text": results["documents"][i],
                    "metadata": results["metadatas"][i]
                })

        return chunks

    def list_available_documents(self) -> Dict:
        """List all documents in the collection."""
        all_docs = self.collection.get(include=["metadatas"])
        documents = {}

        for metadata in all_docs["metadatas"]:
            doc_id = metadata["document_id"]
            if doc_id not in documents:
                documents[doc_id] = {
                    "filename": metadata["filename"],
                    "category": metadata["category"],
                    "subcategory": metadata.get("subcategory"),
                    "source_path": metadata["source_path"],
                }

        return documents