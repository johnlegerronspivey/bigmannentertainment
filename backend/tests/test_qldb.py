"""
AWS QLDB Dispute Ledger - Backend Tests

These tests validate the core QLDB API endpoints using a FAKE service
wired via FastAPI dependency overrides, so no real MongoDB or AWS
QLDB is touched. We still verify routing and response contracts.
"""

import os
import sys

import pytest
from httpx import AsyncClient, ASGITransport

# Ensure we can import the FastAPI app and endpoint dependencies
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from server import app  # type: ignore  # noqa: E402
from qldb_endpoints import get_service as get_qldb_dep  # type: ignore  # noqa: E402
from qldb_models import (  # type: ignore  # noqa: E402
    QLDBHealthResponse,
    Dispute,
    DisputeStatus,
    DisputeType,
    Priority,
    VerificationResponse,
    DisputeParty,
)


class FakeQLDBService:
    """Minimal fake QLDB service for testing.

    Implements only the methods used by the endpoints under test.
    """

    async def check_health(self) -> QLDBHealthResponse:
        return QLDBHealthResponse(
            status="healthy",
            service="AWS QLDB Dispute Ledger",
            version="1.0.0",
            ledger_active=True,
            chain_integrity=True,
            aws_region="us-east-1",
            features=["immutable_ledger", "audit_trail"],
        )

    async def get_disputes(self, *_, **__):
        """Return a single fake dispute plus total count."""
        claimant = DisputeParty(
            party_id="artist-test",
            party_type="claimant",
            name="Test Artist",
        )
        dispute = Dispute(
            dispute_number="DISP-TEST-001",
            type=DisputeType.ROYALTY_DISPUTE,
            status=DisputeStatus.OPEN,
            priority=Priority.MEDIUM,
            title="Test Dispute",
            description="Test dispute for automated backend checks.",
            claimant=claimant,
        )
        # Endpoint wraps this into DisputesResponse
        return [dispute], 1

    async def verify_chain_integrity(self) -> VerificationResponse:
        return VerificationResponse(
            document_id="CHAIN",
            verified=True,
            content_hash=None,
            chain_valid=True,
        )

    async def verify_audit_entry(self, entry_id: str) -> VerificationResponse:
        """Minimal stub to satisfy /audit/{entry_id}/verify path in middleware.

        Tests don't hit this endpoint directly; we just need it so that any
        internal calls (e.g., from other endpoints or middleware) don't fail.
        """
        return VerificationResponse(
            document_id=entry_id,
            verified=True,
            content_hash=None,
            chain_valid=True,
        )


@pytest.fixture(scope="module", autouse=True)
def override_qldb_service():
    """Override QLDB service dependency with a fake implementation."""
    app.dependency_overrides[get_qldb_dep] = lambda: FakeQLDBService()
    try:
        yield
    finally:
        app.dependency_overrides.pop(get_qldb_dep, None)


@pytest.mark.asyncio
async def test_qldb_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/qldb/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["service"] == "AWS QLDB Dispute Ledger"
    assert data["ledger_active"] is True
    assert data["chain_integrity"] is True


@pytest.mark.asyncio
async def test_qldb_list_disputes():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/qldb/disputes")
    assert resp.status_code == 200
    data = resp.json()
    assert "disputes" in data
    assert data["total"] == 1
    assert len(data["disputes"]) == 1


@pytest.mark.asyncio
async def test_qldb_chain_verification():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/qldb/audit/chain/verify")
    assert resp.status_code == 200
    data = resp.json()
    assert "chain_valid" in data
    assert data["chain_valid"] is True
