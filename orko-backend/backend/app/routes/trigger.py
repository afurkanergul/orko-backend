from __future__ import annotations

from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Header,
    Request,
    HTTPException,
    status,
)
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.schemas.trigger import TriggerRequest, TriggerResponse
from backend.app.schemas.auth import CurrentUser
from backend.app.api.deps.auth import require_trigger_role
from backend.app.api.deps.db import get_db

from backend.app.services.trigger_service import TriggerService
from backend.app.services.workflow.confirmation_service import ConfirmationService
from backend.app.services.workflow.orchestrator import Orchestrator

# ⭐ Rate limiter imports (Day 9)
from backend.app.services.rate_limit.trigger_rate_limiter import (
    TriggerRateLimiter,
    RateLimitExceeded,
)

# ⭐ Abuse monitor (Day 9)
from backend.app.services.monitoring.abuse_monitor import AbuseMonitor

# ⭐ Confidence gating
from backend.app.services.parsing.parser_engine import ParserEngine

from backend.app.core.config import settings

router = APIRouter(prefix="/api", tags=["trigger"])
_trigger_service = TriggerService()


# ---------------------------------------------------------------------------
# MAIN /trigger ENDPOINT
# ---------------------------------------------------------------------------
@router.post("/trigger", response_model=TriggerResponse)
async def post_trigger(
    req: TriggerRequest,
    request: Request,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_trigger_role),
    user_agent: Annotated[str | None, Header(alias="User-Agent")] = None,
) -> TriggerResponse:

    # -----------------------------------------------------------
    # ⭐ DAY 9 — Rate Limiting (Per-user + Per-org)
    # -----------------------------------------------------------
    limiter = TriggerRateLimiter()
    abuse_monitor = AbuseMonitor()

    user_id = getattr(user, "id", None)
    org_id = getattr(req, "org_id", None)

    try:
        limiter.check_and_increment(user_id=user_id, org_id=org_id)
    except RateLimitExceeded:
        abuse_monitor.record_violation(user_id=user_id, org_id=org_id)
        retry_after = settings.RATE_LIMIT_WINDOW_SECONDS

        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please retry later.",
            headers={"Retry-After": str(retry_after)},
        )

    # -----------------------------------------------------------
    # CLIENT IP
    # -----------------------------------------------------------
    client_ip = request.client.host if request.client else None

    # -----------------------------------------------------------
    # ⭐ DAY 9 — Confidence Threshold Gate (<0.6 → human review)
    # -----------------------------------------------------------
    parser = ParserEngine()

    parsed = parser.parse_command(
        text=req.command,
        context={
            "org_id": req.org_id,
            "user_id": user_id,
            "source": getattr(req, "source", None),
            "channel": getattr(req, "channel", None),
        },
    )

    confidence = parsed.get("context", {}).get("confidence", 1.0)
    try:
        confidence = float(confidence)
    except Exception:
        confidence = 1.0

    CONF_THRESHOLD = 0.6

    if confidence < CONF_THRESHOLD:
        parsed.setdefault("context", {})
        parsed["context"]["requires_human_review"] = True

        return TriggerResponse(
            trigger_job_id=None,
            status="requires_review",
            message="Command parsed with low confidence; human review required.",
            parsed=parsed,
        )

    # -----------------------------------------------------------
    # HIGH CONFIDENCE PATH → TriggerService pipeline
    # -----------------------------------------------------------
    result = await _trigger_service.trigger(
        db=db,
        user=user,
        req=req,
        client_ip=client_ip,
        user_agent=user_agent,
        simulate=req.simulate,
    )

    # -----------------------------------------------------------
    # DAY 7 — DEBUG REASONING MODE
    # -----------------------------------------------------------
    if getattr(req, "debug", False) and user.role == "admin":
        reasoning = None
        if hasattr(result, "context") and isinstance(result.context, dict):
            reasoning = result.context.get("reasoning_trace")

        return {
            **result.dict(),
            "debug_reasoning": reasoning,
        }

    return result


# ---------------------------------------------------------------------------
# Confirmation request body
# ---------------------------------------------------------------------------
class ConfirmRequest(BaseModel):
    confirmation_id: str


# ---------------------------------------------------------------------------
# APPROVE PENDING DESTRUCTIVE WORKFLOW
# ---------------------------------------------------------------------------
@router.post("/trigger/confirm")
async def confirm_trigger(
    payload: ConfirmRequest,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_trigger_role),
):
    svc = ConfirmationService()
    req = svc.approve(db, payload.confirmation_id)

    if not req:
        raise HTTPException(status_code=404, detail="Confirmation request not found")

    orchestrator = Orchestrator()
    result = await orchestrator.run(
        workflow_steps=[],
        context=req.parameters,
        scenario="confirmed_destructive",
        workflow_name=req.workflow_name,
        user_id=user.id,
        simulate=False,
    )

    return {
        "status": "confirmed",
        "workflow": req.workflow_name,
        "result": result,
    }


# ---------------------------------------------------------------------------
# REJECT PENDING DESTRUCTIVE WORKFLOW
# ---------------------------------------------------------------------------
@router.post("/trigger/reject")
async def reject_trigger(
    payload: ConfirmRequest,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_trigger_role),
):
    svc = ConfirmationService()
    req = svc.reject(db, payload.confirmation_id)

    if not req:
        raise HTTPException(status_code=404, detail="Confirmation request not found")

    return {"status": "rejected", "workflow": req.workflow_name}
