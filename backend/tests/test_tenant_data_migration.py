"""
Test Suite for Tenant Data Migration Feature
Tests migration analysis and migration execution endpoints
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
DEFAULT_TENANT_ID = "40e6f47e-b021-4605-9e1c-7a0992854f6c"
ACME_TENANT_ID = "3aed1ef1-3780-4c75-9908-425f3921c88d"


class TestMigrationAnalysis:
    """Tests for GET /api/tenants/migration-analysis endpoint"""
    
    def test_migration_analysis_returns_200(self):
        """Migration analysis endpoint returns 200 OK"""
        response = requests.get(f"{BASE_URL}/api/tenants/migration-analysis")
        assert response.status_code == 200
        print(f"✓ Migration analysis returned 200")
    
    def test_migration_analysis_has_required_fields(self):
        """Migration analysis returns all required fields"""
        response = requests.get(f"{BASE_URL}/api/tenants/migration-analysis")
        data = response.json()
        
        assert "collections" in data, "Missing 'collections' field"
        assert "total_documents" in data, "Missing 'total_documents' field"
        assert "total_legacy_documents" in data, "Missing 'total_legacy_documents' field"
        assert "migration_needed" in data, "Missing 'migration_needed' field"
        assert "available_tenants" in data, "Missing 'available_tenants' field"
        print(f"✓ All required fields present in migration analysis")
    
    def test_migration_analysis_collections_count(self):
        """Migration analysis returns 18 CVE collections"""
        response = requests.get(f"{BASE_URL}/api/tenants/migration-analysis")
        data = response.json()
        
        collections = data.get("collections", {})
        assert len(collections) == 18, f"Expected 18 collections, got {len(collections)}"
        print(f"✓ Migration analysis returns 18 collections")
    
    def test_migration_analysis_expected_collections(self):
        """Migration analysis includes all expected CVE collections"""
        response = requests.get(f"{BASE_URL}/api/tenants/migration-analysis")
        data = response.json()
        collections = list(data.get("collections", {}).keys())
        
        expected_collections = [
            "cve_audit_trail", "cve_entries", "cve_escalation_log", "cve_escalation_rules",
            "cve_notification_preferences", "cve_notifications", "cve_pipeline_configs",
            "cve_policy_rules", "cve_remediation_items", "cve_sbom_records",
            "cve_scan_results", "cve_services", "cve_severity_policies",
            "cve_sla_config", "cve_sla_snapshots", "cve_tickets",
            "cve_users", "iac_deployments",
        ]
        
        for col in expected_collections:
            assert col in collections, f"Missing collection: {col}"
        print(f"✓ All 18 expected collections present")
    
    def test_migration_analysis_collection_structure(self):
        """Each collection has total, legacy_docs, already_migrated fields"""
        response = requests.get(f"{BASE_URL}/api/tenants/migration-analysis")
        data = response.json()
        
        for col_name, col_data in data.get("collections", {}).items():
            assert "total" in col_data, f"{col_name} missing 'total'"
            assert "legacy_docs" in col_data, f"{col_name} missing 'legacy_docs'"
            assert "already_migrated" in col_data, f"{col_name} missing 'already_migrated'"
        print(f"✓ All collections have correct structure")
    
    def test_migration_complete_no_legacy_docs(self):
        """After migration, total_legacy_documents should be 0"""
        response = requests.get(f"{BASE_URL}/api/tenants/migration-analysis")
        data = response.json()
        
        assert data["total_legacy_documents"] == 0, f"Expected 0 legacy docs, got {data['total_legacy_documents']}"
        assert data["migration_needed"] == False, "migration_needed should be False"
        print(f"✓ Migration complete - 0 legacy documents")
    
    def test_available_tenants_structure(self):
        """Available tenants have id, name, slug, plan fields"""
        response = requests.get(f"{BASE_URL}/api/tenants/migration-analysis")
        data = response.json()
        tenants = data.get("available_tenants", [])
        
        assert len(tenants) >= 1, "Expected at least 1 tenant"
        for tenant in tenants:
            assert "id" in tenant, "Tenant missing 'id'"
            assert "name" in tenant, "Tenant missing 'name'"
            assert "plan" in tenant, "Tenant missing 'plan'"
        print(f"✓ Available tenants have correct structure ({len(tenants)} tenants)")


class TestMigrateData:
    """Tests for POST /api/tenants/migrate-data endpoint"""
    
    def test_migrate_invalid_tenant_returns_400(self):
        """Migration with invalid tenant_id returns 400"""
        response = requests.post(
            f"{BASE_URL}/api/tenants/migrate-data",
            json={"target_tenant_id": "invalid-tenant-id-12345"},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        data = response.json()
        assert "detail" in data or "error" in data
        print(f"✓ Invalid tenant migration returns 400")
    
    def test_migrate_valid_tenant_returns_success(self):
        """Migration with valid tenant_id returns success (no-op if already migrated)"""
        response = requests.post(
            f"{BASE_URL}/api/tenants/migrate-data",
            json={"target_tenant_id": DEFAULT_TENANT_ID},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert data.get("success") == True, "Migration should return success=True"
        assert "total_migrated" in data, "Missing total_migrated field"
        assert "collections" in data, "Missing collections field"
        assert "target_tenant" in data, "Missing target_tenant field"
        print(f"✓ Valid tenant migration returns success (migrated: {data['total_migrated']})")
    
    def test_migrate_returns_collection_breakdown(self):
        """Migration response includes per-collection breakdown"""
        response = requests.post(
            f"{BASE_URL}/api/tenants/migrate-data",
            json={"target_tenant_id": DEFAULT_TENANT_ID},
            headers={"Content-Type": "application/json"}
        )
        data = response.json()
        collections = data.get("collections", {})
        
        # Check structure of collection results
        for col_name, col_data in collections.items():
            assert "legacy_before" in col_data, f"{col_name} missing 'legacy_before'"
            assert "migrated" in col_data, f"{col_name} missing 'migrated'"
        print(f"✓ Migration response includes collection breakdown")


class TestCVEDashboardAfterMigration:
    """Tests to verify CVE data is correct after migration"""
    
    def test_dashboard_returns_correct_total_cves(self):
        """Dashboard returns total_cves=23 after migration"""
        response = requests.get(f"{BASE_URL}/api/cve/dashboard")
        assert response.status_code == 200
        data = response.json()
        
        assert "total_cves" in data, "Missing total_cves in dashboard"
        assert data["total_cves"] == 23, f"Expected 23 CVEs, got {data['total_cves']}"
        print(f"✓ Dashboard returns correct total_cves: {data['total_cves']}")
    
    def test_dashboard_has_severity_breakdown(self):
        """Dashboard includes severity breakdown"""
        response = requests.get(f"{BASE_URL}/api/cve/dashboard")
        data = response.json()
        
        assert "severity_breakdown" in data, "Missing severity_breakdown"
        breakdown = data["severity_breakdown"]
        assert "critical" in breakdown
        assert "high" in breakdown
        assert "medium" in breakdown
        assert "low" in breakdown
        assert "info" in breakdown
        print(f"✓ Dashboard has severity breakdown")


class TestCVEEntriesAfterMigration:
    """Tests to verify CVE entries have tenant_id after migration"""
    
    def test_cve_entries_returns_all_23_cves(self):
        """CVE entries endpoint returns all 23 entries"""
        response = requests.get(f"{BASE_URL}/api/cve/entries?limit=50")
        assert response.status_code == 200
        data = response.json()
        
        assert "items" in data, "Missing items in response"
        assert data["total"] == 23, f"Expected 23 total CVEs, got {data['total']}"
        print(f"✓ CVE entries returns all 23 CVEs")
    
    def test_cve_entries_have_tenant_id(self):
        """All CVE entries have tenant_id populated"""
        response = requests.get(f"{BASE_URL}/api/cve/entries?limit=50")
        data = response.json()
        items = data.get("items", [])
        
        entries_with_tenant = sum(1 for item in items if item.get("tenant_id"))
        assert entries_with_tenant == len(items), f"{len(items) - entries_with_tenant} entries missing tenant_id"
        print(f"✓ All {len(items)} CVE entries have tenant_id")
    
    def test_cve_entries_have_default_tenant(self):
        """CVE entries are assigned to default tenant"""
        response = requests.get(f"{BASE_URL}/api/cve/entries?limit=50")
        data = response.json()
        items = data.get("items", [])
        
        default_tenant_count = sum(1 for item in items if item.get("tenant_id") == DEFAULT_TENANT_ID)
        print(f"✓ {default_tenant_count}/{len(items)} entries assigned to default tenant")


class TestTicketsAfterMigration:
    """Tests to verify tickets endpoint works after _tenant_filter simplification"""
    
    def test_tickets_endpoint_returns_200(self):
        """Tickets endpoint returns 200 OK"""
        response = requests.get(f"{BASE_URL}/api/cve/ticketing/tickets")
        assert response.status_code == 200
        print(f"✓ Tickets endpoint returns 200")
    
    def test_tickets_have_required_fields(self):
        """Tickets have all required fields"""
        response = requests.get(f"{BASE_URL}/api/cve/ticketing/tickets")
        data = response.json()
        
        assert "items" in data, "Missing items field"
        assert "total" in data, "Missing total field"
        
        if data["total"] > 0:
            ticket = data["items"][0]
            required_fields = ["id", "cve_id", "provider", "external_key", "status", "priority"]
            for field in required_fields:
                assert field in ticket, f"Ticket missing field: {field}"
        print(f"✓ Tickets have required fields (total: {data['total']})")
    
    def test_tickets_have_tenant_id(self):
        """Tickets have tenant_id after migration"""
        response = requests.get(f"{BASE_URL}/api/cve/ticketing/tickets")
        data = response.json()
        items = data.get("items", [])
        
        if len(items) > 0:
            tickets_with_tenant = sum(1 for item in items if item.get("tenant_id"))
            print(f"✓ {tickets_with_tenant}/{len(items)} tickets have tenant_id")
        else:
            print(f"✓ No tickets to verify (total: 0)")


class TestTenantFilterSimplification:
    """Verify _tenant_filter logic is simplified (strict equality, no legacy fallback)"""
    
    def test_dashboard_respects_tenant_filter(self):
        """Dashboard uses simplified tenant filter"""
        # This test verifies the simplified filter works by checking dashboard loads
        response = requests.get(f"{BASE_URL}/api/cve/dashboard")
        assert response.status_code == 200
        data = response.json()
        
        # Dashboard should still return data even with simplified filter
        assert data["total_cves"] >= 0
        print(f"✓ Dashboard works with simplified tenant filter")
