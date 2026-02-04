"""
AWS GuardDuty Threat Detection - Backend Tests

These tests validate the core GuardDuty API endpoints using a
FAKE service implementation wired via FastAPI dependency overrides.

This avoids Motor + event loop issues in pytest while still verifying
that the HTTP contract, routing, and response shapes are correct.
"""

import os
import sys

import pytest
from httpx import AsyncClient, ASGITransport

# Ensure we can import the FastAPI app and endpoint dependencies
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from server import app  # type: ignore  # noqa: E402
from guardduty_endpoints import get_service as get_guardduty_dep  # type: ignore  # noqa: E402
from guardduty_models import (  # type: ignore  # noqa: E402
    GuardDutyHealthResponse,
    GuardDutyDashboardStats,
    SeveritySummary,
    StatusSummary,
)


class FakeGuardDutyService:
    """Minimal fake GuardDuty service for testing.

    Returns static, deterministic data without touching MongoDB or AWS.
    """

    async def check_health(self) -> GuardDutyHealthResponse:
        return GuardDutyHealthResponse(
            status="healthy",
            service="AWS GuardDuty Threat Detection",
            version="1.0.0",
            guardduty_enabled=True,
            aws_connected=True,
            aws_region="us-east-1",
            features=["realtime_threat_detection", "dashboard", "findings_api"],
        )

    async def get_findings(self, *_, **__):
        """Return empty findings list but valid paging metadata.

        Endpoint wraps this into a FindingsResponse, so we just
        need a (list, total) tuple here.
        """

        return [], 0

    async def get_dashboard_stats(self) -> GuardDutyDashboardStats:
        return GuardDutyDashboardStats(
            total_detectors=1,
            active_detectors=1,
            total_findings=0,
            new_findings=0,
            severity_summary=SeveritySummary(),
            status_summary=StatusSummary(),
            threats_by_category=[],
            top_threat_types=[],
            resources_by_type=[],
            most_targeted_resources=[],
            findings_last_24h=0,
            findings_last_7d=0,
            findings_last_30d=0,
            trend_data=[],
        )


@pytest.fixture(scope="module", autouse=True)
def override_guardduty_service():
    """Override GuardDuty service dependency with a fake implementation."""
    app.dependency_overrides[get_guardduty_dep] = lambda: FakeGuardDutyService()
    try:
        yield
    finally:
        app.dependency_overrides.pop(get_guardduty_dep, None)


@pytest.mark.asyncio
async def test_guardduty_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/guardduty/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["service"] == "AWS GuardDuty Threat Detection"
    assert data["guardduty_enabled"] is True
    assert data["aws_connected"] is True


@pytest.mark.asyncio
async def test_guardduty_list_findings():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/guardduty/findings")
    assert resp.status_code == 200
    data = resp.json()
    assert "findings" in data
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_guardduty_dashboard_stats():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/guardduty/dashboard")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_detectors"] == 1
    assert data["active_detectors"] == 1
    assert data["total_findings"] == 0
