# backend/app/db/base.py

import os
from sqlalchemy import DateTime, func, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from typing import Optional

# 👇 Patch for SQLite compatibility during testing
# This replaces PostgreSQL JSONB with plain Text when TESTING=1
try:
    from sqlalchemy.dialects.postgresql import JSONB
except ImportError:
    JSONB = Text  # fallback, should never happen unless dialect missing

if os.environ.get("TESTING", "0") == "1":
    JSONB = Text  # type: ignore


class Base(DeclarativeBase):
    """Base for all ORM models."""
    pass


class TimestampMixin:
    created_at: Mapped[Optional["DateTime"]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[Optional["DateTime"]] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class StatusMixin:
    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False)


# 👇 Ensure all models are imported so Base.metadata sees them
from backend.app.db import models  # ✅ fixed path here
