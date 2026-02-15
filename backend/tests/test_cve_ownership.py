"""
CVE Ownership Model API Tests
Tests for assigning owners (people/teams) to CVEs, viewing unassigned CVEs, 
bulk assigning, and managing ownership endpoints.
Phase 4 Enhancement: CVE Ownership Model
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://remediation-dash.preview.emergentagent.com').rstrip('/')


class TestCVEOwnershipEndpoints:
    """Test CVE Ownership Model endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test data"""
        self.test_cve_ids = []
    
    def test_get_available_owners_returns_structure(self):
        """GET /api/cve/owners returns people, teams, unassigned count"""
        response = requests.get(f"{BASE_URL}/api/cve/owners")
        assert response.status_code == 200
        
        data = response.json()
        assert "people" in data
        assert "teams" in data
        assert "unassigned_open_cves" in data
        
        assert isinstance(data["people"], list)
        assert isinstance(data["teams"], list)
        assert isinstance(data["unassigned_open_cves"], int)
        print(f"GET /owners: {len(data['people'])} people, {len(data['teams'])} teams, {data['unassigned_open_cves']} unassigned")
    
    def test_get_unassigned_cves_returns_structure(self):
        """GET /api/cve/unassigned returns unassigned open CVEs"""
        response = requests.get(f"{BASE_URL}/api/cve/unassigned")
        assert response.status_code == 200
        
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert isinstance(data["items"], list)
        assert isinstance(data["total"], int)
        print(f"GET /unassigned: {data['total']} unassigned CVEs")
    
    def test_get_unassigned_cves_with_severity_filter(self):
        """GET /api/cve/unassigned?severity=high filters by severity"""
        response = requests.get(f"{BASE_URL}/api/cve/unassigned?severity=high")
        assert response.status_code == 200
        
        data = response.json()
        assert "items" in data
        # All returned CVEs should have the requested severity
        for cve in data["items"]:
            assert cve.get("severity") == "high"
        print(f"GET /unassigned?severity=high: {data['total']} high severity unassigned CVEs")
    
    def test_assign_owner_to_cve(self):
        """PUT /api/cve/entries/{id}/owner assigns owner and team to a CVE"""
        # First create a test CVE
        create_response = requests.post(f"{BASE_URL}/api/cve/entries", json={
            "title": f"TEST_Ownership_Test_{uuid.uuid4().hex[:6]}",
            "severity": "medium",
            "affected_package": "test-ownership-pkg"
        })
        assert create_response.status_code == 200
        cve_id = create_response.json()["id"]
        
        # Assign owner
        assign_response = requests.put(f"{BASE_URL}/api/cve/entries/{cve_id}/owner", json={
            "assigned_to": "TEST_Owner_User",
            "assigned_team": "TEST_Team_Alpha",
            "notes": "Test assignment"
        })
        assert assign_response.status_code == 200
        
        # Verify assignment
        data = assign_response.json()
        assert data["assigned_to"] == "TEST_Owner_User"
        assert data["assigned_team"] == "TEST_Team_Alpha"
        print(f"PUT /entries/{cve_id[:8]}../owner: assigned to TEST_Owner_User / TEST_Team_Alpha")
        
        # GET to verify persistence
        get_response = requests.get(f"{BASE_URL}/api/cve/entries/{cve_id}")
        assert get_response.status_code == 200
        persisted = get_response.json()
        assert persisted["assigned_to"] == "TEST_Owner_User"
        assert persisted["assigned_team"] == "TEST_Team_Alpha"
        print(f"GET verify: Owner assignment persisted correctly")
    
    def test_assign_owner_updates_owners_list(self):
        """Assigning a new owner/team updates the available owners list"""
        unique_person = f"TEST_Person_{uuid.uuid4().hex[:6]}"
        unique_team = f"TEST_Team_{uuid.uuid4().hex[:6]}"
        
        # Create CVE
        create_response = requests.post(f"{BASE_URL}/api/cve/entries", json={
            "title": f"TEST_Unique_Owner_{uuid.uuid4().hex[:6]}",
            "severity": "low",
            "affected_package": "test-unique-pkg"
        })
        cve_id = create_response.json()["id"]
        
        # Assign unique owner
        requests.put(f"{BASE_URL}/api/cve/entries/{cve_id}/owner", json={
            "assigned_to": unique_person,
            "assigned_team": unique_team
        })
        
        # Check owners list includes new person/team
        owners_response = requests.get(f"{BASE_URL}/api/cve/owners")
        owners = owners_response.json()
        
        assert unique_person in owners["people"], f"New person {unique_person} should be in owners list"
        assert unique_team in owners["teams"], f"New team {unique_team} should be in teams list"
        print(f"New owner '{unique_person}' and team '{unique_team}' appear in /owners list")
    
    def test_assign_owner_invalid_cve_returns_404(self):
        """PUT /api/cve/entries/{invalid_id}/owner returns 404"""
        response = requests.put(f"{BASE_URL}/api/cve/entries/non-existent-id-123/owner", json={
            "assigned_to": "Someone",
            "assigned_team": "Some Team"
        })
        assert response.status_code == 404
        print("PUT /entries/invalid/owner: Returns 404 as expected")
    
    def test_bulk_assign_owner_success(self):
        """POST /api/cve/entries/bulk-assign bulk assigns owners"""
        # Create two test CVEs
        cve_ids = []
        for i in range(2):
            create_response = requests.post(f"{BASE_URL}/api/cve/entries", json={
                "title": f"TEST_Bulk_{i}_{uuid.uuid4().hex[:6]}",
                "severity": "info",
                "affected_package": f"test-bulk-pkg-{i}"
            })
            cve_ids.append(create_response.json()["id"])
        
        # Bulk assign
        bulk_response = requests.post(f"{BASE_URL}/api/cve/entries/bulk-assign", json={
            "cve_ids": cve_ids,
            "assigned_to": "TEST_Bulk_Owner",
            "assigned_team": "TEST_Bulk_Team",
            "notes": "Bulk assignment test"
        })
        assert bulk_response.status_code == 200
        
        data = bulk_response.json()
        assert data["updated"] == 2
        assert data["failed"] == []
        assert data["total_requested"] == 2
        print(f"POST /entries/bulk-assign: {data['updated']}/{data['total_requested']} updated, {len(data['failed'])} failed")
        
        # Verify each CVE was updated
        for cve_id in cve_ids:
            get_response = requests.get(f"{BASE_URL}/api/cve/entries/{cve_id}")
            cve = get_response.json()
            assert cve["assigned_to"] == "TEST_Bulk_Owner"
            assert cve["assigned_team"] == "TEST_Bulk_Team"
        print(f"GET verify: All {len(cve_ids)} CVEs have bulk-assigned owner/team")
    
    def test_bulk_assign_partial_failure(self):
        """POST /api/cve/entries/bulk-assign handles partial failures"""
        # Create one valid CVE
        create_response = requests.post(f"{BASE_URL}/api/cve/entries", json={
            "title": f"TEST_Partial_Bulk_{uuid.uuid4().hex[:6]}",
            "severity": "medium",
            "affected_package": "test-partial-pkg"
        })
        valid_id = create_response.json()["id"]
        
        # Mix valid and invalid IDs
        bulk_response = requests.post(f"{BASE_URL}/api/cve/entries/bulk-assign", json={
            "cve_ids": [valid_id, "invalid-id-xyz", "another-invalid-123"],
            "assigned_to": "TEST_Partial_Owner",
            "assigned_team": "TEST_Partial_Team"
        })
        assert bulk_response.status_code == 200
        
        data = bulk_response.json()
        assert data["updated"] == 1
        assert len(data["failed"]) == 2
        assert data["total_requested"] == 3
        print(f"Partial bulk assign: {data['updated']} updated, {len(data['failed'])} failed")
    
    def test_reassign_owner(self):
        """Reassigning owner updates CVE correctly"""
        # Create CVE
        create_response = requests.post(f"{BASE_URL}/api/cve/entries", json={
            "title": f"TEST_Reassign_{uuid.uuid4().hex[:6]}",
            "severity": "high",
            "affected_package": "test-reassign-pkg"
        })
        cve_id = create_response.json()["id"]
        
        # Initial assignment
        requests.put(f"{BASE_URL}/api/cve/entries/{cve_id}/owner", json={
            "assigned_to": "First Owner",
            "assigned_team": "First Team"
        })
        
        # Reassign
        reassign_response = requests.put(f"{BASE_URL}/api/cve/entries/{cve_id}/owner", json={
            "assigned_to": "Second Owner",
            "assigned_team": "Second Team"
        })
        assert reassign_response.status_code == 200
        
        data = reassign_response.json()
        assert data["assigned_to"] == "Second Owner"
        assert data["assigned_team"] == "Second Team"
        print(f"Reassignment: Owner changed from 'First Owner' to 'Second Owner'")
    
    def test_clear_assignment(self):
        """Can clear owner assignment by setting empty strings"""
        # Create and assign
        create_response = requests.post(f"{BASE_URL}/api/cve/entries", json={
            "title": f"TEST_Clear_{uuid.uuid4().hex[:6]}",
            "severity": "low",
            "affected_package": "test-clear-pkg"
        })
        cve_id = create_response.json()["id"]
        
        requests.put(f"{BASE_URL}/api/cve/entries/{cve_id}/owner", json={
            "assigned_to": "Temporary Owner",
            "assigned_team": "Temporary Team"
        })
        
        # Clear assignment
        clear_response = requests.put(f"{BASE_URL}/api/cve/entries/{cve_id}/owner", json={
            "assigned_to": "",
            "assigned_team": ""
        })
        assert clear_response.status_code == 200
        
        data = clear_response.json()
        assert data["assigned_to"] == ""
        assert data["assigned_team"] == ""
        print(f"Clear assignment: Owner and team set to empty strings")


class TestCreateCVEWithOwnership:
    """Test CVE creation with assigned_to and assigned_team fields"""
    
    def test_create_cve_with_owner(self):
        """Creating a CVE can include assigned_to and assigned_team"""
        response = requests.post(f"{BASE_URL}/api/cve/entries", json={
            "title": f"TEST_CreateWithOwner_{uuid.uuid4().hex[:6]}",
            "severity": "critical",
            "affected_package": "test-create-owner-pkg",
            "assigned_to": "Initial Owner",
            "assigned_team": "Initial Team"
        })
        assert response.status_code == 200
        
        data = response.json()
        assert data["assigned_to"] == "Initial Owner"
        assert data["assigned_team"] == "Initial Team"
        print(f"Create CVE with owner: assigned_to='Initial Owner', assigned_team='Initial Team'")
    
    def test_create_cve_without_owner(self):
        """Creating a CVE without owner fields results in empty strings"""
        response = requests.post(f"{BASE_URL}/api/cve/entries", json={
            "title": f"TEST_CreateNoOwner_{uuid.uuid4().hex[:6]}",
            "severity": "medium",
            "affected_package": "test-no-owner-pkg"
        })
        assert response.status_code == 200
        
        data = response.json()
        assert data["assigned_to"] == ""
        assert data["assigned_team"] == ""
        print(f"Create CVE without owner: assigned_to='', assigned_team=''")


class TestGovernanceOwnershipView:
    """Test Governance > Ownership view API"""
    
    def test_governance_ownership_endpoint(self):
        """GET /api/cve/governance/ownership returns ownership breakdown"""
        response = requests.get(f"{BASE_URL}/api/cve/governance/ownership")
        assert response.status_code == 200
        
        data = response.json()
        assert "by_team" in data
        assert "by_person" in data
        assert "by_source" in data
        assert "by_status" in data
        
        assert isinstance(data["by_team"], list)
        assert isinstance(data["by_person"], list)
        assert isinstance(data["by_source"], list)
        assert isinstance(data["by_status"], list)
        print(f"GET /governance/ownership: {len(data['by_team'])} teams, {len(data['by_person'])} people")
    
    def test_governance_ownership_team_structure(self):
        """by_team entries have correct structure"""
        response = requests.get(f"{BASE_URL}/api/cve/governance/ownership")
        data = response.json()
        
        for entry in data["by_team"]:
            assert "team" in entry
            assert "count" in entry
            assert isinstance(entry["count"], int)
        print(f"by_team structure verified: team + count fields present")
    
    def test_governance_ownership_person_structure(self):
        """by_person entries have correct structure"""
        response = requests.get(f"{BASE_URL}/api/cve/governance/ownership")
        data = response.json()
        
        for entry in data["by_person"]:
            assert "person" in entry
            assert "count" in entry
            assert isinstance(entry["count"], int)
        print(f"by_person structure verified: person + count fields present")


class TestUnassignedCVECount:
    """Test unassigned CVE counting"""
    
    def test_unassigned_count_matches_unassigned_list(self):
        """unassigned_open_cves count matches total from /unassigned endpoint"""
        owners_response = requests.get(f"{BASE_URL}/api/cve/owners")
        owners_data = owners_response.json()
        
        unassigned_response = requests.get(f"{BASE_URL}/api/cve/unassigned?limit=200")
        unassigned_data = unassigned_response.json()
        
        assert owners_data["unassigned_open_cves"] == unassigned_data["total"], \
            f"Mismatch: /owners reports {owners_data['unassigned_open_cves']} but /unassigned has {unassigned_data['total']}"
        print(f"Unassigned count consistent: {owners_data['unassigned_open_cves']} unassigned open CVEs")
    
    def test_unassigned_only_includes_open_cves(self):
        """Unassigned list only includes CVEs with open status"""
        response = requests.get(f"{BASE_URL}/api/cve/unassigned?limit=100")
        data = response.json()
        
        open_statuses = ["detected", "triaged", "in_progress"]
        for cve in data["items"]:
            assert cve["status"] in open_statuses, f"CVE {cve['cve_id']} has status {cve['status']} which is not open"
        print(f"All {len(data['items'])} unassigned CVEs have open status (detected/triaged/in_progress)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
