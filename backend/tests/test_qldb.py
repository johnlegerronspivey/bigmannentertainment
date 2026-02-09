"""
QLDB Dispute Ledger API Tests
Tests the PostgreSQL-based dispute ledger endpoints
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://dispute-tracker-3.preview.emergentagent.com')

class TestQLDBHealth:
    """Health and Dashboard endpoint tests"""
    
    def test_health_endpoint(self):
        """Test GET /api/qldb/health returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/qldb/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
        print(f"Health check passed: {data['service']}")
    
    def test_dashboard_stats(self):
        """Test GET /api/qldb/dashboard returns dispute and audit stats"""
        response = requests.get(f"{BASE_URL}/api/qldb/dashboard")
        assert response.status_code == 200
        data = response.json()
        
        # Verify dispute_stats structure
        assert "dispute_stats" in data
        dispute_stats = data["dispute_stats"]
        assert dispute_stats["total_disputes"] >= 0
        assert dispute_stats["total_amount_disputed"] >= 0
        assert "disputes_by_type" in dispute_stats
        
        # Verify audit_stats structure
        assert "audit_stats" in data
        audit_stats = data["audit_stats"]
        assert audit_stats["total_entries"] >= 0
        
        # Verify chain_verified
        assert "chain_verified" in data
        
        print(f"Dashboard stats: {dispute_stats['total_disputes']} disputes, {audit_stats['total_entries']} audit entries")


class TestQLDBDisputes:
    """Dispute CRUD operations tests"""
    
    def test_list_disputes(self):
        """Test GET /api/qldb/disputes returns list of disputes"""
        response = requests.get(f"{BASE_URL}/api/qldb/disputes")
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert "disputes" in data
        assert "total" in data
        assert isinstance(data["disputes"], list)
        print(f"Retrieved {len(data['disputes'])} disputes (total: {data['total']})")
    
    def test_disputes_have_required_fields(self):
        """Test that disputes have all required fields"""
        response = requests.get(f"{BASE_URL}/api/qldb/disputes")
        assert response.status_code == 200
        data = response.json()
        
        if len(data["disputes"]) > 0:
            dispute = data["disputes"][0]
            required_fields = ["id", "dispute_number", "type", "status", "priority", "title", "created_at"]
            for field in required_fields:
                assert field in dispute, f"Missing field: {field}"
            print(f"Dispute fields verified: {dispute['dispute_number']}")
    
    def test_create_dispute(self):
        """Test POST /api/qldb/disputes creates a new dispute"""
        unique_id = str(uuid.uuid4())[:8]
        payload = {
            "type": "ROYALTY_DISPUTE",
            "title": f"TEST_Dispute_{unique_id}",
            "description": "Automated test dispute for pytest verification",
            "amount_disputed": 1500.00,
            "currency": "USD",
            "claimant_name": "Test Claimant",
            "claimant_email": "test@pytest.com",
            "priority": "HIGH"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/qldb/disputes",
            json=payload
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["title"] == payload["title"]
        assert data["type"] == payload["type"]
        assert data["status"] == "OPEN"
        assert "dispute_number" in data
        assert data["dispute_number"].startswith("DISP-")
        
        print(f"Created dispute: {data['dispute_number']}")
        return data["id"]
    
    def test_create_and_verify_persistence(self):
        """Test that created dispute is persisted and retrievable"""
        unique_id = str(uuid.uuid4())[:8]
        payload = {
            "type": "CONTRACT_DISPUTE",
            "title": f"TEST_Persist_{unique_id}",
            "description": "Testing persistence",
            "amount_disputed": 2000.00,
            "claimant_name": "Persistence Test",
            "claimant_email": "persist@test.com",
            "priority": "MEDIUM"
        }
        
        # Create dispute
        create_response = requests.post(f"{BASE_URL}/api/qldb/disputes", json=payload)
        assert create_response.status_code == 200
        created_dispute = create_response.json()
        dispute_id = created_dispute["id"]
        
        # Verify via GET
        get_response = requests.get(f"{BASE_URL}/api/qldb/disputes/{dispute_id}")
        assert get_response.status_code == 200
        fetched_dispute = get_response.json()
        
        assert fetched_dispute["id"] == dispute_id
        assert fetched_dispute["title"] == payload["title"]
        print(f"Persistence verified for dispute: {fetched_dispute['dispute_number']}")
    
    def test_get_nonexistent_dispute(self):
        """Test that getting a non-existent dispute returns 404"""
        response = requests.get(f"{BASE_URL}/api/qldb/disputes/nonexistent-id-12345")
        assert response.status_code == 404
        print("Correctly returned 404 for non-existent dispute")


class TestQLDBAudit:
    """Audit trail tests"""
    
    def test_list_audit_entries(self):
        """Test GET /api/qldb/audit returns audit entries"""
        response = requests.get(f"{BASE_URL}/api/qldb/audit")
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert "entries" in data
        assert "total" in data
        assert isinstance(data["entries"], list)
        print(f"Retrieved {len(data['entries'])} audit entries (total: {data['total']})")
    
    def test_audit_entries_have_required_fields(self):
        """Test that audit entries have all required fields"""
        response = requests.get(f"{BASE_URL}/api/qldb/audit")
        assert response.status_code == 200
        data = response.json()
        
        if len(data["entries"]) > 0:
            entry = data["entries"][0]
            required_fields = ["id", "event_type", "entity_type", "entity_id", "actor_id", "timestamp"]
            for field in required_fields:
                assert field in entry, f"Missing field: {field}"
            print(f"Audit entry fields verified: {entry['event_type']}")
    
    def test_verify_chain_integrity(self):
        """Test GET /api/qldb/audit/chain/verify returns chain verification"""
        response = requests.get(f"{BASE_URL}/api/qldb/audit/chain/verify")
        assert response.status_code == 200
        data = response.json()
        
        assert "chain_valid" in data
        assert data["chain_valid"] == True
        print("Chain integrity verified")


class TestQLDBReferenceData:
    """Reference data endpoint tests"""
    
    def test_dispute_types(self):
        """Test GET /api/qldb/dispute-types returns available dispute types"""
        response = requests.get(f"{BASE_URL}/api/qldb/dispute-types")
        assert response.status_code == 200
        data = response.json()
        
        assert "dispute_types" in data
        assert len(data["dispute_types"]) > 0
        
        # Verify expected types exist
        type_ids = [t["id"] for t in data["dispute_types"]]
        expected_types = ["ROYALTY_DISPUTE", "CONTRACT_DISPUTE", "PAYMENT_DISPUTE", "COPYRIGHT_CLAIM"]
        for expected in expected_types:
            assert expected in type_ids, f"Missing dispute type: {expected}"
        
        print(f"Retrieved {len(data['dispute_types'])} dispute types")
    
    def test_dispute_statuses(self):
        """Test GET /api/qldb/dispute-statuses returns available statuses"""
        response = requests.get(f"{BASE_URL}/api/qldb/dispute-statuses")
        assert response.status_code == 200
        data = response.json()
        
        assert "statuses" in data
        assert len(data["statuses"]) > 0
        
        status_ids = [s["id"] for s in data["statuses"]]
        expected_statuses = ["OPEN", "UNDER_REVIEW", "RESOLVED", "ESCALATED", "CLOSED"]
        for expected in expected_statuses:
            assert expected in status_ids, f"Missing status: {expected}"
        
        print(f"Retrieved {len(data['statuses'])} statuses")
    
    def test_priorities(self):
        """Test GET /api/qldb/priorities returns priority levels"""
        response = requests.get(f"{BASE_URL}/api/qldb/priorities")
        assert response.status_code == 200
        data = response.json()
        
        assert "priorities" in data
        assert len(data["priorities"]) > 0
        
        priority_ids = [p["id"] for p in data["priorities"]]
        expected_priorities = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        for expected in expected_priorities:
            assert expected in priority_ids, f"Missing priority: {expected}"
        
        print(f"Retrieved {len(data['priorities'])} priorities")
    
    def test_event_types(self):
        """Test GET /api/qldb/event-types returns audit event types"""
        response = requests.get(f"{BASE_URL}/api/qldb/event-types")
        assert response.status_code == 200
        data = response.json()
        
        assert "event_types" in data
        assert len(data["event_types"]) > 0
        
        event_ids = [e["id"] for e in data["event_types"]]
        expected_events = ["DISPUTE_CREATED", "DISPUTE_UPDATED", "DISPUTE_RESOLVED"]
        for expected in expected_events:
            assert expected in event_ids, f"Missing event type: {expected}"
        
        print(f"Retrieved {len(data['event_types'])} event types")


class TestQLDBDataIntegrity:
    """Data integrity and workflow tests"""
    
    def test_create_dispute_creates_audit_entry(self):
        """Test that creating a dispute also creates an audit entry"""
        # Get initial audit count
        initial_audit = requests.get(f"{BASE_URL}/api/qldb/audit")
        initial_count = initial_audit.json()["total"]
        
        # Create a new dispute
        unique_id = str(uuid.uuid4())[:8]
        payload = {
            "type": "PAYMENT_DISPUTE",
            "title": f"TEST_AuditCheck_{unique_id}",
            "description": "Testing audit entry creation",
            "amount_disputed": 500.00,
            "claimant_name": "Audit Checker",
            "claimant_email": "audit@test.com"
        }
        
        create_response = requests.post(f"{BASE_URL}/api/qldb/disputes", json=payload)
        assert create_response.status_code == 200
        created_dispute = create_response.json()
        
        # Verify audit count increased
        final_audit = requests.get(f"{BASE_URL}/api/qldb/audit")
        final_count = final_audit.json()["total"]
        
        assert final_count > initial_count, "Audit entry was not created"
        print(f"Audit count increased from {initial_count} to {final_count}")
    
    def test_dashboard_stats_reflect_disputes(self):
        """Test that dashboard stats accurately reflect dispute data"""
        # Get dashboard stats
        dashboard = requests.get(f"{BASE_URL}/api/qldb/dashboard").json()
        
        # Get disputes list
        disputes = requests.get(f"{BASE_URL}/api/qldb/disputes").json()
        
        # Verify total matches
        assert dashboard["dispute_stats"]["total_disputes"] == disputes["total"], \
            "Dashboard total does not match disputes list total"
        
        print(f"Dashboard stats match: {disputes['total']} disputes")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
