from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ============================================================
# Trigger Context
# ============================================================

class TriggerContext(BaseModel):
    """
    Additional context passed into the parser / workflow engine.
    Example: org, desk, session metadata, etc.
    """
    data: Dict[str, Any] = Field(default_factory=dict)


# ============================================================
# Trigger Request Schema
# ============================================================

class TriggerRequest(BaseModel):
    """
    Request body for POST /api/trigger.
    Supports two modes:

    1. raw_command = free text (Parser generates intent automatically)
    2. intent_name + parameters (manual trigger, no parser)

    simulate=True:
        - prevents side effects
        - used by guardrails + destructive workflows + tests

    debug=True:
        - if AND ONLY IF user.role == "admin", returns model reasoning_trace
        - used for Day 7 debugging (masked & controlled)
    """

    raw_command: Optional[str] = Field(
        default=None,
        description="Natural language command. Example: 'Create daily PnL for Black Sea today'.",
    )

    intent_name: Optional[str] = Field(
        default=None,
        description="Explicit intent name (if known). Used to bypass NLP parsing.",
    )

    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Workflow parameters (either extracted by parser or manually supplied).",
    )

    context: TriggerContext = Field(
        default_factory=TriggerContext,
        description="Context container for parser + orchestrator (slot filling, org, desk, etc).",
    )

    simulate: bool = Field(
        default=False,
        description="If true, workflow runs in simulate/dry-run mode (no side-effects).",
    )

    debug: bool = Field(
        default=False,
        description="If true AND user is admin, includes reasoning_trace in response.",
    )


# ============================================================
# Trigger Response Schema
# ============================================================

class TriggerResponse(BaseModel):
    """
    Response returned by TriggerService after:
    - parser execution
    - slot filling (if needed)
    - orchestrator workflow run
    - audit logging (unless simulate=True)

    missing_parameters is relevant to Step 6 slot filling.
    """

    trigger_id: str
    workflow_name: str
    status: str
    simulate: bool

    missing_parameters: List[str] = Field(
        default_factory=list,
        description="If slot filling is required, parser identifies missing parameters here.",
    )
