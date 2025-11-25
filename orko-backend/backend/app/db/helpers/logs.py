# backend/app/db/helpers/logs.py
import os, sys
from datetime import datetime, timezone
from sqlalchemy import text
from dotenv import load_dotenv

# ==========================================================
# 1️⃣ Ensure environment is loaded for Render / local use
# ==========================================================
dotenv_path = os.path.join(os.path.dirname(__file__), "../../../.env.local")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    print("⚠️ .env.local not found — assuming environment variables set in environment (Render).")

# ==========================================================
# 2️⃣ Ensure backend is on import path
# ==========================================================
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

# ==========================================================
# 3️⃣ Import shared session manager (dynamic DATABASE_URL)
# ==========================================================
from backend.app.db.session import SessionLocal

# ==========================================================
# 4️⃣ Logging function
# ==========================================================
def log_ingest(source: str, message: str, level: str = "info") -> None:
    """
    Writes a short, safe log line into ingestion_logs table.
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
