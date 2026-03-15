"""
AWS Phase F Integration Tests
Tests for: Translate, Polly, Textract, SageMaker, Kinesis, SNS, SQS, EventBridge, Step Functions, ElastiCache, Neptune
All 11 new AWS services from Phase F implementation
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAuthSetup:
    """Get auth token for all tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Login and get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "owner@bigmannentertainment.com",
            "password": "Test1234!"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data or "token" in data
        return data.get("access_token") or data.get("token")
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        """Auth headers for requests"""
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }


class TestAWSAIContentStatus(TestAuthSetup):
    """Test /api/aws-ai-content/status endpoint - returns Translate, Polly, Textract, SageMaker statuses"""
    
    def test_ai_content_status_returns_all_4_services(self, headers):
        response = requests.get(f"{BASE_URL}/api/aws-ai-content/status", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        # Verify all 4 services are present
        assert "translate" in data
        assert "polly" in data
        assert "textract" in data
        assert "sagemaker" in data
        
        # Verify each has expected structure
        for service in ["translate", "polly", "textract", "sagemaker"]:
            assert "available" in data[service]
            assert "service" in data[service]
            assert "region" in data[service]
        
        print(f"AI Content Status: translate={data['translate']['available']}, polly={data['polly']['available']}, textract={data['textract']['available']}, sagemaker={data['sagemaker']['available']}")


class TestTranslateService(TestAuthSetup):
    """Test Translate endpoints"""
    
    def test_translate_text_success(self, headers):
        """POST /api/aws-ai-content/translate/text - translate text"""
        response = requests.post(f"{BASE_URL}/api/aws-ai-content/translate/text", headers=headers, json={
            "text": "Hello, this is a test message",
            "source_language": "en",
            "target_language": "es"
        })
        assert response.status_code == 200
        data = response.json()
        
        # Verify translation response structure
        assert "translated_text" in data
        assert "source_language" in data
        assert "target_language" in data
        assert len(data["translated_text"]) > 0
        print(f"Translation result: '{data['translated_text']}'")
    
    def test_translate_languages_list(self, headers):
        """GET /api/aws-ai-content/translate/languages - list supported languages"""
        response = requests.get(f"{BASE_URL}/api/aws-ai-content/translate/languages", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "languages" in data
        assert "total" in data
        assert data["total"] > 0
        assert len(data["languages"]) > 0
        
        # Verify language structure
        if data["languages"]:
            lang = data["languages"][0]
            assert "code" in lang or "LanguageCode" in lang
        
        print(f"Found {data['total']} supported languages")


class TestPollyService(TestAuthSetup):
    """Test Polly TTS endpoints"""
    
    def test_polly_voices_list(self, headers):
        """GET /api/aws-ai-content/polly/voices - list available voices"""
        response = requests.get(f"{BASE_URL}/api/aws-ai-content/polly/voices", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "voices" in data
        assert "total" in data
        assert data["total"] > 0
        
        # Verify voice structure
        if data["voices"]:
            voice = data["voices"][0]
            assert "id" in voice or "Id" in voice or "name" in voice
        
        print(f"Found {data['total']} Polly voices")


class TestSageMakerService(TestAuthSetup):
    """Test SageMaker ML endpoints"""
    
    def test_sagemaker_notebooks_list(self, headers):
        """GET /api/aws-ai-content/sagemaker/notebooks - list notebook instances"""
        response = requests.get(f"{BASE_URL}/api/aws-ai-content/sagemaker/notebooks", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "notebooks" in data
        assert "total" in data
        assert isinstance(data["notebooks"], list)
        print(f"Found {data['total']} SageMaker notebooks")
    
    def test_sagemaker_models_list(self, headers):
        """GET /api/aws-ai-content/sagemaker/models - list models"""
        response = requests.get(f"{BASE_URL}/api/aws-ai-content/sagemaker/models", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "models" in data
        assert "total" in data
        assert isinstance(data["models"], list)
        print(f"Found {data['total']} SageMaker models")


class TestAWSMessagingStatus(TestAuthSetup):
    """Test /api/aws-messaging/status endpoint - returns Kinesis, SNS, SQS, EventBridge statuses"""
    
    def test_messaging_status_returns_all_4_services(self, headers):
        response = requests.get(f"{BASE_URL}/api/aws-messaging/status", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        # Verify all 4 services are present
        assert "kinesis" in data
        assert "sns" in data
        assert "sqs" in data
        assert "eventbridge" in data
        
        # Verify each has expected structure
        for service in ["kinesis", "sns", "sqs", "eventbridge"]:
            assert "available" in data[service]
            assert "service" in data[service]
            assert "region" in data[service]
        
        print(f"Messaging Status: kinesis={data['kinesis']['available']}, sns={data['sns']['available']}, sqs={data['sqs']['available']}, eventbridge={data['eventbridge']['available']}")


class TestKinesisService(TestAuthSetup):
    """Test Kinesis streaming endpoints"""
    
    def test_kinesis_streams_list(self, headers):
        """GET /api/aws-messaging/kinesis/streams - list data streams"""
        response = requests.get(f"{BASE_URL}/api/aws-messaging/kinesis/streams", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "streams" in data
        assert "total" in data
        assert isinstance(data["streams"], list)
        print(f"Found {data['total']} Kinesis streams")


class TestSNSService(TestAuthSetup):
    """Test SNS notification endpoints"""
    
    def test_sns_topics_list(self, headers):
        """GET /api/aws-messaging/sns/topics - list SNS topics"""
        response = requests.get(f"{BASE_URL}/api/aws-messaging/sns/topics", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "topics" in data
        assert "total" in data
        assert isinstance(data["topics"], list)
        print(f"Found {data['total']} SNS topics")


class TestSQSService(TestAuthSetup):
    """Test SQS queue endpoints"""
    
    def test_sqs_queues_list(self, headers):
        """GET /api/aws-messaging/sqs/queues - list SQS queues"""
        response = requests.get(f"{BASE_URL}/api/aws-messaging/sqs/queues", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "queues" in data
        assert "total" in data
        assert isinstance(data["queues"], list)
        print(f"Found {data['total']} SQS queues")


class TestEventBridgeService(TestAuthSetup):
    """Test EventBridge endpoints"""
    
    def test_eventbridge_buses_list(self, headers):
        """GET /api/aws-messaging/eventbridge/buses - list event buses"""
        response = requests.get(f"{BASE_URL}/api/aws-messaging/eventbridge/buses", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "event_buses" in data
        assert "total" in data
        assert isinstance(data["event_buses"], list)
        print(f"Found {data['total']} EventBridge buses")
    
    def test_eventbridge_rules_list(self, headers):
        """GET /api/aws-messaging/eventbridge/rules - list rules"""
        response = requests.get(f"{BASE_URL}/api/aws-messaging/eventbridge/rules", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "rules" in data
        assert "total" in data
        assert isinstance(data["rules"], list)
        print(f"Found {data['total']} EventBridge rules")


class TestAWSInfraStatus(TestAuthSetup):
    """Test /api/aws-infra/status endpoint - returns Step Functions, ElastiCache, Neptune statuses"""
    
    def test_infra_status_returns_all_3_services(self, headers):
        response = requests.get(f"{BASE_URL}/api/aws-infra/status", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        # Verify all 3 services are present
        assert "step_functions" in data
        assert "elasticache" in data
        assert "neptune" in data
        
        # Verify each has expected structure
        for service in ["step_functions", "elasticache", "neptune"]:
            assert "available" in data[service]
            assert "service" in data[service]
            assert "region" in data[service]
        
        print(f"Infra Status: step_functions={data['step_functions']['available']}, elasticache={data['elasticache']['available']}, neptune={data['neptune']['available']}")


class TestStepFunctionsService(TestAuthSetup):
    """Test Step Functions workflow endpoints"""
    
    def test_stepfunctions_state_machines_list(self, headers):
        """GET /api/aws-infra/stepfunctions/state-machines - list state machines"""
        response = requests.get(f"{BASE_URL}/api/aws-infra/stepfunctions/state-machines", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "state_machines" in data
        assert "total" in data
        assert isinstance(data["state_machines"], list)
        print(f"Found {data['total']} Step Function state machines")


class TestElastiCacheService(TestAuthSetup):
    """Test ElastiCache endpoints"""
    
    def test_elasticache_clusters_list(self, headers):
        """GET /api/aws-infra/elasticache/clusters - list cache clusters"""
        response = requests.get(f"{BASE_URL}/api/aws-infra/elasticache/clusters", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "clusters" in data
        assert "total" in data
        assert isinstance(data["clusters"], list)
        print(f"Found {data['total']} ElastiCache clusters")


class TestNeptuneService(TestAuthSetup):
    """Test Neptune graph database endpoints"""
    
    def test_neptune_clusters_list(self, headers):
        """GET /api/aws-infra/neptune/clusters - list Neptune clusters"""
        response = requests.get(f"{BASE_URL}/api/aws-infra/neptune/clusters", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "clusters" in data
        assert "total" in data
        assert isinstance(data["clusters"], list)
        print(f"Found {data['total']} Neptune clusters")


class TestUnauthenticatedAccess:
    """Test that all endpoints require authentication"""
    
    def test_ai_content_status_requires_auth(self):
        response = requests.get(f"{BASE_URL}/api/aws-ai-content/status")
        assert response.status_code in [401, 403]
    
    def test_messaging_status_requires_auth(self):
        response = requests.get(f"{BASE_URL}/api/aws-messaging/status")
        assert response.status_code in [401, 403]
    
    def test_infra_status_requires_auth(self):
        response = requests.get(f"{BASE_URL}/api/aws-infra/status")
        assert response.status_code in [401, 403]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
