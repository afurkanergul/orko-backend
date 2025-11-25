from __future__ import annotations

from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from backend.app.schemas.trigger import TriggerRequest, TriggerResponse
from backend.app.schemas.auth import CurrentUser
from backend.app.models.trigger_audit import TriggerAudit

from backend.app.services.parser.command_parser import CommandParser
from backend.app.services.workflow.trigger_queue import TriggerQueue


class TriggerService:
    """
    TriggerService (Option A — Async via Celery Queue)
    --------------------------------------------------
    New responsibility:

    - Parse raw_command → intent + workflow mapping
    - Create TriggerAudit row with status="queued"
    - Enqueue job to Celery TriggerQueue
    - Return TriggerResponse(status="queued")

    Actual workflow execution now happens inside Celery workers
    (see backend/app/services/workflow/trigger_queue.py).
    """

    def __init__(self) -> None:
        # Existing parser (you already use this in your project)
        self._parser = CommandParser()

    async def trigger(
        self,
        db: Session,
        user: CurrentUser,
        req: TriggerRequest,
        client_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> TriggerResponse:
        """
        Main entry point for /api/trigger.

        IMPORTANT (Option A):
        - Does NOT execute the workflow directly.
        - Only parses + audits + enqueues job to Celery.
        """

        # ------------------------------------------------------------
        # 1) Parse + map intent (only if raw_command exists)
        # ------------------------------------------------------------
        if req.raw_command:
            # Your existing parser path
            parsed_intent, mapped = self._parser.parse_and_map(
                req.raw_command,
                context=req.context.data,
            )

            intent_name = parsed_intent.name
            workflow_name = mapped["workflow_name"]
            parameters: Dict[str, Any] = mapped["parameters"]

        else:
            # Manual trigger without NLP parsing
            intent_name = req.intent_name
            workflow_name = req.parameters.get("workflow_name") or intent_name
            parameters = req.parameters

        # ------------------------------------------------------------
        # 2) Create initial TriggerAudit row with status="queued"
        # ------------------------------------------------------------
        audit = TriggerAudit(
            user_id=user.id,
            user_role=user.role,
            intent_name=intent_name,
            workflow_name=workflow_name,
            raw_command=req.raw_command,
            parameters=parameters,
            simulate=req.simulate,
            status="queued",          # 🔥 Option A: queued, not running
            client_ip=client_ip,
            user_agent=user_agent,
        )

        db.add(audit)
        db.commit()
        db.refresh(audit)

        # ------------------------------------------------------------
        # 3) Enqueue job to Celery (TriggerQueue)
        # ------------------------------------------------------------
        payload: Dict[str, Any] = {
            "audit_id": audit.id,
            "user_id": user.id,
            "user_role": user.role,
            "workflow_name": workflow_name,
            "parameters": parameters,
            "simulate": req.simulate,
        }

        # Returns Celery task id (you can store/use later if needed)
        trigger_job_id = TriggerQueue.enqueue_trigger(payload)

        # (Optional) you could store trigger_job_id in a new column later

        # ------------------------------------------------------------
        # 4) Return queued TriggerResponse (non-blocking)
        # ------------------------------------------------------------
        return TriggerResponse(
            trigger_id=str(audit.id),
            workflow_name=workflow_name or "",
            status="queued",           # 🔥 now queued, not success/error
            simulate=req.simulate,
            missing_parameters=[],     # slot-filling step will populate later
        )
