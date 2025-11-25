# backend/app/core/config.py
# ✅ Safe, backward-compatible, and auto-loading configuration for ORKO backend

from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path
import os

# -------------------------------------------------------------------
# 🌍 Settings class definition
# -------------------------------------------------------------------
class Settings(BaseSettings):
    # 💾 Database & Infrastructure
    database_url: Optional[str] = None
    vector_db_url: Optional[str] = None
    redis_url: Optional[str] = None

    # 🔑 Keys & Secrets
    openai_api_key: Optional[str] = None
    openai_project_id: Optional[str] = None
    pinecone_api_key: Optional[str] = None
    jwt_secret: Optional[str] = None
    api_token: Optional[str] = "supersecret123"

    # 💬 Telegram & Webhook Integration
    telegram_bot_token: Optional[str] = None
    telegram_webhook_secret: Optional[str] = None
    public_base_url: Optional[str] = None

    # 🧠 ORKO AI Models
    embed_model: Optional[str] = None
    chat_model: Optional[str] = None
    reasoning_model: Optional[str] = None

    # ⚙️ Logging & Environment
    log_level: Optional[str] = "debug"
    env: Optional[str] = "development"
    debug: Optional[bool] = True

    # 📂 Google Drive Integration
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None

    # 🗂 Microsoft SharePoint Integration
    ms_client_id: Optional[str] = None
    ms_tenant_id: Optional[str] = None
    ms_client_secret: Optional[str] = None
    ms_redirect_uri: Optional[str] = None

    # ⚙️ Celery / Redis for async trigger queue (Day 8)
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    TRIGGER_QUEUE_NAME: str = "orko_trigger_queue"
    TRIGGER_DLQ_NAME: str = "orko_trigger_dlq"

    # -------------------------------------------------------
    # ⚡ Step 6 Day 9 — Rate Limiting Configuration
    # -------------------------------------------------------
    RATE_LIMIT_REDIS_URL: str = "redis://localhost:6379/2"
    RATE_LIMIT_PER_MINUTE: int = 5
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    class Config:
        env_file = ".env.local"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Safe: ignores unknown env vars


# -------------------------------------------------------------------
# 🧩 Force-load .env.local manually
# -------------------------------------------------------------------
# Ensures environment variables load even when running from different directories
env_path = Path(__file__).resolve().parents[2] / ".env.local"

if env_path.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=env_path, override=True)
        print(f"✅ Loaded environment variables from: {env_path}")
    except Exception as e:
        print(f"⚠️ Failed to manually load .env.local: {e}")
else:
    print(f"⚠️ .env.local file not found at expected path: {env_path}")

# -------------------------------------------------------------------
# 🌍 Create global settings instance
# -------------------------------------------------------------------
settings = Settings()

# -------------------------------------------------------------------
# 🧠 Quick runtime validation
# -------------------------------------------------------------------
try:
    print("🔧 Database URL:", settings.database_url)
    print("🔧 Redis URL:", settings.redis_url)
except Exception as e:
    print("⚠️ Error checking config values:", e)
