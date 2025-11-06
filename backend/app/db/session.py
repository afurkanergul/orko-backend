from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# ------------------------------------------------------------
# Load environment variables
# ------------------------------------------------------------
dotenv_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env.local")
print(f"🌍 Loading .env from: {os.path.abspath(dotenv_path)}")
load_dotenv(dotenv_path)

# ------------------------------------------------------------
# Database URL
# ------------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL not found in .env.local")

# ------------------------------------------------------------
# SQLAlchemy engine and session
# ------------------------------------------------------------
engine = create_engine(DATABASE_URL)
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
        _engine_singleton = create_engine(DATABASE_URL)
    return _engine_singleton
