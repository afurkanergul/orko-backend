# backend/app/deps.py
# 🛡️ Token-based authentication dependency for FastAPI routes

from fastapi import Header, HTTPException, status
from backend.app.core.config import settings  # ✅ fixed import path


def verify_auth(authorization: str = Header(...)):
    """
    Checks the Authorization header for a valid Bearer token.
    Example header:
        Authorization: Bearer supersecret123
    """
    expected = f"Bearer {settings.api_token}"

    if authorization != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API token"
        )
