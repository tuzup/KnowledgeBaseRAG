"""
OpenAI embedding service.
"""
import logging
from typing import List
from openai import OpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating embeddings."""

    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_EMBEDDING_MODEL

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        logger.info(f"Generating embeddings for {len(texts)} texts")

        response = self.client.embeddings.create(
            model=self.model,
            input=texts,
        )

        embeddings = [d.embedding for d in response.data]
        logger.info(f"Generated {len(embeddings)} embeddings")

        return embeddings
