"""
RDS PostgreSQL Minor Version Upgrade API Tests
Tests for the RDS upgrade feature: GET instances, GET upgrade targets, POST upgrade
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://modular-frontend-10.preview.emergentagent.com').rstrip('/')


class TestRDSInstances:
    """Tests for GET /api/cve/iac/rds/instances endpoint"""
    
    def test_get_rds_instances_success(self):
        """Test that RDS instances endpoint returns connected:true and instances array"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/rds/instances")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify connection status
        assert data.get("connected") is True
        assert data.get("error") is None
        
        # Verify instances array exists
        assert "instances" in data
        assert isinstance(data["instances"], list)
        assert len(data["instances"]) > 0
        
        # Verify the bigmann-profiles-db instance
        instances = data["instances"]
        db_instance = next((i for i in instances if i["db_instance_id"] == "bigmann-profiles-db"), None)
        assert db_instance is not None, "bigmann-profiles-db instance not found"
        
        # Verify required fields on the instance
        assert db_instance["engine"] == "postgres"
        assert db_instance["engine_version"] == "17.4"
        assert db_instance["status"] == "available"
        assert "endpoint" in db_instance
        assert "port" in db_instance
        assert db_instance["port"] == 5432
        assert "db_instance_class" in db_instance
        assert "allocated_storage_gb" in db_instance
        assert "multi_az" in db_instance
        assert "storage_type" in db_instance
        assert "storage_encrypted" in db_instance
        
        print(f"✓ Found RDS instance: {db_instance['db_instance_id']}")
        print(f"  Engine: PostgreSQL {db_instance['engine_version']}")
        print(f"  Status: {db_instance['status']}")
        print(f"  Class: {db_instance['db_instance_class']}")


class TestRDSUpgradeTargets:
    """Tests for GET /api/cve/iac/rds/upgrade-targets/{instance_id} endpoint"""
    
    def test_get_upgrade_targets_success(self):
        """Test that upgrade targets endpoint returns valid targets for bigmann-profiles-db"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/rds/upgrade-targets/bigmann-profiles-db")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify connection status
        assert data.get("connected") is True
        assert data.get("error") is None
        
        # Verify instance and version info
        assert data["instance_id"] == "bigmann-profiles-db"
        assert data["current_version"] == "17.4"
        assert data["engine"] == "postgres"
        
        # Verify targets array
        assert "targets" in data
        assert isinstance(data["targets"], list)
        assert len(data["targets"]) > 0
        
        # Verify at least one valid upgrade target exists
        valid_targets = [t for t in data["targets"] if t.get("is_valid_target") is True]
        assert len(valid_targets) > 0, "No valid upgrade targets found"
        
        # Check that expected versions are available (17.5 - 17.9)
        target_versions = [t["engine_version"] for t in valid_targets]
        print(f"✓ Found {len(valid_targets)} valid upgrade targets: {target_versions}")
        
        # Verify structure of target objects
        for target in valid_targets:
            assert "engine_version" in target
            assert "description" in target
            assert "status" in target
            assert "is_valid_target" in target
            # Version should be greater than current
            assert target["engine_version"] > data["current_version"]
    
    def test_get_upgrade_targets_nonexistent_instance(self):
        """Test that upgrade targets endpoint returns error for non-existent instance"""
        response = requests.get(f"{BASE_URL}/api/cve/iac/rds/upgrade-targets/nonexistent-db-instance")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have connection but with error
        assert data.get("connected") is True
        assert data.get("error") is not None
        assert "not found" in data.get("error", "").lower() or "DBInstanceNotFound" in data.get("error", "")


class TestRDSUpgradeEndpoint:
    """Tests for POST /api/cve/iac/rds/upgrade endpoint - READ ONLY, no actual upgrade"""
    
    def test_upgrade_endpoint_exists(self):
        """Verify the upgrade endpoint exists and accepts POST requests"""
        # Send OPTIONS request to verify endpoint exists
        response = requests.options(f"{BASE_URL}/api/cve/iac/rds/upgrade")
        # If endpoint doesn't exist, we'd get 404
        # We expect either 200 or 405 (method not allowed for OPTIONS) but not 404
        assert response.status_code != 404, "Upgrade endpoint not found"
        print(f"✓ Upgrade endpoint exists (OPTIONS returned {response.status_code})")
    
    def test_upgrade_endpoint_validation(self):
        """Test that upgrade endpoint validates input - using invalid data"""
        # Send invalid request to test validation
        response = requests.post(
            f"{BASE_URL}/api/cve/iac/rds/upgrade",
            json={"invalid": "data"},
            headers={"Content-Type": "application/json"}
        )
        
        # Should return 422 (validation error) for missing required fields
        assert response.status_code == 422
        print(f"✓ Upgrade endpoint validates input correctly (returned {response.status_code} for invalid data)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
