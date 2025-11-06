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
from fastapi.middleware.cors import CORSMiddleware   # ✅ Added

# 👇 Ensure project root ("backend") is on the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# ✅ Routers
from backend.app.routes import (
    auth_email,
    emails,
    users,
    ingest,
    telegram,
    whatsapp,
    health,
    dashboard,
    overview   # ✅ added
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
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
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
app.include_router(overview.router)   # ✅ added


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
    """
    Periodically checks Drive & SharePoint for new files
    and writes them into the database.
    """
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

                    # ✅ Log successful persistence
                    try:
                        log_ingest("watcher", f"Persisted {len(all_changes)} change(s)")
                    except Exception as _e:
                        print(f"⚠️ log_ingest persist note failed: {_e}")

                except Exception as e:
                    print(f"⚠️ DB insert error during File Watcher tick: {e}")

                    # ✅ Log DB insert failure
                    try:
                        log_ingest("watcher", f"DB insert error: {e}", level="error")
                    except Exception as _e:
                        print(f"⚠️ log_ingest error note failed: {_e}")

        except Exception as e:
            print(f"⚠️ File Watcher error: {e}")

        # check every 60 seconds
        await asyncio.sleep(60)


# =====================================================
# 🚦 Startup: run both listeners
# =====================================================

@app.on_event("startup")
async def startup_event():
    # Gmail listener
    asyncio.create_task(start_gmail_listener(interval_minutes=15))
    print("📬 Gmail auto-listener started.")

    # File watcher
    if not hasattr(app.state, "file_watcher_started"):
        app.state.file_watcher_started = True
        asyncio.create_task(start_file_watcher())
        print("✅ File Watcher scheduled.")
    else:
        print("↩️ File Watcher already scheduled; skipping.")
