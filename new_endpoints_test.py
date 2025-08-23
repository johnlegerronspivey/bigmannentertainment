#!/usr/bin/env python3
"""
NEW ENDPOINTS TESTING for Big Mann Entertainment Platform
Testing the newly implemented endpoints for DDEX, Distribution, Media, and Licensing modules
"""

import requests
import json
import time
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Configuration
BACKEND_URL = "https://bme-platform-fix.preview.emergentagent.com/api"
TEST_USER_EMAIL = "licensing.test@bigmannentertainment.com"
TEST_USER_PASSWORD = "BigMann2025!"
TEST_USER_NAME = "Licensing Test User"

class NewEndpointsTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test results"""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            self.failed_tests += 1
            status = "❌ FAIL"
            
        result = {
            "test_name": test_name,
            "status": status,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"    Details: {details}")
        if not success and response_data:
            print(f"    Response: {response_data}")
        print()

    def authenticate(self) -> bool:
        """Authenticate and get access token"""
        try:
            # First try to register the test user
            register_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD,
                "full_name": TEST_USER_NAME,
                "business_name": "Big Mann Entertainment Test",
                "date_of_birth": "1990-01-01T00:00:00",
                "address_line1": "123 Test Street",
                "city": "Test City",
                "state_province": "Test State",
                "postal_code": "12345",
                "country": "US"
            }
            
            register_response = self.session.post(f"{BACKEND_URL}/auth/register", json=register_data)
            
            # Now try to login
            login_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                self.log_test("Authentication", True, f"Successfully authenticated as {TEST_USER_EMAIL}")
                return True
            else:
                self.log_test("Authentication", False, f"Login failed: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Authentication", False, f"Authentication error: {str(e)}")
            return False

    def test_new_ddex_endpoints(self):
        """Test NEW DDEX endpoints"""
        print("🎵 TESTING NEW DDEX ENDPOINTS")
        print("=" * 50)
        
        # Test 1: /api/ddex/dashboard (NEW)
        try:
            response = self.session.get(f"{BACKEND_URL}/ddex/dashboard")
            if response.status_code == 200:
                data = response.json()
                dashboard = data.get("dashboard", {})
                overview = dashboard.get("overview", {})
                self.log_test("DDEX Dashboard (NEW)", True, 
                             f"Dashboard loaded - Releases: {overview.get('total_releases', 0)}, Works: {overview.get('total_works', 0)}, Success rate: {overview.get('success_rate', 0)}%")
            else:
                self.log_test("DDEX Dashboard (NEW)", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_test("DDEX Dashboard (NEW)", False, f"Error: {str(e)}")

        # Test 2: /api/ddex/ern (NEW)
        try:
            response = self.session.get(f"{BACKEND_URL}/ddex/ern")
            if response.status_code == 200:
                data = response.json()
                ern_messages = data.get("ern_messages", [])
                total = data.get("total", 0)
                self.log_test("DDEX ERN Endpoint (NEW)", True, 
                             f"ERN messages retrieved - Count: {len(ern_messages)}, Total: {total}")
            else:
                self.log_test("DDEX ERN Endpoint (NEW)", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_test("DDEX ERN Endpoint (NEW)", False, f"Error: {str(e)}")

        # Test 3: /api/ddex/cwr (NEW)
        try:
            response = self.session.get(f"{BACKEND_URL}/ddex/cwr")
            if response.status_code == 200:
                data = response.json()
                cwr_messages = data.get("cwr_messages", [])
                total = data.get("total", 0)
                self.log_test("DDEX CWR Endpoint (NEW)", True, 
                             f"CWR messages retrieved - Count: {len(cwr_messages)}, Total: {total}")
            else:
                self.log_test("DDEX CWR Endpoint (NEW)", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_test("DDEX CWR Endpoint (NEW)", False, f"Error: {str(e)}")

        # Test 4: /api/ddex/identifiers (NEW)
        try:
            response = self.session.get(f"{BACKEND_URL}/ddex/identifiers")
            if response.status_code == 200:
                data = response.json()
                identifiers = data.get("identifiers", {})
                business_ids = identifiers.get("business_identifiers", {})
                self.log_test("DDEX Identifiers (NEW)", True, 
                             f"Identifiers retrieved - ISRC prefix: {identifiers.get('isrc_prefix')}, Business EIN: {business_ids.get('business_ein')}")
            else:
                self.log_test("DDEX Identifiers (NEW)", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_test("DDEX Identifiers (NEW)", False, f"Error: {str(e)}")

        # Test 5: /api/ddex/music-reports/cwr (NEW)
        try:
            response = self.session.get(f"{BACKEND_URL}/ddex/music-reports/cwr")
            if response.status_code == 200:
                data = response.json()
                music_reports = data.get("music_reports_cwr", {})
                integration_status = music_reports.get("integration_status", {})
                self.log_test("DDEX Music Reports CWR (NEW)", True, 
                             f"Music Reports integration - Works: {integration_status.get('total_works_registered', 0)}, Pending: {integration_status.get('pending_sync', 0)}")
            else:
                self.log_test("DDEX Music Reports CWR (NEW)", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_test("DDEX Music Reports CWR (NEW)", False, f"Error: {str(e)}")

    def test_new_distribution_endpoints(self):
        """Test NEW Distribution endpoints"""
        print("📡 TESTING NEW DISTRIBUTION ENDPOINTS")
        print("=" * 50)
        
        # Test 1: /api/distribution/status (NEW)
        try:
            response = self.session.get(f"{BACKEND_URL}/distribution/status")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Distribution Status (NEW)", True, 
                             f"Status retrieved - Active: {data.get('active_distributions', 0)}, Success rate: {data.get('success_rate', 0)}%")
            else:
                self.log_test("Distribution Status (NEW)", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Distribution Status (NEW)", False, f"Error: {str(e)}")

        # Test 2: /api/distribution/analytics (NEW)
        try:
            response = self.session.get(f"{BACKEND_URL}/distribution/analytics")
            if response.status_code == 200:
                data = response.json()
                analytics = data.get("analytics", {})
                self.log_test("Distribution Analytics (NEW)", True, 
                             f"Analytics retrieved - Total distributions: {analytics.get('total_distributions', 0)}")
            else:
                self.log_test("Distribution Analytics (NEW)", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Distribution Analytics (NEW)", False, f"Error: {str(e)}")

        # Test 3: /api/distribution/platforms/{platform_id} (NEW)
        try:
            platform_id = "spotify"
            response = self.session.get(f"{BACKEND_URL}/distribution/platforms/{platform_id}")
            if response.status_code == 200:
                data = response.json()
                platform_info = data.get("platform", {})
                self.log_test("Distribution Platform Details (NEW)", True, 
                             f"Platform {platform_id} - Name: {platform_info.get('name')}, Type: {platform_info.get('type')}")
            else:
                self.log_test("Distribution Platform Details (NEW)", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Distribution Platform Details (NEW)", False, f"Error: {str(e)}")

        # Test 4: /api/distribution/schedule (NEW)
        try:
            schedule_data = {
                "media_id": "test-media-id",
                "platforms": ["spotify", "apple_music"],
                "scheduled_time": (datetime.now() + timedelta(hours=1)).isoformat(),
                "custom_message": "Test scheduled distribution"
            }
            response = self.session.post(f"{BACKEND_URL}/distribution/schedule", json=schedule_data)
            if response.status_code in [200, 201]:
                data = response.json()
                self.log_test("Distribution Schedule (NEW)", True, 
                             f"Distribution scheduled - ID: {data.get('distribution_id', 'N/A')}")
            else:
                self.log_test("Distribution Schedule (NEW)", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Distribution Schedule (NEW)", False, f"Error: {str(e)}")

        # Test 5: /api/distribution/{id} DELETE (NEW)
        try:
            # First create a distribution to delete
            distribution_data = {
                "media_id": "test-media-id",
                "platforms": ["spotify"],
                "custom_message": "Test distribution for deletion"
            }
            create_response = self.session.post(f"{BACKEND_URL}/distribution/distribute", json=distribution_data)
            
            if create_response.status_code in [200, 201]:
                create_data = create_response.json()
                distribution_id = create_data.get("distribution_id")
                
                if distribution_id:
                    delete_response = self.session.delete(f"{BACKEND_URL}/distribution/{distribution_id}")
                    if delete_response.status_code in [200, 204]:
                        self.log_test("Distribution DELETE (NEW)", True, 
                                     f"Distribution {distribution_id} deleted successfully")
                    else:
                        self.log_test("Distribution DELETE (NEW)", False, f"Delete status: {delete_response.status_code}", delete_response.text)
                else:
                    self.log_test("Distribution DELETE (NEW)", False, "No distribution ID returned from creation")
            else:
                self.log_test("Distribution DELETE (NEW)", False, f"Failed to create test distribution: {create_response.status_code}")
        except Exception as e:
            self.log_test("Distribution DELETE (NEW)", False, f"Error: {str(e)}")

    def test_new_media_endpoints(self):
        """Test NEW Media endpoints"""
        print("🎬 TESTING NEW MEDIA ENDPOINTS")
        print("=" * 50)
        
        # Get existing media to test with
        existing_media_id = None
        try:
            response = self.session.get(f"{BACKEND_URL}/media/library")
            if response.status_code == 200:
                data = response.json()
                media_list = data.get("media", [])
                if media_list:
                    existing_media_id = media_list[0].get("id")
        except:
            pass

        # Test 1: /api/media/{id} PUT (NEW)
        try:
            test_media_id = existing_media_id or "test-media-id"
            update_data = {
                "title": "Updated Test Media Title",
                "description": "Updated description for testing",
                "tags": ["test", "updated", "big-mann"],
                "category": "music"
            }
            response = self.session.put(f"{BACKEND_URL}/media/{test_media_id}", json=update_data)
            if response.status_code == 200:
                self.log_test("Media PUT Update (NEW)", True, 
                             f"Media {test_media_id} updated successfully")
            elif response.status_code == 404 and not existing_media_id:
                self.log_test("Media PUT Update (NEW)", True, 
                             f"Correctly returned 404 for non-existent media ID")
            else:
                self.log_test("Media PUT Update (NEW)", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Media PUT Update (NEW)", False, f"Error: {str(e)}")

        # Test 2: /api/media/{id} DELETE (NEW)
        try:
            test_media_id = "test-media-id-for-deletion"
            response = self.session.delete(f"{BACKEND_URL}/media/{test_media_id}")
            if response.status_code == 404:
                self.log_test("Media DELETE (NEW)", True, 
                             f"Correctly returned 404 for non-existent media ID")
            elif response.status_code in [200, 204]:
                self.log_test("Media DELETE (NEW)", True, 
                             f"Media deletion endpoint working (returned {response.status_code})")
            else:
                self.log_test("Media DELETE (NEW)", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Media DELETE (NEW)", False, f"Error: {str(e)}")

        # Test 3: /api/media/{id}/metadata (NEW)
        try:
            test_media_id = existing_media_id or "test-media-id"
            metadata_data = {
                "artist": "Big Mann Entertainment",
                "album": "Test Album",
                "genre": "Hip-Hop",
                "year": 2025,
                "duration": 180,
                "bpm": 120
            }
            response = self.session.post(f"{BACKEND_URL}/media/{test_media_id}/metadata", json=metadata_data)
            if response.status_code in [200, 201]:
                self.log_test("Media Metadata (NEW)", True, 
                             f"Metadata updated for media {test_media_id}")
            elif response.status_code == 404 and not existing_media_id:
                self.log_test("Media Metadata (NEW)", True, 
                             f"Correctly returned 404 for non-existent media ID")
            else:
                self.log_test("Media Metadata (NEW)", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Media Metadata (NEW)", False, f"Error: {str(e)}")

        # Test 4: /api/media/search (NEW)
        try:
            search_params = {
                "query": "test",
                "category": "music",
                "limit": 10
            }
            response = self.session.get(f"{BACKEND_URL}/media/search", params=search_params)
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                total = data.get("total", 0)
                self.log_test("Media Search (NEW)", True, 
                             f"Search completed - Found {len(results)} results, total: {total}")
            else:
                self.log_test("Media Search (NEW)", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Media Search (NEW)", False, f"Error: {str(e)}")

    def test_new_licensing_endpoints(self):
        """Test NEW Licensing endpoints"""
        print("⚖️ TESTING NEW LICENSING ENDPOINTS")
        print("=" * 50)
        
        # Test 1: /api/licensing/compliance (NEW)
        try:
            response = self.session.get(f"{BACKEND_URL}/licensing/compliance")
            if response.status_code == 200:
                data = response.json()
                compliance_overview = data.get("compliance_overview", {})
                self.log_test("Licensing Compliance (NEW)", True, 
                             f"Compliance - Rate: {compliance_overview.get('overall_compliance_rate', 0)}%, Platforms: {compliance_overview.get('total_platforms', 0)}")
            else:
                self.log_test("Licensing Compliance (NEW)", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Licensing Compliance (NEW)", False, f"Error: {str(e)}")

        # Test 2: /api/licensing/usage-tracking (NEW)
        try:
            response = self.session.get(f"{BACKEND_URL}/licensing/usage-tracking")
            if response.status_code == 200:
                data = response.json()
                usage_tracking = data.get("usage_tracking", {})
                total_usage = usage_tracking.get("total_usage", {})
                self.log_test("Licensing Usage Tracking (NEW)", True, 
                             f"Usage - Streams: {total_usage.get('streams', 0)}, Revenue: ${total_usage.get('revenue', 0)}")
            else:
                self.log_test("Licensing Usage Tracking (NEW)", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Licensing Usage Tracking (NEW)", False, f"Error: {str(e)}")

        # Test 3: /api/licensing/compensation (NEW)
        try:
            response = self.session.get(f"{BACKEND_URL}/licensing/compensation")
            if response.status_code == 200:
                data = response.json()
                compensation = data.get("compensation", {})
                self.log_test("Licensing Compensation (NEW)", True, 
                             f"Compensation - Period: {compensation.get('period_days', 0)} days, Type: {compensation.get('compensation_type')}")
            else:
                self.log_test("Licensing Compensation (NEW)", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Licensing Compensation (NEW)", False, f"Error: {str(e)}")

        # Test 4: /api/licensing/payouts (NEW)
        try:
            response = self.session.get(f"{BACKEND_URL}/licensing/payouts")
            if response.status_code == 200:
                data = response.json()
                payouts = data.get("payouts", {})
                payout_summary = payouts.get("payout_summary", {})
                self.log_test("Licensing Payouts (NEW)", True, 
                             f"Payouts - Total: {payout_summary.get('total_payouts', 0)}, Amount: ${payout_summary.get('total_amount', 0)}")
            else:
                self.log_test("Licensing Payouts (NEW)", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Licensing Payouts (NEW)", False, f"Error: {str(e)}")

        # Test 5: /api/licensing/history (NEW)
        try:
            response = self.session.get(f"{BACKEND_URL}/licensing/history")
            if response.status_code == 200:
                data = response.json()
                licensing_history = data.get("licensing_history", {})
                self.log_test("Licensing History (NEW)", True, 
                             f"History retrieved - Period: {licensing_history.get('period_start')} to {licensing_history.get('period_end')}")
            else:
                self.log_test("Licensing History (NEW)", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Licensing History (NEW)", False, f"Error: {str(e)}")

        # Test 6: /api/licensing/register (NEW)
        try:
            register_data = {
                "platform_ids": ["spotify", "apple_music", "youtube"],
                "license_type": "standard",
                "duration_months": 12
            }
            response = self.session.post(f"{BACKEND_URL}/licensing/register", json=register_data)
            if response.status_code in [200, 201]:
                data = response.json()
                registered_licenses = data.get("registered_licenses", [])
                self.log_test("Licensing Register (NEW)", True, 
                             f"Licenses registered - Count: {len(registered_licenses)}")
            else:
                self.log_test("Licensing Register (NEW)", False, f"Status: {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Licensing Register (NEW)", False, f"Error: {str(e)}")

    def generate_summary_report(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 80)
        print("🎯 NEW ENDPOINTS TESTING SUMMARY - BIG MANN ENTERTAINMENT")
        print("=" * 80)
        
        # Calculate success rate
        success_rate = (self.passed_tests / max(self.total_tests, 1)) * 100
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Total NEW Endpoints Tested: {self.total_tests}")
        print(f"   Working: {self.passed_tests} ✅")
        print(f"   Failed: {self.failed_tests} ❌")
        print(f"   Success Rate: {success_rate:.1f}%")
        print()
        
        # Module breakdown
        modules = {
            "DDEX": [r for r in self.test_results if "DDEX" in r["test_name"]],
            "Distribution": [r for r in self.test_results if "Distribution" in r["test_name"]],
            "Media": [r for r in self.test_results if "Media" in r["test_name"]],
            "Licensing": [r for r in self.test_results if "Licensing" in r["test_name"]],
            "Authentication": [r for r in self.test_results if "Authentication" in r["test_name"]]
        }
        
        print("📋 MODULE BREAKDOWN:")
        for module_name, module_tests in modules.items():
            if module_tests:
                module_passed = sum(1 for t in module_tests if t["success"])
                module_total = len(module_tests)
                module_rate = (module_passed / module_total) * 100
                print(f"   {module_name}: {module_passed}/{module_total} ({module_rate:.1f}%)")
        print()
        
        # Failed tests details
        failed_tests = [r for r in self.test_results if not r["success"]]
        if failed_tests:
            print("❌ FAILED ENDPOINTS:")
            for test in failed_tests:
                print(f"   • {test['test_name']}: {test['details']}")
            print()
        
        # Success summary
        successful_tests = [r for r in self.test_results if r["success"]]
        if successful_tests:
            print("✅ WORKING ENDPOINTS:")
            for test in successful_tests:
                if "NEW" in test['test_name']:
                    print(f"   • {test['test_name']}: {test['details']}")
            print()
        
        return {
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": self.failed_tests,
            "success_rate": success_rate,
            "module_breakdown": {name: {"passed": sum(1 for t in tests if t["success"]), 
                                       "total": len(tests)} for name, tests in modules.items() if tests}
        }

    def run_all_tests(self):
        """Run all NEW endpoint tests"""
        print("🚀 TESTING NEW ENDPOINTS FOR BIG MANN ENTERTAINMENT")
        print("🎯 Focus: DDEX, Distribution, Media, and Licensing NEW endpoints")
        print("=" * 80)
        print()
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with testing.")
            return False
        
        # Run all test modules for NEW endpoints
        self.test_new_ddex_endpoints()
        self.test_new_distribution_endpoints()
        self.test_new_media_endpoints()
        self.test_new_licensing_endpoints()
        
        # Generate summary
        summary = self.generate_summary_report()
        
        return summary

def main():
    """Main testing function"""
    tester = NewEndpointsTester()
    summary = tester.run_all_tests()
    
    # Exit with appropriate code
    if summary and summary["success_rate"] >= 75:
        print("🎉 NEW Endpoints testing completed successfully!")
        sys.exit(0)
    else:
        print("⚠️  NEW Endpoints testing completed with issues.")
        sys.exit(1)

if __name__ == "__main__":
    main()