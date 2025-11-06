# ⚙️ Fix for local "queue" folder conflict with Python's built-in module
import builtins, sys, importlib
if 'queue' in sys.modules:
    del sys.modules['queue']
import queue as _real_queue
sys.modules['queue'] = _real_queue

import sys, os
from fastapi import FastAPI

# 👇 Ensure project root ("backend") is on the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# ✅ Correct imports — all routes come from backend/app/routes
from backend.app.routes import auth_email, emails, users, ingest, telegram, whatsapp

# ✅ NEW: import Gmail listener
from backend.app.integrations.email.gmail_listener import start_gmail_listener
import asyncio

# 👇 Create FastAPI app
app = FastAPI(
    title="ORKO API",
    version="0.0.1",
    description="ORKO AI backend service — messaging, automation, and webhook endpoints.",
)

# 👇 Include routers
app.include_router(telegram.router, prefix="")
app.include_router(auth_email.router)
app.include_router(emails.router)
app.include_router(users.router)
app.include_router(ingest.router)
app.include_router(whatsapp.router)  # 👈 WhatsApp endpoint now active

# 👇 Health check endpoint
@app.get("/healthz")
def healthz():
    return {"status": "ok", "service": "orko-api"}

# 👇 Simple test endpoint
@app.get("/hello")
def say_hello():
    return {"message": "Hello, ORKO is alive and learning!"}

# 🧠 Gmail listener background task (runs automatically)
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(start_gmail_listener(interval_minutes=15))
    print("📬 Gmail auto-listener started.")
