#!/usr/bin/env python3
"""
Emergent Ledger (QLDB replacement) API Testing
Testing the specific endpoints requested in the review
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# Backend URL from frontend/.env
BACKEND_URL = "https://aws-qldb-sync.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = []
    
    def add_result(self, test_name: str, passed: bool, details: str = ""):
        self.results.append({
            "test": test_name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        if passed:
            self.passed += 1
            print(f"✅ {test_name}")
        else:
            self.failed += 1
            print(f"❌ {test_name}: {details}")
    
    def summary(self):
        total = self.passed + self.failed
        print(f"\n📊 Test Summary: {self.passed}/{total} passed ({(self.passed/total*100):.1f}%)")
        return self.passed, self.failed, total

def make_request(method: str, endpoint: str, **kwargs) -> tuple[int, Dict[Any, Any]]:
    """Make HTTP request and return status code and response data"""
    url = f"{API_BASE}{endpoint}"
    try:
        response = requests.request(method, url, timeout=30, **kwargs)
        try:
            data = response.json()
        except:
            data = {"text": response.text}
        return response.status_code, data
    except Exception as e:
        return 0, {"error": str(e)}

def create_sample_finding_via_mongodb():
    """Create a sample finding directly via MongoDB API if available"""
    # Since we can't directly access MongoDB, we'll create a mock finding through the API
    # by checking if there's a way to seed data or use the existing detector
    pass

def test_emergent_ledger_api():
    """Test Emergent Ledger (QLDB replacement) API as requested in review"""
    print("\n📘 Testing Emergent Ledger (QLDB replacement) API")
    results = TestResults()
    
    # Test 1: Check health at /api/qldb/health (should say "healthy" and "Emergent Ledger")
    print("🔍 Testing QLDB Health endpoint...")
    status, data = make_request("GET", "/qldb/health")
    if status == 200:
        status_value = data.get("status", "").lower()
        service_name = data.get("service", "")
        
        if "healthy" in status_value and "emergent ledger" in service_name.lower():
            results.add_result("QLDB Health Check", True, f"Status: {status_value}, Service: {service_name}")
        else:
            results.add_result("QLDB Health Check", False, f"Expected 'healthy' status and 'Emergent Ledger' service. Got status: {status_value}, service: {service_name}")
    else:
        results.add_result("QLDB Health Check", False, f"HTTP {status}: {data}")
    
    # Test 2: Create a dispute via POST /api/qldb/disputes (use dummy data)
    print("🔍 Testing dispute creation...")
    dispute_payload = {
        "type": "ROYALTY_DISPUTE",
        "title": "Test Music Royalty Dispute",
        "description": "Testing dispute creation for Emergent Ledger API verification",
        "amount_disputed": 1500.75,
        "currency": "USD",
        "claimant_name": "John Artist",
        "claimant_email": "john.artist@musiclabel.com"
    }
    
    status, create_data = make_request("POST", "/qldb/disputes", json=dispute_payload)
    dispute_id = None
    
    if status == 200 or status == 201:
        # Try different possible field names for the dispute ID
        dispute_id = (create_data.get("id") or 
                     create_data.get("dispute_id") or 
                     create_data.get("dispute_number") or
                     create_data.get("data", {}).get("id"))
        
        if dispute_id:
            results.add_result("Create Dispute", True, f"Successfully created dispute with ID: {dispute_id}")
        else:
            results.add_result("Create Dispute", False, f"Dispute created but no ID found in response: {create_data}")
    else:
        results.add_result("Create Dispute", False, f"HTTP {status}: {create_data}")
    
    # Test 3: Verify the dispute exists via GET /api/qldb/disputes/{id}
    if dispute_id:
        print(f"🔍 Testing dispute retrieval for ID: {dispute_id}...")
        status, dispute_data = make_request("GET", f"/qldb/disputes/{dispute_id}")
        
        if status == 200:
            # Verify the dispute data matches what we created
            retrieved_title = dispute_data.get("title") or dispute_data.get("data", {}).get("title")
            retrieved_amount = dispute_data.get("amount_disputed") or dispute_data.get("data", {}).get("amount_disputed")
            
            if retrieved_title == dispute_payload["title"]:
                results.add_result("Verify Dispute Exists", True, f"Dispute {dispute_id} retrieved successfully with correct title: {retrieved_title}")
            else:
                results.add_result("Verify Dispute Exists", False, f"Dispute retrieved but title mismatch. Expected: {dispute_payload['title']}, Got: {retrieved_title}")
        else:
            results.add_result("Verify Dispute Exists", False, f"HTTP {status}: {dispute_data}")
    else:
        results.add_result("Verify Dispute Exists", False, "Skipped - no dispute ID available from creation step")
    
    return results

def test_content_moderation_api():
    """Test Content Moderation API to ensure other services weren't broken"""
    print("\n🛡️ Testing Content Moderation API")
    results = TestResults()
    
    # Test 4: Verify the Content Moderation API /api/moderation/text with text "hello world"
    print("🔍 Testing content moderation with 'hello world'...")
    moderation_payload = {
        "text": "hello world"
    }
    
    status, mod_data = make_request("POST", "/moderation/text", json=moderation_payload)
    
    if status == 200:
        # Check if the response has expected moderation fields
        if "safe" in mod_data or "classification" in mod_data or "result" in mod_data:
            results.add_result("Content Moderation API", True, f"Moderation API working correctly: {mod_data}")
        else:
            results.add_result("Content Moderation API", False, f"Unexpected response format: {mod_data}")
    else:
        results.add_result("Content Moderation API", False, f"HTTP {status}: {mod_data}")
    
    return results

def main():
    """Main test execution"""
    print("🔍 AWS GuardDuty and QLDB Backend Integration Testing")
    print(f"🌐 Backend URL: {BACKEND_URL}")
    print(f"📡 API Base: {API_BASE}")
    
    # Test GuardDuty Integration
    guardduty_results = test_guardduty_integration()
    
    # Test QLDB Integration
    qldb_results = test_qldb_integration()
    
    # Combined Results
    print("\n" + "="*60)
    print("📊 COMPREHENSIVE TEST RESULTS")
    print("="*60)
    
    print("\n🛡️  GuardDuty Integration:")
    gd_passed, gd_failed, gd_total = guardduty_results.summary()
    
    print("\n📘 QLDB Integration:")
    qldb_passed, qldb_failed, qldb_total = qldb_results.summary()
    
    # Overall Summary
    total_passed = gd_passed + qldb_passed
    total_failed = gd_failed + qldb_failed
    total_tests = gd_total + qldb_total
    
    print(f"\n🎯 OVERALL RESULTS:")
    print(f"   Total Tests: {total_tests}")
    print(f"   Passed: {total_passed}")
    print(f"   Failed: {total_failed}")
    print(f"   Success Rate: {(total_passed/total_tests*100):.1f}%")
    
    # Detailed Results for Failed Tests
    if total_failed > 0:
        print(f"\n❌ FAILED TESTS DETAILS:")
        for result in guardduty_results.results + qldb_results.results:
            if not result["passed"]:
                print(f"   • {result['test']}: {result['details']}")
    
    # Test Status
    if total_failed == 0:
        print(f"\n🎉 ALL TESTS PASSED! Both GuardDuty and QLDB integrations are fully operational.")
        return 0
    else:
        print(f"\n⚠️  {total_failed} tests failed. Review the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())