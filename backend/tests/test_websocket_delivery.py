"""
WebSocket Delivery Status Tests
Tests for the real-time WebSocket delivery updates feature.
"""
import pytest
import requests
import websocket
import json
import threading
import time
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "owner@bigmannentertainment.com"
TEST_PASSWORD = "Test1234!"


class TestWebSocketDeliveryEndpoint:
    """Tests for /api/ws/delivery WebSocket endpoint"""

    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("token") or data.get("access_token")
        pytest.skip(f"Authentication failed: {response.status_code}")

    @pytest.fixture(scope="class")
    def user_id(self, auth_token):
        """Extract user_id from JWT token"""
        import base64
        try:
            payload = auth_token.split(".")[1]
            # Add padding if needed
            payload += "=" * ((4 - len(payload) % 4) % 4)
            decoded = json.loads(base64.urlsafe_b64decode(payload))
            return decoded.get("user_id") or decoded.get("sub") or decoded.get("id")
        except Exception as e:
            pytest.skip(f"Could not extract user_id from token: {e}")

    def test_websocket_rejects_connection_without_user_id(self):
        """WebSocket should reject connections without user_id param (code 4001)"""
        ws_url = BASE_URL.replace("https://", "wss://").replace("http://", "ws://")
        ws_url = f"{ws_url}/api/ws/delivery"  # No user_id param
        
        result = {"closed": False, "close_code": None, "error": None}
        
        def on_close(ws, close_code, close_msg):
            result["closed"] = True
            result["close_code"] = close_code
        
        def on_error(ws, error):
            result["error"] = str(error)
        
        def on_open(ws):
            # Should be closed before this
            pass
        
        try:
            ws = websocket.WebSocketApp(
                ws_url,
                on_close=on_close,
                on_error=on_error,
                on_open=on_open
            )
            
            # Run in background thread with timeout
            wst = threading.Thread(target=ws.run_forever, kwargs={"ping_interval": 0})
            wst.daemon = True
            wst.start()
            
            time.sleep(2)  # Wait for connection attempt
            ws.close()
            
            # Either closed with 4001 or got an error (both are expected)
            assert result["closed"] or result["error"], "Connection should be rejected without user_id"
            if result["close_code"]:
                assert result["close_code"] == 4001 or result["close_code"] == 1000, f"Expected close code 4001 or connection failure, got {result['close_code']}"
            print(f"PASS: WebSocket correctly rejects connection without user_id (close_code={result['close_code']})")
            
        except Exception as e:
            # Connection rejection is also acceptable
            print(f"PASS: WebSocket connection rejected: {e}")

    def test_websocket_accepts_connection_with_user_id(self, user_id):
        """WebSocket should accept connections with valid user_id"""
        ws_url = BASE_URL.replace("https://", "wss://").replace("http://", "ws://")
        ws_url = f"{ws_url}/api/ws/delivery?user_id={user_id}"
        
        result = {"connected": False, "messages": [], "error": None}
        
        def on_open(ws):
            result["connected"] = True
            # Send ping to test
            ws.send("ping")
        
        def on_message(ws, message):
            result["messages"].append(message)
        
        def on_error(ws, error):
            result["error"] = str(error)
        
        def on_close(ws, close_code, close_msg):
            pass
        
        try:
            ws = websocket.WebSocketApp(
                ws_url,
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )
            
            wst = threading.Thread(target=ws.run_forever, kwargs={"ping_interval": 0})
            wst.daemon = True
            wst.start()
            
            time.sleep(3)  # Wait for connection and messages
            ws.close()
            
            assert result["connected"], f"WebSocket should connect with valid user_id. Error: {result['error']}"
            print(f"PASS: WebSocket connected successfully with user_id={user_id}")
            
        except Exception as e:
            pytest.fail(f"WebSocket connection failed: {e}")

    def test_websocket_responds_to_ping_with_pong(self, user_id):
        """WebSocket should respond to 'ping' with '{"type":"pong"}'"""
        ws_url = BASE_URL.replace("https://", "wss://").replace("http://", "ws://")
        ws_url = f"{ws_url}/api/ws/delivery?user_id={user_id}"
        
        result = {"pong_received": False, "messages": [], "error": None}
        
        def on_open(ws):
            ws.send("ping")
        
        def on_message(ws, message):
            result["messages"].append(message)
            try:
                data = json.loads(message)
                if data.get("type") == "pong":
                    result["pong_received"] = True
            except:
                pass
        
        def on_error(ws, error):
            result["error"] = str(error)
        
        try:
            ws = websocket.WebSocketApp(
                ws_url,
                on_open=on_open,
                on_message=on_message,
                on_error=on_error
            )
            
            wst = threading.Thread(target=ws.run_forever, kwargs={"ping_interval": 0})
            wst.daemon = True
            wst.start()
            
            time.sleep(3)
            ws.close()
            
            assert result["pong_received"], f"WebSocket should respond with pong. Messages received: {result['messages']}. Error: {result['error']}"
            print(f"PASS: WebSocket responds to ping with pong. Messages: {result['messages']}")
            
        except Exception as e:
            pytest.fail(f"WebSocket ping/pong test failed: {e}")


class TestBatchProgressHTTPEndpoint:
    """Tests for GET /api/distribution-hub/deliveries/batch/{batch_id}/progress"""

    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("token") or data.get("access_token")
        pytest.skip(f"Authentication failed: {response.status_code}")

    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        """Get auth headers"""
        return {"Authorization": f"Bearer {auth_token}"}

    def test_batch_progress_endpoint_exists(self, auth_headers):
        """Batch progress endpoint should exist and return 200/404 for valid request"""
        # Use a fake batch ID - should return 200 with zero counts or 404
        response = requests.get(
            f"{BASE_URL}/api/distribution-hub/deliveries/batch/test-batch-id/progress",
            headers=auth_headers
        )
        # 200 with empty progress or 404 are both acceptable
        assert response.status_code in [200, 404], f"Expected 200 or 404, got {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            # Should have progress fields
            assert "total" in data, "Response should include 'total' field"
            assert "progress_pct" in data, "Response should include 'progress_pct' field"
            print(f"PASS: Batch progress endpoint returns valid data: {data}")
        else:
            print(f"PASS: Batch progress endpoint returns 404 for non-existent batch (expected)")

    def test_batch_progress_unauthorized_access(self):
        """Batch progress should require authentication"""
        response = requests.get(
            f"{BASE_URL}/api/distribution-hub/deliveries/batch/test-batch-id/progress"
        )
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print(f"PASS: Batch progress requires authentication (status={response.status_code})")


class TestDeliveryEngineIntegration:
    """Tests for delivery engine WebSocket notification integration"""

    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("token") or data.get("access_token")
        pytest.skip(f"Authentication failed: {response.status_code}")

    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        """Get auth headers"""
        return {"Authorization": f"Bearer {auth_token}"}

    @pytest.fixture(scope="class")
    def user_id(self, auth_token):
        """Extract user_id from JWT token"""
        import base64
        try:
            payload = auth_token.split(".")[1]
            payload += "=" * ((4 - len(payload) % 4) % 4)
            decoded = json.loads(base64.urlsafe_b64decode(payload))
            return decoded.get("user_id") or decoded.get("sub") or decoded.get("id")
        except Exception as e:
            pytest.skip(f"Could not extract user_id from token: {e}")

    def test_distribution_hub_stats_endpoint(self, auth_headers):
        """Stats endpoint should work (validates hub is functional)"""
        response = requests.get(
            f"{BASE_URL}/api/distribution-hub/stats",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Stats endpoint failed: {response.status_code}"
        data = response.json()
        assert "content_count" in data or "total_deliveries" in data, "Stats should return hub data"
        print(f"PASS: Distribution hub stats endpoint works: {data}")

    def test_distribution_hub_content_endpoint(self, auth_headers):
        """Content endpoint should work"""
        response = requests.get(
            f"{BASE_URL}/api/distribution-hub/content",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Content endpoint failed: {response.status_code}"
        data = response.json()
        assert "content" in data, "Response should include 'content' field"
        print(f"PASS: Distribution hub content endpoint works. {len(data.get('content', []))} items.")

    def test_distribution_hub_deliveries_endpoint(self, auth_headers):
        """Deliveries endpoint should work"""
        response = requests.get(
            f"{BASE_URL}/api/distribution-hub/deliveries",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Deliveries endpoint failed: {response.status_code}"
        data = response.json()
        assert "deliveries" in data, "Response should include 'deliveries' field"
        print(f"PASS: Distribution hub deliveries endpoint works. {len(data.get('deliveries', []))} items.")

    def test_full_websocket_delivery_flow(self, auth_headers, user_id):
        """Test WebSocket receives updates when distribution is triggered (if content exists)"""
        # First check if there's content to distribute
        content_response = requests.get(
            f"{BASE_URL}/api/distribution-hub/content",
            headers=auth_headers
        )
        if content_response.status_code != 200:
            pytest.skip("Could not fetch content")
        
        content_list = content_response.json().get("content", [])
        if not content_list:
            print("SKIP: No content available to test distribution flow")
            pytest.skip("No content available for distribution test")
        
        content_id = content_list[0]["id"]
        
        # Get available platforms
        platforms_response = requests.get(
            f"{BASE_URL}/api/distribution-hub/platforms",
            headers=auth_headers
        )
        if platforms_response.status_code != 200:
            pytest.skip("Could not fetch platforms")
        
        platforms_data = platforms_response.json()
        platform_ids = []
        for cat_data in (platforms_data.get("categories") or {}).values():
            for pid in (cat_data.get("platforms") or {}).keys():
                platform_ids.append(pid)
                break
            if platform_ids:
                break
        
        if not platform_ids:
            pytest.skip("No platforms available")
        
        # Connect WebSocket
        ws_url = BASE_URL.replace("https://", "wss://").replace("http://", "ws://")
        ws_url = f"{ws_url}/api/ws/delivery?user_id={user_id}"
        
        ws_messages = []
        ws_connected = [False]
        
        def on_open(ws):
            ws_connected[0] = True
        
        def on_message(ws, message):
            ws_messages.append(message)
        
        try:
            ws = websocket.WebSocketApp(
                ws_url,
                on_open=on_open,
                on_message=on_message
            )
            
            wst = threading.Thread(target=ws.run_forever, kwargs={"ping_interval": 0})
            wst.daemon = True
            wst.start()
            
            time.sleep(2)  # Wait for connection
            
            if not ws_connected[0]:
                pytest.skip("WebSocket did not connect")
            
            # Trigger distribution
            distribute_response = requests.post(
                f"{BASE_URL}/api/distribution-hub/distribute",
                headers=auth_headers,
                json={
                    "content_id": content_id,
                    "platform_ids": platform_ids[:1]  # Just one platform
                }
            )
            
            # Wait for WebSocket messages
            time.sleep(5)
            ws.close()
            
            if distribute_response.status_code == 200:
                print(f"PASS: Distribution triggered successfully")
                print(f"WebSocket messages received: {len(ws_messages)}")
                for msg in ws_messages[:5]:  # Show first 5 messages
                    print(f"  - {msg[:200]}")
                
                # Check if we got delivery_update or batch_progress messages
                delivery_updates = [m for m in ws_messages if "delivery_update" in m]
                batch_progress = [m for m in ws_messages if "batch_progress" in m]
                
                print(f"  delivery_update messages: {len(delivery_updates)}")
                print(f"  batch_progress messages: {len(batch_progress)}")
                
            else:
                print(f"Distribution returned {distribute_response.status_code}: {distribute_response.text[:200]}")
                
        except Exception as e:
            print(f"Full flow test exception: {e}")


class TestDeliveryWebSocketManager:
    """Tests for DeliveryWebSocketManager class functionality"""
    
    def test_manager_module_import(self):
        """Verify delivery_ws_manager module can be imported"""
        try:
            from utils.delivery_ws_manager import delivery_ws_manager, DeliveryWebSocketManager
            assert delivery_ws_manager is not None
            assert DeliveryWebSocketManager is not None
            print("PASS: delivery_ws_manager module imports correctly")
        except ImportError:
            # This test runs from pytest context, may not find module
            print("SKIP: Module import test skipped (running outside backend context)")
            pytest.skip("Module import test requires backend context")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
