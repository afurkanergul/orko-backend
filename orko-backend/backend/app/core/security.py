# backend/app/core/security.py

from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError

SECRET_KEY = "REPLACE_WITH_REAL_SECRET"
ALGORITHM = "HS256"

class User:
    def __init__(self, id: str, role: str):
        self.id = id
        self.role = role

def verify_jwt(token: str) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return User(id=payload["sub"], role=payload["role"])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token."
        )

def get_current_user(token: str = Depends(verify_jwt)):
    return token

def require_role(required: str):
    def wrapper(user: User = Depends(get_current_user)):
        hierarchy = ["viewer", "operator", "admin"]
        if hierarchy.index(user.role) < hierarchy.index(required):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required}' is required."
            )
        return user
    return wrapper
