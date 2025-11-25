# backend/app/services/workflow/dlq_helpers.py

from datetime import datetime, timezone
from typing import Dict, Any, Optional

from backend.app.db.session import SessionLocal
from backend.app.db import models
from backend.app.services.workflow.dlq import write_trigger_dlq_record


# ============================================================
# WORKFLOW ENGINE DLQ (ALREADY EXISTING)
# ============================================================

def record_dlq_failure(scenario: str, error_message: str, context: dict):
    """Insert one failed workflow entry into the WorkflowDLQ table."""
    db = SessionLocal()
    try:
        row = models.WorkflowDLQ(
            scenario=scenario,
            error_message=error_message,
            context=context,
            created_at=datetime.now(timezone.utc),
            replayed=False
        )
        db.add(row)
        db.commit()
    finally:
        db.close()


def fetch_failed_workflows():
    """Retrieve all unreplayed DLQ entries."""
    db = SessionLocal()
    try:
        rows = db.query(models.WorkflowDLQ).filter(
            models.WorkflowDLQ.replayed == False
        ).all()
        return rows
    finally:
        db.close()


def mark_replayed(dlq_id: int):
    """Mark a DLQ entry as successfully replayed."""
    db = SessionLocal()
    try:
        entry = db.query(models.WorkflowDLQ).filter(
            models.WorkflowDLQ.id == dlq_id
        ).first()
        if entry:
            entry.replayed = True
            entry.replayed_at = datetime.now(timezone.utc)
            db.commit()
    finally:
        db.close()


# ============================================================
# NEW — TRIGGER FAILURE DLQ WRAPPER (POINTS TO dlq.py)
# ============================================================

def record_trigger_dlq(payload: Dict[str, Any], error: str, job_id: Optional[str] = None):
    """
    Uniform entrypoint for writing TriggerQueue failures to DLQ.
    Makes code in Celery worker very clean.
    """
    write_trigger_dlq_record(
        payload=payload,
        error=error,
        trigger_job_id=job_id,
    )
