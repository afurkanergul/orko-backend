# backend/app/api/deps/db.py

from __future__ import annotations
from typing import Generator

from sqlalchemy.orm import Session

from backend.app.db.session import SessionLocal  # ✓ correct path for your project


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a SQLAlchemy Session.
    Closes the session after the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
