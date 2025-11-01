from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, func, String
from typing import Optional

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
