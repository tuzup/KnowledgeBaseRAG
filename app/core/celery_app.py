"""
Celery application configuration with RabbitMQ RPC backend.
"""
from celery import Celery
from app.core.config import settings

# Initialize Celery app with RabbitMQ as both broker and backend
celery_app = Celery(
    "document_processor",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,  # RPC backend using RabbitMQ
    include=["app.tasks.document_tasks"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=settings.CELERY_TASK_TIME_LIMIT,
    task_soft_time_limit=settings.CELERY_TASK_SOFT_TIME_LIMIT,
    worker_prefetch_multiplier=settings.CELERY_WORKER_PREFETCH_MULTIPLIER,
    worker_max_tasks_per_child=1000,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    result_expires=3600,
    # RPC backend specific settings
    result_persistent=False,
)

# Task routes configuration
celery_app.conf.task_routes = {
    "app.tasks.document_tasks.process_pdf_task": {"queue": "pdf_processing"},
}
