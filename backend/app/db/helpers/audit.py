# backend/app/db/helpers/audit.py
# -------------------------------------------------------------
#  Sub-Step 2 Part C — Writer Helpers
#  Purpose: Write breadcrumb entries into ingestion_audit table
# -------------------------------------------------------------

from datetime import datetime, timezone
from sqlalchemy.orm import Session
from backend.app.db.models import IngestionAudit

# -------------------------------------------------------------
# Helper 1:  audit_received
# -------------------------------------------------------------
def audit_received(db: Session, source: str, msg_id: str | None = None,
                   org_id: int | None = None) -> int:
    """
    Record that a message/file was received.
    Returns the new audit row's ID.
    """
    audit = IngestionAudit(
        source=source.lower(),
        msg_id=msg_id,
        org_id=org_id,
        received_at=datetime.now(timezone.utc),
        status="received",
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)
    return audit.id


# -------------------------------------------------------------
# Helper 2:  audit_processed
# -------------------------------------------------------------
def audit_processed(db: Session, audit_id: int) -> None:
    """
    Mark an audit row as processed.
    """
    row = db.query(IngestionAudit).filter(IngestionAudit.id == audit_id).first()
    if not row:
        return
    row.status = "processed"
    row.processed_at = datetime.now(timezone.utc)
    db.commit()


# -------------------------------------------------------------
# Helper 3:  audit_failed
# -------------------------------------------------------------
def audit_failed(db: Session, audit_id: int, error: str) -> None:
    """
    Mark an audit row as failed and store error message.
    """
    row = db.query(IngestionAudit).filter(IngestionAudit.id == audit_id).first()
    if not row:
        return
    row.status = "failed"
    row.error = error[:500]  # avoid extremely long traces
    row.processed_at = datetime.now(timezone.utc)
    db.commit()
