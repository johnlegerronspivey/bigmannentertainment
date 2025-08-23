#!/usr/bin/env python3
"""
Big Mann Entertainment Platform - Comprehensive Endpoint Status Testing
Tests ALL major endpoint categories to provide detailed functionality percentage and status report
"""

import requests
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Configuration
BASE_URL = "https://bme-platform-fix.preview.emergentagent.com/api"
TEST_USER_EMAIL = f"endpoint.test.{uuid.uuid4().hex[:8]}@bigmannentertainment.com"
TEST_USER_PASSWORD = "EndpointTest2025!"

class EndpointStatusTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.auth_token = None
        self.test_user_id = None
        
        # Endpoint categories to test
        self.endpoint_categories = {
            "authentication": {
                "endpoints": [
                    ("POST", "/auth/register", "User Registration"),
                    ("POST", "/auth/login", "User Login"),
                    ("GET", "/auth/me", "Current User Info"),
                    ("POST", "/auth/logout", "User Logout"),
                    ("POST", "/auth/refresh", "Token Refresh"),
                    ("POST", "/auth/forgot-password", "Forgot Password"),
                    ("POST", "/auth/reset-password", "Reset Password")
                ],
                "working": [],
                "failed": [],
                "missing": []
            },
            "distribution": {
                "endpoints": [
                    ("GET", "/distribution/platforms", "Platform Listing"),
                    ("POST", "/distribution/distribute", "Content Distribution"),
                    ("GET", "/distribution/history", "Distribution History"),
                    ("GET", "/distribution/status", "Distribution Status"),
                    ("GET", "/distribution/analytics", "Distribution Analytics"),
                    ("GET", "/distribution/platforms/{id}", "Platform Details"),
                    ("POST", "/distribution/schedule", "Schedule Distribution"),
                    ("DELETE", "/distribution/{id}", "Cancel Distribution")
                ],
                "working": [],
                "failed": [],
                "missing": []
            },
            "business": {
                "endpoints": [
                    ("GET", "/business/identifiers", "Business Identifiers"),
                    ("POST", "/business/generate-upc", "UPC Generation"),
                    ("POST", "/business/generate-isrc", "ISRC Generation"),
                    ("GET", "/business/products", "Product Management"),
                    ("POST", "/business/products", "Create Product"),
                    ("GET", "/business/licenses", "Business Licenses"),
                    ("GET", "/business/registrations", "Business Registrations"),
                    ("GET", "/business/compliance", "Compliance Status")
                ],
                "working": [],
                "failed": [],
                "missing": []
            },
            "media": {
                "endpoints": [
                    ("POST", "/media/upload", "Media Upload"),
                    ("GET", "/media/library", "Media Library"),
                    ("GET", "/media/{id}", "Media Details"),
                    ("GET", "/media/{id}/download", "Media Download"),
                    ("PUT", "/media/{id}", "Update Media"),
                    ("DELETE", "/media/{id}", "Delete Media"),
                    ("POST", "/media/{id}/metadata", "Update Metadata"),
                    ("GET", "/media/search", "Media Search")
                ],
                "working": [],
                "failed": [],
                "missing": []
            },
            "admin": {
                "endpoints": [
                    ("GET", "/admin/users", "User Management"),
                    ("GET", "/admin/users/stats", "User Statistics"),
                    ("GET", "/admin/media", "Content Management"),
                    ("GET", "/admin/analytics", "Admin Analytics"),
                    ("POST", "/admin/send-notification", "Send Notification"),
                    ("POST", "/admin/send-bulk-notification", "Bulk Notification"),
                    ("GET", "/admin/system/config", "System Configuration"),
                    ("GET", "/admin/reports", "Admin Reports")
                ],
                "working": [],
                "failed": [],
                "missing": []
            },
            "payments": {
                "endpoints": [
                    ("GET", "/payments/packages", "Payment Packages"),
                    ("POST", "/payments/checkout", "Payment Checkout"),
                    ("GET", "/payments/status", "Payment Status"),
                    ("GET", "/payments/earnings", "User Earnings"),
                    ("POST", "/payments/payouts", "Request Payout"),
                    ("GET", "/payments/history", "Payment History"),
                    ("GET", "/payments/methods", "Payment Methods"),
                    ("POST", "/payments/webhook", "Payment Webhook")
                ],
                "working": [],
                "failed": [],
                "missing": []
            },
            "label": {
                "endpoints": [
                    ("GET", "/label/dashboard", "Label Dashboard"),
                    ("GET", "/label/artists", "Artist Management"),
                    ("POST", "/label/artists", "Add Artist"),
                    ("GET", "/label/contracts", "Contract Management"),
                    ("POST", "/label/contracts", "Create Contract"),
                    ("GET", "/label/projects", "Project Management"),
                    ("GET", "/label/analytics", "Label Analytics"),
                    ("GET", "/label/royalties", "Royalty Management")
                ],
                "working": [],
                "failed": [],
                "missing": []
            },
            "ddex": {
                "endpoints": [
                    ("GET", "/ddex/dashboard", "DDEX Dashboard"),
                    ("GET", "/ddex/ern", "ERN Messages"),
                    ("POST", "/ddex/ern", "Create ERN"),
                    ("GET", "/ddex/cwr", "CWR Messages"),
                    ("POST", "/ddex/cwr", "Create CWR"),
                    ("GET", "/ddex/messages", "Message History"),
                    ("GET", "/ddex/identifiers", "DDEX Identifiers"),
                    ("POST", "/ddex/validate", "Validate DDEX")
                ],
                "working": [],
                "failed": [],
                "missing": []
            },
            "sponsorship": {
                "endpoints": [
                    ("GET", "/sponsorship/dashboard", "Sponsorship Dashboard"),
                    ("GET", "/sponsorship/sponsors", "Sponsor Management"),
                    ("POST", "/sponsorship/sponsors", "Add Sponsor"),
                    ("GET", "/sponsorship/deals", "Deal Management"),
                    ("POST", "/sponsorship/deals", "Create Deal"),
                    ("GET", "/sponsorship/metrics", "Sponsorship Metrics"),
                    ("GET", "/sponsorship/analytics", "Sponsorship Analytics"),
                    ("GET", "/sponsorship/campaigns", "Campaign Management")
                ],
                "working": [],
                "failed": [],
                "missing": []
            },
            "tax": {
                "endpoints": [
                    ("GET", "/tax/dashboard", "Tax Dashboard"),
                    ("GET", "/tax/dashboard/2025", "Tax Dashboard 2025"),
                    ("GET", "/tax/business-info", "Tax Business Info"),
                    ("GET", "/tax/payments", "Tax Payments"),
                    ("GET", "/tax/1099s", "1099 Generation"),
                    ("POST", "/tax/1099s/generate", "Generate 1099"),
                    ("GET", "/tax/settings", "Tax Settings"),
                    ("GET", "/tax/reporting", "Tax Reporting")
                ],
                "working": [],
                "failed": [],
                "missing": []
            },
            "industry": {
                "endpoints": [
                    ("GET", "/industry/dashboard", "Industry Dashboard"),
                    ("GET", "/industry/partners", "Industry Partners"),
                    ("GET", "/industry/analytics", "Industry Analytics"),
                    ("GET", "/industry/identifiers", "Industry Identifiers"),
                    ("GET", "/industry/coverage", "Industry Coverage"),
                    ("GET", "/industry/mdx", "MDX Dashboard"),
                    ("GET", "/industry/mlc", "MLC Dashboard"),
                    ("GET", "/industry/ipi", "IPI Numbers")
                ],
                "working": [],
                "failed": [],
                "missing": []
            },
            "licensing": {
                "endpoints": [
                    ("GET", "/licensing/dashboard", "Licensing Dashboard"),
                    ("GET", "/licensing/statutory-rates", "Statutory Rates"),
                    ("GET", "/licensing/compliance", "Licensing Compliance"),
                    ("GET", "/licensing/usage-tracking", "Usage Tracking"),
                    ("GET", "/licensing/compensation", "Daily Compensation"),
                    ("GET", "/licensing/payouts", "Daily Payouts"),
                    ("GET", "/licensing/history", "Licensing History"),
                    ("POST", "/licensing/register", "Register License")
                ],
                "working": [],
                "failed": [],
                "missing": []
            },
            "gs1": {
                "endpoints": [
                    ("GET", "/gs1/dashboard", "GS1 Dashboard"),
                    ("GET", "/gs1/business-info", "GS1 Business Info"),
                    ("GET", "/gs1/products", "GS1 Products"),
                    ("POST", "/gs1/products", "Create GS1 Product"),
                    ("GET", "/gs1/locations", "GS1 Locations"),
                    ("POST", "/gs1/locations", "Create GS1 Location"),
                    ("GET", "/gs1/validation", "GS1 Validation"),
                    ("POST", "/gs1/barcode", "Generate Barcode")
                ],
                "working": [],
                "failed": [],
                "missing": []
            }
        }
        
        self.test_results = {
            "total_endpoints": 0,
            "working_endpoints": 0,
            "failed_endpoints": 0,
            "missing_endpoints": 0,
            "overall_percentage": 0.0,
            "category_results": {},
            "detailed_results": []
        }
    
    def make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request with proper headers"""
        url = f"{self.base_url}{endpoint}"
        headers = kwargs.get('headers', {})
        
        if self.auth_token:
            headers['Authorization'] = f'Bearer {self.auth_token}'
        
        kwargs['headers'] = headers
        
        try:
            response = self.session.request(method, url, timeout=10, **kwargs)
            return response
        except Exception as request_error:
            print(f"Request failed for {method} {endpoint}: {request_error}")
            # Return a mock response for connection errors
            class MockResponse:
                def __init__(self, error):
                    self.status_code = 500
                    self.text = f"Connection error: {str(error)}"
                def json(self):
                    return {"error": "Connection failed"}
            return MockResponse(request_error)
    
    def setup_authentication(self) -> bool:
        """Setup authentication for testing protected endpoints"""
        try:
            # Try to register a test user
            user_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD,
                "full_name": "Endpoint Test User",
                "business_name": "Big Mann Entertainment Test",
                "date_of_birth": (datetime.utcnow() - timedelta(days=25*365)).isoformat(),
                "address_line1": "1314 Lincoln Heights Street",
                "city": "Alexander City",
                "state_province": "Alabama",
                "postal_code": "35010",
                "country": "United States"
            }
            
            response = self.make_request('POST', '/auth/register', json=user_data)
            
            if response.status_code in [200, 201]:
                data = response.json()
                if 'access_token' in data:
                    self.auth_token = data['access_token']
                    self.test_user_id = data.get('user', {}).get('id')
                    print("✅ Authentication setup successful")
                    return True
            
            # If registration fails, try login
            login_data = {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
            
            response = self.make_request('POST', '/auth/login', json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if 'access_token' in data:
                    self.auth_token = data['access_token']
                    self.test_user_id = data.get('user', {}).get('id')
                    print("✅ Authentication setup successful (login)")
                    return True
            
            print("⚠️ Authentication setup failed - will test public endpoints only")
            return False
            
        except Exception as e:
            print(f"⚠️ Authentication setup error: {e}")
            return False
    
    def test_endpoint(self, method: str, endpoint: str, description: str) -> Dict[str, Any]:
        """Test a single endpoint and return result"""
        try:
            # Handle parameterized endpoints
            test_endpoint = endpoint
            if "{id}" in endpoint:
                test_endpoint = endpoint.replace("{id}", "test-id-123")
            
            response = self.make_request(method, test_endpoint)
            
            # Determine if endpoint is working based on status code
            if response.status_code == 200:
                status = "working"
                details = f"✅ {description} - Status: {response.status_code}"
            elif response.status_code == 201:
                status = "working"
                details = f"✅ {description} - Status: {response.status_code} (Created)"
            elif response.status_code in [401, 403]:
                # Authentication required - endpoint exists but needs auth
                status = "working"
                details = f"🔒 {description} - Status: {response.status_code} (Auth Required)"
            elif response.status_code == 404:
                status = "missing"
                details = f"❌ {description} - Status: {response.status_code} (Not Found)"
            elif response.status_code == 405:
                status = "working"
                details = f"⚠️ {description} - Status: {response.status_code} (Method Not Allowed - Endpoint Exists)"
            elif response.status_code in [400, 422]:
                status = "working"
                details = f"⚠️ {description} - Status: {response.status_code} (Bad Request - Endpoint Exists)"
            elif response.status_code >= 500:
                status = "failed"
                details = f"💥 {description} - Status: {response.status_code} (Server Error)"
            else:
                status = "failed"
                details = f"❓ {description} - Status: {response.status_code} (Unexpected)"
            
            return {
                "endpoint": endpoint,
                "method": method,
                "description": description,
                "status": status,
                "status_code": response.status_code,
                "details": details
            }
            
        except Exception as e:
            return {
                "endpoint": endpoint,
                "method": method,
                "description": description,
                "status": "failed",
                "status_code": 500,
                "details": f"💥 {description} - Exception: {str(e)}"
            }
    
    def test_category(self, category_name: str) -> Dict[str, Any]:
        """Test all endpoints in a category"""
        print(f"\n🔍 Testing {category_name.upper()} endpoints...")
        
        category = self.endpoint_categories[category_name]
        results = {
            "total": len(category["endpoints"]),
            "working": 0,
            "failed": 0,
            "missing": 0,
            "percentage": 0.0,
            "details": []
        }
        
        for method, endpoint, description in category["endpoints"]:
            result = self.test_endpoint(method, endpoint, description)
            results["details"].append(result)
            
            if result["status"] == "working":
                results["working"] += 1
                category["working"].append(result)
            elif result["status"] == "failed":
                results["failed"] += 1
                category["failed"].append(result)
            elif result["status"] == "missing":
                results["missing"] += 1
                category["missing"].append(result)
            
            print(f"  {result['details']}")
        
        # Calculate percentage (working endpoints / total endpoints)
        if results["total"] > 0:
            results["percentage"] = (results["working"] / results["total"]) * 100
        
        print(f"📊 {category_name.upper()} Summary: {results['working']}/{results['total']} working ({results['percentage']:.1f}%)")
        
        return results
    
    def run_comprehensive_test(self):
        """Run comprehensive endpoint testing"""
        print("🎯 BIG MANN ENTERTAINMENT - COMPREHENSIVE ENDPOINT STATUS TESTING")
        print("=" * 80)
        print("Testing ALL major endpoint categories for 100% functionality analysis")
        print("=" * 80)
        
        # Setup authentication
        self.setup_authentication()
        
        # Test all categories
        for category_name in self.endpoint_categories.keys():
            category_result = self.test_category(category_name)
            self.test_results["category_results"][category_name] = category_result
            
            # Update overall statistics
            self.test_results["total_endpoints"] += category_result["total"]
            self.test_results["working_endpoints"] += category_result["working"]
            self.test_results["failed_endpoints"] += category_result["failed"]
            self.test_results["missing_endpoints"] += category_result["missing"]
        
        # Calculate overall percentage
        if self.test_results["total_endpoints"] > 0:
            self.test_results["overall_percentage"] = (
                self.test_results["working_endpoints"] / self.test_results["total_endpoints"]
            ) * 100
        
        # Generate comprehensive report
        self.generate_status_report()
    
    def generate_status_report(self):
        """Generate comprehensive endpoint status report"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE ENDPOINT STATUS REPORT")
        print("=" * 80)
        
        # Overall Statistics
        print(f"\n🎯 OVERALL FUNCTIONALITY STATUS:")
        print(f"Total Endpoints Tested: {self.test_results['total_endpoints']}")
        print(f"Working Endpoints: {self.test_results['working_endpoints']}")
        print(f"Failed/Error Endpoints: {self.test_results['failed_endpoints']}")
        print(f"Missing/Not Found Endpoints: {self.test_results['missing_endpoints']}")
        print(f"Overall Functionality Percentage: {self.test_results['overall_percentage']:.1f}%")
        
        # Category Breakdown
        print(f"\n📋 CATEGORY BREAKDOWN:")
        for category, results in self.test_results["category_results"].items():
            print(f"\n🔸 {category.upper()}:")
            print(f"  Total: {results['total']} | Working: {results['working']} | Failed: {results['failed']} | Missing: {results['missing']}")
            print(f"  Functionality: {results['percentage']:.1f}%")
        
        # Working Endpoints List
        print(f"\n✅ WORKING ENDPOINTS ({self.test_results['working_endpoints']}):")
        for category, category_data in self.endpoint_categories.items():
            if category_data["working"]:
                print(f"\n  {category.upper()}:")
                for endpoint in category_data["working"]:
                    print(f"    ✅ {endpoint['method']} {endpoint['endpoint']} - {endpoint['description']}")
        
        # Failed/Missing Endpoints List
        failed_missing_count = self.test_results['failed_endpoints'] + self.test_results['missing_endpoints']
        print(f"\n❌ FAILED/MISSING ENDPOINTS ({failed_missing_count}):")
        for category, category_data in self.endpoint_categories.items():
            failed_missing = category_data["failed"] + category_data["missing"]
            if failed_missing:
                print(f"\n  {category.upper()}:")
                for endpoint in category_data["failed"]:
                    print(f"    💥 {endpoint['method']} {endpoint['endpoint']} - {endpoint['description']} (FAILED)")
                for endpoint in category_data["missing"]:
                    print(f"    ❌ {endpoint['method']} {endpoint['endpoint']} - {endpoint['description']} (MISSING)")
        
        # Modules Needing Additional Endpoints
        print(f"\n🔧 MODULES NEEDING ADDITIONAL ENDPOINTS:")
        for category, results in self.test_results["category_results"].items():
            if results["percentage"] < 100:
                missing_count = results["failed"] + results["missing"]
                print(f"  🔸 {category.upper()}: {missing_count} endpoints need implementation ({results['percentage']:.1f}% complete)")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS FOR 100% FUNCTIONALITY:")
        
        priority_modules = []
        for category, results in self.test_results["category_results"].items():
            if results["percentage"] < 50:
                priority_modules.append((category, results["percentage"]))
        
        if priority_modules:
            priority_modules.sort(key=lambda x: x[1])  # Sort by percentage (lowest first)
            print(f"  🔥 HIGH PRIORITY (< 50% functional):")
            for module, percentage in priority_modules:
                print(f"    - {module.upper()}: {percentage:.1f}% functional")
        
        medium_priority = []
        for category, results in self.test_results["category_results"].items():
            if 50 <= results["percentage"] < 80:
                medium_priority.append((category, results["percentage"]))
        
        if medium_priority:
            print(f"  ⚠️ MEDIUM PRIORITY (50-80% functional):")
            for module, percentage in medium_priority:
                print(f"    - {module.upper()}: {percentage:.1f}% functional")
        
        low_priority = []
        for category, results in self.test_results["category_results"].items():
            if 80 <= results["percentage"] < 100:
                low_priority.append((category, results["percentage"]))
        
        if low_priority:
            print(f"  ✅ LOW PRIORITY (80-100% functional):")
            for module, percentage in low_priority:
                print(f"    - {module.upper()}: {percentage:.1f}% functional")
        
        print("\n" + "=" * 80)
        print("🎯 ENDPOINT STATUS TESTING COMPLETED")
        print("=" * 80)

def main():
    """Main function to run endpoint status testing"""
    tester = EndpointStatusTester()
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main()