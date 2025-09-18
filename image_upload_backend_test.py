#!/usr/bin/env python3
"""
Advanced Image Upload Functionality Backend Testing
Big Mann Entertainment Platform - Comprehensive Testing Suite

Testing Areas:
1. Image Upload Endpoints Testing
2. Web3 NFT Integration Testing  
3. DAO Governance Testing
4. Additional Endpoints Testing
5. Form Data and File Upload Testing
"""

import asyncio
import aiohttp
import json
import os
import io
from PIL import Image
import base64
import logging
from datetime import datetime
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedImageUploadTester:
    def __init__(self):
        # Get backend URL from environment
        try:
            with open('/app/frontend/.env', 'r') as f:
                for line in f:
                    if line.startswith('REACT_APP_BACKEND_URL'):
                        self.base_url = line.split('=')[1].strip()
                        break
                else:
                    self.base_url = "https://content-workflow-1.preview.emergentagent.com"
        except Exception:
            self.base_url = "https://content-workflow-1.preview.emergentagent.com"
        
        self.api_url = f"{self.base_url}/api"
        self.session = None
        self.auth_token = None
        self.test_user_id = None
        
        # Test results tracking
        self.test_results = {
            "image_upload_endpoints": [],
            "web3_nft_integration": [],
            "dao_governance": [],
            "additional_endpoints": [],
            "form_data_validation": [],
            "summary": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "success_rate": 0.0
            }
        }

    async def setup_session(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()

    def create_test_image(self, width=800, height=600, format_type='JPEG'):
        """Create a test image for upload testing"""
        # Create a simple test image
        img = Image.new('RGB', (width, height), color='red')
        
        # Add some text to make it more realistic
        try:
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(img)
            draw.text((10, 10), "Big Mann Entertainment Test Image", fill='white')
        except Exception:
            pass  # Skip text if font not available
        
        # Convert to bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format=format_type)
        img_bytes.seek(0)
        
        return img_bytes.getvalue()

    async def authenticate_user(self):
        """Create test user and authenticate"""
        try:
            # Register test user
            register_data = {
                "email": f"test_image_user_{datetime.now().strftime('%Y%m%d_%H%M%S')}@bigmannentertainment.com",
                "password": "TestPassword123!",
                "full_name": "Image Upload Test User",
                "date_of_birth": "1990-01-01T00:00:00Z",
                "address_line1": "123 Test Street",
                "city": "Test City",
                "state_province": "Test State",
                "postal_code": "12345",
                "country": "United States"
            }
            
            async with self.session.post(f"{self.api_url}/auth/register", json=register_data) as response:
                if response.status in [200, 201]:
                    register_result = await response.json()
                    self.auth_token = register_result.get('access_token')
                    self.test_user_id = register_result.get('user', {}).get('id')
                    logger.info("✅ Test user registered and authenticated successfully")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"❌ User registration failed: {response.status} - {error_text}")
                    print(f"Registration error details: {error_text}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Authentication error: {str(e)}")
            return False

    def get_auth_headers(self):
        """Get authentication headers"""
        if self.auth_token:
            return {"Authorization": f"Bearer {self.auth_token}"}
        return {}

    async def test_image_upload_endpoint(self):
        """Test POST /api/images/upload endpoint"""
        logger.info("🎯 Testing Image Upload Endpoint...")
        
        test_cases = [
            {
                "name": "Basic Image Upload - Editorial Only",
                "data": {
                    "model_name": "Sarah Johnson",
                    "agency_name": "Elite Model Management",
                    "photographer_name": "John Smith Photography",
                    "shoot_date": "2024-01-15T10:00:00Z",
                    "usage_rights": "editorial_only",
                    "territory_rights": "worldwide",
                    "duration_rights": "perpetual",
                    "exclusive": "false",
                    "headline": "Professional Fashion Portrait",
                    "caption": "High-fashion editorial portrait for Big Mann Entertainment",
                    "keywords": "fashion,portrait,editorial,professional",
                    "copyright_notice": "© 2024 John Smith Photography",
                    "license_terms": "Editorial use only, no commercial applications",
                    "content_rating": "general",
                    "base_pricing": "0",
                    "max_resolution": "4000"
                }
            },
            {
                "name": "Commercial Image Upload with Model Release",
                "data": {
                    "model_name": "Maria Rodriguez",
                    "agency_name": "IMG Models",
                    "photographer_name": "David Wilson Studios",
                    "shoot_date": "2024-01-20T14:30:00Z",
                    "usage_rights": "commercial",
                    "territory_rights": "north_america",
                    "duration_rights": "5_years",
                    "exclusive": "true",
                    "headline": "Commercial Beauty Campaign",
                    "caption": "Beauty campaign for luxury cosmetics brand",
                    "keywords": "beauty,commercial,cosmetics,luxury",
                    "copyright_notice": "© 2024 David Wilson Studios",
                    "license_terms": "Commercial use permitted for cosmetics advertising",
                    "content_rating": "general",
                    "target_agencies": '["IMG Models", "Elite Model Management"]',
                    "base_pricing": "2500",
                    "max_resolution": "6000"
                }
            },
            {
                "name": "Unrestricted Usage Rights",
                "data": {
                    "model_name": "Alex Thompson",
                    "photographer_name": "Creative Studios LLC",
                    "shoot_date": "2024-01-25T09:00:00Z",
                    "usage_rights": "unrestricted",
                    "territory_rights": "worldwide",
                    "duration_rights": "perpetual",
                    "exclusive": "false",
                    "headline": "Lifestyle Photography Session",
                    "caption": "Versatile lifestyle images for multiple applications",
                    "keywords": "lifestyle,versatile,commercial,editorial",
                    "copyright_notice": "© 2024 Creative Studios LLC",
                    "content_rating": "general",
                    "base_pricing": "1500",
                    "max_resolution": "unlimited"
                }
            }
        ]
        
        for test_case in test_cases:
            try:
                # Create test image
                image_data = self.create_test_image()
                
                # Prepare form data
                form_data = aiohttp.FormData()
                form_data.add_field('file', image_data, filename='test_image.jpg', content_type='image/jpeg')
                
                # Add all form fields
                for key, value in test_case["data"].items():
                    form_data.add_field(key, str(value))
                
                # Make request
                async with self.session.post(
                    f"{self.api_url}/images/upload",
                    data=form_data,
                    headers=self.get_auth_headers()
                ) as response:
                    
                    response_text = await response.text()
                    
                    if response.status == 200:
                        try:
                            result = await response.json()
                        except Exception:
                            result = {"raw_response": response_text}
                        
                        # Validate response structure
                        expected_fields = ["success", "metadata_id", "file_info", "metadata_summary"]
                        has_required_fields = all(field in result for field in expected_fields)
                        
                        self.test_results["image_upload_endpoints"].append({
                            "test": test_case["name"],
                            "status": "✅ PASS" if has_required_fields else "⚠️ PARTIAL",
                            "response_status": response.status,
                            "has_metadata_id": "metadata_id" in result,
                            "has_file_info": "file_info" in result,
                            "has_metadata_summary": "metadata_summary" in result,
                            "usage_rights": test_case["data"]["usage_rights"],
                            "details": f"Metadata ID: {result.get('metadata_id', 'N/A')}"
                        })
                        
                        logger.info(f"✅ {test_case['name']}: Upload successful")
                        
                    else:
                        self.test_results["image_upload_endpoints"].append({
                            "test": test_case["name"],
                            "status": "❌ FAIL",
                            "response_status": response.status,
                            "error": response_text[:200],
                            "usage_rights": test_case["data"]["usage_rights"]
                        })
                        
                        logger.error(f"❌ {test_case['name']}: Failed with status {response.status}")
                        
            except Exception as e:
                self.test_results["image_upload_endpoints"].append({
                    "test": test_case["name"],
                    "status": "❌ ERROR",
                    "error": str(e),
                    "usage_rights": test_case["data"]["usage_rights"]
                })
                logger.error(f"❌ {test_case['name']}: Exception - {str(e)}")

    async def test_batch_upload_endpoint(self):
        """Test POST /api/images/batch-upload endpoint"""
        logger.info("🎯 Testing Batch Upload Endpoint...")
        
        try:
            # Create multiple test images
            images = []
            for i in range(3):
                image_data = self.create_test_image(width=600+i*100, height=400+i*50)
                images.append((f'test_batch_{i+1}.jpg', image_data))
            
            # Prepare form data
            form_data = aiohttp.FormData()
            
            # Add files
            for filename, image_data in images:
                form_data.add_field('files', image_data, filename=filename, content_type='image/jpeg')
            
            # Add batch metadata
            batch_data = {
                "model_name": "Batch Model Test",
                "agency_name": "Test Agency",
                "photographer_name": "Batch Photographer",
                "shoot_date": "2024-01-30T12:00:00Z",
                "usage_rights": "editorial_only",
                "territory_rights": "worldwide",
                "duration_rights": "perpetual",
                "exclusive": "false",
                "headline": "Batch Upload Test",
                "caption": "Testing batch upload functionality",
                "keywords": "batch,test,upload",
                "copyright_notice": "© 2024 Test Photographer",
                "content_rating": "general",
                "base_pricing": "0",
                "max_resolution": "4000"
            }
            
            for key, value in batch_data.items():
                form_data.add_field(key, str(value))
            
            # Make request
            async with self.session.post(
                f"{self.api_url}/images/batch-upload",
                data=form_data,
                headers=self.get_auth_headers()
            ) as response:
                
                response_text = await response.text()
                
                if response.status == 200:
                    try:
                        result = await response.json()
                    except Exception:
                        result = {"raw_response": response_text}
                    
                    # Validate batch response
                    expected_fields = ["success", "batch_processing", "total_files", "successful_uploads", "results"]
                    has_required_fields = all(field in result for field in expected_fields)
                    
                    self.test_results["image_upload_endpoints"].append({
                        "test": "Batch Upload - Multiple Images",
                        "status": "✅ PASS" if has_required_fields else "⚠️ PARTIAL",
                        "response_status": response.status,
                        "total_files": result.get("total_files", 0),
                        "successful_uploads": result.get("successful_uploads", 0),
                        "failed_uploads": result.get("failed_uploads", 0),
                        "batch_processing": result.get("batch_processing", False),
                        "details": f"Processed {result.get('total_files', 0)} files"
                    })
                    
                    logger.info(f"✅ Batch Upload: {result.get('successful_uploads', 0)}/{result.get('total_files', 0)} files processed")
                    
                else:
                    self.test_results["image_upload_endpoints"].append({
                        "test": "Batch Upload - Multiple Images",
                        "status": "❌ FAIL",
                        "response_status": response.status,
                        "error": response_text[:200]
                    })
                    
                    logger.error(f"❌ Batch Upload: Failed with status {response.status}")
                    
        except Exception as e:
            self.test_results["image_upload_endpoints"].append({
                "test": "Batch Upload - Multiple Images",
                "status": "❌ ERROR",
                "error": str(e)
            })
            logger.error(f"❌ Batch Upload: Exception - {str(e)}")

    async def test_web3_nft_integration(self):
        """Test Web3 NFT Integration with enable_nft=true"""
        logger.info("🎯 Testing Web3 NFT Integration...")
        
        nft_test_cases = [
            {
                "name": "NFT Minting - Polygon ERC721",
                "data": {
                    "model_name": "NFT Model Test",
                    "photographer_name": "NFT Photographer",
                    "shoot_date": "2024-02-01T10:00:00Z",
                    "usage_rights": "commercial",
                    "headline": "NFT License Test Image",
                    "caption": "Testing NFT minting functionality",
                    "keywords": "nft,blockchain,licensing",
                    "copyright_notice": "© 2024 NFT Test",
                    "content_rating": "general",
                    "enable_nft": "true",
                    "blockchain": "polygon",
                    "token_standard": "ERC721",
                    "royalty_recipients": json.dumps([
                        {
                            "address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d4d4",
                            "percentage": 85,
                            "role": "creator"
                        },
                        {
                            "address": "0x8ba1f109551bD432803012645Hac136c22C85B",
                            "percentage": 15,
                            "role": "platform"
                        }
                    ]),
                    "base_pricing": "0.1"
                }
            },
            {
                "name": "NFT Minting - Ethereum ERC1155",
                "data": {
                    "model_name": "Ethereum NFT Model",
                    "photographer_name": "ETH Photographer",
                    "shoot_date": "2024-02-02T14:00:00Z",
                    "usage_rights": "unrestricted",
                    "headline": "Ethereum NFT License",
                    "caption": "Testing Ethereum ERC1155 minting",
                    "keywords": "ethereum,erc1155,nft",
                    "copyright_notice": "© 2024 ETH Test",
                    "content_rating": "general",
                    "enable_nft": "true",
                    "blockchain": "ethereum",
                    "token_standard": "ERC1155",
                    "royalty_recipients": json.dumps([
                        {
                            "address": "0x1234567890123456789012345678901234567890",
                            "percentage": 100,
                            "role": "creator"
                        }
                    ]),
                    "base_pricing": "0.05"
                }
            },
            {
                "name": "NFT Minting - Base Network",
                "data": {
                    "model_name": "Base Network Model",
                    "photographer_name": "Base Photographer",
                    "shoot_date": "2024-02-03T16:00:00Z",
                    "usage_rights": "commercial",
                    "headline": "Base Network NFT",
                    "caption": "Testing Base network integration",
                    "keywords": "base,layer2,nft",
                    "copyright_notice": "© 2024 Base Test",
                    "content_rating": "general",
                    "enable_nft": "true",
                    "blockchain": "base",
                    "token_standard": "ERC721",
                    "base_pricing": "0.02"
                }
            }
        ]
        
        for test_case in nft_test_cases:
            try:
                # Create test image
                image_data = self.create_test_image()
                
                # Prepare form data
                form_data = aiohttp.FormData()
                form_data.add_field('file', image_data, filename='nft_test.jpg', content_type='image/jpeg')
                
                # Add all form fields
                for key, value in test_case["data"].items():
                    form_data.add_field(key, str(value))
                
                # Make request
                async with self.session.post(
                    f"{self.api_url}/images/upload",
                    data=form_data,
                    headers=self.get_auth_headers()
                ) as response:
                    
                    response_text = await response.text()
                    
                    if response.status == 200:
                        try:
                            result = await response.json()
                        except Exception:
                            result = {"raw_response": response_text}
                        
                        # Check for NFT minting response
                        has_nft_minting = "nft_minting" in result
                        nft_success = False
                        
                        if has_nft_minting:
                            nft_result = result["nft_minting"]
                            nft_success = nft_result.get("success", False)
                        
                        self.test_results["web3_nft_integration"].append({
                            "test": test_case["name"],
                            "status": "✅ PASS" if has_nft_minting else "⚠️ NO_NFT_RESPONSE",
                            "response_status": response.status,
                            "blockchain": test_case["data"]["blockchain"],
                            "token_standard": test_case["data"]["token_standard"],
                            "nft_minting_present": has_nft_minting,
                            "nft_success": nft_success,
                            "transaction_hash": result.get("nft_minting", {}).get("transaction_hash", "N/A"),
                            "token_id": result.get("nft_minting", {}).get("token_id", "N/A"),
                            "simulated": result.get("nft_minting", {}).get("simulated", False)
                        })
                        
                        logger.info(f"✅ {test_case['name']}: NFT integration {'working' if has_nft_minting else 'not detected'}")
                        
                    else:
                        self.test_results["web3_nft_integration"].append({
                            "test": test_case["name"],
                            "status": "❌ FAIL",
                            "response_status": response.status,
                            "blockchain": test_case["data"]["blockchain"],
                            "token_standard": test_case["data"]["token_standard"],
                            "error": response_text[:200]
                        })
                        
                        logger.error(f"❌ {test_case['name']}: Failed with status {response.status}")
                        
            except Exception as e:
                self.test_results["web3_nft_integration"].append({
                    "test": test_case["name"],
                    "status": "❌ ERROR",
                    "blockchain": test_case["data"]["blockchain"],
                    "token_standard": test_case["data"]["token_standard"],
                    "error": str(e)
                })
                logger.error(f"❌ {test_case['name']}: Exception - {str(e)}")

    async def test_dao_governance_integration(self):
        """Test DAO Governance with enable_dao=true"""
        logger.info("🎯 Testing DAO Governance Integration...")
        
        dao_test_cases = [
            {
                "name": "DAO Proposal - Licensing Terms",
                "data": {
                    "model_name": "DAO Model Test",
                    "photographer_name": "DAO Photographer",
                    "shoot_date": "2024-02-05T10:00:00Z",
                    "usage_rights": "commercial",
                    "headline": "DAO Governance Test",
                    "caption": "Testing DAO proposal creation",
                    "keywords": "dao,governance,licensing",
                    "copyright_notice": "© 2024 DAO Test",
                    "content_rating": "general",
                    "enable_dao": "true",
                    "proposal_type": "licensing_terms",
                    "voting_period": "7",
                    "blockchain": "polygon",
                    "base_pricing": "1.0"
                }
            },
            {
                "name": "DAO Proposal - Agency Onboarding",
                "data": {
                    "model_name": "Agency DAO Model",
                    "agency_name": "New Agency Test",
                    "photographer_name": "Agency Photographer",
                    "shoot_date": "2024-02-06T12:00:00Z",
                    "usage_rights": "editorial_only",
                    "headline": "Agency Onboarding Proposal",
                    "caption": "Testing agency onboarding DAO proposal",
                    "keywords": "dao,agency,onboarding",
                    "copyright_notice": "© 2024 Agency Test",
                    "content_rating": "general",
                    "enable_dao": "true",
                    "proposal_type": "agency_onboarding",
                    "voting_period": "14",
                    "blockchain": "ethereum"
                }
            }
        ]
        
        for test_case in dao_test_cases:
            try:
                # Create test image
                image_data = self.create_test_image()
                
                # Prepare form data
                form_data = aiohttp.FormData()
                form_data.add_field('file', image_data, filename='dao_test.jpg', content_type='image/jpeg')
                
                # Add all form fields
                for key, value in test_case["data"].items():
                    form_data.add_field(key, str(value))
                
                # Make request
                async with self.session.post(
                    f"{self.api_url}/images/upload",
                    data=form_data,
                    headers=self.get_auth_headers()
                ) as response:
                    
                    response_text = await response.text()
                    
                    if response.status == 200:
                        try:
                            result = await response.json()
                        except Exception:
                            result = {"raw_response": response_text}
                        
                        # Check for DAO proposal response
                        has_dao_proposal = "dao_proposal" in result
                        dao_success = False
                        
                        if has_dao_proposal:
                            dao_result = result["dao_proposal"]
                            dao_success = dao_result.get("success", False)
                        
                        self.test_results["dao_governance"].append({
                            "test": test_case["name"],
                            "status": "✅ PASS" if has_dao_proposal else "⚠️ NO_DAO_RESPONSE",
                            "response_status": response.status,
                            "proposal_type": test_case["data"]["proposal_type"],
                            "voting_period": test_case["data"]["voting_period"],
                            "blockchain": test_case["data"]["blockchain"],
                            "dao_proposal_present": has_dao_proposal,
                            "dao_success": dao_success,
                            "proposal_id": result.get("dao_proposal", {}).get("proposal_id", "N/A"),
                            "transaction_hash": result.get("dao_proposal", {}).get("transaction_hash", "N/A"),
                            "simulated": result.get("dao_proposal", {}).get("simulated", False)
                        })
                        
                        logger.info(f"✅ {test_case['name']}: DAO integration {'working' if has_dao_proposal else 'not detected'}")
                        
                    else:
                        self.test_results["dao_governance"].append({
                            "test": test_case["name"],
                            "status": "❌ FAIL",
                            "response_status": response.status,
                            "proposal_type": test_case["data"]["proposal_type"],
                            "blockchain": test_case["data"]["blockchain"],
                            "error": response_text[:200]
                        })
                        
                        logger.error(f"❌ {test_case['name']}: Failed with status {response.status}")
                        
            except Exception as e:
                self.test_results["dao_governance"].append({
                    "test": test_case["name"],
                    "status": "❌ ERROR",
                    "proposal_type": test_case["data"]["proposal_type"],
                    "blockchain": test_case["data"]["blockchain"],
                    "error": str(e)
                })
                logger.error(f"❌ {test_case['name']}: Exception - {str(e)}")

    async def test_additional_endpoints(self):
        """Test additional image-related endpoints"""
        logger.info("🎯 Testing Additional Image Endpoints...")
        
        # Test GET /api/images/nfts
        try:
            async with self.session.get(
                f"{self.api_url}/images/nfts",
                headers=self.get_auth_headers()
            ) as response:
                
                response_text = await response.text()
                
                if response.status == 200:
                    try:
                        result = await response.json()
                    except Exception:
                        result = {"raw_response": response_text}
                    
                    expected_fields = ["success", "nfts", "total"]
                    has_required_fields = all(field in result for field in expected_fields)
                    
                    self.test_results["additional_endpoints"].append({
                        "test": "GET /api/images/nfts - User NFT Retrieval",
                        "status": "✅ PASS" if has_required_fields else "⚠️ PARTIAL",
                        "response_status": response.status,
                        "has_success_field": "success" in result,
                        "has_nfts_array": "nfts" in result,
                        "has_total_count": "total" in result,
                        "nft_count": result.get("total", 0)
                    })
                    
                    logger.info(f"✅ GET /api/images/nfts: Retrieved {result.get('total', 0)} NFTs")
                    
                else:
                    self.test_results["additional_endpoints"].append({
                        "test": "GET /api/images/nfts - User NFT Retrieval",
                        "status": "❌ FAIL",
                        "response_status": response.status,
                        "error": response_text[:200]
                    })
                    
                    logger.error(f"❌ GET /api/images/nfts: Failed with status {response.status}")
                    
        except Exception as e:
            self.test_results["additional_endpoints"].append({
                "test": "GET /api/images/nfts - User NFT Retrieval",
                "status": "❌ ERROR",
                "error": str(e)
            })
            logger.error(f"❌ GET /api/images/nfts: Exception - {str(e)}")
        
        # Test GET /api/images/dao/proposals
        try:
            async with self.session.get(
                f"{self.api_url}/images/dao/proposals",
                headers=self.get_auth_headers()
            ) as response:
                
                response_text = await response.text()
                
                if response.status == 200:
                    try:
                        result = await response.json()
                    except Exception:
                        result = {"raw_response": response_text}
                    
                    expected_fields = ["success", "proposals", "total"]
                    has_required_fields = all(field in result for field in expected_fields)
                    
                    self.test_results["additional_endpoints"].append({
                        "test": "GET /api/images/dao/proposals - DAO Proposal Retrieval",
                        "status": "✅ PASS" if has_required_fields else "⚠️ PARTIAL",
                        "response_status": response.status,
                        "has_success_field": "success" in result,
                        "has_proposals_array": "proposals" in result,
                        "has_total_count": "total" in result,
                        "proposal_count": result.get("total", 0)
                    })
                    
                    logger.info(f"✅ GET /api/images/dao/proposals: Retrieved {result.get('total', 0)} proposals")
                    
                else:
                    self.test_results["additional_endpoints"].append({
                        "test": "GET /api/images/dao/proposals - DAO Proposal Retrieval",
                        "status": "❌ FAIL",
                        "response_status": response.status,
                        "error": response_text[:200]
                    })
                    
                    logger.error(f"❌ GET /api/images/dao/proposals: Failed with status {response.status}")
                    
        except Exception as e:
            self.test_results["additional_endpoints"].append({
                "test": "GET /api/images/dao/proposals - DAO Proposal Retrieval",
                "status": "❌ ERROR",
                "error": str(e)
            })
            logger.error(f"❌ GET /api/images/dao/proposals: Exception - {str(e)}")
        
        # Test GET /api/images/agencies/{agency_id}/portfolio
        try:
            test_agency_id = "test_agency_123"
            
            async with self.session.get(
                f"{self.api_url}/images/agencies/{test_agency_id}/portfolio",
                headers=self.get_auth_headers()
            ) as response:
                
                response_text = await response.text()
                
                if response.status == 200:
                    try:
                        result = await response.json()
                    except Exception:
                        result = {"raw_response": response_text}
                    
                    expected_fields = ["success", "agency_id", "portfolio", "total"]
                    has_required_fields = all(field in result for field in expected_fields)
                    
                    self.test_results["additional_endpoints"].append({
                        "test": "GET /api/images/agencies/{agency_id}/portfolio - Agency Portfolio Access",
                        "status": "✅ PASS" if has_required_fields else "⚠️ PARTIAL",
                        "response_status": response.status,
                        "has_success_field": "success" in result,
                        "has_agency_id": "agency_id" in result,
                        "has_portfolio_array": "portfolio" in result,
                        "has_total_count": "total" in result,
                        "portfolio_count": result.get("total", 0)
                    })
                    
                    logger.info(f"✅ GET /api/images/agencies/portfolio: Retrieved {result.get('total', 0)} portfolio items")
                    
                else:
                    self.test_results["additional_endpoints"].append({
                        "test": "GET /api/images/agencies/{agency_id}/portfolio - Agency Portfolio Access",
                        "status": "❌ FAIL",
                        "response_status": response.status,
                        "error": response_text[:200]
                    })
                    
                    logger.error(f"❌ GET /api/images/agencies/portfolio: Failed with status {response.status}")
                    
        except Exception as e:
            self.test_results["additional_endpoints"].append({
                "test": "GET /api/images/agencies/{agency_id}/portfolio - Agency Portfolio Access",
                "status": "❌ ERROR",
                "error": str(e)
            })
            logger.error(f"❌ GET /api/images/agencies/portfolio: Exception - {str(e)}")

    def calculate_summary(self):
        """Calculate test summary statistics"""
        total_tests = 0
        passed_tests = 0
        
        for category in ["image_upload_endpoints", "web3_nft_integration", "dao_governance", "additional_endpoints", "form_data_validation"]:
            for test in self.test_results[category]:
                total_tests += 1
                if test["status"].startswith("✅"):
                    passed_tests += 1
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        self.test_results["summary"] = {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": total_tests - passed_tests,
            "success_rate": round(success_rate, 1)
        }

    def print_detailed_results(self):
        """Print comprehensive test results"""
        print("\n" + "="*80)
        print("🎯 ADVANCED IMAGE UPLOAD FUNCTIONALITY - COMPREHENSIVE BACKEND TESTING RESULTS")
        print("="*80)
        
        # Summary
        summary = self.test_results["summary"]
        print(f"\n📊 OVERALL SUMMARY:")
        print(f"   Total Tests: {summary['total_tests']}")
        print(f"   Passed: {summary['passed']}")
        print(f"   Failed: {summary['failed']}")
        print(f"   Success Rate: {summary['success_rate']}%")
        
        # Detailed results by category
        categories = [
            ("image_upload_endpoints", "🖼️ IMAGE UPLOAD ENDPOINTS TESTING"),
            ("web3_nft_integration", "🔗 WEB3 NFT INTEGRATION TESTING"),
            ("dao_governance", "🏛️ DAO GOVERNANCE TESTING"),
            ("additional_endpoints", "📡 ADDITIONAL ENDPOINTS TESTING"),
            ("form_data_validation", "✅ FORM DATA AND FILE UPLOAD TESTING")
        ]
        
        for category_key, category_title in categories:
            tests = self.test_results[category_key]
            if tests:
                print(f"\n{category_title}")
                print("-" * len(category_title))
                
                for test in tests:
                    print(f"   {test['status']} {test['test']}")
                    
                    # Print relevant details based on test type
                    if category_key == "image_upload_endpoints":
                        if "usage_rights" in test:
                            print(f"      Usage Rights: {test['usage_rights']}")
                        if "metadata_id" in test:
                            print(f"      Metadata ID: {test.get('metadata_id', 'N/A')}")
                        if "total_files" in test:
                            print(f"      Files Processed: {test.get('successful_uploads', 0)}/{test.get('total_files', 0)}")
                    
                    elif category_key == "web3_nft_integration":
                        if "blockchain" in test:
                            print(f"      Blockchain: {test['blockchain']} ({test.get('token_standard', 'N/A')})")
                        if "transaction_hash" in test:
                            print(f"      Transaction: {test.get('transaction_hash', 'N/A')}")
                        if "simulated" in test:
                            print(f"      Simulated: {test.get('simulated', False)}")
                    
                    elif category_key == "dao_governance":
                        if "proposal_type" in test:
                            print(f"      Proposal Type: {test['proposal_type']}")
                        if "voting_period" in test:
                            print(f"      Voting Period: {test.get('voting_period', 'N/A')} days")
                        if "proposal_id" in test:
                            print(f"      Proposal ID: {test.get('proposal_id', 'N/A')}")
                    
                    elif category_key == "additional_endpoints":
                        if "nft_count" in test:
                            print(f"      NFT Count: {test.get('nft_count', 0)}")
                        if "proposal_count" in test:
                            print(f"      Proposal Count: {test.get('proposal_count', 0)}")
                        if "portfolio_count" in test:
                            print(f"      Portfolio Count: {test.get('portfolio_count', 0)}")
                    
                    if "error" in test:
                        print(f"      Error: {test['error']}")
                    
                    print()

    async def run_comprehensive_tests(self):
        """Run all advanced image upload tests"""
        print("🚀 Starting Advanced Image Upload Functionality Testing...")
        print(f"🌐 Backend URL: {self.base_url}")
        
        try:
            await self.setup_session()
            
            # Authenticate
            if not await self.authenticate_user():
                print("❌ Authentication failed - cannot proceed with testing")
                return
            
            # Run all test categories
            await self.test_image_upload_endpoint()
            await self.test_batch_upload_endpoint()
            await self.test_web3_nft_integration()
            await self.test_dao_governance_integration()
            await self.test_additional_endpoints()
            
            # Calculate summary
            self.calculate_summary()
            
            # Print results
            self.print_detailed_results()
            
        except Exception as e:
            logger.error(f"❌ Testing failed with exception: {str(e)}")
            
        finally:
            await self.cleanup_session()

async def main():
    """Main testing function"""
    tester = AdvancedImageUploadTester()
    await tester.run_comprehensive_tests()

if __name__ == "__main__":
    asyncio.run(main())