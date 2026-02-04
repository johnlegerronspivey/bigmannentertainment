"""
AWS QLDB Dispute Ledger - Backend Tests

These tests validate the core QLDB service and API endpoints using the
local MongoDB-backed immutable ledger models (no real AWS QLDB needed).
"""

import os
import sys

import pytest
from fastapi.testclient import TestClient

# Ensure we can import the FastAPI app
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from server import app, db  # type: ignore  # noqa: E402
from qldb_service import initialize_qldb_service  # type: ignore  # noqa: E402


@pytest.fixture(scope="session")
def client():
    """Return a TestClient with QLDB service initialized.

    Session scope keeps the same app/event loop open across tests,
    preventing Motor from hitting a closed loop.
    """
    initialize_qldb_service(db)
    test_client = TestClient(app)
    yield test_client



def test_qldb_health_endpoint():
    resp = client.get("/api/qldb/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["service"] == "AWS QLDB Dispute Ledger"


def test_qldb_list_disputes():
    resp = client.get("/api/qldb/disputes")
    assert resp.status_code == 200
    data = resp.json()
    assert "disputes" in data
    assert data["total"] >= 0


def test_qldb_chain_verification():
    resp = client.get("/api/qldb/audit/chain/verify")
    assert resp.status_code == 200
    data = resp.json()
    assert "chain_valid" in data
