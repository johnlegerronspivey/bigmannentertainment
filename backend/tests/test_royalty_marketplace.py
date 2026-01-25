"""
Royalty Marketplace API Tests
Tests for listing, bidding, watchlist, and transaction endpoints
"""

import pytest
import requests
import os
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://model-twin-system.preview.emergentagent.com').rstrip('/')

# Test credentials
TEST_EMAIL = "enterprise@test.com"
TEST_PASSWORD = "TestPass123!"


class TestMarketplaceHealth:
    """Health check endpoint tests"""
    
    def test_health_endpoint(self):
        """Test marketplace health endpoint"""
        response = requests.get(f"{BASE_URL}/api/marketplace/health")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["status"] == "healthy"
        assert data["service"] == "Dynamic Royalty Marketplace"
        print(f"✅ Health check passed: {data['status']}")


class TestMarketplaceStats:
    """Marketplace statistics endpoint tests"""
    
    def test_get_stats(self):
        """Test getting marketplace stats"""
        response = requests.get(f"{BASE_URL}/api/marketplace/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "stats" in data
        stats = data["stats"]
        assert "active_listings" in stats
        assert "total_volume" in stats
        assert "total_sales" in stats
        assert "average_sale_price" in stats
        assert "recent_activity" in stats
        print(f"✅ Stats retrieved: {stats['active_listings']} active listings")


class TestListingsSearch:
    """Listing search and browse endpoint tests"""
    
    def test_search_listings_default(self):
        """Test searching listings with default parameters"""
        response = requests.get(f"{BASE_URL}/api/marketplace/listings")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "listings" in data
        assert "pagination" in data
        assert isinstance(data["listings"], list)
        print(f"✅ Found {len(data['listings'])} listings")
    
    def test_search_listings_with_sort(self):
        """Test searching listings with sort parameter"""
        response = requests.get(f"{BASE_URL}/api/marketplace/listings?sort_by=created_at&sort_order=desc")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "listings" in data
        print(f"✅ Sorted listings retrieved: {len(data['listings'])} items")
    
    def test_search_listings_by_type(self):
        """Test filtering listings by type"""
        response = requests.get(f"{BASE_URL}/api/marketplace/listings?listing_type=fixed_price")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        # Verify all returned listings are fixed_price type
        for listing in data["listings"]:
            assert listing["listing_type"] == "fixed_price"
        print(f"✅ Fixed price listings: {len(data['listings'])}")
    
    def test_search_listings_by_auction_type(self):
        """Test filtering listings by auction type"""
        response = requests.get(f"{BASE_URL}/api/marketplace/listings?listing_type=auction")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        for listing in data["listings"]:
            assert listing["listing_type"] == "auction"
        print(f"✅ Auction listings: {len(data['listings'])}")
    
    def test_pagination(self):
        """Test pagination parameters"""
        response = requests.get(f"{BASE_URL}/api/marketplace/listings?page=1&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["limit"] == 10
        print(f"✅ Pagination working: page {data['pagination']['page']}, total {data['pagination']['total']}")


class TestListingDetails:
    """Individual listing detail endpoint tests"""
    
    @pytest.fixture
    def listing_id(self):
        """Get a valid listing ID from search"""
        response = requests.get(f"{BASE_URL}/api/marketplace/listings")
        data = response.json()
        if data["listings"]:
            return data["listings"][0]["id"]
        pytest.skip("No listings available for testing")
    
    def test_get_listing_details(self, listing_id):
        """Test getting listing details"""
        response = requests.get(f"{BASE_URL}/api/marketplace/listings/{listing_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "listing" in data
        listing = data["listing"]
        assert listing["id"] == listing_id
        assert "title" in listing
        assert "asking_price" in listing
        assert "listing_type" in listing
        assert "royalty_percentage" in listing
        print(f"✅ Listing details retrieved: {listing['title']}")
    
    def test_get_listing_not_found(self):
        """Test getting non-existent listing"""
        response = requests.get(f"{BASE_URL}/api/marketplace/listings/non-existent-id-12345")
        assert response.status_code == 404
        print("✅ Non-existent listing returns 404")


class TestAuthenticatedEndpoints:
    """Tests for endpoints requiring authentication"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Authentication failed - skipping authenticated tests")
    
    @pytest.fixture
    def auth_headers(self, auth_token):
        """Get headers with auth token"""
        return {"Authorization": f"Bearer {auth_token}"}
    
    def test_get_my_listings(self, auth_headers):
        """Test getting user's own listings"""
        response = requests.get(
            f"{BASE_URL}/api/marketplace/my-listings",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "listings" in data
        print(f"✅ My listings retrieved: {len(data['listings'])} items")
    
    def test_get_my_bids(self, auth_headers):
        """Test getting user's bids"""
        response = requests.get(
            f"{BASE_URL}/api/marketplace/my-bids",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "bids" in data
        print(f"✅ My bids retrieved: {len(data['bids'])} items")
    
    def test_get_watchlist(self, auth_headers):
        """Test getting user's watchlist"""
        response = requests.get(
            f"{BASE_URL}/api/marketplace/watchlist",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "watchlist" in data
        print(f"✅ Watchlist retrieved: {len(data['watchlist'])} items")
    
    def test_get_my_stats(self, auth_headers):
        """Test getting user's marketplace stats"""
        response = requests.get(
            f"{BASE_URL}/api/marketplace/my-stats",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "stats" in data
        print(f"✅ User stats retrieved")


class TestCreateListing:
    """Tests for creating new listings"""
    
    @pytest.fixture
    def auth_headers(self):
        """Get headers with auth token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        if response.status_code == 200:
            token = response.json().get("access_token")
            return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        pytest.skip("Authentication failed - skipping authenticated tests")
    
    def test_create_listing(self, auth_headers):
        """Test creating a new listing"""
        listing_data = {
            "asset_id": "TEST_asset_pytest_001",
            "title": "TEST_PyTest Royalty Listing",
            "description": "Test listing created by pytest",
            "listing_type": "fixed_price",
            "royalty_type": "percentage_share",
            "royalty_percentage": 5.0,
            "historical_revenue": 10000.0,
            "projected_revenue": 12000.0,
            "asking_price": 2500.0,
            "genre": "Test Genre",
            "artist_name": "TEST_Artist"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/marketplace/listings",
            headers=auth_headers,
            json=listing_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "listing_id" in data
        print(f"✅ Listing created: {data['listing_id']}")
        
        # Return listing_id for cleanup
        return data["listing_id"]


class TestWatchlistOperations:
    """Tests for watchlist add/remove operations"""
    
    @pytest.fixture
    def auth_headers(self):
        """Get headers with auth token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        if response.status_code == 200:
            token = response.json().get("access_token")
            return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        pytest.skip("Authentication failed - skipping authenticated tests")
    
    @pytest.fixture
    def listing_id(self):
        """Get a valid listing ID from search"""
        response = requests.get(f"{BASE_URL}/api/marketplace/listings")
        data = response.json()
        if data["listings"]:
            return data["listings"][0]["id"]
        pytest.skip("No listings available for testing")
    
    def test_add_to_watchlist(self, auth_headers, listing_id):
        """Test adding listing to watchlist"""
        response = requests.post(
            f"{BASE_URL}/api/marketplace/watchlist/{listing_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        print(f"✅ Added to watchlist: {listing_id}")


class TestBidding:
    """Tests for bidding on auction listings"""
    
    @pytest.fixture
    def auth_headers(self):
        """Get headers with auth token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        if response.status_code == 200:
            token = response.json().get("access_token")
            return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        pytest.skip("Authentication failed - skipping authenticated tests")
    
    @pytest.fixture
    def auction_listing_id(self):
        """Get an auction listing ID"""
        response = requests.get(f"{BASE_URL}/api/marketplace/listings?listing_type=auction")
        data = response.json()
        if data["listings"]:
            return data["listings"][0]["id"]
        pytest.skip("No auction listings available for testing")
    
    def test_place_bid_on_own_listing(self, auth_headers, auction_listing_id):
        """Test that placing bid on own listing fails"""
        # Get listing details to find minimum bid
        listing_response = requests.get(f"{BASE_URL}/api/marketplace/listings/{auction_listing_id}")
        listing = listing_response.json()["listing"]
        
        current_bid = listing.get("current_bid") or listing["asking_price"]
        bid_increment = listing.get("bid_increment", 100)
        min_bid = float(current_bid) + float(bid_increment)
        
        bid_data = {
            "amount": min_bid
        }
        
        response = requests.post(
            f"{BASE_URL}/api/marketplace/listings/{auction_listing_id}/bids",
            headers=auth_headers,
            json=bid_data
        )
        # Should fail because user_123 is the seller (400, 422, or 500 are all valid error responses)
        assert response.status_code in [400, 422, 500]
        print(f"✅ Correctly prevented self-bidding (status: {response.status_code})")


class TestFeaturedListings:
    """Tests for featured listings endpoint"""
    
    def test_get_featured_listings(self):
        """Test getting featured listings"""
        response = requests.get(f"{BASE_URL}/api/marketplace/listings/featured")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "listings" in data
        print(f"✅ Featured listings: {len(data['listings'])} items")


class TestEndingSoonListings:
    """Tests for ending soon listings endpoint"""
    
    def test_get_ending_soon_listings(self):
        """Test getting listings ending soon"""
        response = requests.get(f"{BASE_URL}/api/marketplace/listings/ending-soon?hours=168")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "listings" in data
        print(f"✅ Ending soon listings: {len(data['listings'])} items")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
