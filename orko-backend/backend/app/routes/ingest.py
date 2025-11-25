# backend/app/routers/ingest.py
# 🌐 Handles message ingestion requests

from fastapi import APIRouter, Depends
from backend.app.schemas.ingestion import IngestMessage
from backend.app.orko_queue.redis_client import push_message
from backend.app.deps import verify_auth

# --- New imports for fallback DB save ---
import datetime
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from backend.app.db.session import SessionLocal
from backend.app.db import models

router = APIRouter()

# ==============================================================
# 🚀 Primary ingestion endpoint (unchanged)
# ==============================================================
@router.post("/ingest/message", dependencies=[Depends(verify_auth)])
async def ingest_message(payload: IngestMessage):
    """
    Receives a message payload, validates it, and enqueues for async processing.
    """
    push_message("messages", payload.to_dict())
    return {"status": "queued", "source": payload.source}


# ==============================================================
# 🧠 Local fallback saver (for Telegram / internal ingestion)
# ==============================================================
async def save_message_to_db(payload: dict):
    """
    🧠 Local fallback: save Telegram message into DB via SessionLocal.
    - Creates table if it does not exist (first run).
    - Uses models.messages if available; otherwise raw SQL (safe, parameterized).
    - Never crashes your webhook: logs and returns on failure.
    """
    db: Session | None = None
    try:
        db = SessionLocal()
        now_iso = datetime.datetime.utcnow().isoformat()

        # Prepare safe fields
        source = payload.get("source", "unknown")
        chat_id = payload.get("chat_id")
        sender = payload.get("sender", "")
        text_value = payload.get("text", "")
        timestamp = payload.get("timestamp", now_iso)

        # 1️⃣ Try ORM/Core table if present
        if hasattr(models, "messages"):
            db.execute(
                models.messages.insert().values(
                    source=source,
                    chat_id=chat_id,
                    sender=sender,
                    text=text_value,
                    timestamp=timestamp,
                    created_at=now_iso,
                )
            )
            db.commit()
            print(f"✅ Saved message (ORM) from {sender!r} to DB.")
            return

        # 2️⃣ Otherwise ensure table exists (raw SQL once)
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                source VARCHAR(50),
                chat_id BIGINT,
                sender VARCHAR(100),
                text TEXT,
                timestamp TEXT,
                created_at TEXT
            )
        """))

        # 3️⃣ Insert row with parameterized SQL
        db.execute(
            text("""
                INSERT INTO messages (source, chat_id, sender, text, timestamp, created_at)
                VALUES (:source, :chat_id, :sender, :text, :timestamp, :created_at)
            """),
            {
                "source": source,
                "chat_id": chat_id,
                "sender": sender,
                "text": text_value,
                "timestamp": timestamp,
                "created_at": now_iso,
            }
        )
        db.commit()
        print(f"✅ Saved message (SQL) from {sender!r} to DB.")

    except SQLAlchemyError as e:
        print("❌ Database insert failed:", repr(e))
    except Exception as e:
        print("❌ Unexpected error while saving message:", repr(e))
    finally:
        if db:
            db.close()
