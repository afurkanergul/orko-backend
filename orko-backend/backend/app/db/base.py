import os
from typing import Optional

from sqlalchemy import DateTime, func, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# -------------------------------------------------------------------------
# JSONB fallback for SQLite tests
# -------------------------------------------------------------------------
try:
    from sqlalchemy.dialects.postgresql import JSONB
except ImportError:
    JSONB = Text  # fallback if dialect missing

# When running tests with SQLite, force JSONB -> TEXT
if os.environ.get("TESTING", "0") == "1":
    JSONB = Text


# -------------------------------------------------------------------------
# Base Model - single source of truth
# -------------------------------------------------------------------------
class Base(DeclarativeBase):
    """Base class for all ORM models in ORKO."""
    pass


# -------------------------------------------------------------------------
# Mixins
# -------------------------------------------------------------------------
class TimestampMixin:
    """
    Common created_at / updated_at timestamps.
    Uses server-side defaults so they work across all domains and services.
    """
    created_at: Mapped[Optional[DateTime]] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[Optional[DateTime]] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class StatusMixin:
    """
    Simple status field for soft lifecycle tracking.
    Typical values: "active", "inactive", "queued", "running", etc.
    """
    status: Mapped[str] = mapped_column(
        String(32),
        default="active",
        nullable=False,
    )


# -------------------------------------------------------------------------
# Optional: import all models so Alembic can detect them
#
# IMPORTANT:
# - We ONLY catch ImportError to avoid hiding real bugs.
# - We do NOT import individual models (avoids circular imports).
# - This is safe even if backend.app.models is not a full package.
# -------------------------------------------------------------------------
try:
    from backend.app.models import *  # noqa: F401,F403
except ImportError:
    # In some environments (tests, partial loads), models may not be importable.
    # Alembic env.py can explicitly import model modules instead.
    pass
