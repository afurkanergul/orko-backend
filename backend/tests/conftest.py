# tests/conftest.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient
from faker import Faker

# 👇 correct import for your project
from app.main import app

fake = Faker()

@pytest.fixture(scope="session")
def client():
    """
    Gives our tests a 'remote control' to talk to the FastAPI app
    without running a real server.
    """
    return TestClient(app)

@pytest.fixture
def fake_user_payload():
    """
    Makes one pretend user we can send to the API.
    """
    return {
        "email": fake.unique.email(),
        "full_name": fake.name(),
        "org_id": 1
    }

@pytest.fixture
def fake_org_payload():
    """
    Makes one pretend organization body we can send to the API.
    """
    return {
        "name": fake.company(),
        "status": "active"
    }

