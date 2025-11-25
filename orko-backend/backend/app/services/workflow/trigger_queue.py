# backend/app/services/workflow/trigger_queue.py

from __future__ import annotations

from typing import Any, Dict

from celery import Celery
from celery.utils.log import get_task_logger

from backend.app.core.config import settings
from backend.app.db.session import SessionLocal
from backend.app.models.trigger_audit import TriggerAudit
from backend.app.services.workflow.orchestrator import Orchestrator
from backend.app.services.workflow.dlq_helpers import record_trigger_dlq

# Step 7 — Telemetry
from backend.app.services.telemetry.telemetry_collector import TelemetryCollector

logger = get_task_logger(__name__)

# Logical version tag for this trigger pipeline (for observability)
TRIGGER_ENGINE_VERSION = "v7"


# ------------------------------------------------------------
# Celery application for ORKO trigger workflows
# ------------------------------------------------------------
celery_app = Celery(
    "orko_trigger_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_default_queue=settings.TRIGGER_QUEUE_NAME,
    task_acks_late=True,
    worker_prefetch_multiplier=4,
    task_time_limit=300,        # 5 minutes hard limit
    task_soft_time_limit=240,   # 4 minutes soft limit
)


# ------------------------------------------------------------
# Celery Task: Execute a single trigger workflow
# ------------------------------------------------------------
@celery_app.task(
    name="trigger.run_workflow",
    bind=True,
    max_retries=3,
    default_retry_delay=30,
)
def run_workflow_task(self, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes a workflow trigger asynchronously.

    Expected payload keys:
    - audit_id        (str | None)
    - user_id         (str | None)
    - user_role       (str | None)
    - workflow_name   (str)
    - parameters      (dict)
    - simulate        (bool)
    - metadata        (dict, optional)
    """
    db = SessionLocal()

    audit_id = payload.get("audit_id")
    workflow_name = payload.get("workflow_name")
    parameters = payload.get("parameters") or {}
    simulate = payload.get("simulate", False)

    # Ensure metadata exists and carry trigger engine version for telemetry
    metadata = payload.get("metadata") or {}
    metadata.setdefault("trigger_engine_version", TRIGGER_ENGINE_VERSION)
    payload["metadata"] = metadata

    logger.info(
        "ORKO Trigger Worker START: audit_id=%s workflow=%s simulate=%s",
        audit_id,
        workflow_name,
        simulate,
    )

    try:
        # --------------------------------------------------------
        # 1) Mark audit row as running
        # --------------------------------------------------------
        audit = None
        if audit_id is not None:
            audit = db.get(TriggerAudit, audit_id)
            if audit:
                audit.status = "running"
                audit.error_message = None
                db.add(audit)
                db.commit()

        # --------------------------------------------------------
        # 2) Execute workflow via Orchestrator
        # --------------------------------------------------------
        orchestrator = Orchestrator()

        result = orchestrator.run(
            workflow_steps=[],        # workflow steps can be attached later
            context=parameters,
            workflow_name=workflow_name,
            user_id=payload.get("user_id"),
            simulate=simulate,
        )

        # --------------------------------------------------------
        # 3) Mark audit as successful
        # --------------------------------------------------------
        if audit:
            audit.status = "success"
            audit.error_message = None
            db.add(audit)
            db.commit()

        logger.info("ORKO Trigger Worker SUCCESS: audit_id=%s", audit_id)

        # Telemetry — workflow-level is already handled in Orchestrator,
        # so we only return structured result here.
        return {
            "status": "success",
            "audit_id": audit_id,
            "workflow_name": workflow_name,
            "result": result,
        }

    except Exception as exc:
        logger.exception("ORKO Trigger Worker ERROR: audit_id=%s", audit_id)

        # --------------------------------------------------------
        # DLQ (Trigger-level)
        # --------------------------------------------------------
        record_trigger_dlq(payload, str(exc), job_id=self.request.id)

        # --------------------------------------------------------
        # Update audit log
        # --------------------------------------------------------
        if audit_id is not None:
            audit = db.get(TriggerAudit, audit_id)
            if audit:
                audit.status = "error"
                audit.error_message = str(exc)
                db.add(audit)
                db.commit()

        # --------------------------------------------------------
        # Retry
        # --------------------------------------------------------
        try:
            raise self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            logger.error("Max retries exceeded for audit_id=%s", audit_id)

            return {
                "status": "failed",
                "audit_id": audit_id,
                "workflow_name": workflow_name,
                "error": str(exc),
            }

    finally:
        db.close()


# ------------------------------------------------------------
# Enqueue façade used from FastAPI/services
# ------------------------------------------------------------
class TriggerQueue:
    """
    Thin façade for queuing triggers into Celery.

    Remains domain-agnostic to respect ORKO’s multi-industry,
    cross-domain architecture.

    This is effectively the v7 'superset' behaviour:
    - supports simulate mode
    - records telemetry
    - carries trigger_engine_version in metadata
    """

    @staticmethod
    def enqueue_trigger(payload: Dict[str, Any]) -> str:
        """
        Enqueue a trigger for async execution.
        Returns Celery job ID.

        Payload may include:
        - parsed: parsed intent (for telemetry)
        - workflow_name, parameters, simulate, metadata, etc.
        """
        # Ensure metadata exists and add engine version (non-breaking)
        metadata = payload.get("metadata") or {}
        metadata.setdefault("trigger_engine_version", TRIGGER_ENGINE_VERSION)
        payload["metadata"] = metadata

        async_result = run_workflow_task.delay(payload)
        job_id = async_result.id

        # -----------------------------------------------
        # Step 7 — Telemetry entry for trigger enqueue
        # -----------------------------------------------
        TelemetryCollector.record_trigger(job_id, payload.get("parsed", {}))

        return job_id
