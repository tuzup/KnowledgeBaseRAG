"""
Core configuration management using Pydantic Settings.
"""
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Configuration
    PROJECT_NAME: str = "FastAPI Docling Service"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: str = "http://localhost:3000"

    # OpenAI Configuration
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-large"

    # Celery Configuration - RabbitMQ for both broker and backend
    CELERY_BROKER_URL: str = "amqp://guest:guest@rabbitmq:5672//"
    CELERY_RESULT_BACKEND: str = "rpc://"

    # RabbitMQ Configuration
    RABBITMQ_HOST: str = "rabbitmq"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASSWORD: str = "guest"
    RABBITMQ_VHOST: str = "/"

    # ChromaDB Configuration
    CHROMA_PERSIST_DIR: str = "./data/chroma"
    CHROMA_COLLECTION_NAME: str = "document_collection"

    # Document Processing Configuration
    MAX_TOKENS: int = 8191
    CHUNKING_MAX_TOKENS: int = 8191
    UPLOAD_DIR: str = "./uploads"
    OUTPUT_DIR: str = "./outputs"
    IMAGES_SCALE: float = 2.0
    PICTURE_DESCRIPTION_TIMEOUT: int = 60
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB

    # Celery Worker Configuration
    CELERY_WORKER_CONCURRENCY: int = 4
    CELERY_WORKER_PREFETCH_MULTIPLIER: int = 1
    CELERY_TASK_TIME_LIMIT: int = 3600
    CELERY_TASK_SOFT_TIME_LIMIT: int = 3000

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()
