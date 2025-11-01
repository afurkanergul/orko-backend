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
