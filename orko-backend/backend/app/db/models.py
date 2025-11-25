from sqlalchemy import (
    Integer, String, Text, ForeignKey, DateTime, UniqueConstraint, Column, Float, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List
from datetime import datetime, timezone

# Import our base, mixins, and portable JSON type
from .base import Base, TimestampMixin, StatusMixin
from .types import JSONType  # portable JSON replacement


# ============================================================
# ORGS
# ============================================================
class Org(TimestampMixin, StatusMixin, Base):
    __tablename__ = "orgs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    domain: Mapped[Optional[str]] = mapped_column(String(200))
    plan: Mapped[str] = mapped_column(String(50), default="free", nullable=False)

    users: Mapped[List["User"]] = relationship(
        back_populates="org",
        cascade="all, delete-orphan"
    )


# ============================================================
# USERS
# ============================================================
class User(TimestampMixin, StatusMixin, Base):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("email", name="uq_users_email"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("orgs.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String(200))
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    hashed_password: Mapped[Optional[str]] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(50), default="member", nullable=False)

    org: Mapped["Org"] = relationship(back_populates="users")
    tokens: Mapped[List["AuthToken"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    automations: Mapped[List["Automation"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    feedbacks: Mapped[List["Feedback"]] = relationship(back_populates="user", cascade="all, delete-orphan")


# ============================================================
# AUTH TOKENS
# ============================================================
class AuthToken(TimestampMixin, StatusMixin, Base):
    __tablename__ = "auth_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship(back_populates="tokens")


# ============================================================
# AUTOMATIONS
# ============================================================
class Automation(TimestampMixin, StatusMixin, Base):
    __tablename__ = "automations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    trigger: Mapped[Optional[str]] = mapped_column(String(200))
    action: Mapped[Optional[str]] = mapped_column(String(200))
    config: Mapped[Optional[dict]] = mapped_column(JSONType)  # JSON
    last_run_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship(back_populates="automations")


# ============================================================
# LOGS
# ============================================================
class Log(Base):
    __tablename__ = "logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    org_id: Mapped[Optional[int]] = mapped_column(ForeignKey("orgs.id", ondelete="SET NULL"))
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    level: Mapped[str] = mapped_column(String(30), default="info", nullable=False)
    event: Mapped[str] = mapped_column(String(200), nullable=False)
    details: Mapped[Optional[dict]] = mapped_column(JSONType)  # JSON
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), server_default=None)


# ============================================================
# FEEDBACK
# ============================================================
class Feedback(TimestampMixin, Base):
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    rating: Mapped[Optional[int]] = mapped_column(Integer)
    comment: Mapped[Optional[str]] = mapped_column(Text)
    context: Mapped[Optional[dict]] = mapped_column(JSONType)

    user: Mapped["User"] = relationship(back_populates="feedbacks")


# ============================================================
# FILE RECORDS
# ============================================================
class FileRecord(Base):
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    remote_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    owner: Mapped[Optional[str]] = mapped_column(String(255))
    modified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


# ============================================================
# INGESTION AUDIT (Step 3 Day 11)
# ============================================================
class IngestionAudit(Base):
    __tablename__ = "ingestion_audit"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(50), nullable=False)
    msg_id = Column(String(128), nullable=True)
    org_id = Column(Integer, nullable=True)
    received_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    processed_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), default="received")
    error = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<IngestionAudit(id={self.id}, source={self.source}, status={self.status})>"


# ============================================================
# WORKFLOW METRICS
# ============================================================
class WorkflowMetrics(Base):
    __tablename__ = "workflow_metrics"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    scenario = Column(String(100), nullable=False)

    total_runs = Column(Integer, nullable=False)
    success_count = Column(Integer, nullable=False)
    failure_count = Column(Integer, nullable=False)

    p50_latency_ms = Column(Float, nullable=False)
    p95_latency_ms = Column(Float, nullable=True)

    notes = Column(Text, nullable=True)


# ============================================================
# WORKFLOW DLQ (NEW)
# ============================================================
class WorkflowDLQ(Base):
    __tablename__ = "workflow_dlq"

    id = Column(Integer, primary_key=True, autoincrement=True)
    scenario = Column(String(100), nullable=False)
    error_message = Column(Text, nullable=False)

    context = Column(JSONType, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    replayed = Column(Integer, default=False)
    replayed_at = Column(DateTime(timezone=True), nullable=True)
