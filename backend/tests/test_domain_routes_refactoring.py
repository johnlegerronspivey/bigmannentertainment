"""
Test suite for domain_routes.py refactoring verification.
Tests that endpoints moved from aws_routes.py to domain_routes.py and health_routes.py work correctly.
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://domain-config-8.preview.emergentagent.com').rstrip('/')

class TestDomainRoutesRefactoring:
    """Test endpoints after refactoring aws_routes.py into domain_routes.py"""
    
    def test_domain_status_endpoint(self):
        """GET /api/domain/status - should return domain info with route53 connected status"""
        response = requests.get(f"{BASE_URL}/api/domain/status")
        assert response.status_code == 200
        
        data = response.json()
        # Verify required fields
        assert "domain" in data
        assert data["domain"] == "bigmannentertainment.com"
        assert "ses" in data
        assert "cloudfront" in data
        assert "route53" in data
        
        # Verify route53 connected status
        assert data["route53"]["status"] == "connected"
        assert "zone_id" in data["route53"]
        assert "name_servers" in data["route53"]
        assert len(data["route53"]["name_servers"]) == 4  # Should have 4 AWS name servers
    
    def test_aws_health_endpoint_moved_to_health_routes(self):
        """GET /api/aws/health - should return healthy status with s3 service info"""
        response = requests.get(f"{BASE_URL}/api/aws/health")
        assert response.status_code == 200
        
        data = response.json()
        # Verify health check structure
        assert "status" in data
        assert data["status"] == "healthy"
        assert "services" in data
        assert "s3" in data["services"]
        
        # Verify S3 service details
        s3_info = data["services"]["s3"]
        assert s3_info["status"] == "healthy"
        assert s3_info["bucket"] == "bigmann-entertainment-media"
        assert s3_info["region"] == "us-east-1"
    
    def test_phase2_status_endpoint_in_aws_routes(self):
        """GET /api/phase2/status - should return cloudfront, lambda, rekognition, s3 availability"""
        response = requests.get(f"{BASE_URL}/api/phase2/status")
        assert response.status_code == 200
        
        data = response.json()
        # Verify phase2 services
        assert "cloudfront" in data
        assert data["cloudfront"]["available"] == True
        assert data["cloudfront"]["domain"] == "cdn.bigmannentertainment.com"
        
        assert "lambda" in data
        assert data["lambda"]["available"] == True
        
        assert "rekognition" in data
        assert data["rekognition"]["available"] == True
        
        assert "s3" in data
        assert data["s3"]["available"] == True
        assert data["s3"]["bucket"] == "bigmann-entertainment-media"
    
    def test_route53_records_endpoint(self):
        """GET /api/route53/records - should return DNS records list"""
        response = requests.get(f"{BASE_URL}/api/route53/records")
        assert response.status_code == 200
        
        data = response.json()
        assert "records" in data
        records = data["records"]
        
        # Verify we have DNS records
        assert len(records) >= 5  # Should have at least NS, SOA, and other records
        
        # Verify each record has required fields
        for record in records:
            assert "name" in record
            assert "type" in record
            assert "ttl" in record
            assert "values" in record
        
        # Verify common record types exist
        record_types = [r["type"] for r in records]
        assert "NS" in record_types
        assert "SOA" in record_types
    
    def test_dns_guide_endpoint(self):
        """GET /api/domain/dns-guide - should return DNS configuration guide"""
        response = requests.get(f"{BASE_URL}/api/domain/dns-guide")
        assert response.status_code == 200
        
        data = response.json()
        assert "domain" in data
        assert data["domain"] == "bigmannentertainment.com"
        assert "required_records" in data
        assert "instructions" in data
        
        # Verify required records structure
        records = data["required_records"]
        assert len(records) >= 5
        
        # Verify each record has required fields
        for record in records:
            assert "type" in record
            assert "name" in record
            assert "value" in record
            assert "purpose" in record
            assert "priority" in record
        
        # Verify instructions
        instructions = data["instructions"]
        assert "step_1" in instructions
        assert "step_6" in instructions  # Should have at least 6 steps


class TestRoutingIntegrity:
    """Test that routing is correctly wired in server.py"""
    
    def test_domain_router_included(self):
        """Verify domain_router is included (domain endpoints work)"""
        # Test an endpoint from domain_routes.py
        response = requests.get(f"{BASE_URL}/api/domain/status")
        assert response.status_code == 200
    
    def test_health_router_with_aws_health(self):
        """Verify health_router includes aws/health endpoint"""
        response = requests.get(f"{BASE_URL}/api/aws/health")
        assert response.status_code == 200
    
    def test_aws_router_with_phase2_status(self):
        """Verify aws_router still has phase2/status endpoint"""
        response = requests.get(f"{BASE_URL}/api/phase2/status")
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
