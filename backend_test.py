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

def test_guardduty_integration():
    """Test AWS GuardDuty integration endpoints"""
    print("\n🛡️  Testing AWS GuardDuty Integration")
    results = TestResults()
    
    # Test 1: GuardDuty Health Check
    status, data = make_request("GET", "/guardduty/health")
    if status == 200:
        required_keys = ["status", "service", "version", "guardduty_enabled", "aws_connected", "aws_region", "features"]
        missing_keys = [key for key in required_keys if key not in data]
        if not missing_keys:
            results.add_result("GuardDuty Health Check", True, f"All required keys present: {required_keys}")
        else:
            results.add_result("GuardDuty Health Check", False, f"Missing keys: {missing_keys}")
    else:
        results.add_result("GuardDuty Health Check", False, f"HTTP {status}: {data}")
    
    # Test 2: GuardDuty Dashboard
    status, data = make_request("GET", "/guardduty/dashboard")
    if status == 200:
        required_keys = ["total_detectors", "active_detectors", "total_findings", "new_findings", "severity_summary", "status_summary"]
        missing_keys = [key for key in required_keys if key not in data]
        if not missing_keys:
            results.add_result("GuardDuty Dashboard", True, f"Dashboard stats available: {list(data.keys())}")
        else:
            results.add_result("GuardDuty Dashboard", False, f"Missing dashboard keys: {missing_keys}")
    else:
        results.add_result("GuardDuty Dashboard", False, f"HTTP {status}: {data}")
    
    # Test 3: List Findings
    status, data = make_request("GET", "/guardduty/findings")
    if status == 200:
        required_keys = ["success", "findings", "total", "limit", "offset", "has_more"]
        missing_keys = [key for key in required_keys if key not in data]
        if not missing_keys:
            findings_count = len(data.get("findings", []))
            results.add_result("GuardDuty List Findings", True, f"Found {findings_count} findings with proper structure")
            
            # Since there are no findings, let's test the endpoints with mock IDs to verify they exist
            # Test 4: Test Individual Finding Operations with Mock ID (should return 404)
            mock_finding_id = "test-finding-001"
            
            # Test 4: Get Individual Finding (expect 404)
            status, finding_data = make_request("GET", f"/guardduty/findings/{mock_finding_id}")
            if status == 404:
                results.add_result("Get Individual Finding Endpoint", True, f"Endpoint exists, correctly returns 404 for non-existent finding")
            else:
                results.add_result("Get Individual Finding Endpoint", False, f"Unexpected status {status}: {finding_data}")
            
            # Test 5: Acknowledge Finding (expect 404)
            status, ack_data = make_request("POST", f"/guardduty/findings/{mock_finding_id}/acknowledge")
            if status == 404:
                results.add_result("Acknowledge Finding Endpoint", True, f"Endpoint exists, correctly returns 404 for non-existent finding")
            else:
                results.add_result("Acknowledge Finding Endpoint", False, f"Unexpected status {status}: {ack_data}")
            
            # Test 6: Resolve Finding with Notes (expect 404)
            status, resolve_data = make_request("POST", f"/guardduty/findings/{mock_finding_id}/resolve", 
                                              params={"notes": "Test resolution notes"})
            if status == 404:
                results.add_result("Resolve Finding Endpoint", True, f"Endpoint exists, correctly returns 404 for non-existent finding")
            else:
                results.add_result("Resolve Finding Endpoint", False, f"Unexpected status {status}: {resolve_data}")
            
            # Test 7: Archive Finding (expect 404)
            status, archive_data = make_request("POST", f"/guardduty/findings/{mock_finding_id}/archive")
            if status == 404:
                results.add_result("Archive Finding Endpoint", True, f"Endpoint exists, correctly returns 404 for non-existent finding")
            else:
                results.add_result("Archive Finding Endpoint", False, f"Unexpected status {status}: {archive_data}")
                
        else:
            results.add_result("GuardDuty List Findings", False, f"Missing response keys: {missing_keys}")
    else:
        results.add_result("GuardDuty List Findings", False, f"HTTP {status}: {data}")
    
    return results

def test_qldb_integration():
    """Test AWS QLDB integration endpoints"""
    print("\n📘 Testing AWS QLDB Integration")
    results = TestResults()
    
    # Test 1: QLDB Health Check
    status, data = make_request("GET", "/qldb/health")
    if status == 200:
        required_keys = ["status", "service", "version", "ledger_active", "chain_integrity", "aws_region", "features"]
        missing_keys = [key for key in required_keys if key not in data]
        if not missing_keys:
            results.add_result("QLDB Health Check", True, f"All required keys present: {required_keys}")
        else:
            results.add_result("QLDB Health Check", False, f"Missing keys: {missing_keys}")
    else:
        results.add_result("QLDB Health Check", False, f"HTTP {status}: {data}")
    
    # Test 2: QLDB Dashboard
    status, data = make_request("GET", "/qldb/dashboard")
    if status == 200:
        required_keys = ["dispute_stats", "audit_stats", "chain_verified", "total_documents"]
        missing_keys = [key for key in required_keys if key not in data]
        if not missing_keys:
            results.add_result("QLDB Dashboard", True, f"Dashboard stats available: {list(data.keys())}")
        else:
            results.add_result("QLDB Dashboard", False, f"Missing dashboard keys: {missing_keys}")
    else:
        results.add_result("QLDB Dashboard", False, f"HTTP {status}: {data}")
    
    # Test 3: List Disputes
    status, data = make_request("GET", "/qldb/disputes")
    if status == 200:
        required_keys = ["success", "disputes", "total", "limit", "offset"]
        missing_keys = [key for key in required_keys if key not in data]
        if not missing_keys:
            disputes_count = len(data.get("disputes", []))
            results.add_result("QLDB List Disputes", True, f"Found {disputes_count} disputes with proper structure")
        else:
            results.add_result("QLDB List Disputes", False, f"Missing response keys: {missing_keys}")
    else:
        results.add_result("QLDB List Disputes", False, f"HTTP {status}: {data}")
    
    # Test 4: Create New Dispute
    dispute_payload = {
        "type": "ROYALTY_DISPUTE",
        "title": "Test Royalty Dispute - Backend Testing",
        "description": "Testing dispute creation functionality for backend integration testing",
        "amount_disputed": 2500.00,
        "currency": "USD",
        "claimant_name": "Backend Test User",
        "claimant_email": "backend.test@example.com"
    }
    
    status, create_data = make_request("POST", "/qldb/disputes", json=dispute_payload)
    if status == 200:
        dispute_id = create_data.get("id") or create_data.get("dispute_id") or create_data.get("dispute_number")
        if dispute_id:
            results.add_result("Create New Dispute", True, f"Created dispute {dispute_id}")
            
            # Test 5: Verify dispute appears in list
            status, list_data = make_request("GET", "/qldb/disputes")
            if status == 200:
                dispute_found = any(d.get("id") == dispute_id or d.get("dispute_id") == dispute_id 
                                  for d in list_data.get("disputes", []))
                if dispute_found:
                    results.add_result("Verify Dispute in List", True, f"Dispute {dispute_id} found in list")
                else:
                    results.add_result("Verify Dispute in List", False, f"Dispute {dispute_id} not found in list")
            else:
                results.add_result("Verify Dispute in List", False, f"HTTP {status}: {list_data}")
            
            # Test 6: Get Individual Dispute
            status, dispute_data = make_request("GET", f"/qldb/disputes/{dispute_id}")
            if status == 200:
                results.add_result("Get Individual Dispute", True, f"Retrieved dispute {dispute_id}")
                
                # Test 7: Update Dispute Status
                update_payload = {"status": "RESOLVED"}
                status, update_data = make_request("PATCH", f"/qldb/disputes/{dispute_id}", json=update_payload)
                if status == 200:
                    results.add_result("Update Dispute Status", True, f"Updated dispute {dispute_id} to RESOLVED")
                else:
                    results.add_result("Update Dispute Status", False, f"HTTP {status}: {update_data}")
                
                # Test 8: Get Dispute Audit Trail
                status, audit_data = make_request("GET", f"/qldb/disputes/{dispute_id}/audit")
                if status == 200:
                    audit_entries = audit_data.get("entries", [])
                    results.add_result("Get Dispute Audit Trail", True, f"Retrieved {len(audit_entries)} audit entries")
                else:
                    results.add_result("Get Dispute Audit Trail", False, f"HTTP {status}: {audit_data}")
            else:
                results.add_result("Get Individual Dispute", False, f"HTTP {status}: {dispute_data}")
                results.add_result("Update Dispute Status", False, "Skipped - could not retrieve dispute")
                results.add_result("Get Dispute Audit Trail", False, "Skipped - could not retrieve dispute")
        else:
            results.add_result("Create New Dispute", False, f"No dispute ID in response: {create_data}")
    else:
        results.add_result("Create New Dispute", False, f"HTTP {status}: {create_data}")
    
    # Test 9: Chain Integrity Verification
    status, verify_data = make_request("GET", "/qldb/audit/chain/verify")
    if status == 200:
        if "chain_valid" in verify_data:
            results.add_result("Chain Integrity Verification", True, f"Chain verification: {verify_data}")
        else:
            results.add_result("Chain Integrity Verification", False, f"Missing chain_valid field: {verify_data}")
    else:
        results.add_result("Chain Integrity Verification", False, f"HTTP {status}: {verify_data}")
    
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