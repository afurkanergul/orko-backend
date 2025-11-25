# backend/app/services/workflow/dlq.py

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

# Trigger DLQ file sink
# This stays generic and domain-safe
_TRIGGER_DLQ_FILE = Path("backend") / "dlq_trigger_errors.jsonl"


def write_trigger_dlq_record(
    payload: Dict[str, Any],
    error: str,
    trigger_job_id: Optional[str] = None,
) -> None:
    """
    Persist a dead-letter record for a failed TRIGGER execution.
    This is separate from WorkflowDLQ (which stores engine-step failures).
    """
    record = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "trigger_job_id": trigger_job_id,
        "payload": payload,
        "error": error,
    }

    _TRIGGER_DLQ_FILE.parent.mkdir(parents=True, exist_ok=True)
    with _TRIGGER_DLQ_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
