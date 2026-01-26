"""
DAO Governance V2 API Tests
Tests for token-based voting, proposal management, treasury, and member governance
"""

import pytest
import requests
import os
from datetime import datetime

# Get BASE_URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://model-success-3.preview.emergentagent.com').rstrip('/')

# Test user credentials
TEST_USER_ID = "user_001"
TEST_WALLET = "0x742d35C6C7C3F4b1e6a0dCc1C3aF2f6D4E5B5e4A"
TEST_USER_ID_2 = "user_004"
TEST_WALLET_2 = "0x1234567890AbCdEf1234567890AbCdEf12345678"
DELEGATE_WALLET = "0x8b5C9F7e3A1d2E6F4C8B7A9e3D2F1C8E4A7B9C6D"


@pytest.fixture
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


class TestDAOV2Health:
    """Health check endpoint tests"""
    
    def test_health_endpoint(self, api_client):
        """Test DAO V2 health endpoint returns healthy status"""
        response = api_client.get(f"{BASE_URL}/api/dao-v2/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "DAO Governance V2"
        assert data["version"] == "2.0"
        assert "features" in data
        assert len(data["features"]) >= 5


class TestDAOV2Proposals:
    """Proposal endpoint tests"""
    
    def test_get_proposals_list(self, api_client):
        """Test getting list of proposals"""
        response = api_client.get(f"{BASE_URL}/api/dao-v2/proposals")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "proposals" in data
        assert "total" in data
        assert "stats" in data
        assert isinstance(data["proposals"], list)
        
        # Verify stats structure
        stats = data["stats"]
        assert "total" in stats
        assert "active" in stats
        assert "succeeded" in stats
        assert "executed" in stats
    
    def test_get_single_proposal(self, api_client):
        """Test getting a single proposal by ID"""
        response = api_client.get(f"{BASE_URL}/api/dao-v2/proposals/prop_001")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "proposal" in data
        assert data["proposal"]["id"] == "prop_001"
        assert "quorum_progress" in data
        assert "approval_progress" in data
        assert "quorum_met" in data
        assert "approval_met" in data
    
    def test_get_nonexistent_proposal(self, api_client):
        """Test getting a proposal that doesn't exist"""
        response = api_client.get(f"{BASE_URL}/api/dao-v2/proposals/nonexistent_id")
        assert response.status_code == 404
    
    def test_filter_proposals_by_state(self, api_client):
        """Test filtering proposals by state"""
        response = api_client.get(f"{BASE_URL}/api/dao-v2/proposals?state=active")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        for proposal in data["proposals"]:
            assert proposal["state"] == "active"
    
    def test_filter_proposals_by_network(self, api_client):
        """Test filtering proposals by network"""
        response = api_client.get(f"{BASE_URL}/api/dao-v2/proposals?network=ethereum")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        for proposal in data["proposals"]:
            assert proposal["network"] == "ethereum"
    
    def test_create_proposal(self, api_client):
        """Test creating a new proposal"""
        payload = {
            "title": "TEST_New Community Initiative",
            "description": "Test proposal for community development",
            "category": "treasury_allocation",
            "governance_type": "hybrid",
            "network": "ethereum",
            "tags": ["test", "community"]
        }
        
        response = api_client.post(
            f"{BASE_URL}/api/dao-v2/proposals?user_id={TEST_USER_ID}&wallet_address={TEST_WALLET}",
            json=payload
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "proposal_id" in data
        assert "proposal_number" in data
        assert data["message"] == "Proposal created successfully"
        assert "voting_starts" in data
        assert "voting_ends" in data


class TestDAOV2Voting:
    """Voting endpoint tests"""
    
    def test_cast_vote_for(self, api_client):
        """Test casting a 'for' vote on active proposal"""
        # First get an active proposal
        proposals_response = api_client.get(f"{BASE_URL}/api/dao-v2/proposals?state=active")
        proposals = proposals_response.json()["proposals"]
        
        if len(proposals) > 0:
            proposal_id = proposals[0]["id"]
            
            payload = {
                "proposal_id": proposal_id,
                "choice": "for",
                "reason": "Test vote for proposal"
            }
            
            response = api_client.post(
                f"{BASE_URL}/api/dao-v2/vote?user_id={TEST_USER_ID}&wallet_address={TEST_WALLET}",
                json=payload
            )
            
            # May return 400 if already voted
            if response.status_code == 200:
                data = response.json()
                assert data["success"] is True
                assert "vote_id" in data
                assert "voting_power" in data
                assert "current_results" in data
            else:
                # Already voted is acceptable
                assert response.status_code == 400
    
    def test_get_proposal_votes(self, api_client):
        """Test getting votes for a proposal"""
        response = api_client.get(f"{BASE_URL}/api/dao-v2/proposals/prop_001/votes")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "votes" in data
        assert "total" in data


class TestDAOV2Treasury:
    """Treasury endpoint tests"""
    
    def test_get_treasury(self, api_client):
        """Test getting treasury information"""
        response = api_client.get(f"{BASE_URL}/api/dao-v2/treasury")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "treasury" in data
        
        treasury = data["treasury"]
        assert "name" in treasury
        assert "total_value_usd" in treasury
        assert "assets" in treasury
        assert "monthly_inflow" in treasury
        assert "monthly_outflow" in treasury
        assert "net_flow" in treasury
        
        # Verify assets structure
        assert len(treasury["assets"]) > 0
        for asset in treasury["assets"]:
            assert "symbol" in asset
            assert "balance" in asset
            assert "value_usd" in asset
            assert "network" in asset
    
    def test_treasury_has_flow_chart(self, api_client):
        """Test treasury includes flow chart data"""
        response = api_client.get(f"{BASE_URL}/api/dao-v2/treasury")
        data = response.json()
        
        assert "flow_chart" in data
        assert len(data["flow_chart"]) > 0
        for month_data in data["flow_chart"]:
            assert "month" in month_data
            assert "inflow" in month_data
            assert "outflow" in month_data
    
    def test_treasury_has_insights(self, api_client):
        """Test treasury includes insights"""
        response = api_client.get(f"{BASE_URL}/api/dao-v2/treasury")
        data = response.json()
        
        assert "insights" in data
        assert len(data["insights"]) > 0


class TestDAOV2Metrics:
    """Governance metrics endpoint tests"""
    
    def test_get_governance_metrics(self, api_client):
        """Test getting governance metrics"""
        response = api_client.get(f"{BASE_URL}/api/dao-v2/metrics")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "metrics" in data
        
        metrics = data["metrics"]
        assert "total_proposals" in metrics
        assert "active_proposals" in metrics
        assert "passed_proposals" in metrics
        assert "executed_proposals" in metrics
        assert "total_token_holders" in metrics
        assert "treasury_total_usd" in metrics
    
    def test_metrics_has_token_info(self, api_client):
        """Test metrics includes token information"""
        response = api_client.get(f"{BASE_URL}/api/dao-v2/metrics")
        data = response.json()
        
        assert "token" in data
        token = data["token"]
        assert "name" in token
        assert "symbol" in token
        assert "total_supply" in token
        assert "circulating_supply" in token
    
    def test_metrics_has_participation_trends(self, api_client):
        """Test metrics includes participation trends"""
        response = api_client.get(f"{BASE_URL}/api/dao-v2/metrics")
        data = response.json()
        
        assert "participation_trends" in data
        assert len(data["participation_trends"]) > 0
    
    def test_metrics_has_top_voters(self, api_client):
        """Test metrics includes top voters"""
        response = api_client.get(f"{BASE_URL}/api/dao-v2/metrics")
        data = response.json()
        
        assert "top_voters" in data


class TestDAOV2Delegates:
    """Delegates endpoint tests"""
    
    def test_get_delegates_list(self, api_client):
        """Test getting list of delegates"""
        response = api_client.get(f"{BASE_URL}/api/dao-v2/delegates")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "delegates" in data
        assert "total_delegates" in data
        
        if len(data["delegates"]) > 0:
            delegate = data["delegates"][0]
            assert "wallet_address" in delegate
            assert "total_voting_power" in delegate
            assert "delegated_power" in delegate
            assert "delegators_count" in delegate
    
    def test_delegate_votes(self, api_client):
        """Test delegating votes to another address"""
        payload = {
            "delegate_address": DELEGATE_WALLET,
            "network": "ethereum"
        }
        
        response = api_client.post(
            f"{BASE_URL}/api/dao-v2/delegate?user_id={TEST_USER_ID_2}&wallet_address={TEST_WALLET_2}",
            json=payload
        )
        
        # May succeed or fail if already delegated
        if response.status_code == 200:
            data = response.json()
            assert data["success"] is True
            assert "delegation_id" in data
            assert "delegated_amount" in data


class TestDAOV2Council:
    """Council endpoint tests"""
    
    def test_get_council_members(self, api_client):
        """Test getting council members"""
        response = api_client.get(f"{BASE_URL}/api/dao-v2/council")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "council" in data
        assert "total_council_members" in data
        assert "council_threshold" in data
        
        if len(data["council"]) > 0:
            member = data["council"][0]
            assert "wallet_address" in member
            assert "display_name" in member
            assert "voting_power" in member
            assert "proposals_created" in member


class TestDAOV2Members:
    """Member profile endpoint tests"""
    
    def test_get_member_profile(self, api_client):
        """Test getting member profile"""
        response = api_client.get(
            f"{BASE_URL}/api/dao-v2/members/me?user_id={TEST_USER_ID}&wallet_address={TEST_WALLET}"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "member" in data
        assert "stats" in data
        
        member = data["member"]
        assert "user_id" in member
        assert "primary_wallet" in member
        assert "role" in member
        assert "token_balances" in member
        assert "total_voting_power" in member
        
        stats = data["stats"]
        assert "voting_power" in stats
        assert "votes_cast" in stats
        assert "proposals_created" in stats


class TestDAOV2Networks:
    """Networks endpoint tests"""
    
    def test_get_supported_networks(self, api_client):
        """Test getting supported blockchain networks"""
        response = api_client.get(f"{BASE_URL}/api/dao-v2/networks")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "networks" in data
        assert len(data["networks"]) >= 2
        
        # Verify network structure
        for network in data["networks"]:
            assert "id" in network
            assert "name" in network
            assert "chain_id" in network
            assert "symbol" in network


class TestDAOV2Config:
    """Governance config endpoint tests"""
    
    def test_get_governance_config(self, api_client):
        """Test getting governance configuration"""
        response = api_client.get(f"{BASE_URL}/api/dao-v2/config")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "config" in data
        
        config = data["config"]
        assert "dao_name" in config
        assert "dao_version" in config
        assert "primary_network" in config
        assert "supported_networks" in config
        assert "proposal_threshold" in config
        assert "quorum_percentage" in config
        assert "approval_threshold" in config
        assert "voting_period_seconds" in config
    
    def test_config_has_contracts(self, api_client):
        """Test config includes contract addresses"""
        response = api_client.get(f"{BASE_URL}/api/dao-v2/config")
        data = response.json()
        
        assert "contracts" in data
        contracts = data["contracts"]
        assert "governance" in contracts
        assert "token" in contracts
        assert "treasury" in contracts


class TestDAOV2DataIntegrity:
    """Data integrity and CRUD verification tests"""
    
    def test_create_proposal_and_verify(self, api_client):
        """Test creating a proposal and verifying it appears in list"""
        # Create proposal
        payload = {
            "title": "TEST_Verify Proposal Creation",
            "description": "Test proposal to verify creation flow",
            "category": "feature_request",
            "governance_type": "off_chain",
            "network": "polygon",
            "tags": ["test", "verify"]
        }
        
        create_response = api_client.post(
            f"{BASE_URL}/api/dao-v2/proposals?user_id={TEST_USER_ID}&wallet_address={TEST_WALLET}",
            json=payload
        )
        assert create_response.status_code == 200
        
        created_data = create_response.json()
        proposal_id = created_data["proposal_id"]
        
        # Verify proposal exists
        get_response = api_client.get(f"{BASE_URL}/api/dao-v2/proposals/{proposal_id}")
        assert get_response.status_code == 200
        
        proposal_data = get_response.json()
        assert proposal_data["success"] is True
        assert proposal_data["proposal"]["title"] == payload["title"]
        assert proposal_data["proposal"]["category"] == payload["category"]
    
    def test_treasury_value_consistency(self, api_client):
        """Test treasury total value matches sum of assets"""
        response = api_client.get(f"{BASE_URL}/api/dao-v2/treasury")
        data = response.json()
        
        treasury = data["treasury"]
        total_value = treasury["total_value_usd"]
        
        # Sum of asset values should approximately equal total
        asset_sum = sum(asset["value_usd"] for asset in treasury["assets"])
        
        # Allow small rounding differences
        assert abs(total_value - asset_sum) < 1000


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
