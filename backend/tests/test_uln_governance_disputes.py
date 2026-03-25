"""
ULN Phase C: Governance & Disputes API Tests
=============================================
Tests for governance rules and disputes CRUD endpoints.
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://uln-phase-b.preview.emergentagent.com')

# Test credentials
TEST_EMAIL = "owner@bigmannentertainment.com"
TEST_PASSWORD = "Test1234!"
LABEL_ID = "BM-LBL-9D0377FB"


class TestAuth:
    """Authentication helper tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, "No access_token in response"
        return data["access_token"]
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        """Get authenticated headers"""
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }


class TestGovernanceRules(TestAuth):
    """Governance Rules CRUD tests"""
    
    created_rule_id = None
    
    def test_01_list_governance_rules(self, headers):
        """GET /api/uln/labels/{label_id}/governance - List governance rules"""
        response = requests.get(
            f"{BASE_URL}/api/uln/labels/{LABEL_ID}/governance",
            headers=headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert "rules" in data
        assert "total_rules" in data
        assert "active_rules" in data
        assert "rules_by_type" in data
        assert data.get("label_id") == LABEL_ID
        print(f"✓ Listed {data['total_rules']} governance rules ({data['active_rules']} active)")
    
    def test_02_create_governance_rule_voting(self, headers):
        """POST /api/uln/labels/{label_id}/governance - Create voting rule"""
        payload = {
            "rule_type": "voting",
            "title": "TEST_Quorum Voting Rule",
            "description": "Requires 60% quorum for major decisions",
            "enforcement": "automatic",
            "status": "active",
            "conditions": {"quorum": 60, "majority": 51}
        }
        response = requests.post(
            f"{BASE_URL}/api/uln/labels/{LABEL_ID}/governance",
            headers=headers,
            json=payload
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert "rule" in data
        rule = data["rule"]
        assert rule["rule_type"] == "voting"
        assert rule["title"] == "TEST_Quorum Voting Rule"
        assert rule["enforcement"] == "automatic"
        assert rule["status"] == "active"
        assert rule["conditions"]["quorum"] == 60
        TestGovernanceRules.created_rule_id = rule["rule_id"]
        print(f"✓ Created voting rule: {rule['rule_id']}")
    
    def test_03_create_governance_rule_content_approval(self, headers):
        """POST /api/uln/labels/{label_id}/governance - Create content_approval rule"""
        payload = {
            "rule_type": "content_approval",
            "title": "TEST_Content Review Policy",
            "description": "All releases require A&R approval",
            "enforcement": "manual",
            "status": "draft"
        }
        response = requests.post(
            f"{BASE_URL}/api/uln/labels/{LABEL_ID}/governance",
            headers=headers,
            json=payload
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert data["rule"]["rule_type"] == "content_approval"
        print(f"✓ Created content_approval rule: {data['rule']['rule_id']}")
    
    def test_04_create_governance_rule_financial(self, headers):
        """POST /api/uln/labels/{label_id}/governance - Create financial rule"""
        payload = {
            "rule_type": "financial",
            "title": "TEST_Budget Approval Threshold",
            "description": "Expenses over $10k require owner approval",
            "enforcement": "manual",
            "status": "active",
            "conditions": {"threshold": 10000, "currency": "USD"}
        }
        response = requests.post(
            f"{BASE_URL}/api/uln/labels/{LABEL_ID}/governance",
            headers=headers,
            json=payload
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert data["rule"]["rule_type"] == "financial"
        print(f"✓ Created financial rule: {data['rule']['rule_id']}")
    
    def test_05_create_governance_rule_distribution(self, headers):
        """POST /api/uln/labels/{label_id}/governance - Create distribution rule"""
        payload = {
            "rule_type": "distribution",
            "title": "TEST_Platform Exclusivity",
            "description": "New releases exclusive to Spotify for 7 days",
            "enforcement": "automatic",
            "status": "active",
            "conditions": {"exclusivity_days": 7, "platform": "Spotify"}
        }
        response = requests.post(
            f"{BASE_URL}/api/uln/labels/{LABEL_ID}/governance",
            headers=headers,
            json=payload
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert data["rule"]["rule_type"] == "distribution"
        print(f"✓ Created distribution rule: {data['rule']['rule_id']}")
    
    def test_06_create_governance_rule_membership(self, headers):
        """POST /api/uln/labels/{label_id}/governance - Create membership rule"""
        payload = {
            "rule_type": "membership",
            "title": "TEST_Member Onboarding",
            "description": "New members require 2 admin approvals",
            "enforcement": "manual",
            "status": "active",
            "conditions": {"required_approvals": 2}
        }
        response = requests.post(
            f"{BASE_URL}/api/uln/labels/{LABEL_ID}/governance",
            headers=headers,
            json=payload
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert data["rule"]["rule_type"] == "membership"
        print(f"✓ Created membership rule: {data['rule']['rule_id']}")
    
    def test_07_create_governance_rule_invalid_type(self, headers):
        """POST /api/uln/labels/{label_id}/governance - Invalid rule_type should fail"""
        payload = {
            "rule_type": "invalid_type",
            "title": "TEST_Invalid Rule",
            "description": "This should fail"
        }
        response = requests.post(
            f"{BASE_URL}/api/uln/labels/{LABEL_ID}/governance",
            headers=headers,
            json=payload
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✓ Invalid rule_type correctly rejected")
    
    def test_08_update_governance_rule(self, headers):
        """PUT /api/uln/labels/{label_id}/governance/{rule_id} - Update rule"""
        rule_id = TestGovernanceRules.created_rule_id
        assert rule_id, "No rule_id from previous test"
        
        payload = {
            "title": "TEST_Updated Quorum Rule",
            "description": "Updated: Requires 70% quorum",
            "status": "inactive",
            "conditions": {"quorum": 70, "majority": 51}
        }
        response = requests.put(
            f"{BASE_URL}/api/uln/labels/{LABEL_ID}/governance/{rule_id}",
            headers=headers,
            json=payload
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert data["rule"]["title"] == "TEST_Updated Quorum Rule"
        assert data["rule"]["status"] == "inactive"
        print(f"✓ Updated governance rule: {rule_id}")
    
    def test_09_verify_update_persisted(self, headers):
        """GET governance rules to verify update persisted"""
        response = requests.get(
            f"{BASE_URL}/api/uln/labels/{LABEL_ID}/governance",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        rule_id = TestGovernanceRules.created_rule_id
        updated_rule = next((r for r in data["rules"] if r["rule_id"] == rule_id), None)
        assert updated_rule is not None, "Updated rule not found"
        assert updated_rule["title"] == "TEST_Updated Quorum Rule"
        assert updated_rule["status"] == "inactive"
        print("✓ Update verified via GET")
    
    def test_10_delete_governance_rule(self, headers):
        """DELETE /api/uln/labels/{label_id}/governance/{rule_id} - Delete rule"""
        rule_id = TestGovernanceRules.created_rule_id
        assert rule_id, "No rule_id from previous test"
        
        response = requests.delete(
            f"{BASE_URL}/api/uln/labels/{LABEL_ID}/governance/{rule_id}",
            headers=headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        print(f"✓ Deleted governance rule: {rule_id}")
    
    def test_11_verify_delete(self, headers):
        """Verify deleted rule no longer exists"""
        response = requests.get(
            f"{BASE_URL}/api/uln/labels/{LABEL_ID}/governance",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        rule_id = TestGovernanceRules.created_rule_id
        deleted_rule = next((r for r in data["rules"] if r["rule_id"] == rule_id), None)
        assert deleted_rule is None, "Deleted rule still exists"
        print("✓ Delete verified - rule no longer exists")


class TestDisputes(TestAuth):
    """Disputes CRUD tests"""
    
    created_dispute_id = None
    
    def test_01_list_disputes(self, headers):
        """GET /api/uln/labels/{label_id}/disputes - List disputes"""
        response = requests.get(
            f"{BASE_URL}/api/uln/labels/{LABEL_ID}/disputes",
            headers=headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert "disputes" in data
        assert "total_disputes" in data
        assert "disputes_by_status" in data
        print(f"✓ Listed {data['total_disputes']} disputes")
    
    def test_02_create_dispute_royalty_split(self, headers):
        """POST /api/uln/labels/{label_id}/disputes - Create royalty_split dispute"""
        payload = {
            "dispute_type": "royalty_split",
            "title": "TEST_Royalty Split Disagreement",
            "description": "Artist claims 50% split instead of agreed 40%",
            "priority": "high"
        }
        response = requests.post(
            f"{BASE_URL}/api/uln/labels/{LABEL_ID}/disputes",
            headers=headers,
            json=payload
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        dispute = data["dispute"]
        assert dispute["dispute_type"] == "royalty_split"
        assert dispute["title"] == "TEST_Royalty Split Disagreement"
        assert dispute["priority"] == "high"
        assert dispute["status"] == "open"
        TestDisputes.created_dispute_id = dispute["dispute_id"]
        print(f"✓ Created royalty_split dispute: {dispute['dispute_id']}")
    
    def test_03_create_dispute_rights_ownership(self, headers):
        """POST /api/uln/labels/{label_id}/disputes - Create rights_ownership dispute"""
        payload = {
            "dispute_type": "rights_ownership",
            "title": "TEST_Master Rights Claim",
            "description": "Producer claims co-ownership of master recording",
            "priority": "critical"
        }
        response = requests.post(
            f"{BASE_URL}/api/uln/labels/{LABEL_ID}/disputes",
            headers=headers,
            json=payload
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert data["dispute"]["dispute_type"] == "rights_ownership"
        assert data["dispute"]["priority"] == "critical"
        print(f"✓ Created rights_ownership dispute: {data['dispute']['dispute_id']}")
    
    def test_04_create_dispute_distribution(self, headers):
        """POST /api/uln/labels/{label_id}/disputes - Create distribution dispute"""
        payload = {
            "dispute_type": "distribution",
            "title": "TEST_Platform Delivery Issue",
            "description": "Release not appearing on Apple Music after 48 hours",
            "priority": "medium"
        }
        response = requests.post(
            f"{BASE_URL}/api/uln/labels/{LABEL_ID}/disputes",
            headers=headers,
            json=payload
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert data["dispute"]["dispute_type"] == "distribution"
        print(f"✓ Created distribution dispute: {data['dispute']['dispute_id']}")
    
    def test_05_create_dispute_content_takedown(self, headers):
        """POST /api/uln/labels/{label_id}/disputes - Create content_takedown dispute"""
        payload = {
            "dispute_type": "content_takedown",
            "title": "TEST_Unauthorized Sample Usage",
            "description": "Third party claims unauthorized sample in track",
            "priority": "high"
        }
        response = requests.post(
            f"{BASE_URL}/api/uln/labels/{LABEL_ID}/disputes",
            headers=headers,
            json=payload
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert data["dispute"]["dispute_type"] == "content_takedown"
        print(f"✓ Created content_takedown dispute: {data['dispute']['dispute_id']}")
    
    def test_06_create_dispute_membership(self, headers):
        """POST /api/uln/labels/{label_id}/disputes - Create membership dispute"""
        payload = {
            "dispute_type": "membership",
            "title": "TEST_Role Access Dispute",
            "description": "Member claims admin access was revoked incorrectly",
            "priority": "low"
        }
        response = requests.post(
            f"{BASE_URL}/api/uln/labels/{LABEL_ID}/disputes",
            headers=headers,
            json=payload
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert data["dispute"]["dispute_type"] == "membership"
        print(f"✓ Created membership dispute: {data['dispute']['dispute_id']}")
    
    def test_07_create_dispute_other(self, headers):
        """POST /api/uln/labels/{label_id}/disputes - Create other dispute"""
        payload = {
            "dispute_type": "other",
            "title": "TEST_General Inquiry",
            "description": "General dispute not fitting other categories",
            "priority": "low"
        }
        response = requests.post(
            f"{BASE_URL}/api/uln/labels/{LABEL_ID}/disputes",
            headers=headers,
            json=payload
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert data["dispute"]["dispute_type"] == "other"
        print(f"✓ Created other dispute: {data['dispute']['dispute_id']}")
    
    def test_08_create_dispute_invalid_type(self, headers):
        """POST /api/uln/labels/{label_id}/disputes - Invalid dispute_type should fail"""
        payload = {
            "dispute_type": "invalid_type",
            "title": "TEST_Invalid Dispute",
            "description": "This should fail"
        }
        response = requests.post(
            f"{BASE_URL}/api/uln/labels/{LABEL_ID}/disputes",
            headers=headers,
            json=payload
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✓ Invalid dispute_type correctly rejected")
    
    def test_09_get_dispute_detail(self, headers):
        """GET /api/uln/labels/{label_id}/disputes/{dispute_id} - Get dispute detail"""
        dispute_id = TestDisputes.created_dispute_id
        assert dispute_id, "No dispute_id from previous test"
        
        response = requests.get(
            f"{BASE_URL}/api/uln/labels/{LABEL_ID}/disputes/{dispute_id}",
            headers=headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert "dispute" in data
        dispute = data["dispute"]
        assert dispute["dispute_id"] == dispute_id
        assert dispute["title"] == "TEST_Royalty Split Disagreement"
        assert "responses" in dispute
        print(f"✓ Got dispute detail: {dispute_id}")
    
    def test_10_update_dispute(self, headers):
        """PUT /api/uln/labels/{label_id}/disputes/{dispute_id} - Update dispute"""
        dispute_id = TestDisputes.created_dispute_id
        assert dispute_id, "No dispute_id from previous test"
        
        payload = {
            "title": "TEST_Updated Royalty Dispute",
            "priority": "critical",
            "assigned_to": "legal-team-001"
        }
        response = requests.put(
            f"{BASE_URL}/api/uln/labels/{LABEL_ID}/disputes/{dispute_id}",
            headers=headers,
            json=payload
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert data["dispute"]["title"] == "TEST_Updated Royalty Dispute"
        assert data["dispute"]["priority"] == "critical"
        assert data["dispute"]["assigned_to"] == "legal-team-001"
        print(f"✓ Updated dispute: {dispute_id}")
    
    def test_11_respond_to_dispute_comment(self, headers):
        """POST /api/uln/labels/{label_id}/disputes/{dispute_id}/respond - Add comment"""
        dispute_id = TestDisputes.created_dispute_id
        assert dispute_id, "No dispute_id from previous test"
        
        payload = {
            "message": "Initial review completed. Requesting additional documentation.",
            "author_name": "Legal Team",
            "action": "comment"
        }
        response = requests.post(
            f"{BASE_URL}/api/uln/labels/{LABEL_ID}/disputes/{dispute_id}/respond",
            headers=headers,
            json=payload
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert len(data["dispute"]["responses"]) >= 1
        print(f"✓ Added comment to dispute: {dispute_id}")
    
    def test_12_respond_to_dispute_status_change_under_review(self, headers):
        """POST /api/uln/labels/{label_id}/disputes/{dispute_id}/respond - Change to under_review"""
        dispute_id = TestDisputes.created_dispute_id
        assert dispute_id, "No dispute_id from previous test"
        
        payload = {
            "message": "Moving to under review status for detailed analysis.",
            "author_name": "Admin",
            "new_status": "under_review"
        }
        response = requests.post(
            f"{BASE_URL}/api/uln/labels/{LABEL_ID}/disputes/{dispute_id}/respond",
            headers=headers,
            json=payload
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert data["dispute"]["status"] == "under_review"
        print(f"✓ Changed dispute status to under_review")
    
    def test_13_respond_to_dispute_escalate(self, headers):
        """POST /api/uln/labels/{label_id}/disputes/{dispute_id}/respond - Escalate"""
        dispute_id = TestDisputes.created_dispute_id
        assert dispute_id, "No dispute_id from previous test"
        
        payload = {
            "message": "Escalating to senior management for resolution.",
            "author_name": "Manager",
            "new_status": "escalated"
        }
        response = requests.post(
            f"{BASE_URL}/api/uln/labels/{LABEL_ID}/disputes/{dispute_id}/respond",
            headers=headers,
            json=payload
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert data["dispute"]["status"] == "escalated"
        print(f"✓ Escalated dispute")
    
    def test_14_respond_to_dispute_resolve(self, headers):
        """POST /api/uln/labels/{label_id}/disputes/{dispute_id}/respond - Resolve"""
        dispute_id = TestDisputes.created_dispute_id
        assert dispute_id, "No dispute_id from previous test"
        
        payload = {
            "message": "Agreement reached: 45% split confirmed. Dispute resolved.",
            "author_name": "Owner",
            "new_status": "resolved",
            "resolution": "Parties agreed to 45% artist split. Contract amended."
        }
        response = requests.post(
            f"{BASE_URL}/api/uln/labels/{LABEL_ID}/disputes/{dispute_id}/respond",
            headers=headers,
            json=payload
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert data["dispute"]["status"] == "resolved"
        assert data["dispute"]["resolution"] is not None
        assert data["dispute"]["resolved_at"] is not None
        print(f"✓ Resolved dispute with resolution")
    
    def test_15_list_disputes_with_status_filter(self, headers):
        """GET /api/uln/labels/{label_id}/disputes?status=open - Filter by status"""
        response = requests.get(
            f"{BASE_URL}/api/uln/labels/{LABEL_ID}/disputes?status=open",
            headers=headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        # All returned disputes should have status=open
        for dispute in data["disputes"]:
            assert dispute["status"] == "open", f"Expected open, got {dispute['status']}"
        print(f"✓ Filtered disputes by status=open: {len(data['disputes'])} found")
    
    def test_16_verify_dispute_timeline(self, headers):
        """Verify dispute has full response timeline"""
        dispute_id = TestDisputes.created_dispute_id
        assert dispute_id, "No dispute_id from previous test"
        
        response = requests.get(
            f"{BASE_URL}/api/uln/labels/{LABEL_ID}/disputes/{dispute_id}",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        dispute = data["dispute"]
        
        # Should have at least 4 responses (comment + 3 status changes)
        assert len(dispute["responses"]) >= 4, f"Expected >=4 responses, got {len(dispute['responses'])}"
        
        # Verify status change actions are recorded
        status_changes = [r for r in dispute["responses"] if r.get("action") == "status_change"]
        assert len(status_changes) >= 3, "Expected at least 3 status change responses"
        print(f"✓ Verified dispute timeline with {len(dispute['responses'])} responses")


class TestGovernanceDisputesSummary(TestAuth):
    """Summary endpoint tests"""
    
    def test_01_get_summary(self, headers):
        """GET /api/uln/labels/{label_id}/governance-disputes-summary"""
        response = requests.get(
            f"{BASE_URL}/api/uln/labels/{LABEL_ID}/governance-disputes-summary",
            headers=headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") is True
        assert "governance_rules" in data
        assert "active_governance_rules" in data
        assert "rules_by_type" in data
        assert "total_disputes" in data
        assert "disputes_by_status" in data
        print(f"✓ Summary: {data['governance_rules']} rules, {data['total_disputes']} disputes")


class TestCleanup(TestAuth):
    """Cleanup test data"""
    
    def test_cleanup_test_governance_rules(self, headers):
        """Delete all TEST_ prefixed governance rules"""
        response = requests.get(
            f"{BASE_URL}/api/uln/labels/{LABEL_ID}/governance",
            headers=headers
        )
        if response.status_code == 200:
            data = response.json()
            test_rules = [r for r in data.get("rules", []) if r.get("title", "").startswith("TEST_")]
            for rule in test_rules:
                del_response = requests.delete(
                    f"{BASE_URL}/api/uln/labels/{LABEL_ID}/governance/{rule['rule_id']}",
                    headers=headers
                )
                if del_response.status_code == 200:
                    print(f"  Cleaned up rule: {rule['rule_id']}")
        print(f"✓ Cleanup completed for governance rules")
    
    def test_cleanup_test_disputes(self, headers):
        """Note: Disputes typically aren't deleted, just closed"""
        # For test cleanup, we could update status to 'closed' for TEST_ disputes
        response = requests.get(
            f"{BASE_URL}/api/uln/labels/{LABEL_ID}/disputes",
            headers=headers
        )
        if response.status_code == 200:
            data = response.json()
            test_disputes = [d for d in data.get("disputes", []) if d.get("title", "").startswith("TEST_")]
            for dispute in test_disputes:
                if dispute["status"] not in ["closed", "resolved"]:
                    # Close the dispute
                    close_response = requests.post(
                        f"{BASE_URL}/api/uln/labels/{LABEL_ID}/disputes/{dispute['dispute_id']}/respond",
                        headers=headers,
                        json={
                            "message": "Test cleanup - closing dispute",
                            "new_status": "closed"
                        }
                    )
                    if close_response.status_code == 200:
                        print(f"  Closed test dispute: {dispute['dispute_id']}")
        print(f"✓ Cleanup completed for disputes")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
