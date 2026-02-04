"""
AWS QLDB Dispute Ledger - Backend Tests

These tests validate the core QLDB service and API endpoints using the
local MongoDB-backed immutable ledger models (no real AWS QLDB needed).
"""

import os
import sys

import pytest
from httpx import AsyncClient
from httpx import ASGITransport

# Ensure we can import the FastAPI app
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from server import app, db  # type: ignore  # noqa: E402
from qldb_service import initialize_qldb_service  # type: ignore  # noqa: E402


@pytest.fixture(scope="module", autouse=True)
def init_qldb_service():
    """Ensure QLDB service is initialized before tests.

    Mirrors the FastAPI startup behaviour but keeps tests explicit and
    independent of lifecycle hooks.
    """
    initialize_qldb_service(db)


@pytest.mark.asyncio
async def test_qldb_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/qldb/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["service"] == "AWS QLDB Dispute Ledger"


@pytest.mark.asyncio
async def test_qldb_list_disputes():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/qldb/disputes")
    assert resp.status_code == 200
    data = resp.json()
    assert "disputes" in data
    assert data["total"] >= 0


@pytest.mark.asyncio
async def test_qldb_chain_verification():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/qldb/audit/chain/verify")
    assert resp.status_code == 200
    data = resp.json()
    assert "chain_valid" in data
