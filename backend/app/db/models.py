from sqlalchemy import (
    Integer, String, Text, ForeignKey, DateTime, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from typing import Optional, List
from datetime import datetime

# Import our base and mixins
from .base import Base, TimestampMixin, StatusMixin


# === STEP 2 / DAY 7 — RBAC PREP (Sub-Step 1) ===
# Plan: add org_id to multi-tenant tables (users, trades, files)
# Create roles, permissions, user_roles tables
# Create ENUM user_role ('admin', 'operator', 'viewer')
# Filtering rule: always limit by org_id for user’s organization
# (Actual ALTER/CREATE statements will be executed in pgAdmin in Sub-Steps 2–5)


# ---------- ORGS ----------
# [RBAC Day 7] This table already represents each organization (root of org_id)
class Org(TimestampMixin, StatusMixin, Base):
    __tablename__ = "orgs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    domain: Mapped[Optional[str]] = mapped_column(String(200))
    plan: Mapped[str] = mapped_column(String(50), default="free", nullable=False)

    users: Mapped[List["User"]] = relationship(back_populates="org", cascade="all, delete-orphan")


# ---------- USERS ----------
# [RBAC Day 7] Will add org_id (INTEGER) + role (ENUM) to this model
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


# ---------- AUTH TOKENS ----------
# [RBAC Day 7] Belongs to a user; no org_id needed (inherits via user)
class AuthToken(TimestampMixin, StatusMixin, Base):
    __tablename__ = "auth_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship(back_populates="tokens")


# ---------- AUTOMATIONS ----------
# [RBAC Day 7] Will add org_id (INTEGER) to this model (each automation belongs to an org)
class Automation(TimestampMixin, StatusMixin, Base):
    __tablename__ = "automations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    trigger: Mapped[Optional[str]] = mapped_column(String(200))   # e.g. "email.received"
    action: Mapped[Optional[str]] = mapped_column(String(200))    # e.g. "send_slack"
    config: Mapped[Optional[dict]] = mapped_column(JSONB)         # flexible settings
    last_run_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship(back_populates="automations")


# ---------- LOGS ----------
# [RBAC Day 7] org_id already exists here — no change needed
class Log(Base):
    __tablename__ = "logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    org_id: Mapped[Optional[int]] = mapped_column(ForeignKey("orgs.id", ondelete="SET NULL"))
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    level: Mapped[str] = mapped_column(String(30), default="info", nullable=False)  # info/warn/error
    event: Mapped[str] = mapped_column(String(200), nullable=False)
    details: Mapped[Optional[dict]] = mapped_column(JSONB)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), server_default=None)


# ---------- FEEDBACK ----------
# [RBAC Day 7] Will add org_id (INTEGER) to this model later (feedback belongs to an org)
class Feedback(TimestampMixin, Base):
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    rating: Mapped[Optional[int]] = mapped_column(Integer)        # 1..5 stars
    comment: Mapped[Optional[str]] = mapped_column(Text)
    context: Mapped[Optional[dict]] = mapped_column(JSONB)        # where feedback happened

    user: Mapped["User"] = relationship(back_populates="feedbacks")
