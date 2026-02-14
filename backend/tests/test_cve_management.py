"""
CVE Management API Tests - Phase 1: CVE Brain & Core Dashboard
Tests all CRUD operations, SBOM, Policies, Audit Trail
"""

import pytest
import requests
import os
import uuid

# Use the public backend URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://dep-guardian.preview.emergentagent.com')
API = f"{BASE_URL}/api/cve"


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


class TestCVEHealth:
    """Health check endpoint tests"""

    def test_health_check(self, api_client):
        """GET /api/cve/health - returns healthy status"""
        response = api_client.get(f"{API}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "CVE Management Platform"
        print(f"PASS: Health check returned: {data}")


class TestCVEDashboard:
    """Dashboard endpoint tests"""

    def test_dashboard_returns_stats(self, api_client):
        """GET /api/cve/dashboard - returns dashboard stats with severity breakdown"""
        response = api_client.get(f"{API}/dashboard")
        assert response.status_code == 200
        data = response.json()
        
        # Verify required fields exist
        assert "total_cves" in data
        assert "open_cves" in data
        assert "fixed_cves" in data
        assert "verified_cves" in data
        assert "dismissed_cves" in data
        assert "severity_breakdown" in data
        assert "total_services" in data
        assert "total_sboms" in data
        assert "recent_cves" in data
        assert "recent_activity" in data
        
        # Verify severity breakdown has all levels
        sev = data["severity_breakdown"]
        assert "critical" in sev
        assert "high" in sev
        assert "medium" in sev
        assert "low" in sev
        assert "info" in sev
        
        print(f"PASS: Dashboard returned total_cves={data['total_cves']}, open={data['open_cves']}, fixed={data['fixed_cves']}")


class TestCVESeed:
    """Seed data endpoint tests"""

    def test_seed_data(self, api_client):
        """POST /api/cve/seed - Seeds sample data (4 services, 5 CVEs)"""
        response = api_client.post(f"{API}/seed")
        assert response.status_code == 200
        data = response.json()
        
        # Either "Data already exists" or "Sample data seeded"
        assert "message" in data
        if "already" in data["message"].lower():
            print(f"PASS: Seed returned - data already exists, cves={data.get('cves', 'N/A')}")
        else:
            assert data.get("services") == 4 or data.get("cves") == 5
            print(f"PASS: Seed created services={data.get('services')}, cves={data.get('cves')}")


class TestCVEEntries:
    """CVE Entries CRUD tests"""

    @pytest.fixture(scope="class")
    def test_cve_id(self):
        """Unique test CVE ID for this test class"""
        return f"CVE-TEST-{uuid.uuid4().hex[:8].upper()}"

    def test_list_cves_returns_items(self, api_client):
        """GET /api/cve/entries - lists CVEs with pagination"""
        response = api_client.get(f"{API}/entries")
        assert response.status_code == 200
        data = response.json()
        
        assert "items" in data
        assert "total" in data
        assert "limit" in data
        assert "skip" in data
        assert isinstance(data["items"], list)
        
        print(f"PASS: List CVEs returned total={data['total']}, items_count={len(data['items'])}")

    def test_list_cves_with_status_filter(self, api_client):
        """GET /api/cve/entries?status=detected - filters by status"""
        response = api_client.get(f"{API}/entries?status=detected")
        assert response.status_code == 200
        data = response.json()
        
        assert "items" in data
        # If items exist, verify they have detected status
        for item in data["items"]:
            assert item["status"] == "detected"
        
        print(f"PASS: Status filter returned {len(data['items'])} detected CVEs")

    def test_list_cves_with_severity_filter(self, api_client):
        """GET /api/cve/entries?severity=critical - filters by severity"""
        response = api_client.get(f"{API}/entries?severity=critical")
        assert response.status_code == 200
        data = response.json()
        
        assert "items" in data
        # If items exist, verify they have critical severity
        for item in data["items"]:
            assert item["severity"] == "critical"
        
        print(f"PASS: Severity filter returned {len(data['items'])} critical CVEs")

    def test_list_cves_with_search_filter(self, api_client):
        """GET /api/cve/entries?search=CVE - filters by search term"""
        response = api_client.get(f"{API}/entries?search=CVE")
        assert response.status_code == 200
        data = response.json()
        
        assert "items" in data
        print(f"PASS: Search filter returned {len(data['items'])} CVEs matching 'CVE'")

    def test_create_cve_entry(self, api_client, test_cve_id):
        """POST /api/cve/entries - creates a new CVE entry"""
        cve_data = {
            "cve_id": test_cve_id,
            "title": "TEST CVE for Automated Testing",
            "description": "This is an automated test CVE entry",
            "severity": "high",
            "cvss_score": 7.5,
            "affected_package": "test-package",
            "affected_version": "1.0.0",
            "fixed_version": "1.0.1",
            "affected_services": ["bigmann-backend"],
            "source": "automated_test"
        }
        
        response = api_client.post(f"{API}/entries", json=cve_data)
        assert response.status_code == 200
        data = response.json()
        
        assert data["cve_id"] == test_cve_id
        assert data["title"] == "TEST CVE for Automated Testing"
        assert data["severity"] == "high"
        assert data["status"] == "detected"  # Default status
        assert "id" in data
        
        print(f"PASS: Created CVE {data['cve_id']} with id={data['id']}")
        return data

    def test_get_cve_entry_by_id(self, api_client, test_cve_id):
        """GET /api/cve/entries/{id} - gets CVE details by id"""
        # First find the CVE we created
        response = api_client.get(f"{API}/entries?search={test_cve_id}")
        assert response.status_code == 200
        items = response.json()["items"]
        
        if len(items) > 0:
            cve_entry = items[0]
            cve_uuid = cve_entry["id"]
            
            # Get by UUID
            response = api_client.get(f"{API}/entries/{cve_uuid}")
            assert response.status_code == 200
            data = response.json()
            assert data["cve_id"] == test_cve_id
            print(f"PASS: Got CVE by id={cve_uuid}, cve_id={data['cve_id']}")
        else:
            # Try to get by cve_id directly
            response = api_client.get(f"{API}/entries/{test_cve_id}")
            assert response.status_code == 200
            print(f"PASS: Got CVE by cve_id={test_cve_id}")

    def test_update_cve_status_to_triaged(self, api_client, test_cve_id):
        """PUT /api/cve/entries/{id}/status - changes CVE lifecycle status"""
        # Find the test CVE
        response = api_client.get(f"{API}/entries?search={test_cve_id}")
        items = response.json().get("items", [])
        
        if len(items) > 0:
            cve_uuid = items[0]["id"]
            
            # Update status to triaged
            status_update = {"status": "triaged", "notes": "Triaged during automated testing"}
            response = api_client.put(f"{API}/entries/{cve_uuid}/status", json=status_update)
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "triaged"
            assert data["triaged_at"] is not None
            
            print(f"PASS: Updated CVE status to triaged, triaged_at={data['triaged_at']}")
        else:
            pytest.skip(f"Test CVE {test_cve_id} not found for status update test")

    def test_update_cve_status_to_in_progress(self, api_client, test_cve_id):
        """PUT /api/cve/entries/{id}/status - status to in_progress"""
        response = api_client.get(f"{API}/entries?search={test_cve_id}")
        items = response.json().get("items", [])
        
        if len(items) > 0:
            cve_uuid = items[0]["id"]
            status_update = {"status": "in_progress"}
            response = api_client.put(f"{API}/entries/{cve_uuid}/status", json=status_update)
            assert response.status_code == 200
            assert response.json()["status"] == "in_progress"
            print(f"PASS: Updated CVE status to in_progress")
        else:
            pytest.skip(f"Test CVE {test_cve_id} not found")

    def test_update_cve_status_to_fixed(self, api_client, test_cve_id):
        """PUT /api/cve/entries/{id}/status - status to fixed"""
        response = api_client.get(f"{API}/entries?search={test_cve_id}")
        items = response.json().get("items", [])
        
        if len(items) > 0:
            cve_uuid = items[0]["id"]
            status_update = {"status": "fixed"}
            response = api_client.put(f"{API}/entries/{cve_uuid}/status", json=status_update)
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "fixed"
            assert data["fixed_at"] is not None
            print(f"PASS: Updated CVE status to fixed, fixed_at={data['fixed_at']}")
        else:
            pytest.skip(f"Test CVE {test_cve_id} not found")

    def test_update_cve_status_to_verified(self, api_client, test_cve_id):
        """PUT /api/cve/entries/{id}/status - status to verified"""
        response = api_client.get(f"{API}/entries?search={test_cve_id}")
        items = response.json().get("items", [])
        
        if len(items) > 0:
            cve_uuid = items[0]["id"]
            status_update = {"status": "verified"}
            response = api_client.put(f"{API}/entries/{cve_uuid}/status", json=status_update)
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "verified"
            assert data["verified_at"] is not None
            print(f"PASS: Updated CVE status to verified, verified_at={data['verified_at']}")
        else:
            pytest.skip(f"Test CVE {test_cve_id} not found")


class TestCVEServices:
    """Service Registry tests"""

    @pytest.fixture(scope="class")
    def test_service_name(self):
        """Unique test service name"""
        return f"TEST-service-{uuid.uuid4().hex[:6]}"

    def test_list_services(self, api_client):
        """GET /api/cve/services - lists services with open_cves count"""
        response = api_client.get(f"{API}/services")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        # If services exist, verify they have open_cves field
        for service in data:
            assert "name" in service
            assert "open_cves" in service
            assert "id" in service
        
        print(f"PASS: Listed {len(data)} services")

    def test_create_service(self, api_client, test_service_name):
        """POST /api/cve/services - creates a new service"""
        service_data = {
            "name": test_service_name,
            "description": "Automated test service",
            "repo_url": "https://github.com/test/repo",
            "owner": "Test Owner",
            "team": "Test Team",
            "environment": "development",
            "criticality": "low",
            "tech_stack": ["Python", "FastAPI", "MongoDB"]
        }
        
        response = api_client.post(f"{API}/services", json=service_data)
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == test_service_name
        assert data["description"] == "Automated test service"
        assert "id" in data
        
        print(f"PASS: Created service {data['name']} with id={data['id']}")
        return data

    def test_delete_service(self, api_client, test_service_name):
        """DELETE /api/cve/services/{id} - deletes a service"""
        # First find the test service
        response = api_client.get(f"{API}/services")
        services = response.json()
        
        test_service = next((s for s in services if s["name"] == test_service_name), None)
        
        if test_service:
            service_id = test_service["id"]
            response = api_client.delete(f"{API}/services/{service_id}")
            assert response.status_code == 200
            assert response.json()["deleted"] == True
            
            # Verify deletion
            response = api_client.get(f"{API}/services/{service_id}")
            assert response.status_code == 404
            
            print(f"PASS: Deleted service {test_service_name}")
        else:
            pytest.skip(f"Test service {test_service_name} not found for deletion")


class TestCVESBOM:
    """SBOM Generation and Management tests"""

    def test_generate_sbom(self, api_client):
        """POST /api/cve/sbom/generate - generates SBOM with frontend/backend components"""
        response = api_client.post(f"{API}/sbom/generate")
        assert response.status_code == 200
        data = response.json()
        
        assert "id" in data
        assert "service_name" in data
        assert "component_summary" in data
        assert data["component_summary"]["frontend"] >= 0
        assert data["component_summary"]["backend"] >= 0
        assert data["component_summary"]["total"] >= 0
        
        print(f"PASS: Generated SBOM with id={data['id']}, total_components={data['component_summary']['total']}")
        return data

    def test_list_sboms(self, api_client):
        """GET /api/cve/sbom/list - lists generated SBOMs"""
        response = api_client.get(f"{API}/sbom/list")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        for sbom in data:
            assert "id" in sbom
            assert "service_name" in sbom
            assert "generated_at" in sbom
        
        print(f"PASS: Listed {len(data)} SBOMs")
        return data

    def test_get_sbom_by_id(self, api_client):
        """GET /api/cve/sbom/{id} - gets full SBOM with component details"""
        # First list SBOMs to get an ID
        list_response = api_client.get(f"{API}/sbom/list")
        sboms = list_response.json()
        
        if len(sboms) > 0:
            sbom_id = sboms[0]["id"]
            response = api_client.get(f"{API}/sbom/{sbom_id}")
            assert response.status_code == 200
            data = response.json()
            
            assert data["id"] == sbom_id
            assert "components" in data
            assert isinstance(data["components"], list)
            
            print(f"PASS: Got SBOM {sbom_id} with {len(data['components'])} components")
        else:
            pytest.skip("No SBOMs found to test get by ID")


class TestCVEPolicies:
    """Severity Policies tests"""

    def test_get_policies(self, api_client):
        """GET /api/cve/policies - gets severity policies"""
        response = api_client.get(f"{API}/policies")
        assert response.status_code == 200
        data = response.json()
        
        # Verify all severity levels exist
        assert "critical" in data
        assert "high" in data
        assert "medium" in data
        assert "low" in data
        assert "info" in data
        
        # Verify policy structure
        assert "sla_hours" in data["critical"]
        assert "auto_block_deploy" in data["critical"]
        
        print(f"PASS: Got policies, critical_sla={data['critical']['sla_hours']}h")

    def test_update_policies(self, api_client):
        """PUT /api/cve/policies - updates severity policies"""
        # First get current policies
        current = api_client.get(f"{API}/policies").json()
        
        # Modify a value
        new_policies = current.copy()
        new_policies["critical"]["sla_hours"] = 12  # Change from 24 to 12
        
        response = api_client.put(f"{API}/policies", json={"policies": new_policies})
        assert response.status_code == 200
        data = response.json()
        
        assert data["critical"]["sla_hours"] == 12
        
        # Restore original
        current["critical"]["sla_hours"] = 24
        api_client.put(f"{API}/policies", json={"policies": current})
        
        print(f"PASS: Updated and restored policies successfully")


class TestCVEAuditTrail:
    """Audit Trail tests"""

    def test_get_audit_trail(self, api_client):
        """GET /api/cve/audit-trail - gets audit trail with filters"""
        response = api_client.get(f"{API}/audit-trail")
        assert response.status_code == 200
        data = response.json()
        
        assert "items" in data
        assert "total" in data
        assert isinstance(data["items"], list)
        
        # Verify audit entry structure if items exist
        for item in data["items"][:5]:  # Check first 5
            assert "id" in item
            assert "action" in item
            assert "target_id" in item
            assert "message" in item
            assert "timestamp" in item
        
        print(f"PASS: Got audit trail with {data['total']} entries")

    def test_get_audit_trail_with_action_filter(self, api_client):
        """GET /api/cve/audit-trail?action=cve_created - filters by action"""
        response = api_client.get(f"{API}/audit-trail?action=cve_created")
        assert response.status_code == 200
        data = response.json()
        
        assert "items" in data
        for item in data["items"]:
            assert item["action"] == "cve_created"
        
        print(f"PASS: Filtered audit trail by cve_created, got {len(data['items'])} entries")

    def test_get_audit_trail_with_limit(self, api_client):
        """GET /api/cve/audit-trail?limit=10 - respects limit"""
        response = api_client.get(f"{API}/audit-trail?limit=10")
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["items"]) <= 10
        print(f"PASS: Audit trail with limit=10 returned {len(data['items'])} entries")


# Cleanup fixture to run after all tests
@pytest.fixture(scope="module", autouse=True)
def cleanup_test_data(api_client):
    """Cleanup TEST_ prefixed CVE data after test module completes"""
    yield
    # Teardown: Delete test CVEs and services
    try:
        # Clean up test CVEs
        response = api_client.get(f"{API}/entries?search=CVE-TEST")
        if response.status_code == 200:
            items = response.json().get("items", [])
            for item in items:
                # Try to delete via status change to dismissed (no delete endpoint for CVEs)
                api_client.put(f"{API}/entries/{item['id']}/status", json={"status": "dismissed"})
                print(f"Cleanup: Dismissed test CVE {item['cve_id']}")
        
        # Clean up test services
        response = api_client.get(f"{API}/services")
        if response.status_code == 200:
            services = response.json()
            for service in services:
                if service["name"].startswith("TEST-"):
                    api_client.delete(f"{API}/services/{service['id']}")
                    print(f"Cleanup: Deleted test service {service['name']}")
    except Exception as e:
        print(f"Cleanup warning: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
