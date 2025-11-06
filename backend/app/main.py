# backend/app/main.py
# =====================================================
# ORKO Backend — FastAPI entry point
# =====================================================

# ⚙️ Fix for local "queue" folder conflict with Python's built-in module
import builtins, sys, importlib
if 'queue' in sys.modules:
    del sys.modules['queue']
import queue as _real_queue
sys.modules['queue'] = _real_queue

import sys, os
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# 👇 Ensure project root ("backend") is on the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# =====================================================
# 🌍 Environment Handling (Render + Local)
# =====================================================

env_path = os.path.join(os.path.dirname(__file__), "..", ".env.local")
if os.path.exists(env_path):
    print(f"🌍 Loading local .env from {env_path}")
    load_dotenv(env_path)
else:
    print("⚙️ Running in Render environment (no .env.local file)")

# =====================================================
# ✅ Routers
# =====================================================
from backend.app.routes import (
    auth_email,
    emails,
    users,
    ingest,
    telegram,
    whatsapp,
    health,
    dashboard,
    overview
)

# ✅ Background integrations
from backend.app.integrations.email.gmail_listener import start_gmail_listener
from backend.app.integrations.files.drive_client import fetch_drive_changes
from backend.app.integrations.files.sharepoint_client import fetch_sharepoint_delta

# ✅ Database helper for file ingestion
from backend.app.db.helpers.file_ingest import ingest_files_bulk
from backend.app.db.helpers.logs import log_ingest


# =====================================================
# 🚀 FastAPI app initialization
# =====================================================

app = FastAPI(
    title="ORKO API",
    version="0.0.1",
    description="ORKO AI backend service — messaging, automation, and webhook endpoints.",
)

# ✅ Enable CORS for frontend → backend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://orko-frontend.onrender.com"  # ✅ allow deployed frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 👇 Include routers
app.include_router(telegram.router, prefix="")
app.include_router(auth_email.router)
app.include_router(emails.router)
app.include_router(users.router)
app.include_router(ingest.router)
app.include_router(whatsapp.router)
app.include_router(health.router)
app.include_router(dashboard.router)
app.include_router(overview.router)


# =====================================================
# ✅ Health & Test Endpoints
# =====================================================

@app.get("/healthz")
def healthz():
    return {"status": "ok", "service": "orko-api"}

@app.get("/hello")
def say_hello():
    return {"message": "Hello, ORKO is alive and learning!"}


# =====================================================
# 🧠 Background Tasks — Gmail & File Watcher
# =====================================================

async def start_file_watcher():
    """Periodically checks Drive & SharePoint for new files and writes them into the database."""
    print("📁 ORKO File Watcher started.")
    while True:
        try:
            drive_changes = fetch_drive_changes() or []
            sp_changes = fetch_sharepoint_delta() or []

            total = len(drive_changes) + len(sp_changes)
            if drive_changes:
                print(f"  • Drive changes: {len(drive_changes)}")
            if sp_changes:
                print(f"  • SharePoint changes: {len(sp_changes)}")
            print(f"🧩 File Watcher tick → {total} total change(s).")

            # 🧩 Logs (Drive & SharePoint changes)
            try:
                if drive_changes:
                    log_ingest("drive", f"Detected {len(drive_changes)} change(s)")
                if sp_changes:
                    log_ingest("sharepoint", f"Detected {len(sp_changes)} change(s)")
                if total == 0:
                    log_ingest("watcher", "No changes")
            except Exception as _e:
                print(f"⚠️ log_ingest watcher error: {_e}")

            # 🧠 Save new files into DB + enqueue for embedding
            if drive_changes or sp_changes:
                all_changes = (drive_changes or []) + (sp_changes or [])
                try:
                    ingest_files_bulk(all_changes)
                    try:
                        log_ingest("watcher", f"Persisted {len(all_changes)} change(s)")
                    except Exception as _e:
                        print(f"⚠️ log_ingest persist note failed: {_e}")
                except Exception as e:
                    print(f"⚠️ DB insert error during File Watcher tick: {e}")
                    try:
                        log_ingest("watcher", f"DB insert error: {e}", level="error")
                    except Exception as _e:
                        print(f"⚠️ log_ingest error note failed: {_e}")

        except Exception as e:
            print(f"⚠️ File Watcher error: {e}")

        await asyncio.sleep(60)


# =====================================================
# 🚦 Startup: run both listeners with resilience
# =====================================================

@app.on_event("startup")
async def startup_event():
    async def safe_run(task_fn, name: str, *args, **kwargs):
        """Safely runs background tasks; auto-restarts on failure."""
        while True:
            try:
                await task_fn(*args, **kwargs)
            except Exception as e:
                print(f"⚠️ {name} crashed with error: {e} — restarting in 30s...")
                await asyncio.sleep(30)

    # Gmail Listener
    asyncio.create_task(safe_run(start_gmail_listener, "Gmail Listener", interval_minutes=15))
    print("📬 Gmail Listener scheduled safely.")

    # File Watcher
    asyncio.create_task(safe_run(start_file_watcher, "File Watcher"))
    print("📁 File Watcher scheduled safely.")

# =====================================================
# 🌐 Root route (Render health check)
# =====================================================
@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "orko-api",
        "note": "ORKO backend is running smoothly on Render."
    }


# =====================================================
# 🏁 Render Entry Point
# =====================================================
if __name__ == "__main__":
    import uvicorn
    # Render dynamically assigns a port via the PORT environment variable
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=port)
