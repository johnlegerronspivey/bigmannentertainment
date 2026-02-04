"""
AWS GuardDuty Threat Detection - Backend Tests

These tests validate the core GuardDuty service and API endpoints.
They rely on the local MongoDB-backed sample data initialized by
GuardDutyService and should NOT require real AWS access to pass.
"""

import os
import sys

import pytest
from httpx import AsyncClient
from httpx import ASGITransport

# Ensure we can import the FastAPI app
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from server import app, db  # type: ignore  # noqa: E402
from guardduty_service import initialize_guardduty_service  # type: ignore  # noqa: E402


@pytest.fixture(scope="module", autouse=True)
def init_guardduty_service():
    """Ensure GuardDuty service is initialized before tests.

    This mirrors what the FastAPI startup event does in production,
    but we call it explicitly here so tests don't depend on startup hooks.
    """
    initialize_guardduty_service(db)


@pytest.mark.asyncio
async def test_guardduty_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/guardduty/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["service"] == "AWS GuardDuty Threat Detection"


@pytest.mark.asyncio
async def test_guardduty_list_findings():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/guardduty/findings")
    assert resp.status_code == 200
    data = resp.json()
    assert "findings" in data
    # Sample data / local DB should always return a non-negative total
    assert data["total"] >= 0


@pytest.mark.asyncio
async def test_guardduty_dashboard_stats():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/guardduty/dashboard")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_detectors" in data
    assert "total_findings" in data
