#!/usr/bin/env python3
"""
🎯 COMPREHENSIVE GS1 ASSET REGISTRY BACKEND TESTING
Testing all GS1 Asset Registry endpoints for Big Mann Entertainment platform
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

# Backend URL from frontend environment
BACKEND_URL = "https://label-network-1.preview.emergentagent.com"

class GS1AssetRegistryTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.session = None
        self.test_results = []
        self.test_assets = []  # Store created assets for cleanup
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test(self, test_name: str, status: str, details: str = "", response_data: Any = None):
        """Log test results"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_emoji} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
        if response_data and isinstance(response_data, dict):
            if "error" in response_data:
                print(f"   Error: {response_data['error']}")
    
    async def test_endpoint(self, method: str, endpoint: str, data: Dict = None, expected_status: int = 200, test_name: str = None) -> Dict:
        """Generic endpoint testing method"""
        url = f"{self.backend_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                async with self.session.get(url) as response:
                    response_data = await response.json()
                    status_code = response.status
            elif method.upper() == "POST":
                headers = {"Content-Type": "application/json"}
                async with self.session.post(url, json=data, headers=headers) as response:
                    response_data = await response.json()
                    status_code = response.status
            elif method.upper() == "PUT":
                headers = {"Content-Type": "application/json"}
                async with self.session.put(url, json=data, headers=headers) as response:
                    response_data = await response.json()
                    status_code = response.status
            elif method.upper() == "DELETE":
                async with self.session.delete(url) as response:
                    response_data = await response.json()
                    status_code = response.status
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            if status_code == expected_status:
                self.log_test(test_name or f"{method} {endpoint}", "PASS", 
                            f"Status: {status_code}", response_data)
            else:
                self.log_test(test_name or f"{method} {endpoint}", "FAIL", 
                            f"Expected {expected_status}, got {status_code}", response_data)
            
            return {"status_code": status_code, "data": response_data}
            
        except Exception as e:
            self.log_test(test_name or f"{method} {endpoint}", "FAIL", 
                        f"Exception: {str(e)}")
            return {"status_code": 0, "data": {"error": str(e)}}

    async def test_gs1_health_check(self):
        """Test GS1 health check endpoint"""
        print("\n🏥 Testing GS1 Health Check...")
        result = await self.test_endpoint("GET", "/api/gs1/health", 
                                        test_name="GS1 Health Check")
        
        if result["status_code"] == 200:
            data = result["data"]
            if data.get("status") == "healthy":
                self.log_test("GS1 Service Health", "PASS", 
                            f"Database: {data.get('database')}, Total Assets: {data.get('total_assets')}")
            else:
                self.log_test("GS1 Service Health", "FAIL", 
                            f"Service status: {data.get('status')}")

    async def test_gs1_config(self):
        """Test GS1 configuration endpoint"""
        print("\n⚙️ Testing GS1 Configuration...")
        result = await self.test_endpoint("GET", "/api/gs1/config", 
                                        test_name="GS1 Configuration")
        
        if result["status_code"] == 200:
            data = result["data"]
            supported_identifiers = data.get("supported_identifiers", [])
            supported_assets = data.get("supported_asset_types", [])
            
            self.log_test("GS1 Supported Identifiers", "PASS" if len(supported_identifiers) >= 5 else "FAIL",
                        f"Identifiers: {supported_identifiers}")
            self.log_test("GS1 Supported Asset Types", "PASS" if len(supported_assets) >= 4 else "FAIL",
                        f"Asset Types: {supported_assets}")

    async def test_create_music_asset(self):
        """Test creating a music asset with ISRC generation"""
        print("\n🎵 Testing Music Asset Creation with ISRC...")
        
        asset_data = {
            "asset_type": "music",
            "metadata": {
                "title": "Test Music Track",
                "description": "A test music track for GS1 Asset Registry",
                "artist": "Big Mann Entertainment Artist",
                "album": "Test Album",
                "genre": "Hip-Hop",
                "duration_seconds": 180,
                "release_date": "2025-01-08T00:00:00Z"
            },
            "generate_identifiers": ["gtin", "isrc"],
            "digital_link_config": {
                "base_uri": "https://label-network-1.preview.emergentagent.com",
                "qr_code_format": "PNG",
                "qr_code_size": 200
            }
        }
        
        result = await self.test_endpoint("POST", "/api/gs1/assets", asset_data,
                                        test_name="Create Music Asset with ISRC")
        
        if result["status_code"] == 200:
            asset = result["data"]
            asset_id = asset.get("asset_id")
            if asset_id:
                self.test_assets.append(asset_id)
                
            # Check ISRC generation
            identifiers = asset.get("identifiers", {})
            if "isrc" in identifiers:
                isrc_value = identifiers["isrc"]["value"]
                self.log_test("ISRC Generation", "PASS", f"Generated ISRC: {isrc_value}")
            else:
                self.log_test("ISRC Generation", "FAIL", "No ISRC identifier found")
                
            # Check GTIN generation
            if "gtin" in identifiers:
                gtin_value = identifiers["gtin"]["value"]
                self.log_test("GTIN Generation", "PASS", f"Generated GTIN: {gtin_value}")
            else:
                self.log_test("GTIN Generation", "FAIL", "No GTIN identifier found")

    async def test_create_video_asset(self):
        """Test creating a video asset with ISAN generation"""
        print("\n🎬 Testing Video Asset Creation with ISAN...")
        
        asset_data = {
            "asset_type": "video",
            "metadata": {
                "title": "Test Music Video",
                "description": "A test music video for GS1 Asset Registry",
                "director": "Big Mann Entertainment Director",
                "producer": "Big Mann Entertainment Producer",
                "runtime_minutes": 4,
                "resolution": "1920x1080",
                "aspect_ratio": "16:9"
            },
            "generate_identifiers": ["gtin", "isan"]
        }
        
        result = await self.test_endpoint("POST", "/api/gs1/assets", asset_data,
                                        test_name="Create Video Asset with ISAN")
        
        if result["status_code"] == 200:
            asset = result["data"]
            asset_id = asset.get("asset_id")
            if asset_id:
                self.test_assets.append(asset_id)
                
            # Check ISAN generation
            identifiers = asset.get("identifiers", {})
            if "isan" in identifiers:
                isan_value = identifiers["isan"]["value"]
                self.log_test("ISAN Generation", "PASS", f"Generated ISAN: {isan_value}")
            else:
                self.log_test("ISAN Generation", "FAIL", "No ISAN identifier found")

    async def test_create_image_asset(self):
        """Test creating an image asset"""
        print("\n🖼️ Testing Image Asset Creation...")
        
        asset_data = {
            "asset_type": "image",
            "metadata": {
                "title": "Test Album Cover",
                "description": "A test album cover image for GS1 Asset Registry",
                "photographer": "Big Mann Entertainment Photographer",
                "width_pixels": 3000,
                "height_pixels": 3000,
                "color_profile": "sRGB",
                "dpi": 300
            },
            "generate_identifiers": ["gtin", "gdti"]
        }
        
        result = await self.test_endpoint("POST", "/api/gs1/assets", asset_data,
                                        test_name="Create Image Asset")
        
        if result["status_code"] == 200:
            asset = result["data"]
            asset_id = asset.get("asset_id")
            if asset_id:
                self.test_assets.append(asset_id)
                
            # Check GDTI generation
            identifiers = asset.get("identifiers", {})
            if "gdti" in identifiers:
                gdti_value = identifiers["gdti"]["value"]
                self.log_test("GDTI Generation", "PASS", f"Generated GDTI: {gdti_value}")
            else:
                self.log_test("GDTI Generation", "FAIL", "No GDTI identifier found")

    async def test_create_merchandise_asset(self):
        """Test creating a merchandise asset"""
        print("\n👕 Testing Merchandise Asset Creation...")
        
        asset_data = {
            "asset_type": "merchandise",
            "metadata": {
                "title": "Big Mann Entertainment T-Shirt",
                "description": "Official Big Mann Entertainment merchandise",
                "brand": "Big Mann Entertainment",
                "size": "L",
                "color": "Black",
                "material": "100% Cotton",
                "sku": "BME-TSHIRT-001",
                "price": 29.99,
                "currency": "USD"
            },
            "generate_identifiers": ["gtin", "gln"]
        }
        
        result = await self.test_endpoint("POST", "/api/gs1/assets", asset_data,
                                        test_name="Create Merchandise Asset")
        
        if result["status_code"] == 200:
            asset = result["data"]
            asset_id = asset.get("asset_id")
            if asset_id:
                self.test_assets.append(asset_id)
                
            # Check GLN generation
            identifiers = asset.get("identifiers", {})
            if "gln" in identifiers:
                gln_value = identifiers["gln"]["value"]
                self.log_test("GLN Generation", "PASS", f"Generated GLN: {gln_value}")
            else:
                self.log_test("GLN Generation", "FAIL", "No GLN identifier found")

    async def test_asset_retrieval(self):
        """Test retrieving assets"""
        print("\n📋 Testing Asset Retrieval...")
        
        if not self.test_assets:
            self.log_test("Asset Retrieval", "SKIP", "No assets created to retrieve")
            return
            
        # Test getting a specific asset
        asset_id = self.test_assets[0]
        result = await self.test_endpoint("GET", f"/api/gs1/assets/{asset_id}",
                                        test_name="Get Specific Asset")
        
        if result["status_code"] == 200:
            asset = result["data"]
            if asset.get("asset_id") == asset_id:
                self.log_test("Asset Data Integrity", "PASS", 
                            f"Retrieved asset matches created asset")
            else:
                self.log_test("Asset Data Integrity", "FAIL", 
                            "Retrieved asset ID doesn't match")

    async def test_asset_search(self):
        """Test asset search functionality"""
        print("\n🔍 Testing Asset Search...")
        
        # Test search all assets
        result = await self.test_endpoint("GET", "/api/gs1/assets",
                                        test_name="Search All Assets")
        
        if result["status_code"] == 200:
            data = result["data"]
            total_count = data.get("total_count", 0)
            assets = data.get("assets", [])
            
            self.log_test("Asset Search Results", "PASS", 
                        f"Found {total_count} assets, returned {len(assets)}")
            
            # Test search by asset type
            result = await self.test_endpoint("GET", "/api/gs1/assets?asset_type=music",
                                            test_name="Search Music Assets")
            
            if result["status_code"] == 200:
                music_data = result["data"]
                music_assets = music_data.get("assets", [])
                music_count = len([a for a in music_assets if a.get("asset_type") == "music"])
                
                self.log_test("Music Asset Filter", "PASS", 
                            f"Found {music_count} music assets")

    async def test_identifier_validation(self):
        """Test identifier validation"""
        print("\n✅ Testing Identifier Validation...")
        
        # Test valid GTIN validation
        gtin_data = {
            "identifier_value": "1234567890128",
            "identifier_type": "gtin"
        }
        
        result = await self.test_endpoint("POST", "/api/gs1/identifiers/validate", gtin_data,
                                        test_name="GTIN Validation")
        
        if result["status_code"] == 200:
            validation = result["data"]
            is_valid = validation.get("is_valid")
            self.log_test("GTIN Validation Result", "PASS" if is_valid is not None else "FAIL",
                        f"Valid: {is_valid}, Errors: {validation.get('errors', [])}")
        
        # Test valid ISRC validation
        isrc_data = {
            "identifier_value": "USBME2500001",
            "identifier_type": "isrc"
        }
        
        result = await self.test_endpoint("POST", "/api/gs1/identifiers/validate", isrc_data,
                                        test_name="ISRC Validation")
        
        if result["status_code"] == 200:
            validation = result["data"]
            is_valid = validation.get("is_valid")
            self.log_test("ISRC Validation Result", "PASS" if is_valid is not None else "FAIL",
                        f"Valid: {is_valid}, Errors: {validation.get('errors', [])}")

    async def test_digital_links(self):
        """Test Digital Link creation and QR code generation"""
        print("\n🔗 Testing Digital Links and QR Codes...")
        
        if not self.test_assets:
            self.log_test("Digital Link Creation", "SKIP", "No assets available")
            return
            
        # Get an asset with GTIN
        asset_id = self.test_assets[0]
        asset_result = await self.test_endpoint("GET", f"/api/gs1/assets/{asset_id}")
        
        if asset_result["status_code"] == 200:
            asset = asset_result["data"]
            identifiers = asset.get("identifiers", {})
            
            if "gtin" in identifiers:
                gtin_value = identifiers["gtin"]["value"]
                
                # Create Digital Link
                digital_link_data = {
                    "asset_id": asset_id,
                    "identifier": gtin_value,
                    "config": {
                        "base_uri": "https://label-network-1.preview.emergentagent.com",
                        "qr_code_format": "PNG",
                        "qr_code_size": 200
                    }
                }
                
                result = await self.test_endpoint("POST", "/api/gs1/digital-links", digital_link_data,
                                                test_name="Create Digital Link")
                
                if result["status_code"] == 200:
                    digital_link = result["data"].get("digital_link", {})
                    link_id = digital_link.get("link_id")
                    uri = digital_link.get("uri")
                    
                    self.log_test("Digital Link URI", "PASS", f"URI: {uri}")
                    
                    if link_id:
                        # Test QR code retrieval
                        qr_result = await self.test_endpoint("GET", f"/api/gs1/digital-links/{link_id}/qr-code",
                                                           test_name="Get QR Code")
                        
                        if qr_result["status_code"] == 200:
                            self.log_test("QR Code Generation", "PASS", "QR code retrieved successfully")

    async def test_analytics(self):
        """Test analytics endpoints"""
        print("\n📊 Testing Analytics...")
        
        # Test main analytics
        result = await self.test_endpoint("GET", "/api/gs1/analytics",
                                        test_name="GS1 Analytics")
        
        if result["status_code"] == 200:
            analytics = result["data"]
            total_assets = analytics.get("total_assets", 0)
            assets_by_type = analytics.get("assets_by_type", {})
            
            self.log_test("Analytics Data", "PASS", 
                        f"Total Assets: {total_assets}, By Type: {assets_by_type}")
        
        # Test assets by type analytics
        result = await self.test_endpoint("GET", "/api/gs1/analytics/assets/by-type",
                                        test_name="Assets by Type Analytics")
        
        if result["status_code"] == 200:
            data = result["data"].get("data", [])
            self.log_test("Asset Type Breakdown", "PASS", 
                        f"Found {len(data)} asset type categories")
        
        # Test identifiers by type analytics
        result = await self.test_endpoint("GET", "/api/gs1/analytics/identifiers/by-type",
                                        test_name="Identifiers by Type Analytics")
        
        if result["status_code"] == 200:
            data = result["data"].get("data", [])
            self.log_test("Identifier Type Breakdown", "PASS", 
                        f"Found {len(data)} identifier type categories")

    async def test_standards_compliance(self):
        """Test GS1 standards compliance information"""
        print("\n📋 Testing Standards Compliance...")
        
        result = await self.test_endpoint("GET", "/api/gs1/standards/compliance",
                                        test_name="Standards Compliance Info")
        
        if result["status_code"] == 200:
            compliance = result["data"]
            gs1_standards = compliance.get("gs1_standards", {})
            industry_standards = compliance.get("industry_standards", {})
            
            # Check GS1 standards
            gtin_standard = gs1_standards.get("gtin", {})
            if gtin_standard.get("compliance_level") == "Full":
                self.log_test("GTIN Compliance", "PASS", "Full GS1 GTIN compliance")
            else:
                self.log_test("GTIN Compliance", "FAIL", "GTIN compliance not full")
            
            # Check industry standards
            isrc_standard = industry_standards.get("isrc", {})
            if isrc_standard.get("compliance_level") == "Full":
                self.log_test("ISRC Compliance", "PASS", "Full ISO 3901 ISRC compliance")
            else:
                self.log_test("ISRC Compliance", "FAIL", "ISRC compliance not full")

    async def test_export_functionality(self):
        """Test asset export functionality"""
        print("\n📤 Testing Export Functionality...")
        
        # Test JSON export
        result = await self.test_endpoint("GET", "/api/gs1/export/assets?format=json",
                                        test_name="JSON Export")
        
        if result["status_code"] == 200:
            export_data = result["data"]
            assets = export_data.get("assets", [])
            count = export_data.get("count", 0)
            
            self.log_test("JSON Export", "PASS", f"Exported {count} assets")
        
        # Test CSV export (this might return different content type)
        try:
            url = f"{self.backend_url}/api/gs1/export/assets?format=csv"
            async with self.session.get(url) as response:
                if response.status == 200:
                    content_type = response.headers.get('content-type', '')
                    if 'csv' in content_type or 'text' in content_type:
                        self.log_test("CSV Export", "PASS", f"CSV export successful")
                    else:
                        self.log_test("CSV Export", "FAIL", f"Unexpected content type: {content_type}")
                else:
                    self.log_test("CSV Export", "FAIL", f"Status: {response.status}")
        except Exception as e:
            self.log_test("CSV Export", "FAIL", f"Exception: {str(e)}")

    async def test_batch_operations(self):
        """Test batch operations"""
        print("\n📦 Testing Batch Operations...")
        
        # Test small batch creation
        batch_data = {
            "operation": "create",
            "assets": [
                {
                    "asset_type": "music",
                    "metadata": {
                        "title": "Batch Test Song 1",
                        "artist": "Batch Test Artist",
                        "genre": "Test"
                    },
                    "generate_identifiers": ["gtin"]
                },
                {
                    "asset_type": "music",
                    "metadata": {
                        "title": "Batch Test Song 2",
                        "artist": "Batch Test Artist",
                        "genre": "Test"
                    },
                    "generate_identifiers": ["gtin"]
                }
            ]
        }
        
        result = await self.test_endpoint("POST", "/api/gs1/batch", batch_data,
                                        test_name="Batch Asset Creation")
        
        if result["status_code"] == 200:
            batch_result = result["data"]
            successful = batch_result.get("successful", 0)
            failed = batch_result.get("failed", 0)
            total = batch_result.get("total_processed", 0)
            
            self.log_test("Batch Operation Results", "PASS", 
                        f"Total: {total}, Successful: {successful}, Failed: {failed}")
            
            # Add successful assets to cleanup list
            results = batch_result.get("results", [])
            for result_item in results:
                if result_item.get("status") == "success":
                    asset_id = result_item.get("asset_id")
                    if asset_id:
                        self.test_assets.append(asset_id)

    async def cleanup_test_assets(self):
        """Clean up test assets"""
        print("\n🧹 Cleaning up test assets...")
        
        cleanup_count = 0
        for asset_id in self.test_assets:
            try:
                result = await self.test_endpoint("DELETE", f"/api/gs1/assets/{asset_id}",
                                                expected_status=200,
                                                test_name=f"Cleanup Asset {asset_id}")
                if result["status_code"] == 200:
                    cleanup_count += 1
            except Exception as e:
                print(f"   Warning: Could not cleanup asset {asset_id}: {e}")
        
        self.log_test("Asset Cleanup", "PASS", f"Cleaned up {cleanup_count}/{len(self.test_assets)} assets")

    async def run_comprehensive_tests(self):
        """Run all GS1 Asset Registry tests"""
        print("🎯 COMPREHENSIVE GS1 ASSET REGISTRY BACKEND TESTING")
        print("=" * 60)
        print(f"Backend URL: {self.backend_url}")
        print(f"Test Start Time: {datetime.now().isoformat()}")
        print("=" * 60)
        
        try:
            # Core system tests
            await self.test_gs1_health_check()
            await self.test_gs1_config()
            
            # Asset creation tests for all 4 types
            await self.test_create_music_asset()
            await self.test_create_video_asset()
            await self.test_create_image_asset()
            await self.test_create_merchandise_asset()
            
            # Asset management tests
            await self.test_asset_retrieval()
            await self.test_asset_search()
            
            # Identifier tests
            await self.test_identifier_validation()
            
            # Digital Link tests
            await self.test_digital_links()
            
            # Analytics tests
            await self.test_analytics()
            
            # Standards compliance tests
            await self.test_standards_compliance()
            
            # Export functionality tests
            await self.test_export_functionality()
            
            # Batch operations tests
            await self.test_batch_operations()
            
            # Cleanup
            await self.cleanup_test_assets()
            
        except Exception as e:
            print(f"❌ Critical error during testing: {e}")
            self.log_test("Critical Error", "FAIL", str(e))
        
        # Print summary
        self.print_test_summary()

    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🎯 GS1 ASSET REGISTRY TESTING SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t["status"] == "PASS"])
        failed_tests = len([t for t in self.test_results if t["status"] == "FAIL"])
        skipped_tests = len([t for t in self.test_results if t["status"] == "SKIP"])
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   ⚠️ Skipped: {skipped_tests}")
        print(f"   📈 Success Rate: {success_rate:.1f}%")
        
        print(f"\n🎯 GS1 ASSET REGISTRY FUNCTIONALITY ASSESSMENT:")
        
        # Categorize tests
        categories = {
            "Health & Configuration": ["GS1 Health Check", "GS1 Configuration", "GS1 Service Health"],
            "Asset Creation": ["Create Music Asset", "Create Video Asset", "Create Image Asset", "Create Merchandise Asset"],
            "Identifier Generation": ["ISRC Generation", "ISAN Generation", "GTIN Generation", "GLN Generation", "GDTI Generation"],
            "Asset Management": ["Get Specific Asset", "Search All Assets", "Asset Data Integrity"],
            "Validation": ["GTIN Validation", "ISRC Validation", "GTIN Validation Result", "ISRC Validation Result"],
            "Digital Links": ["Create Digital Link", "Digital Link URI", "Get QR Code", "QR Code Generation"],
            "Analytics": ["GS1 Analytics", "Assets by Type Analytics", "Identifiers by Type Analytics"],
            "Standards Compliance": ["Standards Compliance Info", "GTIN Compliance", "ISRC Compliance"],
            "Export & Batch": ["JSON Export", "CSV Export", "Batch Asset Creation", "Batch Operation Results"]
        }
        
        for category, test_names in categories.items():
            category_tests = [t for t in self.test_results if t["test"] in test_names]
            if category_tests:
                category_passed = len([t for t in category_tests if t["status"] == "PASS"])
                category_total = len(category_tests)
                category_rate = (category_passed / category_total * 100) if category_total > 0 else 0
                
                status_emoji = "✅" if category_rate >= 80 else "⚠️" if category_rate >= 50 else "❌"
                print(f"   {status_emoji} {category}: {category_passed}/{category_total} ({category_rate:.1f}%)")
        
        print(f"\n🔍 CRITICAL ISSUES:")
        critical_failures = [t for t in self.test_results if t["status"] == "FAIL" and 
                           any(keyword in t["test"].lower() for keyword in ["health", "creation", "generation", "validation"])]
        
        if critical_failures:
            for failure in critical_failures:
                print(f"   ❌ {failure['test']}: {failure['details']}")
        else:
            print("   ✅ No critical issues found!")
        
        print(f"\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status_emoji = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAIL" else "⚠️"
            print(f"   {status_emoji} {result['test']}: {result['status']}")
            if result["details"]:
                print(f"      └─ {result['details']}")
        
        print(f"\n🎉 GS1 ASSET REGISTRY TESTING COMPLETED")
        print(f"   Test End Time: {datetime.now().isoformat()}")
        
        if success_rate >= 90:
            print("   🏆 EXCELLENT: GS1 Asset Registry system is production-ready!")
        elif success_rate >= 75:
            print("   ✅ GOOD: GS1 Asset Registry system is mostly functional with minor issues")
        elif success_rate >= 50:
            print("   ⚠️ NEEDS WORK: GS1 Asset Registry system has significant issues")
        else:
            print("   ❌ CRITICAL: GS1 Asset Registry system requires major fixes")
        
        print("=" * 60)

async def main():
    """Main test execution"""
    async with GS1AssetRegistryTester() as tester:
        await tester.run_comprehensive_tests()

if __name__ == "__main__":
    asyncio.run(main())