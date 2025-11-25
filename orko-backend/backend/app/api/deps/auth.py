# backend/app/api/deps/auth.py

from __future__ import annotations

import os
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from jose import JWTError, jwt

from backend.app.schemas.auth import CurrentUser


# -----------------------------------------------------------------------------
# JWT CONFIGURATION
# -----------------------------------------------------------------------------
JWT_SECRET = os.getenv("ORKO_JWT_SECRET", "dev-secret")  # ⚠️ replace in production
JWT_ALG = os.getenv("ORKO_JWT_ALG", "HS256")

# Allowed roles in the system
ALLOWED_ROLES = {"viewer", "operator", "admin"}

# Roles allowed to trigger workflows
TRIGGER_ROLES = {"operator", "admin"}


# -----------------------------------------------------------------------------
# Decode JWT from Authorization: Bearer <token>
# -----------------------------------------------------------------------------
def get_current_user(
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
) -> CurrentUser:
    """
    Extracts and verifies JWT from the Authorization header.
    Returns a CurrentUser object (id, email, role).
    """

    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
        )

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header",
        )

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    sub = payload.get("sub")
    role = payload.get("role", "viewer")
    email = payload.get("email")

    # Validate claims
    if not sub or role not in ALLOWED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token claims",
        )

    return CurrentUser(
        id=str(sub),
        email=email,
        role=role,
    )


# -----------------------------------------------------------------------------
# RBAC: Only operator/admin can trigger workflows
# -----------------------------------------------------------------------------
def require_trigger_role(
    user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    """
    Ensures user has permission to trigger workflows.
    Allowed roles: operator, admin
    """

    if user.role not in TRIGGER_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to trigger workflows",
        )

    return user
