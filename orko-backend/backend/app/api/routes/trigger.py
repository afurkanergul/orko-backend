# backend/app/api/routes/trigger.py

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.orm import Session

from backend.app.schemas.trigger import TriggerRequest, TriggerResponse
from backend.app.schemas.auth import CurrentUser
from backend.app.api.deps.auth import require_trigger_role
from backend.app.api.deps.db import get_db
from backend.app.services.trigger_service import TriggerService

router = APIRouter(prefix="/api", tags=["trigger"])

# Singleton service instance
_trigger_service = TriggerService()


@router.post("/trigger", response_model=TriggerResponse)
async def post_trigger(
    req: TriggerRequest,
    request: Request,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_trigger_role),
    user_agent: Annotated[str | None, Header(alias="User-Agent")] = None,
) -> TriggerResponse:
    """
    Trigger a workflow execution.
    - Parses intent if raw_command is provided
    - Applies RBAC (operator/admin)
    - Stores audit logs
    - Sends to Workflow Orchestrator
    """

    client_ip = request.client.host if request.client else None

    return _trigger_service.trigger(
        db=db,
        user=user,
        req=req,
        client_ip=client_ip,
        user_agent=user_agent,
    )
