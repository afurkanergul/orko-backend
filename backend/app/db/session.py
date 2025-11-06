# backend/app/db/session.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# ------------------------------------------------------------
# Load environment variables
# ------------------------------------------------------------
dotenv_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env.local")
if os.path.exists(dotenv_path):
    print(f"🌍 Loading .env from: {os.path.abspath(dotenv_path)}")
    load_dotenv(dotenv_path)
else:
    print("⚠️ .env.local not found — assuming environment vars are preloaded (Render)")

# ------------------------------------------------------------
# Database URL
# ------------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL not found in environment variables")

# ✅ Ensure Render uses psycopg2-compatible URL
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)

# ------------------------------------------------------------
# SQLAlchemy engine and session
# ------------------------------------------------------------
engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ------------------------------------------------------------
# Helper for dependency injection
# ------------------------------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ------------------------------------------------------------
# ✅ Helper for background/utility scripts (e.g., file_ingest)
# ------------------------------------------------------------
_engine_singleton = None

def get_engine():
    """
    Returns a reusable SQLAlchemy engine instance.
    Used by Alembic helpers and background workers.
    """
    global _engine_singleton
    if _engine_singleton is None:
        _engine_singleton = engine
    return _engine_singleton
