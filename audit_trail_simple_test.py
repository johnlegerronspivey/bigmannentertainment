#!/usr/bin/env python3
"""
Simplified Audit Trail Testing with Manual Authentication
"""

import asyncio
import aiohttp
import json
import os

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://metadata-maestro-1.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

async def test_audit_endpoints():
    """Test audit endpoints with manual authentication"""
    
    print("🎯 SIMPLIFIED AUDIT TRAIL TESTING")
    print("="*60)
    
    async with aiohttp.ClientSession() as session:
        
        # Test 1: Check if audit endpoints are accessible (should return 401/403)
        print("\n1. Testing Audit Service Integration...")
        
        endpoints_to_test = [
            "/audit/logs",
            "/audit/statistics", 
            "/audit/alerts",
            "/audit/admin/platform-statistics"
        ]
        
        for endpoint in endpoints_to_test:
            try:
                async with session.get(f"{API_BASE}{endpoint}") as response:
                    if response.status in [401, 403]:
                        print(f"   ✅ {endpoint} - Accessible (Status: {response.status})")
                    elif response.status == 404:
                        print(f"   ❌ {endpoint} - Not Found (Status: {response.status})")
                    else:
                        print(f"   ⚠️ {endpoint} - Unexpected (Status: {response.status})")
            except Exception as e:
                print(f"   ❌ {endpoint} - Error: {str(e)}")
        
        # Test 2: Try to login to get auth token
        print("\n2. Testing User Login...")
        
        login_data = {
            "email": "simple.test@bigmannentertainment.com",
            "password": "SimpleTest123!"
        }
        
        try:
            async with session.post(f"{API_BASE}/auth/login", json=login_data) as response:
                print(f"   Login Status: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    auth_token = result.get('access_token')
                    user_id = result.get('user', {}).get('id')
                    print(f"   ✅ User logged in successfully: {user_id}")
                    
                    # Test 3: Test authenticated audit endpoints
                    print("\n3. Testing Authenticated Audit Endpoints...")
                    
                    headers = {"Authorization": f"Bearer {auth_token}"}
                    
                    # Test audit logs
                    async with session.get(f"{API_BASE}/audit/logs", headers=headers, params={"limit": 5}) as audit_response:
                        print(f"   Audit Logs: Status {audit_response.status}")
                        if audit_response.status == 200:
                            audit_result = await audit_response.json()
                            print(f"   ✅ Found {len(audit_result.get('audit_logs', []))} audit logs")
                            print(f"   ✅ Total count: {audit_result.get('total_count', 0)}")
                            print(f"   ✅ User access level: {audit_result.get('user_access_level', 'unknown')}")
                        else:
                            error_text = await audit_response.text()
                            print(f"   ❌ Error: {error_text}")
                    
                    # Test audit statistics
                    async with session.get(f"{API_BASE}/audit/statistics", headers=headers) as stats_response:
                        print(f"   Audit Statistics: Status {stats_response.status}")
                        if stats_response.status == 200:
                            stats_result = await stats_response.json()
                            stats = stats_result.get('statistics', {})
                            print(f"   ✅ Total events: {stats.get('total_events', 0)}")
                            print(f"   ✅ Events by type: {len(stats.get('events_by_type', {}))}")
                        else:
                            error_text = await stats_response.text()
                            print(f"   ❌ Error: {error_text}")
                    
                    # Test metadata snapshots
                    test_content_id = "test-content-123"
                    async with session.get(f"{API_BASE}/audit/snapshots/{test_content_id}", headers=headers) as snapshot_response:
                        print(f"   Metadata Snapshots: Status {snapshot_response.status}")
                        if snapshot_response.status == 200:
                            snapshot_result = await snapshot_response.json()
                            print(f"   ✅ Found {snapshot_result.get('total_count', 0)} snapshots")
                        else:
                            print(f"   ⚠️ No snapshots found (expected for test content)")
                    
                    # Test audit timeline
                    async with session.get(f"{API_BASE}/audit/timeline/{test_content_id}", headers=headers) as timeline_response:
                        print(f"   Audit Timeline: Status {timeline_response.status}")
                        if timeline_response.status == 200:
                            timeline_result = await timeline_response.json()
                            print(f"   ✅ Found {timeline_result.get('total_events', 0)} timeline events")
                        else:
                            print(f"   ⚠️ No timeline events found (expected for test content)")
                    
                    # Test report generation
                    report_data = {
                        "report_name": "Simple Test Report",
                        "report_type": "summary",
                        "export_format": "json"
                    }
                    
                    async with session.post(f"{API_BASE}/audit/reports/generate", headers=headers, data=report_data) as report_response:
                        print(f"   Report Generation: Status {report_response.status}")
                        if report_response.status == 200:
                            report_result = await report_response.json()
                            print(f"   ✅ Report generated: {report_result.get('report_id')}")
                            
                            # Test report download
                            report_id = report_result.get('report_id', 'test-report')
                            async with session.get(f"{API_BASE}/audit/reports/{report_id}/download/json", headers=headers) as download_response:
                                print(f"   Report Download: Status {download_response.status}")
                                if download_response.status == 200:
                                    print(f"   ✅ Report download successful")
                                else:
                                    print(f"   ⚠️ Report download failed (may be expected)")
                        else:
                            error_text = await report_response.text()
                            print(f"   ❌ Report generation error: {error_text}")
                    
                elif response.status == 400:
                    error_result = await response.json()
                    print(f"   ❌ Registration failed: {error_result.get('detail', 'Unknown error')}")
                else:
                    error_text = await response.text()
                    print(f"   ❌ Registration failed: Status {response.status} - {error_text}")
                    
        except Exception as e:
            print(f"   ❌ Registration error: {str(e)}")
        
        # Test 4: Test admin endpoints (should be denied)
        print("\n4. Testing Admin Endpoint Access Control...")
        
        admin_endpoints = [
            "/audit/alerts",
            "/audit/admin/platform-statistics"
        ]
        
        for endpoint in admin_endpoints:
            try:
                async with session.get(f"{API_BASE}{endpoint}") as response:
                    if response.status == 403:
                        print(f"   ✅ {endpoint} - Access denied (Status: {response.status})")
                    elif response.status == 401:
                        print(f"   ✅ {endpoint} - Authentication required (Status: {response.status})")
                    else:
                        print(f"   ⚠️ {endpoint} - Unexpected (Status: {response.status})")
            except Exception as e:
                print(f"   ❌ {endpoint} - Error: {str(e)}")
        
        print("\n" + "="*60)
        print("🎯 AUDIT TRAIL TESTING COMPLETE")
        print("="*60)

if __name__ == "__main__":
    asyncio.run(test_audit_endpoints())