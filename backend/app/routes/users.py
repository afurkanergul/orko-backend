# backend/app/routes/users.py
from fastapi import APIRouter, HTTPException, Depends, status, Query, Path
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.db.models import User   # 👈 fixed import path

router = APIRouter()

# -------------------------------
# Create User (POST /users)
# -------------------------------
@router.post("/users", status_code=status.HTTP_201_CREATED)
def create_user(payload: dict, db: Session = Depends(get_db)):
    email = payload.get("email")
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email required")

    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")

    new_user = User(
        email=email,
        name=payload.get("full_name"),
        org_id=payload.get("org_id", 1),
        role="member"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# -------------------------------
# List Users (GET /users)
# -------------------------------
@router.get("/users")
def list_users(org_id: int = Query(..., description="Filter by organization ID"), db: Session = Depends(get_db)):
    return db.query(User).filter(User.org_id == org_id).all()


# -------------------------------
# Get User by ID (GET /users/{id})
# -------------------------------
@router.get("/users/{user_id}")
def get_user(user_id: int = Path(...), org_id: int = Query(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id, User.org_id == org_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# -------------------------------
# Update User (PUT /users/{id})
# -------------------------------
@router.put("/users/{user_id}")
def update_user(
    user_id: int = Path(...),
    org_id: int = Query(...),
    payload: dict = None,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id, User.org_id == org_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if payload:
        if "full_name" in payload:
            user.name = payload["full_name"]
        if "email" in payload:
            user.email = payload["email"]
        db.commit()
        db.refresh(user)
    return user


# -------------------------------
# Delete User (DELETE /users/{id})
# -------------------------------
@router.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int = Path(...), org_id: int = Query(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id, User.org_id == org_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return None
