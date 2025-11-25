from __future__ import annotations

from datetime import datetime
from sqlalchemy import Column, String, JSON, Boolean, DateTime

# Correct Base import for your project
from backend.app.db.base import Base


class ConfirmationRequest(Base):
    """
    Represents a destructive workflow action that requires explicit
    user approval before execution.

    Workflow lifecycle:
    - Created when ParserEngine detects a destructive intent
    - Stored as a pending approval object
    - Approved → orchestration will execute workflow normally
    - Rejected → workflow is permanently discarded
    """

    __tablename__ = "confirmation_requests"

    # UUID (string) assigned by ConfirmationService.create()
    id = Column(String, primary_key=True, index=True)

    # User who initiated the destructive action
    user_id = Column(String, index=True)

    # Workflow name awaiting approval (e.g., "delete_contract")
    workflow_name = Column(String, index=True)

    # Serialized parameters to be passed into orchestrator after approval
    parameters = Column(JSON)

    # Decision flags
    approved = Column(Boolean, default=False)
    rejected = Column(Boolean, default=False)

    # When created / approved / rejected
    created_at = Column(DateTime, default=datetime.utcnow)
    decided_at = Column(DateTime, nullable=True)
