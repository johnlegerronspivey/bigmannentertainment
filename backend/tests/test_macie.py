"""
AWS Macie PII Detection - Backend API Tests
Tests for automated sensitive data discovery and PII detection endpoints
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestMacieHealth:
    """Health and Dashboard endpoint tests"""
    
    def test_health_endpoint(self):
        """Test Macie health check endpoint"""
        response = requests.get(f"{BASE_URL}/api/macie/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "AWS Macie PII Detection"
        assert "features" in data
        assert len(data["features"]) > 0
        print(f"✅ Health check passed - Features: {data['features']}")
    
    def test_dashboard_stats(self):
        """Test dashboard statistics endpoint"""
        response = requests.get(f"{BASE_URL}/api/macie/dashboard")
        assert response.status_code == 200
        data = response.json()
        # Verify all expected stats fields
        assert "total_findings" in data
        assert "high_severity_findings" in data
        assert "medium_severity_findings" in data
        assert "low_severity_findings" in data
        assert "total_jobs" in data
        assert "running_jobs" in data
        assert "completed_jobs" in data
        assert "monitored_buckets" in data
        assert "pii_types_detected" in data
        print(f"✅ Dashboard stats: {data['total_findings']} findings, {data['total_jobs']} jobs, {data['monitored_buckets']} buckets")
    
    def test_finding_statistics(self):
        """Test finding statistics aggregation endpoint"""
        response = requests.get(f"{BASE_URL}/api/macie/statistics")
        assert response.status_code == 200
        data = response.json()
        assert "total_findings" in data
        assert "findings_by_severity" in data
        assert "findings_by_type" in data
        assert "findings_by_bucket" in data
        print(f"✅ Finding statistics: {data['total_findings']} total, by severity: {data['findings_by_severity']}")


class TestMacieFindings:
    """Findings endpoint tests"""
    
    def test_list_findings(self):
        """Test listing all findings"""
        response = requests.get(f"{BASE_URL}/api/macie/findings")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "findings" in data
        assert "total" in data
        assert isinstance(data["findings"], list)
        print(f"✅ Listed {len(data['findings'])} findings (total: {data['total']})")
    
    def test_filter_findings_by_severity_high(self):
        """Test filtering findings by high severity"""
        response = requests.get(f"{BASE_URL}/api/macie/findings?severity=High")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        # All returned findings should be High severity
        for finding in data["findings"]:
            assert finding["severity"] == "High"
        print(f"✅ High severity filter: {len(data['findings'])} findings")
    
    def test_filter_findings_by_severity_medium(self):
        """Test filtering findings by medium severity"""
        response = requests.get(f"{BASE_URL}/api/macie/findings?severity=Medium")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        for finding in data["findings"]:
            assert finding["severity"] == "Medium"
        print(f"✅ Medium severity filter: {len(data['findings'])} findings")
    
    def test_filter_findings_by_acknowledged(self):
        """Test filtering findings by acknowledgement status"""
        response = requests.get(f"{BASE_URL}/api/macie/findings?acknowledged=false")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        for finding in data["findings"]:
            assert finding["is_acknowledged"] == False
        print(f"✅ Unacknowledged filter: {len(data['findings'])} findings")
    
    def test_acknowledge_finding(self):
        """Test acknowledging a finding"""
        # First get a finding to acknowledge
        response = requests.get(f"{BASE_URL}/api/macie/findings?acknowledged=false&limit=1")
        assert response.status_code == 200
        data = response.json()
        
        if len(data["findings"]) > 0:
            finding_id = data["findings"][0]["id"]
            # Acknowledge the finding
            ack_response = requests.post(f"{BASE_URL}/api/macie/findings/{finding_id}/acknowledge")
            assert ack_response.status_code == 200
            ack_data = ack_response.json()
            assert ack_data["is_acknowledged"] == True
            assert ack_data["acknowledged_by"] is not None
            print(f"✅ Acknowledged finding {finding_id}")
        else:
            print("⚠️ No unacknowledged findings to test")
    
    def test_get_nonexistent_finding(self):
        """Test getting a non-existent finding returns 404"""
        response = requests.get(f"{BASE_URL}/api/macie/findings/nonexistent-id-12345")
        assert response.status_code == 404
        print("✅ Non-existent finding returns 404")


class TestMacieJobs:
    """Classification Jobs endpoint tests"""
    
    def test_list_jobs(self):
        """Test listing all classification jobs"""
        response = requests.get(f"{BASE_URL}/api/macie/jobs")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "jobs" in data
        assert "total" in data
        print(f"✅ Listed {len(data['jobs'])} jobs (total: {data['total']})")
    
    def test_filter_jobs_by_status_running(self):
        """Test filtering jobs by RUNNING status"""
        response = requests.get(f"{BASE_URL}/api/macie/jobs?status=RUNNING")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        for job in data["jobs"]:
            assert job["status"] == "RUNNING"
        print(f"✅ Running jobs filter: {len(data['jobs'])} jobs")
    
    def test_filter_jobs_by_status_complete(self):
        """Test filtering jobs by COMPLETE status"""
        response = requests.get(f"{BASE_URL}/api/macie/jobs?status=COMPLETE")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        for job in data["jobs"]:
            assert job["status"] == "COMPLETE"
        print(f"✅ Complete jobs filter: {len(data['jobs'])} jobs")
    
    def test_create_classification_job(self):
        """Test creating a new classification job"""
        job_data = {
            "name": "TEST_Security_Scan",
            "description": "Test scan for PII detection",
            "bucket_names": ["bme-artist-contracts"],
            "job_type": "ONE_TIME",
            "sampling_percentage": 50
        }
        response = requests.post(f"{BASE_URL}/api/macie/jobs", json=job_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == job_data["name"]
        assert data["description"] == job_data["description"]
        assert data["status"] == "RUNNING"
        assert data["sampling_percentage"] == 50
        assert "bme-artist-contracts" in data["buckets"]
        print(f"✅ Created job: {data['name']} (ID: {data['id']})")
        return data["id"]
    
    def test_get_nonexistent_job(self):
        """Test getting a non-existent job returns 404"""
        response = requests.get(f"{BASE_URL}/api/macie/jobs/nonexistent-job-12345")
        assert response.status_code == 404
        print("✅ Non-existent job returns 404")


class TestMacieCustomIdentifiers:
    """Custom Data Identifiers endpoint tests"""
    
    def test_list_custom_identifiers(self):
        """Test listing all custom identifiers"""
        response = requests.get(f"{BASE_URL}/api/macie/custom-identifiers")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Listed {len(data)} custom identifiers")
    
    def test_create_custom_identifier(self):
        """Test creating a new custom identifier"""
        identifier_data = {
            "name": "TEST_Internal_ID",
            "description": "Test identifier for internal IDs",
            "regex": r"TEST-[A-Z0-9]{8}",
            "keywords": ["test", "internal"],
            "ignore_words": ["example"],
            "maximum_match_distance": 30
        }
        response = requests.post(f"{BASE_URL}/api/macie/custom-identifiers", json=identifier_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == identifier_data["name"]
        assert data["description"] == identifier_data["description"]
        assert data["regex"] == identifier_data["regex"]
        assert data["is_active"] == True
        print(f"✅ Created identifier: {data['name']} (ID: {data['id']})")
        return data["id"]
    
    def test_get_custom_identifier(self):
        """Test getting a specific custom identifier"""
        # First create one
        identifier_data = {
            "name": "TEST_Get_Identifier",
            "description": "Test for get operation",
            "regex": r"GET-[0-9]{6}"
        }
        create_response = requests.post(f"{BASE_URL}/api/macie/custom-identifiers", json=identifier_data)
        assert create_response.status_code == 200
        created = create_response.json()
        
        # Then get it
        get_response = requests.get(f"{BASE_URL}/api/macie/custom-identifiers/{created['id']}")
        assert get_response.status_code == 200
        fetched = get_response.json()
        assert fetched["id"] == created["id"]
        assert fetched["name"] == identifier_data["name"]
        print(f"✅ Retrieved identifier: {fetched['name']}")
    
    def test_delete_custom_identifier(self):
        """Test deleting a custom identifier"""
        # First create one
        identifier_data = {
            "name": "TEST_Delete_Identifier",
            "description": "Test for delete operation",
            "regex": r"DEL-[0-9]{4}"
        }
        create_response = requests.post(f"{BASE_URL}/api/macie/custom-identifiers", json=identifier_data)
        assert create_response.status_code == 200
        created = create_response.json()
        
        # Delete it
        delete_response = requests.delete(f"{BASE_URL}/api/macie/custom-identifiers/{created['id']}")
        assert delete_response.status_code == 200
        delete_data = delete_response.json()
        assert delete_data["success"] == True
        
        # Verify it's gone
        get_response = requests.get(f"{BASE_URL}/api/macie/custom-identifiers/{created['id']}")
        assert get_response.status_code == 404
        print(f"✅ Deleted identifier: {created['name']}")
    
    def test_get_nonexistent_identifier(self):
        """Test getting a non-existent identifier returns 404"""
        response = requests.get(f"{BASE_URL}/api/macie/custom-identifiers/nonexistent-id-12345")
        assert response.status_code == 404
        print("✅ Non-existent identifier returns 404")


class TestMacieBuckets:
    """S3 Buckets endpoint tests"""
    
    def test_list_monitored_buckets(self):
        """Test listing all monitored S3 buckets"""
        response = requests.get(f"{BASE_URL}/api/macie/buckets")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Verify bucket structure
        if len(data) > 0:
            bucket = data[0]
            assert "name" in bucket
            assert "region" in bucket
            assert "is_monitored" in bucket
            assert "findings_count" in bucket
        print(f"✅ Listed {len(data)} monitored buckets")
    
    def test_bucket_has_findings_count(self):
        """Test that buckets include findings count"""
        response = requests.get(f"{BASE_URL}/api/macie/buckets")
        assert response.status_code == 200
        data = response.json()
        for bucket in data:
            assert "findings_count" in bucket
            assert isinstance(bucket["findings_count"], int)
        print("✅ All buckets have findings_count field")


class TestMacieReferenceEndpoints:
    """Reference data endpoint tests"""
    
    def test_pii_types_endpoint(self):
        """Test PII types reference endpoint"""
        response = requests.get(f"{BASE_URL}/api/macie/pii-types")
        assert response.status_code == 200
        data = response.json()
        assert "pii_types" in data
        assert len(data["pii_types"]) > 0
        # Verify structure
        pii_type = data["pii_types"][0]
        assert "id" in pii_type
        assert "name" in pii_type
        assert "category" in pii_type
        assert "risk" in pii_type
        print(f"✅ PII types: {len(data['pii_types'])} types available")
    
    def test_severity_levels_endpoint(self):
        """Test severity levels reference endpoint"""
        response = requests.get(f"{BASE_URL}/api/macie/severity-levels")
        assert response.status_code == 200
        data = response.json()
        assert "severity_levels" in data
        assert len(data["severity_levels"]) == 3  # Low, Medium, High
        # Verify structure
        for level in data["severity_levels"]:
            assert "id" in level
            assert "name" in level
            assert "score_range" in level
            assert "description" in level
            assert "color" in level
            assert "action" in level
        print(f"✅ Severity levels: {[l['name'] for l in data['severity_levels']]}")


class TestMacieDataIntegrity:
    """Data integrity and persistence tests"""
    
    def test_create_job_and_verify(self):
        """Test creating a job and verifying via GET"""
        job_data = {
            "name": "TEST_Verify_Job",
            "description": "Test job for verification",
            "bucket_names": ["bme-hr-records", "bme-marketing"],
            "job_type": "ONE_TIME",
            "sampling_percentage": 75
        }
        # Create
        create_response = requests.post(f"{BASE_URL}/api/macie/jobs", json=job_data)
        assert create_response.status_code == 200
        created = create_response.json()
        
        # Verify via GET
        get_response = requests.get(f"{BASE_URL}/api/macie/jobs/{created['id']}")
        assert get_response.status_code == 200
        fetched = get_response.json()
        assert fetched["name"] == job_data["name"]
        assert fetched["description"] == job_data["description"]
        assert fetched["sampling_percentage"] == 75
        assert "bme-hr-records" in fetched["buckets"]
        assert "bme-marketing" in fetched["buckets"]
        print(f"✅ Job created and verified: {fetched['name']}")
    
    def test_create_identifier_and_verify(self):
        """Test creating an identifier and verifying via GET"""
        identifier_data = {
            "name": "TEST_Verify_Identifier",
            "description": "Test identifier for verification",
            "regex": r"VER-[A-Z]{4}-[0-9]{4}",
            "keywords": ["verify", "test"],
            "maximum_match_distance": 100
        }
        # Create
        create_response = requests.post(f"{BASE_URL}/api/macie/custom-identifiers", json=identifier_data)
        assert create_response.status_code == 200
        created = create_response.json()
        
        # Verify via GET
        get_response = requests.get(f"{BASE_URL}/api/macie/custom-identifiers/{created['id']}")
        assert get_response.status_code == 200
        fetched = get_response.json()
        assert fetched["name"] == identifier_data["name"]
        assert fetched["regex"] == identifier_data["regex"]
        assert fetched["maximum_match_distance"] == 100
        assert "verify" in fetched["keywords"]
        print(f"✅ Identifier created and verified: {fetched['name']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
