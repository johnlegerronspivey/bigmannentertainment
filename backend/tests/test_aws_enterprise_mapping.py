"""
AWS Enterprise Mapping API Tests
Tests for AWS infrastructure discovery, mapping, and management endpoints
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://dynamic-royalties.preview.emergentagent.com').rstrip('/')


class TestAWSEnterpriseHealth:
    """Health check endpoint tests"""
    
    def test_health_endpoint(self):
        """Test health check returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/aws-enterprise/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "account_id" in data
        assert "region" in data
        assert data["message"] == "AWS Enterprise Mapping service operational"


class TestAWSResourceDiscovery:
    """Resource discovery endpoint tests"""
    
    def test_list_ec2_instances(self):
        """Test EC2 instances discovery"""
        response = requests.get(f"{BASE_URL}/api/aws-enterprise/resources/ec2")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        # EC2 instances may be empty if none exist
        if len(data) > 0:
            instance = data[0]
            assert "resource_id" in instance
            assert "resource_type" in instance
            assert instance["resource_type"] == "ec2:instance"
            assert "instance_type" in instance
            assert "state" in instance
    
    def test_list_s3_buckets(self):
        """Test S3 buckets discovery"""
        response = requests.get(f"{BASE_URL}/api/aws-enterprise/resources/s3")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0  # Should have at least some buckets
        
        bucket = data[0]
        assert "resource_id" in bucket
        assert "resource_type" in bucket
        assert bucket["resource_type"] == "s3:bucket"
        assert "bucket_name" in bucket
        assert "versioning_enabled" in bucket
        assert "public_access_blocked" in bucket
        assert "region" in bucket
    
    def test_list_rds_instances(self):
        """Test RDS instances discovery"""
        response = requests.get(f"{BASE_URL}/api/aws-enterprise/resources/rds")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
        if len(data) > 0:
            instance = data[0]
            assert "resource_id" in instance
            assert "resource_type" in instance
            assert instance["resource_type"] == "rds:instance"
            assert "db_instance_identifier" in instance
            assert "engine" in instance
            assert "engine_version" in instance
            assert "instance_class" in instance
    
    def test_list_lambda_functions(self):
        """Test Lambda functions discovery"""
        response = requests.get(f"{BASE_URL}/api/aws-enterprise/resources/lambda")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
        if len(data) > 0:
            func = data[0]
            assert "resource_id" in func
            assert "resource_type" in func
            assert func["resource_type"] == "lambda:function"
            assert "function_name" in func
            assert "runtime" in func
            assert "memory_size" in func
            assert "timeout" in func
    
    def test_list_cloudfront_distributions(self):
        """Test CloudFront distributions discovery"""
        response = requests.get(f"{BASE_URL}/api/aws-enterprise/resources/cloudfront")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
        if len(data) > 0:
            dist = data[0]
            assert "resource_id" in dist
            assert "resource_type" in dist
            assert dist["resource_type"] == "cloudfront:distribution"
            assert "distribution_id" in dist
            assert "domain_name" in dist
            assert "origin_domain" in dist
    
    def test_list_iam_roles(self):
        """Test IAM roles discovery"""
        response = requests.get(f"{BASE_URL}/api/aws-enterprise/resources/iam-roles")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0  # Should have IAM roles
        
        role = data[0]
        assert "resource_id" in role
        assert "resource_type" in role
        assert role["resource_type"] == "iam:role"
        assert "role_name" in role
        assert "arn" in role


class TestAWSInfrastructureMap:
    """Infrastructure mapping endpoint tests"""
    
    def test_get_infrastructure_map(self):
        """Test infrastructure map generation"""
        response = requests.get(f"{BASE_URL}/api/aws-enterprise/infrastructure-map")
        assert response.status_code == 200
        
        data = response.json()
        assert "id" in data
        assert "organization_id" in data
        assert "account_id" in data
        assert "resource_counts" in data
        assert "resources_by_region" in data
        assert "healthy_resources" in data
        assert "warning_resources" in data
        assert "critical_resources" in data
        assert "total_monthly_cost" in data
        assert "cost_by_service" in data
        assert "security_score" in data
        
        # Verify resource counts structure
        resource_counts = data["resource_counts"]
        assert "s3:bucket" in resource_counts
        assert "lambda:function" in resource_counts
        assert "iam:role" in resource_counts


class TestAWSCostManagement:
    """Cost management endpoint tests"""
    
    def test_get_cost_breakdown(self):
        """Test cost breakdown retrieval"""
        response = requests.get(f"{BASE_URL}/api/aws-enterprise/costs")
        assert response.status_code == 200
        
        data = response.json()
        assert "id" in data
        assert "period_start" in data
        assert "period_end" in data
        assert "total_cost" in data
        assert "currency" in data
        assert data["currency"] == "USD"
        assert "by_service" in data
        assert "by_region" in data
        assert "top_resources" in data
        
        # Verify cost is a positive number
        assert isinstance(data["total_cost"], (int, float))
        assert data["total_cost"] >= 0


class TestAWSEnterpriseMetrics:
    """Enterprise metrics endpoint tests"""
    
    def test_get_enterprise_metrics(self):
        """Test enterprise metrics retrieval"""
        response = requests.get(f"{BASE_URL}/api/aws-enterprise/metrics")
        assert response.status_code == 200
        
        data = response.json()
        assert "id" in data
        assert "total_accounts" in data
        assert "active_accounts" in data
        assert "total_resources" in data
        assert "total_monthly_cost" in data
        assert "cost_forecast_next_month" in data
        assert "budget_remaining" in data
        assert "security_score" in data
        assert "compliance_score" in data
        
        # Verify metrics are reasonable
        assert data["total_resources"] > 0
        assert data["security_score"] >= 0 and data["security_score"] <= 100
        assert data["compliance_score"] >= 0 and data["compliance_score"] <= 100


class TestAWSReferenceData:
    """Reference data endpoint tests"""
    
    def test_get_service_types(self):
        """Test service types reference data"""
        response = requests.get(f"{BASE_URL}/api/aws-enterprise/service-types")
        assert response.status_code == 200
        
        data = response.json()
        assert "service_types" in data
        
        service_types = data["service_types"]
        assert "compute" in service_types
        assert "storage" in service_types
        assert "database" in service_types
        assert "networking" in service_types
        assert "security" in service_types
        
        # Verify structure of service type
        compute = service_types["compute"]
        assert "name" in compute
        assert "description" in compute
        assert "icon" in compute
    
    def test_get_regions(self):
        """Test available regions reference data"""
        response = requests.get(f"{BASE_URL}/api/aws-enterprise/regions")
        assert response.status_code == 200
        
        data = response.json()
        assert "regions" in data
        assert "default_region" in data
        assert data["default_region"] == "us-east-1"
        
        regions = data["regions"]
        assert len(regions) > 0
        
        # Verify region structure
        region = regions[0]
        assert "code" in region
        assert "name" in region
        assert "status" in region


class TestAWSResourceCounts:
    """Verify actual resource counts match expected values"""
    
    def test_s3_bucket_count(self):
        """Verify S3 bucket count"""
        response = requests.get(f"{BASE_URL}/api/aws-enterprise/resources/s3")
        assert response.status_code == 200
        data = response.json()
        # Should have 14 S3 buckets as per the context
        assert len(data) == 14
    
    def test_lambda_function_count(self):
        """Verify Lambda function count"""
        response = requests.get(f"{BASE_URL}/api/aws-enterprise/resources/lambda")
        assert response.status_code == 200
        data = response.json()
        # Should have 9 Lambda functions as per the context
        assert len(data) == 9
    
    def test_rds_instance_count(self):
        """Verify RDS instance count"""
        response = requests.get(f"{BASE_URL}/api/aws-enterprise/resources/rds")
        assert response.status_code == 200
        data = response.json()
        # Should have 1 RDS instance as per the context
        assert len(data) == 1
    
    def test_cloudfront_distribution_count(self):
        """Verify CloudFront distribution count"""
        response = requests.get(f"{BASE_URL}/api/aws-enterprise/resources/cloudfront")
        assert response.status_code == 200
        data = response.json()
        # Should have 7 CloudFront distributions as per the context
        assert len(data) == 7
    
    def test_iam_role_count(self):
        """Verify IAM role count"""
        response = requests.get(f"{BASE_URL}/api/aws-enterprise/resources/iam-roles")
        assert response.status_code == 200
        data = response.json()
        # Should have 87 IAM roles as per the context
        assert len(data) == 87


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
