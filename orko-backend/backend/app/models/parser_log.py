# backend/app/models/parser_log.py

from __future__ import annotations

from datetime import datetime
from sqlalchemy import Column, String, JSON, DateTime

# Correct Base import for your folder structure
from backend.app.db.base import Base


class ParserLog(Base):
    """
    Stores masked reasoning traces + parsed command summaries.

    Required for:
    - Day 7 Reasoning Trace Logging
    - Auditing model parsing evolution over time
    """

    __tablename__ = "parser_logs"

    # Primary key (uuid4 passed from ParserEngine)
    id = Column(String, primary_key=True, index=True)

    # Who triggered the command
    user_id = Column(String, index=True)

    # Raw natural-language command
    command = Column(String)

    # Full parsed dictionary: domain, action, parameters, context
    parsed_output = Column(JSON)

    # Masked reasoning trace (safe to store)
    masked_reasoning = Column(JSON)

    # Index for analytics and debugging
    domain = Column(String, index=True)
    action = Column(String, index=True)

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)
