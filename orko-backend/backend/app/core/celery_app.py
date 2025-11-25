# backend/app/core/celery_app.py

from __future__ import annotations
from celery import Celery
from backend.app.core.config import settings

# ---------------------------------------------------------
# Celery Application (ORKO Trigger Queue)
# ---------------------------------------------------------

celery_app = Celery(
    "orko",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Default queue
celery_app.conf.task_default_queue = settings.TRIGGER_QUEUE_NAME

# Dead-letter queue
celery_app.conf.task_queues = {
    settings.TRIGGER_QUEUE_NAME: {
        "exchange": settings.TRIGGER_QUEUE_NAME,
        "binding_key": settings.TRIGGER_QUEUE_NAME,
    },
    settings.TRIGGER_DLQ_NAME: {
        "exchange": settings.TRIGGER_DLQ_NAME,
        "binding_key": settings.TRIGGER_DLQ_NAME,
    },
}

celery_app.conf.task_routes = {
    "backend.app.tasks.trigger_worker.process_trigger": {
        "queue": settings.TRIGGER_QUEUE_NAME
    }
}

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

