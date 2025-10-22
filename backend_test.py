#!/usr/bin/env python3
"""
BME Application Comprehensive Backend Testing
Testing all backend systems including ULN, Creator Profile, Licensing, and Social Media Integration
"""

import requests
import json
import sys
from datetime import datetime

# Configuration - Use production backend URL from review request
BACKEND_URL = "https://bme-social-connect.preview.emergentagent.com/api"
ADMIN_EMAIL = "uln.admin@bigmann.com"
ADMIN_PASSWORD = "Admin123!"

class BMEComprehensiveBackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_results = []
        
    def log_test(self, test_name, status, details):
        """Log test results"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status_symbol = "✅" if status == "PASS" else "❌"
        print(f"{status_symbol} {test_name}: {details}")
        
    def authenticate(self):
        """Authenticate with admin credentials"""
        try:
            login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                self.log_test("Authentication", "PASS", f"Successfully authenticated as {ADMIN_EMAIL}")
                return True
            else:
                self.log_test("Authentication", "FAIL", f"Login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Authentication", "FAIL", f"Authentication error: {str(e)}")
            return False
    
    def test_main_health_endpoint(self):
        """Test main health endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/health")
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status")
                if status == "healthy":
                    self.log_test("Main Health Endpoint", "PASS", 
                                f"System healthy - {data.get('message', 'No message')}")
                    return True
                else:
                    self.log_test("Main Health Endpoint", "FAIL", 
                                f"System status: {status}")
                    return False
            else:
                self.log_test("Main Health Endpoint", "FAIL", 
                            f"Health check failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Main Health Endpoint", "FAIL", 
                        f"Error checking health: {str(e)}")
            return False
    
    def test_uln_health_endpoint(self):
        """Test ULN health endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/uln/health")
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status")
                if status == "healthy":
                    labels_count = data.get("total_labels", 0)
                    self.log_test("ULN Health Endpoint", "PASS", 
                                f"ULN system healthy with {labels_count} labels")
                    return True
                else:
                    self.log_test("ULN Health Endpoint", "FAIL", 
                                f"ULN status: {status}")
                    return False
            else:
                self.log_test("ULN Health Endpoint", "FAIL", 
                            f"ULN health check failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("ULN Health Endpoint", "FAIL", 
                        f"Error checking ULN health: {str(e)}")
            return False
    
    def test_uln_label_hub(self):
        """Test ULN label directory/hub"""
        try:
            response = self.session.get(f"{BACKEND_URL}/uln/dashboard/label-hub")
            
            if response.status_code == 200:
                data = response.json()
                labels = data.get("labels", [])
                total_labels = data.get("total_labels", len(labels))
                self.log_test("ULN Label Hub", "PASS", 
                            f"Retrieved {total_labels} labels from hub")
                return True
            elif response.status_code == 403:
                self.log_test("ULN Label Hub", "FAIL", 
                            "Access denied - requires admin permissions")
                return False
            else:
                self.log_test("ULN Label Hub", "FAIL", 
                            f"Label hub failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_test("ULN Label Hub", "FAIL", 
                        f"Error accessing label hub: {str(e)}")
            return False
    
    def test_uln_edit_label_api(self):
        """Test generic Edit Label API"""
        try:
            # First get a label to edit
            hub_response = self.session.get(f"{BACKEND_URL}/uln/dashboard/label-hub")
            if hub_response.status_code != 200:
                self.log_test("ULN Edit Label API", "FAIL", "Cannot get labels for editing test")
                return False
            
            labels = hub_response.json().get("labels", [])
            if not labels:
                self.log_test("ULN Edit Label API", "FAIL", "No labels available for editing")
                return False
            
            # Test editing the first label
            test_label = labels[0]
            global_id = test_label.get("global_id")
            
            if not global_id:
                self.log_test("ULN Edit Label API", "FAIL", "No global_id found in label")
                return False
            
            # Test update
            update_data = {
                "status": "active",
                "updated_by": "backend_test"
            }
            
            response = self.session.patch(
                f"{BACKEND_URL}/uln/labels/{global_id}",
                json=update_data
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("ULN Edit Label API", "PASS", 
                            f"Successfully updated label {global_id}")
                return True
            else:
                self.log_test("ULN Edit Label API", "FAIL", 
                            f"Edit failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_test("ULN Edit Label API", "FAIL", 
                        f"Error testing edit API: {str(e)}")
            return False
    
    def test_uln_advanced_search(self):
        """Test ULN advanced search"""
        try:
            search_data = {
                "name": "Atlantic",
                "label_type": "major",
                "status": "active"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/uln/labels/advanced-search",
                json=search_data
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                total = data.get("total", 0)
                self.log_test("ULN Advanced Search", "PASS", 
                            f"Search returned {total} results")
                return True
            else:
                self.log_test("ULN Advanced Search", "FAIL", 
                            f"Search failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_test("ULN Advanced Search", "FAIL", 
                        f"Error testing advanced search: {str(e)}")
            return False
    
    def test_uln_bulk_edit(self):
        """Test ULN bulk edit"""
        try:
            # Get some labels first
            hub_response = self.session.get(f"{BACKEND_URL}/uln/dashboard/label-hub")
            if hub_response.status_code != 200:
                self.log_test("ULN Bulk Edit", "FAIL", "Cannot get labels for bulk edit test")
                return False
            
            labels = hub_response.json().get("labels", [])
            if len(labels) < 2:
                self.log_test("ULN Bulk Edit", "FAIL", "Need at least 2 labels for bulk edit test")
                return False
            
            # Test bulk edit on first 2 labels
            label_ids = [labels[0].get("global_id"), labels[1].get("global_id")]
            
            bulk_data = {
                "label_ids": label_ids,
                "update_data": {
                    "status": "active",
                    "updated_by": "bulk_test"
                }
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/uln/labels/bulk-edit",
                json=bulk_data
            )
            
            if response.status_code == 200:
                data = response.json()
                updated_count = data.get("updated_count", 0)
                self.log_test("ULN Bulk Edit", "PASS", 
                            f"Bulk updated {updated_count} labels")
                return True
            else:
                self.log_test("ULN Bulk Edit", "FAIL", 
                            f"Bulk edit failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_test("ULN Bulk Edit", "FAIL", 
                        f"Error testing bulk edit: {str(e)}")
            return False
    
    def test_uln_export(self):
        """Test ULN export"""
        try:
            export_data = {
                "format": "json",
                "include_metadata": True
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/uln/labels/export",
                json=export_data
            )
            
            if response.status_code == 200:
                data = response.json()
                exported_count = data.get("exported_count", 0)
                self.log_test("ULN Export", "PASS", 
                            f"Exported {exported_count} labels")
                return True
            else:
                self.log_test("ULN Export", "FAIL", 
                            f"Export failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_test("ULN Export", "FAIL", 
                        f"Error testing export: {str(e)}")
            return False
    
    def test_profile_health_endpoint(self):
        """Test Creator Profile health endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/profile/health")
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status")
                postgres_status = data.get("postgres", "unknown")
                mongodb_status = data.get("mongodb", "unknown")
                
                self.log_test("Profile Health Endpoint", "PASS", 
                            f"Profile service status: {status}, PostgreSQL: {postgres_status}, MongoDB: {mongodb_status}")
                return True
            else:
                self.log_test("Profile Health Endpoint", "FAIL", 
                            f"Profile health check failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Profile Health Endpoint", "FAIL", 
                        f"Error checking profile health: {str(e)}")
            return False
    
    def test_profile_me_endpoint(self):
        """Test profile retrieval endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/profile/me")
            
            if response.status_code == 200:
                data = response.json()
                has_profile = data.get("hasProfile", False)
                self.log_test("Profile Me Endpoint", "PASS", 
                            f"Profile endpoint working, hasProfile: {has_profile}")
                return True
            elif response.status_code == 500 and "PostgreSQL" in str(response.text):
                self.log_test("Profile Me Endpoint", "FAIL", 
                            "PostgreSQL dependency - endpoint unavailable (expected)")
                return False
            else:
                self.log_test("Profile Me Endpoint", "FAIL", 
                            f"Profile me failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            if "Connection reset by peer" in str(e):
                self.log_test("Profile Me Endpoint", "FAIL", 
                            "PostgreSQL dependency - connection error (expected)")
            else:
                self.log_test("Profile Me Endpoint", "FAIL", 
                            f"Error testing profile me: {str(e)}")
            return False
    
    def test_asset_creation(self):
        """Test asset creation endpoint"""
        try:
            asset_data = {
                "title": "Test Asset",
                "asset_type": "music",
                "description": "Backend test asset"
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/profile/assets/create",
                json=asset_data
            )
            
            if response.status_code == 200:
                data = response.json()
                asset_id = data.get("asset_id")
                gtin = data.get("gtin")
                self.log_test("Asset Creation", "PASS", 
                            f"Asset created with ID: {asset_id}, GTIN: {gtin}")
                return True
            elif response.status_code == 500:
                self.log_test("Asset Creation", "FAIL", 
                            "PostgreSQL dependency - endpoint unavailable (expected)")
                return False
            else:
                self.log_test("Asset Creation", "FAIL", 
                            f"Asset creation failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Asset Creation", "FAIL", 
                        f"PostgreSQL dependency - {str(e)} (expected)")
            return False
    
    def test_dao_proposals(self):
        """Test DAO proposals endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/profile/dao/proposals")
            
            if response.status_code == 200:
                data = response.json()
                proposals = data.get("proposals", [])
                total = data.get("total", 0)
                self.log_test("DAO Proposals", "PASS", 
                            f"Retrieved {total} DAO proposals")
                return True
            elif response.status_code == 500:
                self.log_test("DAO Proposals", "FAIL", 
                            "PostgreSQL dependency - endpoint unavailable (expected)")
                return False
            else:
                self.log_test("DAO Proposals", "FAIL", 
                            f"DAO proposals failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            if "Connection reset by peer" in str(e):
                self.log_test("DAO Proposals", "FAIL", 
                            "PostgreSQL dependency - connection error (expected)")
            else:
                self.log_test("DAO Proposals", "FAIL", 
                            f"Error testing DAO proposals: {str(e)}")
            return False
    
    def test_compensation_dashboard(self):
        """Test compensation dashboard endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/licensing/compensation-dashboard")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for compensation breakdown (nested structure)
                compensation_dashboard = data.get("compensation_dashboard", {})
                breakdown = compensation_dashboard.get("compensation_breakdown", {})
                
                artist_share = breakdown.get("artist_percentage", 0)
                songwriter_share = breakdown.get("songwriter_percentage", 0) 
                publisher_share = breakdown.get("publisher_percentage", 0)
                platform_commission = breakdown.get("big_mann_commission", 0)
                
                total_percentage = artist_share + songwriter_share + publisher_share + platform_commission
                
                if abs(total_percentage - 100.0) < 0.1:  # Allow small floating point differences
                    self.log_test("Compensation Dashboard", "PASS", 
                                f"Compensation breakdown: Artist {artist_share}%, Songwriter {songwriter_share}%, Publisher {publisher_share}%, Platform {platform_commission}% (Total: {total_percentage}%)")
                    return True
                else:
                    self.log_test("Compensation Dashboard", "FAIL", 
                                f"Compensation percentages don't sum to 100%: {total_percentage}%")
                    return False
            else:
                self.log_test("Compensation Dashboard", "FAIL", 
                            f"Compensation dashboard failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Compensation Dashboard", "FAIL", 
                        f"Error testing compensation dashboard: {str(e)}")
            return False
    
    def test_comprehensive_licensing(self):
        """Test comprehensive licensing generation"""
        try:
            response = self.session.post(
                f"{BACKEND_URL}/comprehensive-licensing/generate-all-platform-licenses",
                json={
                    "include_compliance_docs": True,
                    "generate_workflows": True
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                platforms_licensed = data.get("platforms_licensed", 0)
                business_entity = data.get("business_entity", "")
                
                self.log_test("Comprehensive Licensing", "PASS", 
                            f"Generated licenses for {platforms_licensed} platforms, Business: {business_entity}")
                return True
            else:
                self.log_test("Comprehensive Licensing", "FAIL", 
                            f"Comprehensive licensing failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Comprehensive Licensing", "FAIL", 
                        f"Error testing comprehensive licensing: {str(e)}")
            return False
    
    def test_social_health_endpoint(self):
        """Test social media health endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/social/health")
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status")
                providers = data.get("providers_configured", 0)
                self.log_test("Social Health Endpoint", "PASS", 
                            f"Social service status: {status}, Providers: {providers}")
                return True
            else:
                self.log_test("Social Health Endpoint", "FAIL", 
                            f"Social health check failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Social Health Endpoint", "FAIL", 
                        f"Error checking social health: {str(e)}")
            return False
    
    def test_social_connections(self):
        """Test social connections endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/social/connections")
            
            if response.status_code == 200:
                data = response.json()
                connections = data.get("connections", [])
                self.log_test("Social Connections", "PASS", 
                            f"Retrieved {len(connections)} social connections")
                return True
            elif response.status_code == 404:
                self.log_test("Social Connections", "PASS", 
                            "No profile found (expected for new user)")
                return True
            elif response.status_code == 500:
                self.log_test("Social Connections", "FAIL", 
                            "PostgreSQL dependency - endpoint unavailable (expected)")
                return False
            else:
                self.log_test("Social Connections", "FAIL", 
                            f"Social connections failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Social Connections", "FAIL", 
                        f"PostgreSQL dependency - {str(e)} (expected)")
            return False
    
    def test_social_metrics_dashboard(self):
        """Test social metrics dashboard"""
        try:
            response = self.session.get(f"{BACKEND_URL}/social/metrics/dashboard")
            
            if response.status_code == 200:
                data = response.json()
                total_followers = data.get("total_followers", 0)
                total_posts = data.get("total_posts", 0)
                avg_engagement = data.get("avg_engagement", 0.0)
                
                self.log_test("Social Metrics Dashboard", "PASS", 
                            f"Metrics - Followers: {total_followers}, Posts: {total_posts}, Engagement: {avg_engagement}")
                return True
            elif response.status_code == 404:
                self.log_test("Social Metrics Dashboard", "PASS", 
                            "No profile found (expected for new user)")
                return True
            elif response.status_code == 500:
                self.log_test("Social Metrics Dashboard", "FAIL", 
                            "PostgreSQL dependency - endpoint unavailable (expected)")
                return False
            else:
                self.log_test("Social Metrics Dashboard", "FAIL", 
                            f"Social metrics failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Social Metrics Dashboard", "FAIL", 
                        f"PostgreSQL dependency - {str(e)} (expected)")
            return False
    
    # TikTok Integration Tests
    
    def test_tiktok_provider_configuration(self):
        """Test TikTok provider appears in provider list with configured status"""
        try:
            response = self.session.get(f"{BACKEND_URL}/social/providers")
            
            if response.status_code == 200:
                data = response.json()
                providers = data.get("providers", [])
                
                # Find TikTok provider
                tiktok_provider = next((p for p in providers if p.get("provider") == "tiktok"), None)
                
                if tiktok_provider:
                    configured = tiktok_provider.get("configured", False)
                    name = tiktok_provider.get("name", "")
                    
                    if configured:
                        self.log_test("TikTok Provider Configuration", "PASS", 
                                    f"TikTok provider found and configured: {name}")
                        return True
                    else:
                        self.log_test("TikTok Provider Configuration", "FAIL", 
                                    f"TikTok provider found but not configured: {name}")
                        return False
                else:
                    self.log_test("TikTok Provider Configuration", "FAIL", 
                                "TikTok provider not found in provider list")
                    return False
            else:
                self.log_test("TikTok Provider Configuration", "FAIL", 
                            f"Failed to get providers: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_test("TikTok Provider Configuration", "FAIL", 
                        f"Error testing TikTok provider configuration: {str(e)}")
            return False
    
    def test_tiktok_oauth_status(self):
        """Test TikTok OAuth configuration status"""
        try:
            response = self.session.get(f"{BACKEND_URL}/oauth/status")
            
            if response.status_code == 200:
                data = response.json()
                tiktok_config = data.get("tiktok", {})
                
                configured = tiktok_config.get("configured", False)
                scope = tiktok_config.get("scope", "")
                
                if configured:
                    self.log_test("TikTok OAuth Status", "PASS", 
                                f"TikTok OAuth configured with scope: {scope}")
                    return True
                else:
                    self.log_test("TikTok OAuth Status", "FAIL", 
                                "TikTok OAuth not configured")
                    return False
            else:
                self.log_test("TikTok OAuth Status", "FAIL", 
                            f"Failed to get OAuth status: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_test("TikTok OAuth Status", "FAIL", 
                        f"Error testing TikTok OAuth status: {str(e)}")
            return False
    
    def test_tiktok_oauth_connect_endpoint(self):
        """Test TikTok OAuth connect endpoint exists and doesn't return 404/500"""
        try:
            # Test without following redirects to avoid OAuth flow
            response = self.session.get(f"{BACKEND_URL}/social/connect/tiktok", allow_redirects=False)
            
            # Should redirect (302/307) or return authorization URL, not 404/500
            if response.status_code in [302, 307, 200]:
                self.log_test("TikTok OAuth Connect Endpoint", "PASS", 
                            f"TikTok connect endpoint accessible (status: {response.status_code})")
                return True
            elif response.status_code == 401:
                self.log_test("TikTok OAuth Connect Endpoint", "PASS", 
                            "TikTok connect endpoint requires authentication (expected)")
                return True
            elif response.status_code == 400:
                # Check if it's a configuration error vs endpoint not found
                error_text = response.text.lower()
                if "not configured" in error_text or "missing api credentials" in error_text:
                    self.log_test("TikTok OAuth Connect Endpoint", "FAIL", 
                                "TikTok OAuth not properly configured")
                    return False
                else:
                    self.log_test("TikTok OAuth Connect Endpoint", "PASS", 
                                "TikTok connect endpoint exists but has configuration issue")
                    return True
            elif response.status_code == 404:
                self.log_test("TikTok OAuth Connect Endpoint", "FAIL", 
                            "TikTok connect endpoint not found (404)")
                return False
            elif response.status_code == 500:
                self.log_test("TikTok OAuth Connect Endpoint", "FAIL", 
                            f"TikTok connect endpoint server error: {response.text}")
                return False
            else:
                self.log_test("TikTok OAuth Connect Endpoint", "PASS", 
                            f"TikTok connect endpoint accessible (status: {response.status_code})")
                return True
                
        except Exception as e:
            self.log_test("TikTok OAuth Connect Endpoint", "FAIL", 
                        f"Error testing TikTok connect endpoint: {str(e)}")
            return False
    
    def test_tiktok_in_social_health(self):
        """Test TikTok is included in social health endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/social/health")
            
            if response.status_code == 200:
                data = response.json()
                providers = data.get("providers", [])
                
                # Check if TikTok is in the providers list
                tiktok_found = any(p.get("provider") == "tiktok" for p in providers)
                
                if tiktok_found:
                    self.log_test("TikTok in Social Health", "PASS", 
                                "TikTok found in social health providers list")
                    return True
                else:
                    self.log_test("TikTok in Social Health", "FAIL", 
                                "TikTok not found in social health providers list")
                    return False
            else:
                self.log_test("TikTok in Social Health", "FAIL", 
                            f"Social health endpoint failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_test("TikTok in Social Health", "FAIL", 
                        f"Error testing TikTok in social health: {str(e)}")
            return False
    
    def test_tiktok_environment_variables(self):
        """Test TikTok credentials are loaded from environment (indirect test via OAuth status)"""
        try:
            response = self.session.get(f"{BACKEND_URL}/oauth/status")
            
            if response.status_code == 200:
                data = response.json()
                tiktok_config = data.get("tiktok", {})
                
                configured = tiktok_config.get("configured", False)
                
                if configured:
                    self.log_test("TikTok Environment Variables", "PASS", 
                                "TikTok credentials loaded from environment (TIKTOK_CLIENT_KEY and TIKTOK_CLIENT_SECRET)")
                    return True
                else:
                    self.log_test("TikTok Environment Variables", "FAIL", 
                                "TikTok credentials not loaded from environment")
                    return False
            else:
                self.log_test("TikTok Environment Variables", "FAIL", 
                            f"Cannot check environment variables: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("TikTok Environment Variables", "FAIL", 
                        f"Error testing TikTok environment variables: {str(e)}")
            return False
    
    def test_social_connections_endpoint(self):
        """Test social connections endpoint works (may return empty if no connections)"""
        try:
            response = self.session.get(f"{BACKEND_URL}/social/connections")
            
            if response.status_code == 200:
                data = response.json()
                connections = data.get("connections", [])
                self.log_test("Social Connections Endpoint", "PASS", 
                            f"Social connections endpoint working, {len(connections)} connections found")
                return True
            elif response.status_code == 404:
                self.log_test("Social Connections Endpoint", "PASS", 
                            "Social connections endpoint working (no profile found - expected)")
                return True
            elif response.status_code == 500:
                self.log_test("Social Connections Endpoint", "FAIL", 
                            "PostgreSQL dependency - endpoint unavailable (expected)")
                return False
            else:
                self.log_test("Social Connections Endpoint", "FAIL", 
                            f"Social connections failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Social Connections Endpoint", "FAIL", 
                        f"Error testing social connections: {str(e)}")
            return False
    
    # Additional Health & Infrastructure Tests
    
    def test_auth_health_endpoint(self):
        """Test authentication health endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/auth/health")
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status")
                total_users = data.get("total_users", 0)
                active_sessions = data.get("active_sessions", 0)
                
                self.log_test("Auth Health Endpoint", "PASS", 
                            f"Auth service status: {status}, Users: {total_users}, Sessions: {active_sessions}")
                return True
            else:
                self.log_test("Auth Health Endpoint", "FAIL", 
                            f"Auth health check failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Auth Health Endpoint", "FAIL", 
                        f"Error checking auth health: {str(e)}")
            return False
    
    def test_licensing_health_endpoint(self):
        """Test licensing system health endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/licensing/health")
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status")
                capabilities = data.get("capabilities", {})
                
                self.log_test("Licensing Health Endpoint", "PASS", 
                            f"Licensing service status: {status}, Capabilities: {len(capabilities)}")
                return True
            else:
                self.log_test("Licensing Health Endpoint", "FAIL", 
                            f"Licensing health check failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Licensing Health Endpoint", "FAIL", 
                        f"Error checking licensing health: {str(e)}")
            return False
    
    def test_performance_stats_endpoint(self):
        """Test performance monitoring stats endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/performance/stats")
            
            if response.status_code == 200:
                data = response.json()
                total_requests = data.get("total_requests", 0)
                error_rate = data.get("error_rate", 0)
                
                self.log_test("Performance Stats Endpoint", "PASS", 
                            f"Performance stats - Requests: {total_requests}, Error Rate: {error_rate}%")
                return True
            else:
                self.log_test("Performance Stats Endpoint", "FAIL", 
                            f"Performance stats failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Performance Stats Endpoint", "FAIL", 
                        f"Error checking performance stats: {str(e)}")
            return False
    
    def test_database_stats_endpoint(self):
        """Test database statistics endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/database/stats")
            
            if response.status_code == 200:
                data = response.json()
                collections = data.get("collections", 0)
                indexes = data.get("indexes", {})
                
                self.log_test("Database Stats Endpoint", "PASS", 
                            f"Database stats - Collections: {collections}, Indexes: {len(indexes)}")
                return True
            else:
                self.log_test("Database Stats Endpoint", "FAIL", 
                            f"Database stats failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Database Stats Endpoint", "FAIL", 
                        f"Error checking database stats: {str(e)}")
            return False
    
    def test_auth_me_endpoint(self):
        """Test current user info endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/auth/me")
            
            if response.status_code == 200:
                data = response.json()
                email = data.get("email", "")
                role = data.get("role", "")
                business_name = data.get("business_name", "")
                
                self.log_test("Auth Me Endpoint", "PASS", 
                            f"User info - Email: {email}, Role: {role}, Business: {business_name}")
                return True
            else:
                self.log_test("Auth Me Endpoint", "FAIL", 
                            f"Auth me failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Auth Me Endpoint", "FAIL", 
                        f"Error checking auth me: {str(e)}")
            return False
    
    def test_forgot_password_endpoint(self):
        """Test password reset request endpoint"""
        try:
            # Test with a test email (should not actually send email)
            reset_data = {
                "email": "test@example.com"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/forgot-password", json=reset_data)
            
            # Should return 200 regardless of whether email exists (security best practice)
            if response.status_code == 200:
                data = response.json()
                message = data.get("message", "")
                
                self.log_test("Forgot Password Endpoint", "PASS", 
                            f"Password reset endpoint working - {message}")
                return True
            else:
                self.log_test("Forgot Password Endpoint", "FAIL", 
                            f"Forgot password failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Forgot Password Endpoint", "FAIL", 
                        f"Error testing forgot password: {str(e)}")
            return False
    
    def test_uln_audit_trail_endpoint(self):
        """Test ULN audit trail endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/uln/audit/trail")
            
            if response.status_code == 200:
                data = response.json()
                entries = data.get("entries", [])
                total = data.get("total", len(entries))
                
                self.log_test("ULN Audit Trail Endpoint", "PASS", 
                            f"Audit trail - {total} entries found")
                return True
            elif response.status_code == 403:
                self.log_test("ULN Audit Trail Endpoint", "FAIL", 
                            "Access denied - requires admin permissions")
                return False
            else:
                self.log_test("ULN Audit Trail Endpoint", "FAIL", 
                            f"Audit trail failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("ULN Audit Trail Endpoint", "FAIL", 
                        f"Error checking audit trail: {str(e)}")
            return False
    
    def test_qr_generation_endpoint(self):
        """Test QR code generation endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/profile/qr/generate")
            
            if response.status_code == 200:
                data = response.json()
                qr_code = data.get("qr_code", "")
                
                if qr_code:
                    self.log_test("QR Generation Endpoint", "PASS", 
                                f"QR code generated successfully ({len(qr_code)} chars)")
                    return True
                else:
                    self.log_test("QR Generation Endpoint", "FAIL", 
                                "No QR code in response")
                    return False
            elif response.status_code == 500:
                self.log_test("QR Generation Endpoint", "FAIL", 
                            "PostgreSQL dependency - endpoint unavailable (expected)")
                return False
            else:
                self.log_test("QR Generation Endpoint", "FAIL", 
                            f"QR generation failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("QR Generation Endpoint", "FAIL", 
                        f"Error testing QR generation: {str(e)}")
            return False
    
    def test_social_providers_endpoint(self):
        """Test social media providers list endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/social/providers")
            
            if response.status_code == 200:
                data = response.json()
                providers = data.get("providers", [])
                
                # Count configured vs available providers
                configured_count = len([p for p in providers if p.get("configured", False)])
                total_count = len(providers)
                
                self.log_test("Social Providers Endpoint", "PASS", 
                            f"Social providers - {configured_count}/{total_count} configured")
                return True
            else:
                self.log_test("Social Providers Endpoint", "FAIL", 
                            f"Social providers failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Social Providers Endpoint", "FAIL", 
                        f"Error checking social providers: {str(e)}")
            return False
    
    def test_oauth_status_endpoint(self):
        """Test OAuth configuration status endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/oauth/status")
            
            if response.status_code == 200:
                data = response.json()
                
                # Count configured OAuth providers
                configured_providers = []
                for provider, config in data.items():
                    if isinstance(config, dict) and config.get("configured", False):
                        configured_providers.append(provider)
                
                self.log_test("OAuth Status Endpoint", "PASS", 
                            f"OAuth status - {len(configured_providers)} providers configured: {', '.join(configured_providers)}")
                return True
            else:
                self.log_test("OAuth Status Endpoint", "FAIL", 
                            f"OAuth status failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("OAuth Status Endpoint", "FAIL", 
                        f"Error checking OAuth status: {str(e)}")
            return False
    
    def test_social_posts_endpoint(self):
        """Test social media posts endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/social/posts")
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get("posts", [])
                total = data.get("total", len(posts))
                
                self.log_test("Social Posts Endpoint", "PASS", 
                            f"Social posts - {total} posts found")
                return True
            elif response.status_code == 404:
                self.log_test("Social Posts Endpoint", "PASS", 
                            "Social posts endpoint working (no profile found - expected)")
                return True
            elif response.status_code == 500:
                self.log_test("Social Posts Endpoint", "FAIL", 
                            "PostgreSQL dependency - endpoint unavailable (expected)")
                return False
            else:
                self.log_test("Social Posts Endpoint", "FAIL", 
                            f"Social posts failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Social Posts Endpoint", "FAIL", 
                        f"Error testing social posts: {str(e)}")
            return False
    
    def test_distribution_platforms_endpoint(self):
        """Test distribution platforms list endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/distribution/platforms")
            
            if response.status_code == 200:
                data = response.json()
                platforms = data.get("platforms", [])
                total = data.get("total_platforms", data.get("total_count", len(platforms)))
                
                self.log_test("Distribution Platforms Endpoint", "PASS", 
                            f"Distribution platforms - {total} platforms available")
                return True
            else:
                self.log_test("Distribution Platforms Endpoint", "FAIL", 
                            f"Distribution platforms failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Distribution Platforms Endpoint", "FAIL", 
                        f"Error checking distribution platforms: {str(e)}")
            return False
    
    def test_database_connectivity(self):
        """Test database connectivity through various endpoints"""
        try:
            # Test MongoDB connectivity via distribution platforms
            response = self.session.get(f"{BACKEND_URL}/distribution/platforms")
            
            if response.status_code == 200:
                data = response.json()
                platform_count = data.get("total_count", data.get("total_platforms", 0))
                self.log_test("MongoDB Connectivity", "PASS", 
                            f"MongoDB connected - {platform_count} platforms available")
                mongo_ok = True
            else:
                self.log_test("MongoDB Connectivity", "FAIL", 
                            f"MongoDB connection issue: {response.status_code}")
                mongo_ok = False
            
            # Test PostgreSQL connectivity via profile health
            pg_response = self.session.get(f"{BACKEND_URL}/profile/health")
            if pg_response.status_code == 200:
                pg_data = pg_response.json()
                postgres_status = pg_data.get("postgres", "unknown")
                if postgres_status == "connected":
                    self.log_test("PostgreSQL Connectivity", "PASS", "PostgreSQL connected")
                    pg_ok = True
                else:
                    self.log_test("PostgreSQL Connectivity", "FAIL", f"PostgreSQL status: {postgres_status}")
                    pg_ok = False
            else:
                self.log_test("PostgreSQL Connectivity", "FAIL", "Cannot check PostgreSQL status")
                pg_ok = False
            
            return mongo_ok and pg_ok
                
        except Exception as e:
            self.log_test("Database Connectivity", "FAIL", 
                        f"Error testing database connectivity: {str(e)}")
            return False
    
    def test_auth_login(self):
        """Test authentication login endpoint (already done in authenticate but test separately)"""
        try:
            # Test with correct credentials (should work)
            login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            # Use a separate session to avoid interfering with main session
            test_session = requests.Session()
            response = test_session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                access_token = data.get("access_token")
                user_info = data.get("user", {})
                
                if access_token:
                    self.log_test("Auth Login", "PASS", 
                                f"Login successful for {user_info.get('email', 'unknown user')}")
                    return True
                else:
                    self.log_test("Auth Login", "FAIL", "No access token in response")
                    return False
            else:
                self.log_test("Auth Login", "FAIL", 
                            f"Login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Auth Login", "FAIL", 
                        f"Error testing auth login: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all BME comprehensive backend tests"""
        print("🚀 Starting BME Application Comprehensive Backend Testing")
        print("Following Review Request Protocol for https://bme-social-connect.preview.emergentagent.com")
        print("=" * 80)
        
        # Test 1: Authentication
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed with other tests")
            return False
        
        print("\n🔍 HEALTH & INFRASTRUCTURE CHECKS")
        print("-" * 40)
        # Main health endpoints
        self.test_main_health_endpoint()
        self.test_auth_health_endpoint()
        self.test_uln_health_endpoint()
        self.test_profile_health_endpoint()
        self.test_social_health_endpoint()
        self.test_licensing_health_endpoint()
        self.test_performance_stats_endpoint()
        self.test_database_stats_endpoint()
        
        print("\n🔐 AUTHENTICATION SYSTEM TESTING")
        print("-" * 40)
        # Authentication tests
        self.test_auth_login()
        self.test_auth_me_endpoint()
        self.test_forgot_password_endpoint()
        
        print("\n🏷️ ULN SYSTEM (UNIFIED LABEL NETWORK) TESTING")
        print("-" * 40)
        # ULN comprehensive tests
        self.test_uln_label_hub()
        self.test_uln_edit_label_api()
        self.test_uln_advanced_search()
        self.test_uln_bulk_edit()
        self.test_uln_export()
        self.test_uln_audit_trail_endpoint()
        
        print("\n👤 CREATOR PROFILE SYSTEM TESTING")
        print("-" * 40)
        # Profile system tests
        self.test_profile_me_endpoint()
        self.test_asset_creation()
        self.test_qr_generation_endpoint()
        
        print("\n🏛️ DAO GOVERNANCE TESTING")
        print("-" * 40)
        # DAO tests
        self.test_dao_proposals()
        
        print("\n📱 SOCIAL MEDIA INTEGRATION TESTING")
        print("-" * 40)
        # Social media comprehensive tests
        self.test_social_providers_endpoint()
        self.test_oauth_status_endpoint()
        self.test_social_connections()
        self.test_social_posts_endpoint()
        self.test_social_metrics_dashboard()
        
        print("\n💰 LICENSING & COMPENSATION TESTING")
        print("-" * 40)
        # Licensing tests
        self.test_compensation_dashboard()
        self.test_comprehensive_licensing()
        self.test_distribution_platforms_endpoint()
        
        print("\n🎵 TIKTOK INTEGRATION TESTING")
        print("-" * 40)
        # TikTok specific tests
        self.test_tiktok_provider_configuration()
        self.test_tiktok_oauth_status()
        self.test_tiktok_oauth_connect_endpoint()
        self.test_tiktok_in_social_health()
        self.test_tiktok_environment_variables()
        
        print("\n🗄️ DATABASE CONNECTIVITY TESTING")
        print("-" * 40)
        # Database tests
        self.test_database_connectivity()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("=" * 80)
        
        passed_tests = len([t for t in self.test_results if t["status"] == "PASS"])
        total_tests = len(self.test_results)
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Show failed tests with details
        failed_tests = [t for t in self.test_results if t["status"] == "FAIL"]
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['details']}")
        
        # Show passed tests summary
        passed_test_names = [t["test"] for t in self.test_results if t["status"] == "PASS"]
        if passed_test_names:
            print(f"\n✅ PASSED TESTS ({len(passed_test_names)}):")
            for test_name in passed_test_names:
                print(f"  - {test_name}")
        
        return passed_tests == total_tests

def main():
    """Main test execution"""
    tester = BMEComprehensiveBackendTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! BME backend systems are working correctly.")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Please check the results above.")
        sys.exit(1)

if __name__ == "__main__":
    main()