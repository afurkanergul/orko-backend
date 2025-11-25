# backend/tests/test_users_crud.py
import os
os.environ["TESTING"] = "1"  # must be first!

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool  # 👈 shared in-memory DB

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.db import models  # ensure models are registered with Base

# 1) One shared in-memory SQLite for all connections/threads
engine = create_engine(
    "sqlite://",                     # 👈 NOT sqlite:///:memory:
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,            # 👈 share the same connection
    echo=False,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 2) Create tables before the TestClient starts
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

# 3) Override FastAPI dependency to use the test session
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# 4) Create the client after DB is ready
client = TestClient(app)

# 5) The test
def test_users_crud_cycle_and_org_isolation():
    # Create user in Org 1
    p1 = {"email": "alice@example.com", "full_name": "Alice A", "org_id": 1}
    r1 = client.post("/users", json=p1)
    assert r1.status_code in (200, 201), r1.text
    u1 = r1.json()
    assert u1["org_id"] == 1

    # Create user in Org 2
    p2 = {"email": "bob@example.com", "full_name": "Bob B", "org_id": 2}
    r2 = client.post("/users", json=p2)
    assert r2.status_code in (200, 201), r2.text
    u2 = r2.json()
    assert u2["org_id"] == 2

    # Org 1 listing should not include Org 2 users
    r_list = client.get("/users", params={"org_id": 1})
    assert r_list.status_code == 200
    emails = [u["email"] for u in r_list.json()]
    assert "alice@example.com" in emails
    assert "bob@example.com" not in emails

    # Cross-org access forbidden
    r_wrong = client.get(f"/users/{u1['id']}", params={"org_id": 2})
    assert r_wrong.status_code == 404


    # Update + verify
    r_upd = client.put(f"/users/{u1['id']}", params={"org_id": 1}, json={"full_name": "Alice Alpha"})
    print("\n🔍 UPDATE RESPONSE:", r_upd.json())  # <— added line
    assert r_upd.status_code == 200
    assert r_upd.json()["name"] == "Alice Alpha"

    # Delete + verify gone
    r_del = client.delete(f"/users/{u1['id']}", params={"org_id": 1})
    assert r_del.status_code == 204
    r_check = client.get(f"/users/{u1['id']}", params={"org_id": 1})
    assert r_check.status_code == 404
