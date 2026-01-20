"""
Global ChromaDB client management.
"""
import chromadb
from chromadb.config import Settings as ChromaSettings
from app.core.config import settings

# Global client instance
_chroma_client = None


def get_chroma_client(force_refresh: bool = False):
    """Get or create the global ChromaDB client."""
    global _chroma_client
    if _chroma_client is None or force_refresh:
        _chroma_client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
    return _chroma_client


def get_collection(collection_name: str = None):
    """Get or create a collection."""
    client = get_chroma_client()
    name = collection_name or settings.CHROMA_COLLECTION_NAME
    return client.get_or_create_collection(name=name)