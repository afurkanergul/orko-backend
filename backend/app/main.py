import sys, os
# 👇 Add this line to fix imports when pytest runs from inside "backend"
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from fastapi import FastAPI
from app.routes import auth_email, emails  # 👈 changed this line

# Create FastAPI app
app = FastAPI(title="ORKO API", version="0.0.1")

# Health check endpoint
@app.get("/healthz")
def healthz():
    return {"status": "ok", "service": "orko-api"}

# Simple test endpoint
@app.get("/hello")
def say_hello():
    return {"message": "Hello, ORKO is alive and learning!"}

# ✅ Include your new routers
app.include_router(auth_email.router)
app.include_router(emails.router)
