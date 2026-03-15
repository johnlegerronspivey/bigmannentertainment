"""
AWS Phase E Integration Tests - AI Analytics, Data Analytics, Managed Blockchain
Tests AWS Comprehend, Personalize, QuickSight, Athena, and Managed Blockchain endpoints
"""
import pytest
import requests
import os

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")

# Test credentials
TEST_EMAIL = "owner@bigmannentertainment.com"
TEST_PASSWORD = "Test1234!"


class TestSetup:
    """Authentication setup for all tests"""

    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token for testing"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        # Auth returns access_token field (not 'token')
        token = data.get("access_token") or data.get("token")
        assert token, f"No token in response: {data}"
        return token

    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        """Return headers with auth token"""
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
        }


class TestAWSAIStatus(TestSetup):
    """Test AI Analytics status endpoint"""

    def test_get_ai_status(self, headers):
        """GET /api/aws-ai/status - returns comprehend and personalize status"""
        response = requests.get(f"{BASE_URL}/api/aws-ai/status", headers=headers)
        assert response.status_code == 200, f"Status failed: {response.text}"
        data = response.json()

        # Verify comprehend status
        assert "comprehend" in data, "Missing comprehend in status"
        assert "available" in data["comprehend"], "Missing available flag in comprehend"

        # Verify personalize status
        assert "personalize" in data, "Missing personalize in status"
        assert "available" in data["personalize"], "Missing available flag in personalize"

        print(f"Comprehend available: {data['comprehend']['available']}")
        print(f"Personalize available: {data['personalize']['available']}")


class TestComprehendEndpoints(TestSetup):
    """Test AWS Comprehend NLP endpoints"""

    def test_comprehend_sentiment(self, headers):
        """POST /api/aws-ai/comprehend/sentiment - analyzes text sentiment"""
        test_text = "I absolutely love this amazing product! It's fantastic and wonderful."
        response = requests.post(
            f"{BASE_URL}/api/aws-ai/comprehend/sentiment",
            headers=headers,
            json={"text": test_text, "language": "en"},
        )
        assert response.status_code == 200, f"Sentiment failed: {response.text}"
        data = response.json()

        assert "sentiment" in data, "Missing sentiment in response"
        assert data["sentiment"] in ["POSITIVE", "NEGATIVE", "NEUTRAL", "MIXED"], f"Invalid sentiment: {data['sentiment']}"
        assert "scores" in data, "Missing scores in response"
        assert "positive" in data["scores"], "Missing positive score"
        assert "negative" in data["scores"], "Missing negative score"
        print(f"Sentiment: {data['sentiment']}, Scores: {data['scores']}")

    def test_comprehend_entities(self, headers):
        """POST /api/aws-ai/comprehend/entities - detects named entities"""
        test_text = "Apple Inc. was founded by Steve Jobs in Cupertino, California in 1976."
        response = requests.post(
            f"{BASE_URL}/api/aws-ai/comprehend/entities",
            headers=headers,
            json={"text": test_text, "language": "en"},
        )
        assert response.status_code == 200, f"Entities failed: {response.text}"
        data = response.json()

        assert "entities" in data, "Missing entities in response"
        assert "total" in data, "Missing total in response"
        assert isinstance(data["entities"], list), "Entities should be a list"
        print(f"Found {data['total']} entities")

    def test_comprehend_key_phrases(self, headers):
        """POST /api/aws-ai/comprehend/key-phrases - extracts key phrases"""
        test_text = "Big Mann Entertainment provides comprehensive music distribution services."
        response = requests.post(
            f"{BASE_URL}/api/aws-ai/comprehend/key-phrases",
            headers=headers,
            json={"text": test_text, "language": "en"},
        )
        assert response.status_code == 200, f"Key phrases failed: {response.text}"
        data = response.json()

        assert "key_phrases" in data, "Missing key_phrases in response"
        assert "total" in data, "Missing total in response"
        print(f"Found {data['total']} key phrases")

    def test_comprehend_pii(self, headers):
        """POST /api/aws-ai/comprehend/pii - detects PII in text"""
        test_text = "My email is john@example.com and my phone number is 555-123-4567."
        response = requests.post(
            f"{BASE_URL}/api/aws-ai/comprehend/pii",
            headers=headers,
            json={"text": test_text, "language": "en"},
        )
        assert response.status_code == 200, f"PII detection failed: {response.text}"
        data = response.json()

        assert "pii_entities" in data, "Missing pii_entities in response"
        assert "total" in data, "Missing total in response"
        print(f"Found {data['total']} PII entities")

    def test_comprehend_language(self, headers):
        """POST /api/aws-ai/comprehend/language - detects dominant language"""
        test_text = "This is an English text for language detection testing."
        response = requests.post(
            f"{BASE_URL}/api/aws-ai/comprehend/language",
            headers=headers,
            json={"text": test_text},
        )
        assert response.status_code == 200, f"Language detection failed: {response.text}"
        data = response.json()

        assert "languages" in data, "Missing languages in response"
        assert "total" in data, "Missing total in response"
        print(f"Detected languages: {data['languages']}")

    def test_comprehend_syntax(self, headers):
        """POST /api/aws-ai/comprehend/syntax - analyzes syntax/POS tags"""
        test_text = "The quick brown fox jumps over the lazy dog."
        response = requests.post(
            f"{BASE_URL}/api/aws-ai/comprehend/syntax",
            headers=headers,
            json={"text": test_text, "language": "en"},
        )
        assert response.status_code == 200, f"Syntax analysis failed: {response.text}"
        data = response.json()

        assert "tokens" in data, "Missing tokens in response"
        assert "total" in data, "Missing total in response"
        print(f"Found {data['total']} syntax tokens")

    def test_comprehend_batch_sentiment(self, headers):
        """POST /api/aws-ai/comprehend/batch-sentiment - batch sentiment on multiple texts"""
        texts = [
            "I love this product!",
            "This is terrible and awful.",
            "It's okay, nothing special.",
        ]
        response = requests.post(
            f"{BASE_URL}/api/aws-ai/comprehend/batch-sentiment",
            headers=headers,
            json={"texts": texts, "language": "en"},
        )
        assert response.status_code == 200, f"Batch sentiment failed: {response.text}"
        data = response.json()

        assert "results" in data, "Missing results in response"
        assert "total" in data, "Missing total in response"
        assert data["total"] == len(texts), f"Expected {len(texts)} results, got {data['total']}"
        print(f"Batch processed {data['total']} texts")

    def test_comprehend_endpoints_list(self, headers):
        """GET /api/aws-ai/comprehend/endpoints - list comprehend endpoints"""
        response = requests.get(
            f"{BASE_URL}/api/aws-ai/comprehend/endpoints", headers=headers
        )
        assert response.status_code == 200, f"Endpoints list failed: {response.text}"
        data = response.json()

        assert "endpoints" in data, "Missing endpoints in response"
        assert "total" in data, "Missing total in response"
        print(f"Found {data['total']} comprehend endpoints")

    def test_comprehend_history(self, headers):
        """GET /api/aws-ai/comprehend/history - get analysis history"""
        response = requests.get(
            f"{BASE_URL}/api/aws-ai/comprehend/history?limit=10", headers=headers
        )
        assert response.status_code == 200, f"History failed: {response.text}"
        data = response.json()

        assert "history" in data, "Missing history in response"
        assert "total" in data, "Missing total in response"
        print(f"Found {data['total']} history entries")


class TestPersonalizeEndpoints(TestSetup):
    """Test AWS Personalize endpoints"""

    def test_personalize_dataset_groups(self, headers):
        """GET /api/aws-ai/personalize/dataset-groups - list personalize dataset groups"""
        response = requests.get(
            f"{BASE_URL}/api/aws-ai/personalize/dataset-groups", headers=headers
        )
        assert response.status_code == 200, f"Dataset groups failed: {response.text}"
        data = response.json()

        assert "dataset_groups" in data, "Missing dataset_groups in response"
        assert "total" in data, "Missing total in response"
        print(f"Found {data['total']} dataset groups")

    def test_personalize_campaigns(self, headers):
        """GET /api/aws-ai/personalize/campaigns - list personalize campaigns"""
        response = requests.get(
            f"{BASE_URL}/api/aws-ai/personalize/campaigns", headers=headers
        )
        assert response.status_code == 200, f"Campaigns failed: {response.text}"
        data = response.json()

        assert "campaigns" in data, "Missing campaigns in response"
        assert "total" in data, "Missing total in response"
        print(f"Found {data['total']} campaigns")

    def test_personalize_solutions(self, headers):
        """GET /api/aws-ai/personalize/solutions - list personalize solutions"""
        response = requests.get(
            f"{BASE_URL}/api/aws-ai/personalize/solutions", headers=headers
        )
        assert response.status_code == 200, f"Solutions failed: {response.text}"
        data = response.json()

        assert "solutions" in data, "Missing solutions in response"
        assert "total" in data, "Missing total in response"
        print(f"Found {data['total']} solutions")

    def test_personalize_recipes(self, headers):
        """GET /api/aws-ai/personalize/recipes - list personalize recipes (should return ~22)"""
        response = requests.get(
            f"{BASE_URL}/api/aws-ai/personalize/recipes", headers=headers
        )
        assert response.status_code == 200, f"Recipes failed: {response.text}"
        data = response.json()

        assert "recipes" in data, "Missing recipes in response"
        assert "total" in data, "Missing total in response"
        # AWS Personalize typically has 20+ built-in recipes
        assert data["total"] >= 15, f"Expected at least 15 recipes, got {data['total']}"
        print(f"Found {data['total']} recipes")

    def test_personalize_datasets(self, headers):
        """GET /api/aws-ai/personalize/datasets - list datasets"""
        response = requests.get(
            f"{BASE_URL}/api/aws-ai/personalize/datasets", headers=headers
        )
        assert response.status_code == 200, f"Datasets failed: {response.text}"
        data = response.json()

        assert "datasets" in data, "Missing datasets in response"
        assert "total" in data, "Missing total in response"
        print(f"Found {data['total']} datasets")

    def test_personalize_event_trackers(self, headers):
        """GET /api/aws-ai/personalize/event-trackers - list event trackers"""
        response = requests.get(
            f"{BASE_URL}/api/aws-ai/personalize/event-trackers", headers=headers
        )
        assert response.status_code == 200, f"Event trackers failed: {response.text}"
        data = response.json()

        assert "event_trackers" in data, "Missing event_trackers in response"
        assert "total" in data, "Missing total in response"
        print(f"Found {data['total']} event trackers")


class TestDataAnalyticsStatus(TestSetup):
    """Test Data Analytics status endpoint"""

    def test_get_data_status(self, headers):
        """GET /api/aws-data/status - returns quicksight and athena status"""
        response = requests.get(f"{BASE_URL}/api/aws-data/status", headers=headers)
        assert response.status_code == 200, f"Data status failed: {response.text}"
        data = response.json()

        # Verify quicksight status
        assert "quicksight" in data, "Missing quicksight in status"
        assert "available" in data["quicksight"], "Missing available flag in quicksight"

        # Verify athena status
        assert "athena" in data, "Missing athena in status"
        assert "available" in data["athena"], "Missing available flag in athena"

        print(f"QuickSight available: {data['quicksight']['available']}")
        print(f"Athena available: {data['athena']['available']}")


class TestQuickSightEndpoints(TestSetup):
    """Test Amazon QuickSight endpoints - Note: QuickSight may return 503 if not subscribed"""

    def test_quicksight_dashboards(self, headers):
        """GET /api/aws-data/quicksight/dashboards - list dashboards"""
        response = requests.get(
            f"{BASE_URL}/api/aws-data/quicksight/dashboards", headers=headers
        )
        # QuickSight may return 503 if not subscribed - this is expected
        assert response.status_code in [200, 503], f"Unexpected status: {response.status_code}"
        if response.status_code == 200:
            data = response.json()
            assert "dashboards" in data, "Missing dashboards in response"
            print(f"Found {data.get('total', 0)} dashboards")
        else:
            print("QuickSight not available (503 - expected if not subscribed)")

    def test_quicksight_datasets(self, headers):
        """GET /api/aws-data/quicksight/datasets - list datasets"""
        response = requests.get(
            f"{BASE_URL}/api/aws-data/quicksight/datasets", headers=headers
        )
        assert response.status_code in [200, 503], f"Unexpected status: {response.status_code}"
        if response.status_code == 200:
            data = response.json()
            assert "datasets" in data, "Missing datasets in response"
            print(f"Found {data.get('total', 0)} QuickSight datasets")
        else:
            print("QuickSight not available (503)")

    def test_quicksight_data_sources(self, headers):
        """GET /api/aws-data/quicksight/data-sources - list data sources"""
        response = requests.get(
            f"{BASE_URL}/api/aws-data/quicksight/data-sources", headers=headers
        )
        assert response.status_code in [200, 503], f"Unexpected status: {response.status_code}"
        if response.status_code == 200:
            data = response.json()
            assert "data_sources" in data, "Missing data_sources in response"
            print(f"Found {data.get('total', 0)} data sources")
        else:
            print("QuickSight not available (503)")

    def test_quicksight_analyses(self, headers):
        """GET /api/aws-data/quicksight/analyses - list analyses"""
        response = requests.get(
            f"{BASE_URL}/api/aws-data/quicksight/analyses", headers=headers
        )
        assert response.status_code in [200, 503], f"Unexpected status: {response.status_code}"
        if response.status_code == 200:
            data = response.json()
            assert "analyses" in data, "Missing analyses in response"
            print(f"Found {data.get('total', 0)} analyses")
        else:
            print("QuickSight not available (503)")


class TestAthenaEndpoints(TestSetup):
    """Test AWS Athena endpoints"""

    def test_athena_work_groups(self, headers):
        """GET /api/aws-data/athena/work-groups - list work groups"""
        response = requests.get(
            f"{BASE_URL}/api/aws-data/athena/work-groups", headers=headers
        )
        assert response.status_code == 200, f"Work groups failed: {response.text}"
        data = response.json()

        assert "work_groups" in data, "Missing work_groups in response"
        assert "total" in data, "Missing total in response"
        assert data["total"] >= 1, "Should have at least 'primary' work group"
        print(f"Found {data['total']} work groups")

    def test_athena_databases(self, headers):
        """GET /api/aws-data/athena/databases - list databases"""
        response = requests.get(
            f"{BASE_URL}/api/aws-data/athena/databases", headers=headers
        )
        assert response.status_code == 200, f"Databases failed: {response.text}"
        data = response.json()

        assert "databases" in data, "Missing databases in response"
        assert "total" in data, "Missing total in response"
        print(f"Found {data['total']} databases")

    def test_athena_executions(self, headers):
        """GET /api/aws-data/athena/executions - list recent executions"""
        response = requests.get(
            f"{BASE_URL}/api/aws-data/athena/executions", headers=headers
        )
        assert response.status_code == 200, f"Executions failed: {response.text}"
        data = response.json()

        assert "executions" in data, "Missing executions in response"
        assert "total" in data, "Missing total in response"
        print(f"Found {data['total']} recent executions")

    def test_athena_saved_queries(self, headers):
        """GET /api/aws-data/athena/saved-queries - list saved queries"""
        response = requests.get(
            f"{BASE_URL}/api/aws-data/athena/saved-queries", headers=headers
        )
        assert response.status_code == 200, f"Saved queries failed: {response.text}"
        data = response.json()

        assert "queries" in data, "Missing queries in response"
        assert "total" in data, "Missing total in response"
        print(f"Found {data['total']} saved queries")


class TestBlockchainStatus(TestSetup):
    """Test Managed Blockchain status endpoint"""

    def test_get_blockchain_status(self, headers):
        """GET /api/aws-blockchain/status - returns managed blockchain status"""
        response = requests.get(
            f"{BASE_URL}/api/aws-blockchain/status", headers=headers
        )
        assert response.status_code == 200, f"Blockchain status failed: {response.text}"
        data = response.json()

        assert "managed_blockchain" in data, "Missing managed_blockchain in status"
        assert "available" in data["managed_blockchain"], "Missing available flag"
        print(f"Managed Blockchain available: {data['managed_blockchain']['available']}")


class TestBlockchainEndpoints(TestSetup):
    """Test Amazon Managed Blockchain endpoints"""

    def test_blockchain_networks(self, headers):
        """GET /api/aws-blockchain/networks - list blockchain networks"""
        response = requests.get(
            f"{BASE_URL}/api/aws-blockchain/networks", headers=headers
        )
        assert response.status_code == 200, f"Networks failed: {response.text}"
        data = response.json()

        assert "networks" in data, "Missing networks in response"
        assert "total" in data, "Missing total in response"
        # May be empty if no networks created
        print(f"Found {data['total']} blockchain networks")

    def test_blockchain_accessors(self, headers):
        """GET /api/aws-blockchain/accessors - list blockchain accessors"""
        response = requests.get(
            f"{BASE_URL}/api/aws-blockchain/accessors", headers=headers
        )
        assert response.status_code == 200, f"Accessors failed: {response.text}"
        data = response.json()

        assert "accessors" in data, "Missing accessors in response"
        assert "total" in data, "Missing total in response"
        print(f"Found {data['total']} blockchain accessors")


class TestAuthenticationRequired(TestSetup):
    """Test that endpoints require authentication"""

    def test_ai_status_requires_auth(self):
        """Verify /api/aws-ai/status requires authentication"""
        response = requests.get(f"{BASE_URL}/api/aws-ai/status")
        assert response.status_code in [401, 403], f"Should require auth: {response.status_code}"

    def test_data_status_requires_auth(self):
        """Verify /api/aws-data/status requires authentication"""
        response = requests.get(f"{BASE_URL}/api/aws-data/status")
        assert response.status_code in [401, 403], f"Should require auth: {response.status_code}"

    def test_blockchain_status_requires_auth(self):
        """Verify /api/aws-blockchain/status requires authentication"""
        response = requests.get(f"{BASE_URL}/api/aws-blockchain/status")
        assert response.status_code in [401, 403], f"Should require auth: {response.status_code}"
