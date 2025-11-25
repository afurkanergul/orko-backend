from __future__ import annotations

from sqlalchemy import Boolean, Column, DateTime, Integer, String, JSON, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base, TimestampMixin


class TriggerAudit(Base, TimestampMixin):
    """
    Audit record for every trigger execution in ORKO.
    Tracks lifecycle (queued -> running -> success/error),
    user identity, intent metadata, workflow parameters,
    and environment information (client IP, user agent).
    """

    __tablename__ = "trigger_audit"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # TimestampMixin gives created_at + updated_at
    # But your original model used created_at only.
    # We'll override created_at to ensure DB-side timestamp consistency.
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
    )

    # User context
    user_id: Mapped[str] = mapped_column(String, nullable=False)
    user_role: Mapped[str] = mapped_column(String, nullable=False)

    # Intent / Workflow metadata
    intent_name: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    workflow_name: Mapped[str | None] = mapped_column(String, nullable=True, index=True)

    # Inputs
    raw_command: Mapped[str | None] = mapped_column(Text, nullable=True)
    parameters: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Execution flags
    simulate: Mapped[bool] = mapped_column(Boolean, default=False)

    # Lifecycle status
    status: Mapped[str] = mapped_column(
        String,
        nullable=False,  # queued, running, success, error
    )

    # Error message from failed workflow
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Environment
    client_ip: Mapped[str | None] = mapped_column(String, nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String, nullable=True)
