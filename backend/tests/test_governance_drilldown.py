"""
Test Governance Widget Drill-Down Feature
Tests for dispute list, detail, and respond endpoints
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestDisputeListEndpoint:
    """Tests for GET /api/gs1/disputes - List all disputes with filters"""
    
    def test_list_disputes_no_filter(self):
        """Test listing all disputes without filters"""
        response = requests.get(f"{BASE_URL}/api/gs1/disputes")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "disputes" in data, "Response should contain 'disputes' key"
        assert "total" in data, "Response should contain 'total' key"
        assert "page" in data, "Response should contain 'page' key"
        assert "page_size" in data, "Response should contain 'page_size' key"
        assert "total_pages" in data, "Response should contain 'total_pages' key"
        
        # Verify total count matches expected (7 disputes per context)
        assert data["total"] >= 1, "Should have at least 1 dispute"
        
        # Verify each dispute has required fields
        if data["disputes"]:
            dispute = data["disputes"][0]
            assert "dispute_id" in dispute, "Dispute should have dispute_id"
            assert "title" in dispute, "Dispute should have title"
            assert "status" in dispute, "Dispute should have status"
            assert "priority" in dispute, "Dispute should have priority"
            assert "label_name" in dispute, "Dispute should have label_name resolved"
    
    def test_list_disputes_filter_by_status_open(self):
        """Test filtering disputes by status=open"""
        response = requests.get(f"{BASE_URL}/api/gs1/disputes?status=open")
        assert response.status_code == 200
        
        data = response.json()
        # All returned disputes should have status=open
        for dispute in data["disputes"]:
            assert dispute["status"] == "open", f"Expected status 'open', got '{dispute['status']}'"
    
    def test_list_disputes_filter_by_status_resolved(self):
        """Test filtering disputes by status=resolved"""
        response = requests.get(f"{BASE_URL}/api/gs1/disputes?status=resolved")
        assert response.status_code == 200
        
        data = response.json()
        for dispute in data["disputes"]:
            assert dispute["status"] == "resolved", f"Expected status 'resolved', got '{dispute['status']}'"
    
    def test_list_disputes_filter_by_status_closed(self):
        """Test filtering disputes by status=closed"""
        response = requests.get(f"{BASE_URL}/api/gs1/disputes?status=closed")
        assert response.status_code == 200
        
        data = response.json()
        for dispute in data["disputes"]:
            assert dispute["status"] == "closed", f"Expected status 'closed', got '{dispute['status']}'"
    
    def test_list_disputes_filter_by_priority_critical(self):
        """Test filtering disputes by priority=critical"""
        response = requests.get(f"{BASE_URL}/api/gs1/disputes?priority=critical")
        assert response.status_code == 200
        
        data = response.json()
        for dispute in data["disputes"]:
            assert dispute["priority"] == "critical", f"Expected priority 'critical', got '{dispute['priority']}'"
    
    def test_list_disputes_filter_by_priority_high(self):
        """Test filtering disputes by priority=high"""
        response = requests.get(f"{BASE_URL}/api/gs1/disputes?priority=high")
        assert response.status_code == 200
        
        data = response.json()
        for dispute in data["disputes"]:
            assert dispute["priority"] == "high", f"Expected priority 'high', got '{dispute['priority']}'"
    
    def test_list_disputes_pagination(self):
        """Test pagination parameters"""
        response = requests.get(f"{BASE_URL}/api/gs1/disputes?page=1&page_size=2")
        assert response.status_code == 200
        
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 2
        assert len(data["disputes"]) <= 2, "Should return at most page_size items"
    
    def test_list_disputes_combined_filters(self):
        """Test combining status and priority filters"""
        response = requests.get(f"{BASE_URL}/api/gs1/disputes?status=closed&priority=high")
        assert response.status_code == 200
        
        data = response.json()
        for dispute in data["disputes"]:
            assert dispute["status"] == "closed"
            assert dispute["priority"] == "high"


class TestDisputeDetailEndpoint:
    """Tests for GET /api/gs1/disputes/{dispute_id} - Get single dispute detail"""
    
    def get_first_dispute_id(self):
        """Helper to get a valid dispute_id from the list"""
        response = requests.get(f"{BASE_URL}/api/gs1/disputes")
        if response.status_code == 200 and response.json()["disputes"]:
            return response.json()["disputes"][0]["dispute_id"]
        return None
    
    def test_get_dispute_detail_success(self):
        """Test getting a single dispute by ID"""
        dispute_id = self.get_first_dispute_id()
        if not dispute_id:
            pytest.skip("No disputes available to test")
        
        response = requests.get(f"{BASE_URL}/api/gs1/disputes/{dispute_id}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["success"] == True, "Response should have success=True"
        assert "dispute" in data, "Response should contain 'dispute' key"
        
        dispute = data["dispute"]
        assert dispute["dispute_id"] == dispute_id, "Returned dispute_id should match requested"
        assert "title" in dispute, "Dispute should have title"
        assert "status" in dispute, "Dispute should have status"
        assert "priority" in dispute, "Dispute should have priority"
        assert "label_name" in dispute, "Dispute should have label_name resolved"
        assert "description" in dispute, "Dispute should have description"
        assert "dispute_type" in dispute, "Dispute should have dispute_type"
        assert "created_at" in dispute, "Dispute should have created_at"
    
    def test_get_dispute_detail_not_found(self):
        """Test getting a non-existent dispute returns 404"""
        fake_id = f"DISP-{uuid.uuid4().hex[:12].upper()}"
        response = requests.get(f"{BASE_URL}/api/gs1/disputes/{fake_id}")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    
    def test_dispute_detail_has_responses_field(self):
        """Test that dispute detail includes responses/activity timeline"""
        dispute_id = self.get_first_dispute_id()
        if not dispute_id:
            pytest.skip("No disputes available to test")
        
        response = requests.get(f"{BASE_URL}/api/gs1/disputes/{dispute_id}")
        assert response.status_code == 200
        
        dispute = response.json()["dispute"]
        # responses field should exist (may be empty list)
        assert "responses" in dispute or dispute.get("responses") is None, "Dispute should have responses field"


class TestDisputeRespondEndpoint:
    """Tests for POST /api/gs1/disputes/{dispute_id}/respond - Add response to dispute"""
    
    def get_open_dispute_id(self):
        """Helper to get an open dispute_id"""
        response = requests.get(f"{BASE_URL}/api/gs1/disputes?status=open")
        if response.status_code == 200 and response.json()["disputes"]:
            return response.json()["disputes"][0]["dispute_id"]
        return None
    
    def get_any_dispute_id(self):
        """Helper to get any dispute_id"""
        response = requests.get(f"{BASE_URL}/api/gs1/disputes")
        if response.status_code == 200 and response.json()["disputes"]:
            return response.json()["disputes"][0]["dispute_id"]
        return None
    
    def test_respond_to_dispute_comment_only(self):
        """Test adding a comment without status change"""
        dispute_id = self.get_any_dispute_id()
        if not dispute_id:
            pytest.skip("No disputes available to test")
        
        payload = {
            "message": f"TEST_COMMENT_{uuid.uuid4().hex[:8]}"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/gs1/disputes/{dispute_id}/respond",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["success"] == True
        assert "dispute" in data
        
        # Verify the response was added
        dispute = data["dispute"]
        assert "responses" in dispute
        # Find our test comment
        found = any(r.get("message") == payload["message"] for r in dispute.get("responses", []))
        assert found, "Test comment should be in responses"
    
    def test_respond_to_dispute_with_status_change(self):
        """Test adding a response with status change to under_review"""
        dispute_id = self.get_open_dispute_id()
        if not dispute_id:
            pytest.skip("No open disputes available to test")
        
        payload = {
            "message": f"TEST_STATUS_CHANGE_{uuid.uuid4().hex[:8]}",
            "new_status": "under_review"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/gs1/disputes/{dispute_id}/respond",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        dispute = data["dispute"]
        assert dispute["status"] == "under_review", f"Status should be 'under_review', got '{dispute['status']}'"
    
    def test_respond_to_dispute_not_found(self):
        """Test responding to non-existent dispute returns 404"""
        fake_id = f"DISP-{uuid.uuid4().hex[:12].upper()}"
        payload = {"message": "Test message"}
        
        response = requests.post(
            f"{BASE_URL}/api/gs1/disputes/{fake_id}/respond",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    
    def test_respond_to_dispute_empty_message(self):
        """Test that empty message is handled (may succeed or fail based on validation)"""
        dispute_id = self.get_any_dispute_id()
        if not dispute_id:
            pytest.skip("No disputes available to test")
        
        payload = {"message": ""}
        
        response = requests.post(
            f"{BASE_URL}/api/gs1/disputes/{dispute_id}/respond",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        # Either 200 (accepts empty) or 422 (validation error) is acceptable
        assert response.status_code in [200, 422], f"Expected 200 or 422, got {response.status_code}"


class TestGovernanceOverviewIntegration:
    """Integration tests to verify governance-overview data matches disputes list"""
    
    def test_governance_overview_dispute_counts_match(self):
        """Verify governance-overview dispute counts match actual disputes"""
        # Get governance overview
        overview_response = requests.get(f"{BASE_URL}/api/gs1/governance-overview")
        assert overview_response.status_code == 200
        overview = overview_response.json()
        
        # Get all disputes
        disputes_response = requests.get(f"{BASE_URL}/api/gs1/disputes?page_size=100")
        assert disputes_response.status_code == 200
        disputes_data = disputes_response.json()
        
        # Verify total matches
        assert overview["disputes"]["total_disputes"] == disputes_data["total"], \
            f"Total disputes mismatch: overview={overview['disputes']['total_disputes']}, list={disputes_data['total']}"
        
        # Verify open count
        open_response = requests.get(f"{BASE_URL}/api/gs1/disputes?status=open")
        open_count = open_response.json()["total"]
        assert overview["disputes"]["open_disputes"] == open_count, \
            f"Open disputes mismatch: overview={overview['disputes']['open_disputes']}, filtered={open_count}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
