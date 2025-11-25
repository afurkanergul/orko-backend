from __future__ import annotations

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class Intent(BaseModel):
    """
    Core structured intent model for ORKO.

    This is the single source of truth for everything the CommandParser produces.
    """

    command: str = Field(..., description="Original user command text")
    action: str = Field(..., description="Normalized ORKO action verb")
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Key-value slots extracted for execution"
    )
    context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Any contextual metadata (domain, workflow context, etc.)"
    )

    # Safety flags
    risk_level: str = Field(
        default="medium",
        description="Risk classification: low / medium / high"
    )
    requires_confirmation: bool = Field(
        default=False,
        description="True if user must confirm before execution"
    )

    # Optional debugging field
    raw_text: Optional[str] = Field(
        default=None,
        description="Original user text if provided by LLM response"
    )
