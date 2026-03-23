"""
ULN Enhanced Features Test Suite
================================
Tests for the 5 major ULN enhancements:
1. Real blockchain integration (hash chains, mining, verification, smart contracts)
2. Live royalty data analytics
3. ULN Analytics dashboard
4. Label onboarding workflow
5. Inter-label messaging
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "owner@bigmannentertainment.com"
TEST_PASSWORD = "Test1234!"


class TestAuth:
    """Authentication helper - get token for authenticated requests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        # Note: endpoint returns 'access_token' not 'token'
        token = data.get("access_token") or data.get("token")
        assert token, f"No token in response: {data}"
        return token
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        """Get headers with auth token"""
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }


class TestBlockchainEndpoints(TestAuth):
    """Test blockchain ledger endpoints"""
    
    def test_blockchain_stats(self, auth_headers):
        """GET /api/uln-enhanced/blockchain/stats - returns chain statistics"""
        response = requests.get(f"{BASE_URL}/api/uln-enhanced/blockchain/stats", headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") == True
        assert "total_blocks" in data
        assert "total_transactions" in data
        assert "pending_transactions" in data
        assert "active_contracts" in data
        assert "difficulty" in data
        print(f"Blockchain stats: {data['total_blocks']} blocks, {data['total_transactions']} txs")
    
    def test_get_blocks(self, auth_headers):
        """GET /api/uln-enhanced/blockchain/blocks - returns blocks list"""
        response = requests.get(f"{BASE_URL}/api/uln-enhanced/blockchain/blocks?limit=10", headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "blocks" in data
        assert "total" in data
        assert isinstance(data["blocks"], list)
        if data["blocks"]:
            block = data["blocks"][0]
            assert "index" in block
            assert "hash" in block
            assert "previous_hash" in block
        print(f"Retrieved {len(data['blocks'])} blocks, total: {data['total']}")
    
    def test_add_transaction(self, auth_headers):
        """POST /api/uln-enhanced/blockchain/transactions - adds pending transaction"""
        payload = {
            "tx_type": "label_action",
            "payload": {"action": "test_action", "data": "test_data"}
        }
        response = requests.post(f"{BASE_URL}/api/uln-enhanced/blockchain/transactions", 
                                 json=payload, headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") == True
        assert "transaction" in data
        tx = data["transaction"]
        assert tx["tx_type"] == "label_action"
        assert tx["status"] == "pending"
        assert "tx_id" in tx
        assert "tx_hash" in tx
        print(f"Created transaction: {tx['tx_id']}")
    
    def test_get_transactions(self, auth_headers):
        """GET /api/uln-enhanced/blockchain/transactions - returns transactions list"""
        response = requests.get(f"{BASE_URL}/api/uln-enhanced/blockchain/transactions?limit=20", headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") == True
        assert "transactions" in data
        assert "count" in data
        print(f"Retrieved {data['count']} transactions")
    
    def test_mine_block(self, auth_headers):
        """POST /api/uln-enhanced/blockchain/mine - mines pending transactions"""
        # First add a transaction to mine
        payload = {"tx_type": "test_mine", "payload": {"test": "mining"}}
        requests.post(f"{BASE_URL}/api/uln-enhanced/blockchain/transactions", 
                     json=payload, headers=auth_headers)
        
        # Now mine
        response = requests.post(f"{BASE_URL}/api/uln-enhanced/blockchain/mine", headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        # May return success=False if no pending transactions
        if data.get("success"):
            assert "block_index" in data
            assert "block_hash" in data
            assert "transactions_mined" in data
            print(f"Mined block #{data['block_index']} with {data['transactions_mined']} txs")
        else:
            print(f"Mining result: {data.get('message', 'No pending transactions')}")
    
    def test_verify_chain(self, auth_headers):
        """GET /api/uln-enhanced/blockchain/verify - verifies chain integrity"""
        response = requests.get(f"{BASE_URL}/api/uln-enhanced/blockchain/verify", headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") == True
        assert "valid" in data
        assert "blocks_checked" in data
        print(f"Chain valid: {data['valid']}, blocks checked: {data['blocks_checked']}")
    
    def test_deploy_contract(self, auth_headers):
        """POST /api/uln-enhanced/blockchain/contracts/deploy - deploys smart contract"""
        payload = {
            "contract_type": "rights_split",
            "label_id": "TEST-LABEL-001",
            "parameters": {
                "initial_state": {"rights_splits": {"master": 70, "publishing": 30}}
            }
        }
        response = requests.post(f"{BASE_URL}/api/uln-enhanced/blockchain/contracts/deploy",
                                json=payload, headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") == True
        assert "contract" in data
        contract = data["contract"]
        assert "contract_id" in contract
        assert "contract_address" in contract
        assert contract["contract_type"] == "rights_split"
        assert contract["status"] == "active"
        print(f"Deployed contract: {contract['contract_id']}")
    
    def test_get_contracts(self, auth_headers):
        """GET /api/uln-enhanced/blockchain/contracts - lists deployed contracts"""
        response = requests.get(f"{BASE_URL}/api/uln-enhanced/blockchain/contracts", headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") == True
        assert "contracts" in data
        assert "count" in data
        print(f"Retrieved {data['count']} contracts")


class TestAnalyticsEndpoints(TestAuth):
    """Test analytics dashboard endpoints"""
    
    def test_seed_royalties(self, auth_headers):
        """POST /api/uln-enhanced/analytics/seed-royalties - seeds sample data"""
        response = requests.post(f"{BASE_URL}/api/uln-enhanced/analytics/seed-royalties", headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") == True
        print(f"Seed result: {data.get('message', 'Seeded')}")
    
    def test_cross_label_performance(self, auth_headers):
        """GET /api/uln-enhanced/analytics/cross-label-performance - returns label rankings"""
        response = requests.get(f"{BASE_URL}/api/uln-enhanced/analytics/cross-label-performance", headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") == True
        assert "labels" in data
        assert "total" in data
        if data["labels"]:
            label = data["labels"][0]
            assert "label_id" in label
            assert "name" in label
            assert "total_royalties" in label
        print(f"Cross-label performance: {data['total']} labels")
    
    def test_revenue_trends(self, auth_headers):
        """GET /api/uln-enhanced/analytics/revenue-trends - returns monthly trends"""
        response = requests.get(f"{BASE_URL}/api/uln-enhanced/analytics/revenue-trends?months=12", headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") == True
        assert "trends" in data
        assert "period_months" in data
        if data["trends"]:
            trend = data["trends"][0]
            assert "month" in trend
            assert "revenue" in trend
            assert "transactions" in trend
        print(f"Revenue trends: {len(data['trends'])} months")
    
    def test_genre_breakdown(self, auth_headers):
        """GET /api/uln-enhanced/analytics/genre-breakdown - returns genre distribution"""
        response = requests.get(f"{BASE_URL}/api/uln-enhanced/analytics/genre-breakdown", headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") == True
        assert "genres" in data
        print(f"Genre breakdown: {len(data['genres'])} genres")
    
    def test_territory_breakdown(self, auth_headers):
        """GET /api/uln-enhanced/analytics/territory-breakdown - returns territory data"""
        response = requests.get(f"{BASE_URL}/api/uln-enhanced/analytics/territory-breakdown", headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") == True
        assert "territories" in data
        print(f"Territory breakdown: {len(data['territories'])} territories")
    
    def test_content_sharing_analytics(self, auth_headers):
        """GET /api/uln-enhanced/analytics/content-sharing - returns sharing analytics"""
        response = requests.get(f"{BASE_URL}/api/uln-enhanced/analytics/content-sharing", headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") == True
        assert "total_shared_content" in data
        assert "by_access_level" in data
        assert "top_sharers" in data
        print(f"Content sharing: {data['total_shared_content']} shared items")
    
    def test_dao_analytics(self, auth_headers):
        """GET /api/uln-enhanced/analytics/dao - returns DAO analytics"""
        response = requests.get(f"{BASE_URL}/api/uln-enhanced/analytics/dao", headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") == True
        assert "total_proposals" in data
        assert "by_status" in data
        assert "by_type" in data
        print(f"DAO analytics: {data['total_proposals']} proposals")


class TestOnboardingEndpoints(TestAuth):
    """Test label onboarding workflow endpoints"""
    
    @pytest.fixture(scope="class")
    def onboarding_session(self, auth_headers):
        """Create an onboarding session for testing"""
        response = requests.post(f"{BASE_URL}/api/uln-enhanced/onboarding/start", headers=auth_headers)
        assert response.status_code == 200, f"Failed to start onboarding: {response.text}"
        data = response.json()
        assert data.get("success") == True
        return data["session_id"]
    
    def test_start_onboarding(self, auth_headers):
        """POST /api/uln-enhanced/onboarding/start - creates session"""
        response = requests.post(f"{BASE_URL}/api/uln-enhanced/onboarding/start", headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") == True
        assert "session_id" in data
        assert "current_step" in data
        assert data["current_step"] == 1
        assert "steps" in data
        print(f"Started onboarding session: {data['session_id']}")
    
    def test_save_step(self, auth_headers, onboarding_session):
        """POST /api/uln-enhanced/onboarding/{session_id}/step - saves step data"""
        step_data = {
            "step": 1,
            "data": {
                "name": "Test Label",
                "label_type": "independent",
                "jurisdiction": "US",
                "headquarters": "New York, NY"
            }
        }
        response = requests.post(
            f"{BASE_URL}/api/uln-enhanced/onboarding/{onboarding_session}/step",
            json=step_data, headers=auth_headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") == True
        assert data["step_saved"] == 1
        assert data["next_step"] == 2
        print(f"Saved step 1, next step: {data['next_step']}")
    
    def test_get_session(self, auth_headers, onboarding_session):
        """GET /api/uln-enhanced/onboarding/{session_id} - gets session state"""
        response = requests.get(
            f"{BASE_URL}/api/uln-enhanced/onboarding/{onboarding_session}",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") == True
        assert "session" in data
        session = data["session"]
        assert "session_id" in session
        assert "current_step" in session
        assert "steps_completed" in session
        print(f"Session state: step {session['current_step']}, completed: {session['steps_completed']}")
    
    def test_complete_onboarding_flow(self, auth_headers):
        """Test complete onboarding flow through all steps"""
        # Start new session
        response = requests.post(f"{BASE_URL}/api/uln-enhanced/onboarding/start", headers=auth_headers)
        session_id = response.json()["session_id"]
        
        # Step 1: Basic Info
        requests.post(f"{BASE_URL}/api/uln-enhanced/onboarding/{session_id}/step",
                     json={"step": 1, "data": {"name": "Complete Test Label", "label_type": "independent", "jurisdiction": "US"}},
                     headers=auth_headers)
        
        # Step 2: Business Details
        requests.post(f"{BASE_URL}/api/uln-enhanced/onboarding/{session_id}/step",
                     json={"step": 2, "data": {"legal_name": "Complete Test Label LLC", "tax_status": "llc"}},
                     headers=auth_headers)
        
        # Step 3: Key Personnel
        requests.post(f"{BASE_URL}/api/uln-enhanced/onboarding/{session_id}/step",
                     json={"step": 3, "data": {"entities": [{"name": "John Doe", "role": "CEO"}]}},
                     headers=auth_headers)
        
        # Step 4: Smart Contract
        requests.post(f"{BASE_URL}/api/uln-enhanced/onboarding/{session_id}/step",
                     json={"step": 4, "data": {"contract_type": "rights_split", "dao_integration": False}},
                     headers=auth_headers)
        
        # Complete
        response = requests.post(f"{BASE_URL}/api/uln-enhanced/onboarding/{session_id}/complete", headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") == True
        assert data["status"] == "completed"
        assert "registration_payload" in data
        print(f"Completed onboarding: {data['registration_payload']['metadata_profile']['name']}")


class TestMessagingEndpoints(TestAuth):
    """Test inter-label messaging endpoints"""
    
    @pytest.fixture(scope="class")
    def test_thread(self, auth_headers):
        """Create a test thread for messaging tests"""
        payload = {
            "sender_label_id": "TEST-SENDER-001",
            "recipient_label_id": "TEST-RECIPIENT-001",
            "subject": "Test Thread for Messaging"
        }
        response = requests.post(f"{BASE_URL}/api/uln-enhanced/messaging/threads",
                                json=payload, headers=auth_headers)
        assert response.status_code == 200, f"Failed to create thread: {response.text}"
        data = response.json()
        assert data.get("success") == True
        return data["thread_id"]
    
    def test_create_thread(self, auth_headers):
        """POST /api/uln-enhanced/messaging/threads - creates thread"""
        payload = {
            "sender_label_id": "LABEL-A",
            "recipient_label_id": "LABEL-B",
            "subject": "Test Collaboration Discussion"
        }
        response = requests.post(f"{BASE_URL}/api/uln-enhanced/messaging/threads",
                                json=payload, headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") == True
        assert "thread_id" in data
        assert "thread" in data
        thread = data["thread"]
        assert thread["subject"] == "Test Collaboration Discussion"
        assert "LABEL-A" in thread["participants"]
        assert "LABEL-B" in thread["participants"]
        print(f"Created thread: {data['thread_id']}")
    
    def test_send_message(self, auth_headers, test_thread):
        """POST /api/uln-enhanced/messaging/messages - sends message"""
        payload = {
            "thread_id": test_thread,
            "sender_label_id": "TEST-SENDER-001",
            "sender_name": "Test Sender Label",
            "content": "Hello, this is a test message!"
        }
        response = requests.post(f"{BASE_URL}/api/uln-enhanced/messaging/messages",
                                json=payload, headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") == True
        assert "message_id" in data
        assert "message" in data
        msg = data["message"]
        assert msg["content"] == "Hello, this is a test message!"
        print(f"Sent message: {data['message_id']}")
    
    def test_get_threads(self, auth_headers, test_thread):
        """GET /api/uln-enhanced/messaging/threads?label_id= - gets threads for label"""
        response = requests.get(
            f"{BASE_URL}/api/uln-enhanced/messaging/threads?label_id=TEST-SENDER-001",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") == True
        assert "threads" in data
        assert "count" in data
        print(f"Retrieved {data['count']} threads for label")
    
    def test_get_thread_messages(self, auth_headers, test_thread):
        """GET /api/uln-enhanced/messaging/threads/{id} - gets messages in thread"""
        response = requests.get(
            f"{BASE_URL}/api/uln-enhanced/messaging/threads/{test_thread}",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("success") == True
        assert "thread" in data
        assert "messages" in data
        assert "total" in data
        print(f"Thread has {data['total']} messages")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
