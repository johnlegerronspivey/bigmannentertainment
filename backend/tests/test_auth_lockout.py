"""
Authentication Lockout Feature Tests
Tests for the P0 account lockout bug fix:
- MAX_LOGIN_ATTEMPTS = 10
- LOCKOUT_DURATION_MINUTES = 15
- Auto-clear expired lockouts
- Remaining attempts in error messages
- Admin unlock endpoints
"""

import pytest
import requests
import os
from datetime import datetime, timedelta
from pymongo import MongoClient

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'bigmann_entertainment_production')

# Test credentials
OWNER_EMAIL = "owner@bigmannentertainment.com"
OWNER_PASSWORD = "Test1234!"
ADMIN_EMAIL = "cveadmin@test.com"
ADMIN_PASSWORD = "Test1234!"
TEST_USER_EMAIL = "lockout_test_user@bigmannentertainment.com"


@pytest.fixture(scope="module")
def mongo_client():
    """MongoDB client fixture for direct DB manipulation"""
    client = MongoClient(MONGO_URL)
    yield client[DB_NAME]
    client.close()


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def admin_token(api_client):
    """Get admin authentication token"""
    response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    # Try owner account as fallback
    response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        "email": OWNER_EMAIL,
        "password": OWNER_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip("Admin authentication failed - skipping admin tests")


@pytest.fixture(autouse=True)
def cleanup_test_user(mongo_client):
    """Cleanup test user lockout state before/after each test"""
    yield
    # Reset test user's lockout state after test
    mongo_client.users.update_one(
        {"email": TEST_USER_EMAIL},
        {"$set": {"failed_login_attempts": 0, "locked_until": None}}
    )


class TestLoginSuccess:
    """Tests for successful login flow"""
    
    def test_login_with_valid_credentials(self, api_client, mongo_client):
        """Test successful login with correct credentials"""
        # First reset any lockout state
        mongo_client.users.update_one(
            {"email": OWNER_EMAIL},
            {"$set": {"failed_login_attempts": 0, "locked_until": None}}
        )
        
        response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "email": OWNER_EMAIL,
            "password": OWNER_PASSWORD
        })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "access_token" in data, "Response should contain access_token"
        assert "refresh_token" in data, "Response should contain refresh_token"
        assert "user" in data, "Response should contain user object"
        assert data["user"]["email"] == OWNER_EMAIL
    
    def test_successful_login_resets_failed_attempts(self, api_client, mongo_client):
        """Verify successful login resets failed_login_attempts to 0"""
        # Set some failed attempts first
        mongo_client.users.update_one(
            {"email": OWNER_EMAIL},
            {"$set": {"failed_login_attempts": 5, "locked_until": None}}
        )
        
        # Login successfully
        response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "email": OWNER_EMAIL,
            "password": OWNER_PASSWORD
        })
        assert response.status_code == 200
        
        # Verify failed_login_attempts is reset
        user = mongo_client.users.find_one({"email": OWNER_EMAIL})
        assert user["failed_login_attempts"] == 0, "Failed attempts should be reset to 0"
        assert user["locked_until"] is None, "locked_until should be None"


class TestFailedLoginWithRemainingAttempts:
    """Tests for failed login showing remaining attempts"""
    
    def test_failed_login_shows_remaining_attempts(self, api_client, mongo_client):
        """Test that failed login shows remaining attempts in error message"""
        # Reset lockout state first
        mongo_client.users.update_one(
            {"email": OWNER_EMAIL},
            {"$set": {"failed_login_attempts": 0, "locked_until": None}}
        )
        
        response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "email": OWNER_EMAIL,
            "password": "WrongPassword123!"
        })
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        
        data = response.json()
        detail = data.get("detail", "")
        
        # Should show 9 remaining attempts (10 max - 1 failed = 9)
        assert "9 attempt(s) remaining" in detail, f"Expected '9 attempt(s) remaining' in: {detail}"
        assert "Invalid email or password" in detail
    
    def test_failed_attempts_decrement_correctly(self, api_client, mongo_client):
        """Test remaining attempts decrement with each failed login"""
        # Reset to clean state
        mongo_client.users.update_one(
            {"email": OWNER_EMAIL},
            {"$set": {"failed_login_attempts": 0, "locked_until": None}}
        )
        
        # First failed attempt - should show 9 remaining
        response1 = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "email": OWNER_EMAIL,
            "password": "WrongPassword1"
        })
        assert "9 attempt(s) remaining" in response1.json().get("detail", "")
        
        # Second failed attempt - should show 8 remaining
        response2 = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "email": OWNER_EMAIL,
            "password": "WrongPassword2"
        })
        assert "8 attempt(s) remaining" in response2.json().get("detail", "")
        
        # Verify in database
        user = mongo_client.users.find_one({"email": OWNER_EMAIL})
        assert user["failed_login_attempts"] == 2
        
        # Reset for other tests
        mongo_client.users.update_one(
            {"email": OWNER_EMAIL},
            {"$set": {"failed_login_attempts": 0, "locked_until": None}}
        )


class TestAutoExpiredLockoutReset:
    """Tests for auto-clearing expired lockouts (the P0 bug fix)"""
    
    def test_expired_lockout_auto_clears_failed_attempts(self, api_client, mongo_client):
        """CRITICAL: After lockout expires, failed_login_attempts should reset to 0"""
        # Set an EXPIRED lockout (in the past) with high failed attempts
        expired_time = datetime.utcnow() - timedelta(minutes=30)  # 30 minutes ago
        mongo_client.users.update_one(
            {"email": OWNER_EMAIL},
            {"$set": {"failed_login_attempts": 10, "locked_until": expired_time}}
        )
        
        # Attempt login with wrong password - should NOT immediately re-lock
        response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "email": OWNER_EMAIL,
            "password": "WrongPasswordAfterExpiry"
        })
        
        # Should get 401 (wrong password) not 423 (locked)
        assert response.status_code == 401, f"Expected 401, got {response.status_code} - expired lock should auto-clear"
        
        # Should show 9 remaining attempts (fresh start)
        detail = response.json().get("detail", "")
        assert "9 attempt(s) remaining" in detail, f"Expected 9 remaining after auto-reset: {detail}"
        
        # Verify in DB that failed_attempts was reset
        user = mongo_client.users.find_one({"email": OWNER_EMAIL})
        assert user["failed_login_attempts"] == 1, "Should be 1 (just this failed attempt)"
        
        # Cleanup
        mongo_client.users.update_one(
            {"email": OWNER_EMAIL},
            {"$set": {"failed_login_attempts": 0, "locked_until": None}}
        )
    
    def test_expired_lockout_allows_successful_login(self, api_client, mongo_client):
        """After lockout expires, user can login successfully"""
        # Set an expired lockout
        expired_time = datetime.utcnow() - timedelta(minutes=30)
        mongo_client.users.update_one(
            {"email": OWNER_EMAIL},
            {"$set": {"failed_login_attempts": 10, "locked_until": expired_time}}
        )
        
        # Should be able to login with correct password
        response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "email": OWNER_EMAIL,
            "password": OWNER_PASSWORD
        })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code} - should login after expired lock"
        
        # Verify lockout cleared
        user = mongo_client.users.find_one({"email": OWNER_EMAIL})
        assert user["failed_login_attempts"] == 0
        assert user["locked_until"] is None


class TestAccountLockAfter10Attempts:
    """Tests for account locking after MAX_LOGIN_ATTEMPTS (10)"""
    
    def test_account_locks_after_10_failed_attempts(self, api_client, mongo_client):
        """Test that account locks after exactly 10 failed attempts"""
        # Reset to clean state
        mongo_client.users.update_one(
            {"email": OWNER_EMAIL},
            {"$set": {"failed_login_attempts": 0, "locked_until": None}}
        )
        
        # Make 9 failed attempts (should not lock)
        for i in range(9):
            response = api_client.post(f"{BASE_URL}/api/auth/login", json={
                "email": OWNER_EMAIL,
                "password": f"WrongPassword{i}"
            })
            assert response.status_code == 401, f"Attempt {i+1} should return 401"
        
        # 10th attempt should trigger lock
        response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "email": OWNER_EMAIL,
            "password": "WrongPassword10"
        })
        
        assert response.status_code == 423, f"Expected 423 (locked) after 10 attempts, got {response.status_code}"
        
        detail = response.json().get("detail", "")
        assert "Too many failed attempts" in detail or "Account locked" in detail
        assert "15 minutes" in detail, f"Should mention 15 minute lockout: {detail}"
        
        # Verify in database
        user = mongo_client.users.find_one({"email": OWNER_EMAIL})
        assert user["failed_login_attempts"] == 10
        assert user["locked_until"] is not None
        assert user["locked_until"] > datetime.utcnow()
        
        # Cleanup
        mongo_client.users.update_one(
            {"email": OWNER_EMAIL},
            {"$set": {"failed_login_attempts": 0, "locked_until": None}}
        )


class TestLockedAccountResponse:
    """Tests for locked account behavior"""
    
    def test_locked_account_returns_423_with_time_remaining(self, api_client, mongo_client):
        """Test locked account returns 423 with time remaining message"""
        # Set active lockout (15 minutes in the future)
        lock_time = datetime.utcnow() + timedelta(minutes=15)
        mongo_client.users.update_one(
            {"email": OWNER_EMAIL},
            {"$set": {"failed_login_attempts": 10, "locked_until": lock_time}}
        )
        
        response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "email": OWNER_EMAIL,
            "password": OWNER_PASSWORD  # Even correct password should fail
        })
        
        assert response.status_code == 423, f"Expected 423, got {response.status_code}"
        
        detail = response.json().get("detail", "")
        assert "locked" in detail.lower(), f"Should mention 'locked': {detail}"
        assert "minute" in detail.lower(), f"Should mention time remaining: {detail}"
        
        # Cleanup
        mongo_client.users.update_one(
            {"email": OWNER_EMAIL},
            {"$set": {"failed_login_attempts": 0, "locked_until": None}}
        )


class TestAdminUnlockEndpoints:
    """Tests for admin account management endpoints"""
    
    def test_get_locked_accounts_requires_admin(self, api_client):
        """Test that GET /api/auth/admin/locked-accounts requires admin auth"""
        # Without auth
        response = api_client.get(f"{BASE_URL}/api/auth/admin/locked-accounts")
        assert response.status_code in [401, 403], "Should require authentication"
    
    def test_get_locked_accounts_returns_list(self, api_client, admin_token, mongo_client):
        """Test admin can get list of locked accounts"""
        # Create a locked account for testing
        lock_time = datetime.utcnow() + timedelta(minutes=15)
        mongo_client.users.update_one(
            {"email": OWNER_EMAIL},
            {"$set": {"failed_login_attempts": 10, "locked_until": lock_time}}
        )
        
        response = api_client.get(
            f"{BASE_URL}/api/auth/admin/locked-accounts",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "locked_accounts" in data
        assert isinstance(data["locked_accounts"], list)
        
        # Should find our locked account
        locked_emails = [acc.get("email") for acc in data["locked_accounts"]]
        assert OWNER_EMAIL in locked_emails, f"Should find {OWNER_EMAIL} in locked accounts"
        
        # Cleanup
        mongo_client.users.update_one(
            {"email": OWNER_EMAIL},
            {"$set": {"failed_login_attempts": 0, "locked_until": None}}
        )
    
    def test_admin_unlock_account_success(self, api_client, admin_token, mongo_client):
        """Test admin can unlock a locked account"""
        # Lock the account first
        lock_time = datetime.utcnow() + timedelta(minutes=15)
        mongo_client.users.update_one(
            {"email": OWNER_EMAIL},
            {"$set": {"failed_login_attempts": 10, "locked_until": lock_time}}
        )
        
        response = api_client.post(
            f"{BASE_URL}/api/auth/admin/unlock-account",
            json={"email": OWNER_EMAIL},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Verify in database
        user = mongo_client.users.find_one({"email": OWNER_EMAIL})
        assert user["failed_login_attempts"] == 0, "Failed attempts should be reset"
        assert user["locked_until"] is None, "locked_until should be cleared"
        
        # Verify message
        data = response.json()
        assert "unlocked" in data.get("message", "").lower()
    
    def test_admin_unlock_nonexistent_user_returns_404(self, api_client, admin_token):
        """Test unlocking nonexistent user returns 404"""
        response = api_client.post(
            f"{BASE_URL}/api/auth/admin/unlock-account",
            json={"email": "nonexistent_user_that_does_not_exist@test.com"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        assert "not found" in response.json().get("detail", "").lower()
    
    def test_admin_unlock_requires_email(self, api_client, admin_token):
        """Test unlock endpoint requires email parameter"""
        response = api_client.post(
            f"{BASE_URL}/api/auth/admin/unlock-account",
            json={},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"


class TestPasswordResetClearsLockout:
    """Tests for password reset clearing lockout state"""
    
    def test_forgot_password_endpoint_works(self, api_client):
        """Test forgot password endpoint accepts email"""
        response = api_client.post(f"{BASE_URL}/api/auth/forgot-password", json={
            "email": OWNER_EMAIL
        })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "message" in data
        # The endpoint returns reset_token for testing purposes
        assert "reset_token" in data or "reset_url" in data
    
    def test_password_reset_clears_lockout(self, api_client, mongo_client):
        """Test that resetting password clears lockout state"""
        import bcrypt
        
        # Lock the account
        lock_time = datetime.utcnow() + timedelta(minutes=15)
        mongo_client.users.update_one(
            {"email": OWNER_EMAIL},
            {"$set": {"failed_login_attempts": 10, "locked_until": lock_time}}
        )
        
        # Get reset token
        forgot_response = api_client.post(f"{BASE_URL}/api/auth/forgot-password", json={
            "email": OWNER_EMAIL
        })
        assert forgot_response.status_code == 200
        reset_token = forgot_response.json().get("reset_token")
        
        if not reset_token:
            pytest.skip("Reset token not returned - check email service")
        
        # Reset password
        reset_response = api_client.post(f"{BASE_URL}/api/auth/reset-password", json={
            "token": reset_token,
            "new_password": "NewTest1234!"
        })
        
        assert reset_response.status_code == 200, f"Expected 200, got {reset_response.status_code}"
        
        # Verify lockout cleared in database
        user = mongo_client.users.find_one({"email": OWNER_EMAIL})
        assert user["failed_login_attempts"] == 0, "Failed attempts should be reset"
        assert user["locked_until"] is None, "locked_until should be cleared"
        
        # IMPORTANT: Reset password back to original Test1234!
        original_hash = bcrypt.hashpw(OWNER_PASSWORD.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")
        mongo_client.users.update_one(
            {"email": OWNER_EMAIL},
            {"$set": {
                "password_hash": original_hash,
                "failed_login_attempts": 0,
                "locked_until": None
            }}
        )


class TestInvalidCredentials:
    """Tests for invalid credential scenarios"""
    
    def test_nonexistent_email_returns_401(self, api_client):
        """Test login with nonexistent email returns 401"""
        response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "email": "nonexistent_user_test_12345@bigmannentertainment.com",
            "password": "SomePassword123!"
        })
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        assert "Invalid email or password" in response.json().get("detail", "")
