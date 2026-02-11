"""
Phase 13 Testing: Real AWS Integration Tests
Tests CloudWatch, GuardDuty, and Macie with real AWS data
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestCloudWatchHealth:
    """CloudWatch health and AWS connection tests"""
    
    def test_cloudwatch_health_endpoint(self):
        """Test CloudWatch health returns aws_connected: true"""
        response = requests.get(f"{BASE_URL}/api/cloudwatch/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["aws_connected"] == True
        assert data["account_id"] == "314108682794"
        assert data["region"] == "us-east-1"
        assert data["alarms_count"] == 3
        assert data["sns_topics_count"] == 4
        assert data["eventbridge_rules_count"] == 5


class TestCloudWatchDashboard:
    """CloudWatch dashboard API tests"""
    
    def test_dashboard_returns_real_data(self):
        """Test dashboard returns real alarms (3), SNS topics (4), EventBridge rules (5)"""
        response = requests.get(f"{BASE_URL}/api/cloudwatch/dashboard")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total_alarms"] == 3
        assert data["total_sns_topics"] == 4
        assert data["total_eventbridge_rules"] == 5
        
        # Verify real data exists
        assert "alarms" in data
        assert "sns_topics" in data
        assert "eventbridge_rules" in data
        assert len(data["alarms"]) == 3
        assert len(data["sns_topics"]) == 4
        assert len(data["eventbridge_rules"]) == 5
        
        # Verify account info
        assert data["account_id"] == "314108682794"
        assert data["region"] == "us-east-1"


class TestCloudWatchAlarms:
    """CloudWatch alarms API tests"""
    
    def test_alarms_endpoint_returns_3_alarms(self):
        """Test /api/cloudwatch/alarms returns 3 real alarms"""
        response = requests.get(f"{BASE_URL}/api/cloudwatch/alarms")
        assert response.status_code == 200
        
        alarms = response.json()
        assert len(alarms) == 3
        
        # Verify alarm structure
        expected_alarm_names = [
            "bigmann-development-cloudfront-errors",
            "bigmann-development-high-error-rate",
            "bigmann-development-high-response-time"
        ]
        
        alarm_names = [a["alarm_name"] for a in alarms]
        for expected in expected_alarm_names:
            assert expected in alarm_names
        
        # Verify alarm fields
        for alarm in alarms:
            assert "alarm_name" in alarm
            assert "state_value" in alarm
            assert alarm["state_value"] in ["OK", "ALARM", "INSUFFICIENT_DATA"]


class TestCloudWatchSNSTopics:
    """CloudWatch SNS topics API tests"""
    
    def test_sns_topics_returns_4_topics(self):
        """Test /api/cloudwatch/sns-topics returns 4 real topics"""
        response = requests.get(f"{BASE_URL}/api/cloudwatch/sns-topics")
        assert response.status_code == 200
        
        topics = response.json()
        assert len(topics) == 4
        
        # Verify topic structure
        for topic in topics:
            assert "topic_arn" in topic
            assert "display_name" in topic
            assert "subscription_count" in topic
            assert "region" in topic
        
        # Check for known topic
        topic_names = [t["display_name"] for t in topics]
        assert "Big Mann Entertainment development Alerts" in topic_names


class TestCloudWatchEventBridge:
    """CloudWatch EventBridge rules API tests"""
    
    def test_eventbridge_rules_returns_5_rules(self):
        """Test /api/cloudwatch/eventbridge-rules returns 5 real rules"""
        response = requests.get(f"{BASE_URL}/api/cloudwatch/eventbridge-rules")
        assert response.status_code == 200
        
        rules = response.json()
        assert len(rules) == 5
        
        # Verify rule structure
        for rule in rules:
            assert "name" in rule
            assert "state" in rule
            assert rule["state"] in ["ENABLED", "DISABLED"]
        
        # Check all are enabled
        enabled_count = sum(1 for r in rules if r["state"] == "ENABLED")
        assert enabled_count == 5


class TestSNSPublish:
    """SNS publish message API tests"""
    
    def test_sns_publish_message(self):
        """Test POST /api/cloudwatch/sns/publish sends real message to SNS"""
        # Get a real topic ARN
        topics_resp = requests.get(f"{BASE_URL}/api/cloudwatch/sns-topics")
        topics = topics_resp.json()
        
        # Find the alerts topic (non-FIFO)
        topic_arn = None
        for t in topics:
            if "Alerts" in t["display_name"]:
                topic_arn = t["topic_arn"]
                break
        
        if not topic_arn:
            topic_arn = topics[0]["topic_arn"]
        
        # Publish test message
        response = requests.post(
            f"{BASE_URL}/api/cloudwatch/sns/publish",
            json={
                "topic_arn": topic_arn,
                "subject": "Test Message from Phase 13",
                "message": "This is a test message from Phase 13 automated testing."
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "message_id" in data
        assert len(data["message_id"]) > 0


class TestGuardDutyHealth:
    """GuardDuty health API tests"""
    
    def test_guardduty_health_aws_connected(self):
        """Test /api/guardduty/health shows aws_connected: true"""
        response = requests.get(f"{BASE_URL}/api/guardduty/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["aws_connected"] == True
        assert data["guardduty_enabled"] == True


class TestGuardDutyDashboard:
    """GuardDuty dashboard API tests"""
    
    def test_guardduty_dashboard_real_data(self):
        """Test /api/guardduty/dashboard shows real findings from AWS"""
        response = requests.get(f"{BASE_URL}/api/guardduty/dashboard")
        assert response.status_code == 200
        
        data = response.json()
        
        # Verify structure
        assert "total_detectors" in data
        assert "total_findings" in data
        assert "severity_summary" in data
        assert "status_summary" in data
        
        # Verify real detector exists (user account has 1 detector with 1 finding)
        assert data["total_detectors"] >= 1
        assert data["active_detectors"] >= 1


class TestMacieBuckets:
    """Macie S3 buckets API tests"""
    
    def test_macie_buckets_returns_14_real_buckets(self):
        """Test /api/macie/buckets returns 14 real S3 buckets from AWS"""
        response = requests.get(f"{BASE_URL}/api/macie/buckets")
        assert response.status_code == 200
        
        buckets = response.json()
        assert len(buckets) == 14
        
        # Verify bucket structure
        for bucket in buckets:
            assert "name" in bucket
            assert "region" in bucket
            assert "account_id" in bucket
        
        # Check for known bucket names
        bucket_names = [b["name"] for b in buckets]
        expected_buckets = [
            "bigmann-entertainment-media",
            "bigmann-frontend-development-314108682794"
        ]
        for expected in expected_buckets:
            assert expected in bucket_names


# Ensure tests run
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
