import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient
from faker import Faker

# Import FastAPI app
from backend.app.main import app

# --- NEW IMPORTS FOR DB SETUP ---
from backend.app.db.session import engine, SessionLocal
from backend.app.db.models import Base, Org


# ============================================================
# 🏗️  CREATE ALL TABLES ONCE BEFORE THE TEST SESSION STARTS
# ============================================================

# Drop + recreate all tables to ensure a clean test DB
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

# Seed required orgs for multi-tenant tests
db = SessionLocal()
db.add_all([
    Org(id=1, name="Org 1"),
    Org(id=2, name="Org 2"),
])
db.commit()
db.close()


# ============================================================
# CLIENT FIXTURE
# ============================================================

fake = Faker()

@pytest.fixture(scope="session")
def client():
    """
    Provides a TestClient that interacts with the FastAPI app
    without running a real server.
    """
    return TestClient(app)


# ============================================================
# PAYLOAD FIXTURES
# ============================================================

@pytest.fixture
def fake_user_payload():
    """
    Generates a fake user payload for testing.
    """
    return {
        "email": fake.unique.email(),
        "full_name": fake.name(),
        "org_id": 1
    }

@pytest.fixture
def fake_org_payload():
    """
    Generates a fake organization payload for testing.
    """
    return {
        "name": fake.company(),
        "status": "active"
    }
