from __future__ import annotations

from typing import Any, Dict
from sqlalchemy.orm import Session

from backend.app.db.session import SessionLocal
from backend.app.models.trigger_audit import TriggerAudit


class AuditLogger:
    """
    Centralized audit logger for ORKO workflow executions.

    This logger appends details to the TriggerAudit entry that was
    created by the API/TriggerService before enqueueing the Celery task.

    The logger DOES NOT create new audit rows.
    It updates the existing row with result details.
    """

    def log(
        self,
        workflow_name: str,
        parameters: Dict[str, Any],
        result: Dict[str, Any],
        user_id: str,
    ) -> None:
        """
        Update the existing TriggerAudit record for this workflow.
        """
        db: Session = SessionLocal()
        try:
            # Look up most recent audit record for this user + workflow
            # (API + TriggerQueue created this row earlier)
            audit_row = (
                db.query(TriggerAudit)
                  .filter(TriggerAudit.workflow_name == workflow_name)
                  .filter(TriggerAudit.user_id == user_id)
                  .order_by(TriggerAudit.id.desc())
                  .first()
            )

            if not audit_row:
                # If no audit row exists, skip logging silently
                return

            # Update fields
            audit_row.parameters = parameters
            audit_row.error_message = result.get("error")
            audit_row.status = "success" if result.get("success") else "error"

            # Commit
            db.add(audit_row)
            db.commit()

        finally:
            db.close()
