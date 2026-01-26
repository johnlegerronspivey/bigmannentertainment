"""
Agency Success Automation API Tests
Tests for automated onboarding, KPI tracking, contracts, bookings, and revenue forecasting
"""

import pytest
import requests
import os
from datetime import datetime, timedelta
import uuid

# Get BASE_URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test agency ID
AGENCY_ID = "agency-default"


class TestHealthCheck:
    """Health check endpoint tests"""
    
    def test_health_endpoint(self):
        """Test health check returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/agency-automation/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "Agency Success Automation"
        assert "features" in data
        assert len(data["features"]) == 5
        print(f"✅ Health check passed: {data['status']}")


class TestOnboardingWorkflows:
    """Onboarding workflow endpoint tests"""
    
    def test_create_onboarding_workflow(self):
        """Test creating a new onboarding workflow"""
        payload = {
            "talent_id": f"TEST_talent_{uuid.uuid4().hex[:8]}",
            "talent_name": "TEST John Doe",
            "talent_email": "test.john@example.com",
            "agency_id": AGENCY_ID,
            "assigned_to": "agent-001"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/agency-automation/onboarding",
            json=payload
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "id" in data
        assert data["talent_name"] == payload["talent_name"]
        assert data["talent_email"] == payload["talent_email"]
        assert data["agency_id"] == AGENCY_ID
        assert data["status"] == "in_progress"
        assert "steps" in data
        assert len(data["steps"]) > 0
        
        print(f"✅ Created onboarding workflow: {data['id']}")
        return data["id"]
    
    def test_list_onboarding_workflows(self):
        """Test listing onboarding workflows"""
        response = requests.get(
            f"{BASE_URL}/api/agency-automation/onboarding",
            params={"agency_id": AGENCY_ID}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        print(f"✅ Listed {len(data)} onboarding workflows")
    
    def test_get_onboarding_stats(self):
        """Test getting onboarding statistics"""
        response = requests.get(
            f"{BASE_URL}/api/agency-automation/onboarding/stats",
            params={"agency_id": AGENCY_ID}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify stats structure
        assert "total_workflows" in data
        assert "in_progress" in data
        assert "pending_review" in data
        assert "completed_this_month" in data
        assert "average_completion_days" in data
        assert "overdue_count" in data
        
        print(f"✅ Onboarding stats: {data['total_workflows']} total, {data['in_progress']} in progress")


class TestContractManagement:
    """Contract management endpoint tests"""
    
    def test_create_contract(self):
        """Test creating a new contract"""
        payload = {
            "contract_type": "exclusive_representation",
            "title": "TEST Exclusive Representation Agreement",
            "agency_id": AGENCY_ID,
            "created_by": "admin-001",
            "parties": [
                {
                    "party_id": f"party_{uuid.uuid4().hex[:8]}",
                    "party_type": "talent",
                    "name": "TEST Jane Smith",
                    "email": "jane.smith@example.com",
                    "role": "signer"
                }
            ],
            "terms": {
                "compensation": {"amount": 50000, "currency": "USD"},
                "duration": "12 months",
                "exclusivity": True
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/agency-automation/contracts",
            json=payload
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "id" in data
        assert "contract_number" in data
        assert data["title"] == payload["title"]
        assert data["contract_type"] == "exclusive_representation"
        assert data["status"] == "draft"
        assert "parties" in data
        assert "clauses" in data
        
        print(f"✅ Created contract: {data['contract_number']}")
        return data["id"]
    
    def test_list_contracts(self):
        """Test listing contracts"""
        response = requests.get(
            f"{BASE_URL}/api/agency-automation/contracts",
            params={"agency_id": AGENCY_ID}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        print(f"✅ Listed {len(data)} contracts")
    
    def test_get_contract_stats(self):
        """Test getting contract statistics"""
        response = requests.get(
            f"{BASE_URL}/api/agency-automation/contracts/stats",
            params={"agency_id": AGENCY_ID}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify stats structure
        assert "total_contracts" in data
        assert "active_contracts" in data
        assert "pending_signature" in data
        assert "expiring_soon" in data
        assert "total_contract_value" in data
        
        print(f"✅ Contract stats: {data['total_contracts']} total, {data['active_contracts']} active")


class TestBookingManagement:
    """Booking management endpoint tests"""
    
    def test_create_booking(self):
        """Test creating a new booking"""
        start_time = datetime.now() + timedelta(days=7)
        end_time = start_time + timedelta(hours=8)
        
        payload = {
            "booking_type": "photoshoot",
            "agency_id": AGENCY_ID,
            "talent_id": f"TEST_talent_{uuid.uuid4().hex[:8]}",
            "talent_name": "TEST Model Alice",
            "client_id": f"TEST_client_{uuid.uuid4().hex[:8]}",
            "client_name": "TEST Vogue Magazine",
            "title": "TEST Cover Photoshoot",
            "start_datetime": start_time.isoformat(),
            "end_datetime": end_time.isoformat(),
            "rate": 1500.00,
            "rate_type": "daily",
            "commission_percentage": 20.0,
            "description": "Cover shoot for spring edition",
            "location": "NYC Studio"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/agency-automation/bookings",
            json=payload
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "id" in data
        assert "booking_number" in data
        assert data["title"] == payload["title"]
        assert data["booking_type"] == "photoshoot"
        assert data["status"] == "pending_confirmation"
        assert data["rate"] == 1500.00
        assert "total_fee" in data
        assert "agency_commission" in data
        assert "talent_payout" in data
        
        # Verify fee calculations
        assert data["total_fee"] > 0
        assert data["agency_commission"] > 0
        assert data["talent_payout"] > 0
        
        print(f"✅ Created booking: {data['booking_number']} - Total fee: ${data['total_fee']}")
        return data["id"]
    
    def test_list_bookings(self):
        """Test listing bookings"""
        response = requests.get(
            f"{BASE_URL}/api/agency-automation/bookings",
            params={"agency_id": AGENCY_ID}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        print(f"✅ Listed {len(data)} bookings")
    
    def test_get_booking_stats(self):
        """Test getting booking statistics"""
        response = requests.get(
            f"{BASE_URL}/api/agency-automation/bookings/stats",
            params={"agency_id": AGENCY_ID}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify stats structure
        assert "total_bookings" in data
        assert "confirmed_bookings" in data
        assert "pending_bookings" in data
        assert "completed_this_month" in data
        assert "total_revenue_this_month" in data
        assert "average_booking_value" in data
        
        print(f"✅ Booking stats: {data['total_bookings']} total, ${data['total_revenue_this_month']} revenue this month")


class TestKPIDashboard:
    """KPI dashboard endpoint tests"""
    
    def test_get_agency_kpis(self):
        """Test getting agency KPIs"""
        response = requests.get(
            f"{BASE_URL}/api/agency-automation/kpis",
            params={"agency_id": AGENCY_ID, "period": "month"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify KPI structure
        assert "agency_id" in data
        assert "period" in data
        assert "total_revenue" in data
        assert "total_bookings" in data
        assert "active_talent" in data
        assert "active_clients" in data
        assert "metrics" in data
        
        print(f"✅ KPIs: Revenue ${data['total_revenue']}, {data['total_bookings']} bookings")
    
    def test_get_kpis_quarterly(self):
        """Test getting quarterly KPIs"""
        response = requests.get(
            f"{BASE_URL}/api/agency-automation/kpis",
            params={"agency_id": AGENCY_ID, "period": "quarter"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["period"] == "quarter"
        print(f"✅ Quarterly KPIs retrieved successfully")


class TestRevenueForecast:
    """Revenue forecasting endpoint tests"""
    
    def test_get_monthly_forecast(self):
        """Test getting monthly revenue forecast"""
        response = requests.get(
            f"{BASE_URL}/api/agency-automation/forecast",
            params={"agency_id": AGENCY_ID, "forecast_period": "monthly"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify forecast structure
        assert "id" in data
        assert "agency_id" in data
        assert "forecast_period" in data
        assert "predicted_revenue" in data
        assert "confidence_level" in data
        assert "lower_bound" in data
        assert "upper_bound" in data
        assert "by_booking_type" in data
        assert "seasonal_factor" in data
        assert "growth_factor" in data
        assert "assumptions" in data
        assert "risks" in data
        assert "opportunities" in data
        
        # Verify bounds make sense
        assert data["lower_bound"] <= data["predicted_revenue"] <= data["upper_bound"]
        assert 0 <= data["confidence_level"] <= 1
        
        print(f"✅ Monthly forecast: ${data['predicted_revenue']:.2f} (confidence: {data['confidence_level']*100:.0f}%)")
    
    def test_get_quarterly_forecast(self):
        """Test getting quarterly revenue forecast"""
        response = requests.get(
            f"{BASE_URL}/api/agency-automation/forecast",
            params={"agency_id": AGENCY_ID, "forecast_period": "quarterly"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["forecast_period"] == "quarterly"
        print(f"✅ Quarterly forecast: ${data['predicted_revenue']:.2f}")
    
    def test_get_yearly_forecast(self):
        """Test getting yearly revenue forecast"""
        response = requests.get(
            f"{BASE_URL}/api/agency-automation/forecast",
            params={"agency_id": AGENCY_ID, "forecast_period": "yearly"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["forecast_period"] == "yearly"
        print(f"✅ Yearly forecast: ${data['predicted_revenue']:.2f}")


class TestAlerts:
    """Alerts endpoint tests"""
    
    def test_list_alerts(self):
        """Test listing alerts"""
        response = requests.get(
            f"{BASE_URL}/api/agency-automation/alerts",
            params={"agency_id": AGENCY_ID}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        print(f"✅ Listed {len(data)} alerts")
    
    def test_list_unread_alerts(self):
        """Test listing unread alerts only"""
        response = requests.get(
            f"{BASE_URL}/api/agency-automation/alerts",
            params={"agency_id": AGENCY_ID, "unread_only": True}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        # All returned alerts should be unread
        for alert in data:
            assert alert.get("is_read") == False
        
        print(f"✅ Listed {len(data)} unread alerts")


class TestDashboard:
    """Dashboard endpoint tests"""
    
    def test_get_automation_dashboard(self):
        """Test getting comprehensive automation dashboard"""
        response = requests.get(
            f"{BASE_URL}/api/agency-automation/dashboard",
            params={"agency_id": AGENCY_ID}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify dashboard structure
        assert "agency_id" in data
        assert "onboarding_stats" in data
        assert "contract_stats" in data
        assert "booking_stats" in data
        assert "recent_alerts" in data
        assert "upcoming_deadlines" in data
        
        # Verify nested stats
        assert "total_workflows" in data["onboarding_stats"]
        assert "total_contracts" in data["contract_stats"]
        assert "total_bookings" in data["booking_stats"]
        
        print(f"✅ Dashboard loaded: {data['onboarding_stats']['total_workflows']} onboardings, "
              f"{data['contract_stats']['total_contracts']} contracts, "
              f"{data['booking_stats']['total_bookings']} bookings")


class TestCRUDWorkflows:
    """End-to-end CRUD workflow tests"""
    
    def test_onboarding_create_and_verify(self):
        """Test creating onboarding and verifying via list"""
        # Create
        payload = {
            "talent_id": f"TEST_crud_{uuid.uuid4().hex[:8]}",
            "talent_name": "TEST CRUD Talent",
            "talent_email": "crud.test@example.com",
            "agency_id": AGENCY_ID
        }
        
        create_response = requests.post(
            f"{BASE_URL}/api/agency-automation/onboarding",
            json=payload
        )
        assert create_response.status_code == 200
        created = create_response.json()
        workflow_id = created["id"]
        
        # Verify via list
        list_response = requests.get(
            f"{BASE_URL}/api/agency-automation/onboarding",
            params={"agency_id": AGENCY_ID}
        )
        assert list_response.status_code == 200
        workflows = list_response.json()
        
        # Find our created workflow
        found = any(w["id"] == workflow_id for w in workflows)
        assert found, f"Created workflow {workflow_id} not found in list"
        
        print(f"✅ CRUD test passed: Created and verified onboarding {workflow_id}")
    
    def test_contract_create_and_verify(self):
        """Test creating contract and verifying via list"""
        # Create
        payload = {
            "contract_type": "non_exclusive",
            "title": "TEST CRUD Contract",
            "agency_id": AGENCY_ID,
            "created_by": "test-admin",
            "parties": [
                {
                    "party_id": f"party_{uuid.uuid4().hex[:8]}",
                    "party_type": "talent",
                    "name": "TEST CRUD Party",
                    "email": "crud.party@example.com",
                    "role": "signer"
                }
            ],
            "terms": {"duration": "6 months"}
        }
        
        create_response = requests.post(
            f"{BASE_URL}/api/agency-automation/contracts",
            json=payload
        )
        assert create_response.status_code == 200
        created = create_response.json()
        contract_id = created["id"]
        
        # Verify via list
        list_response = requests.get(
            f"{BASE_URL}/api/agency-automation/contracts",
            params={"agency_id": AGENCY_ID}
        )
        assert list_response.status_code == 200
        contracts = list_response.json()
        
        # Find our created contract
        found = any(c["id"] == contract_id for c in contracts)
        assert found, f"Created contract {contract_id} not found in list"
        
        print(f"✅ CRUD test passed: Created and verified contract {contract_id}")
    
    def test_booking_create_and_verify(self):
        """Test creating booking and verifying via list"""
        start_time = datetime.now() + timedelta(days=14)
        end_time = start_time + timedelta(hours=4)
        
        # Create
        payload = {
            "booking_type": "runway",
            "agency_id": AGENCY_ID,
            "talent_id": f"TEST_talent_{uuid.uuid4().hex[:8]}",
            "talent_name": "TEST CRUD Model",
            "client_id": f"TEST_client_{uuid.uuid4().hex[:8]}",
            "client_name": "TEST CRUD Client",
            "title": "TEST CRUD Runway Show",
            "start_datetime": start_time.isoformat(),
            "end_datetime": end_time.isoformat(),
            "rate": 2000.00,
            "rate_type": "flat"
        }
        
        create_response = requests.post(
            f"{BASE_URL}/api/agency-automation/bookings",
            json=payload
        )
        assert create_response.status_code == 200
        created = create_response.json()
        booking_id = created["id"]
        
        # Verify via list
        list_response = requests.get(
            f"{BASE_URL}/api/agency-automation/bookings",
            params={"agency_id": AGENCY_ID}
        )
        assert list_response.status_code == 200
        bookings = list_response.json()
        
        # Find our created booking
        found = any(b["id"] == booking_id for b in bookings)
        assert found, f"Created booking {booking_id} not found in list"
        
        print(f"✅ CRUD test passed: Created and verified booking {booking_id}")


class TestEdgeCases:
    """Edge case and error handling tests"""
    
    def test_missing_agency_id(self):
        """Test that missing agency_id returns error"""
        response = requests.get(f"{BASE_URL}/api/agency-automation/onboarding")
        # Should return 422 for missing required parameter
        assert response.status_code == 422
        print("✅ Missing agency_id correctly returns 422")
    
    def test_invalid_booking_type(self):
        """Test that invalid booking type returns error"""
        start_time = datetime.now() + timedelta(days=7)
        end_time = start_time + timedelta(hours=8)
        
        payload = {
            "booking_type": "invalid_type",
            "agency_id": AGENCY_ID,
            "talent_id": "test-talent",
            "talent_name": "Test",
            "client_id": "test-client",
            "client_name": "Test Client",
            "title": "Test",
            "start_datetime": start_time.isoformat(),
            "end_datetime": end_time.isoformat(),
            "rate": 100.00
        }
        
        response = requests.post(
            f"{BASE_URL}/api/agency-automation/bookings",
            json=payload
        )
        # Should return 500 or 422 for invalid enum value
        assert response.status_code in [422, 500]
        print("✅ Invalid booking type correctly returns error")
    
    def test_invalid_contract_type(self):
        """Test that invalid contract type returns error"""
        payload = {
            "contract_type": "invalid_type",
            "title": "Test Contract",
            "agency_id": AGENCY_ID,
            "created_by": "test",
            "parties": [],
            "terms": {}
        }
        
        response = requests.post(
            f"{BASE_URL}/api/agency-automation/contracts",
            json=payload
        )
        # Should return 500 or 422 for invalid enum value
        assert response.status_code in [422, 500]
        print("✅ Invalid contract type correctly returns error")


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
