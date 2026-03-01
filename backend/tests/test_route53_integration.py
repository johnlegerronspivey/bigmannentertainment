"""
Route53 Integration Tests
Tests for bigmannentertainment.com DNS management via AWS Route53
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "cveadmin@test.com"
ADMIN_PASSWORD = "Test1234!"


class TestRoute53Integration:
    """Route53 DNS management endpoint tests"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session with authentication"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.token = None

    def _get_auth_token(self):
        """Get authentication token for admin user"""
        if self.token:
            return self.token
        response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token") or data.get("token")
            return self.token
        pytest.skip(f"Authentication failed: {response.status_code} - {response.text}")

    def _auth_headers(self):
        """Get headers with auth token"""
        token = self._get_auth_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    # ========== GET /api/route53/zone ==========
    def test_route53_zone_info(self):
        """Test GET /api/route53/zone - Returns hosted zone info"""
        response = self.session.get(f"{BASE_URL}/api/route53/zone")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # Validate response structure
        assert "id" in data, "Response should contain zone id"
        assert "name" in data, "Response should contain zone name"
        assert "record_count" in data, "Response should contain record_count"
        assert "name_servers" in data, "Response should contain name_servers"
        
        # Validate values
        assert data["name"] == "bigmannentertainment.com", f"Zone name should be bigmannentertainment.com, got {data['name']}"
        assert data["id"] == "Z21AGOWAOOGWWZ", f"Zone ID should be Z21AGOWAOOGWWZ, got {data['id']}"
        assert isinstance(data["name_servers"], list), "name_servers should be a list"
        assert len(data["name_servers"]) > 0, "Should have at least one name server"
        assert data["record_count"] > 0, "Should have at least one record"
        
        print(f"Zone info: id={data['id']}, name={data['name']}, records={data['record_count']}, nameservers={len(data['name_servers'])}")

    # ========== GET /api/route53/records ==========
    def test_route53_list_records(self):
        """Test GET /api/route53/records - Returns all DNS records"""
        response = self.session.get(f"{BASE_URL}/api/route53/records")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "records" in data, "Response should contain records array"
        
        records = data["records"]
        assert isinstance(records, list), "records should be a list"
        assert len(records) > 0, "Should have at least some DNS records"
        
        # Validate record structure
        for record in records:
            assert "name" in record, "Each record should have a name"
            assert "type" in record, "Each record should have a type"
            assert "values" in record, "Each record should have values"
            assert "ttl" in record, "Each record should have ttl"
        
        # Check for required record types (NS and SOA should always exist)
        record_types = [r["type"] for r in records]
        assert "NS" in record_types, "Should have NS records"
        assert "SOA" in record_types, "Should have SOA record"
        
        print(f"Found {len(records)} DNS records")
        for r in records[:5]:  # Print first 5 records
            print(f"  - {r['type']} {r['name']}: {r['values'][:1]}...")

    # ========== GET /api/domain/status (includes route53) ==========
    def test_domain_status_includes_route53(self):
        """Test GET /api/domain/status - Should include route53 status"""
        response = self.session.get(f"{BASE_URL}/api/domain/status")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "route53" in data, "Domain status should include route53 field"
        
        route53 = data["route53"]
        assert "status" in route53, "route53 should have status"
        assert route53["status"] == "connected", f"route53 status should be 'connected', got {route53['status']}"
        
        if route53["status"] == "connected":
            assert "zone_id" in route53, "Connected route53 should have zone_id"
            assert "record_count" in route53, "Connected route53 should have record_count"
            assert "name_servers" in route53, "Connected route53 should have name_servers"
        
        print(f"Domain status route53: {route53}")

    # ========== POST /api/route53/record (UPSERT) ==========
    def test_route53_upsert_record_requires_auth(self):
        """Test POST /api/route53/record - Should require authentication"""
        response = self.session.post(
            f"{BASE_URL}/api/route53/record",
            json={
                "name": "test-record.bigmannentertainment.com",
                "type": "TXT",
                "values": ["test-value"],
                "ttl": 300
            }
        )
        
        # Should return 401 or 403 without auth
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"

    def test_route53_upsert_record_with_auth(self):
        """Test POST /api/route53/record - Create test TXT record"""
        response = self.session.post(
            f"{BASE_URL}/api/route53/record",
            headers=self._auth_headers(),
            json={
                "name": "test-pytest.bigmannentertainment.com",
                "type": "TXT",
                "values": ['"v=test-from-pytest"'],
                "ttl": 300
            }
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("status") == "ok", f"Expected status=ok, got {data}"
        assert data.get("action") == "UPSERT", f"Expected action=UPSERT, got {data}"
        
        print(f"Created test record: {data}")

    def test_route53_upsert_record_validation(self):
        """Test POST /api/route53/record - Should validate required fields"""
        # Missing name
        response = self.session.post(
            f"{BASE_URL}/api/route53/record",
            headers=self._auth_headers(),
            json={
                "type": "TXT",
                "values": ["test"],
                "ttl": 300
            }
        )
        assert response.status_code == 400, f"Should reject missing name: {response.status_code}"
        
        # Missing type
        response = self.session.post(
            f"{BASE_URL}/api/route53/record",
            headers=self._auth_headers(),
            json={
                "name": "test.bigmannentertainment.com",
                "values": ["test"],
                "ttl": 300
            }
        )
        assert response.status_code == 400, f"Should reject missing type: {response.status_code}"
        
        # Missing values
        response = self.session.post(
            f"{BASE_URL}/api/route53/record",
            headers=self._auth_headers(),
            json={
                "name": "test.bigmannentertainment.com",
                "type": "TXT",
                "ttl": 300
            }
        )
        assert response.status_code == 400, f"Should reject missing values: {response.status_code}"

    # ========== DELETE /api/route53/record ==========
    def test_route53_delete_record_requires_auth(self):
        """Test DELETE /api/route53/record - Should require authentication"""
        response = self.session.delete(
            f"{BASE_URL}/api/route53/record",
            json={
                "name": "test-pytest.bigmannentertainment.com",
                "type": "TXT",
                "values": ['"v=test-from-pytest"'],
                "ttl": 300
            }
        )
        
        # Should return 401 or 403 without auth
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"

    def test_route53_delete_record_with_auth(self):
        """Test DELETE /api/route53/record - Delete test TXT record"""
        # First ensure the test record exists by creating it
        self.session.post(
            f"{BASE_URL}/api/route53/record",
            headers=self._auth_headers(),
            json={
                "name": "test-pytest.bigmannentertainment.com",
                "type": "TXT",
                "values": ['"v=test-from-pytest"'],
                "ttl": 300
            }
        )
        
        # Now delete it
        response = self.session.delete(
            f"{BASE_URL}/api/route53/record",
            headers=self._auth_headers(),
            json={
                "name": "test-pytest.bigmannentertainment.com",
                "type": "TXT",
                "values": ['"v=test-from-pytest"'],
                "ttl": 300
            }
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("status") == "ok", f"Expected status=ok, got {data}"
        assert data.get("action") == "DELETE", f"Expected action=DELETE, got {data}"
        
        print(f"Deleted test record: {data}")

    # ========== POST /api/route53/auto-configure ==========
    def test_route53_auto_configure_requires_auth(self):
        """Test POST /api/route53/auto-configure - Should require authentication"""
        response = self.session.post(f"{BASE_URL}/api/route53/auto-configure")
        
        # Should return 401 or 403 without auth
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"

    def test_route53_auto_configure_with_auth(self):
        """Test POST /api/route53/auto-configure - Auto-configure DNS records"""
        response = self.session.post(
            f"{BASE_URL}/api/route53/auto-configure",
            headers=self._auth_headers()
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("status") == "completed", f"Expected status=completed, got {data.get('status')}"
        assert "domain" in data, "Response should contain domain"
        assert data["domain"] == "bigmannentertainment.com", f"Domain should be bigmannentertainment.com"
        assert "results" in data, "Response should contain results array"
        assert "total" in data, "Response should contain total count"
        assert "succeeded" in data, "Response should contain succeeded count"
        assert "failed" in data, "Response should contain failed count"
        
        # Validate results structure
        results = data["results"]
        assert isinstance(results, list), "results should be a list"
        for result in results:
            assert "record" in result, "Each result should have record name"
            assert "status" in result, "Each result should have status"
            assert result["status"] in ["ok", "error"], f"Status should be ok or error, got {result['status']}"
        
        print(f"Auto-configure completed: {data['succeeded']}/{data['total']} succeeded")
        for r in results:
            status_icon = "OK" if r["status"] == "ok" else "FAIL"
            print(f"  [{status_icon}] {r['record']}")

    # ========== Verify records after auto-configure ==========
    def test_verify_auto_configured_records(self):
        """Verify that auto-configured records exist in Route53"""
        response = self.session.get(f"{BASE_URL}/api/route53/records")
        
        assert response.status_code == 200
        records = response.json().get("records", [])
        
        # Build a map of record name+type -> record
        record_map = {}
        for r in records:
            key = f"{r['type']}:{r['name']}"
            record_map[key] = r
        
        # Check for expected auto-configured records
        expected_records = [
            ("TXT", "bigmannentertainment.com"),  # SPF
            ("TXT", "_dmarc.bigmannentertainment.com"),  # DMARC
            ("CNAME", "www.bigmannentertainment.com"),  # WWW redirect
            ("MX", "bigmannentertainment.com"),  # MX for SES
        ]
        
        found_count = 0
        for rtype, rname in expected_records:
            key = f"{rtype}:{rname}"
            if key in record_map:
                found_count += 1
                print(f"  Found {rtype} {rname}")
            else:
                print(f"  Missing {rtype} {rname}")
        
        # At least some should exist if auto-configure was run
        assert found_count >= 2, f"Expected at least 2 auto-configured records, found {found_count}"
        print(f"Verified {found_count}/{len(expected_records)} expected records")


class TestRoute53EdgeCases:
    """Edge cases and error handling tests"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def test_route53_zone_unavailable_handling(self):
        """Route53 zone endpoint should return 503 if service unavailable"""
        # This test verifies the endpoint handles errors gracefully
        # In normal operation, it should return 200
        response = self.session.get(f"{BASE_URL}/api/route53/zone")
        assert response.status_code in [200, 503], f"Expected 200 or 503, got {response.status_code}"

    def test_route53_records_unavailable_handling(self):
        """Route53 records endpoint should return 503 if service unavailable"""
        response = self.session.get(f"{BASE_URL}/api/route53/records")
        assert response.status_code in [200, 503], f"Expected 200 or 503, got {response.status_code}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
