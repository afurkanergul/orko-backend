# backend/app/db/helpers/logs.py
from datetime import datetime, timezone
from sqlalchemy import text
import sys, os

# ✅ Ensure the project root ("backend") is on sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

# ✅ Fixed import — works in both local test and app runtime
from backend.app.db.session import SessionLocal


def log_ingest(source: str, message: str, level: str = "info") -> None:
    """
    Write a short, safe log line into ingestion_logs.
    Keeps messages short; do not pass huge payloads.
    """
    db = SessionLocal()
    try:
        db.execute(
            text("""
                INSERT INTO ingestion_logs (source, level, message, created_at)
                VALUES (:source, :level, :message, :created_at)
            """),
            {
                "source": (source or "")[:50],
                "level": (level or "info")[:20],
                "message": (message or "")[:500],
                "created_at": datetime.now(timezone.utc),
            },
        )
        db.commit()
    except Exception as e:
        print(f"⚠️ log_ingest failed for {source}: {e}")
    finally:
        db.close()
