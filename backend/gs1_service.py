import logging
import httpx
from typing import Dict, Any, Optional, List
from decimal import Decimal
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

class GS1USService:
    def __init__(self, api_key: str, company_prefix: str, account_id: str):
        self.api_key = api_key
        self.company_prefix = company_prefix
        self.account_id = account_id
        self.base_url = "https://api.gs1us.org"
        
        self.headers = {
            "APIKey": self.api_key,
            "X-Product-Owner-Account-Id": self.account_id,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def calculate_check_digit(self, identifier: str) -> str:
        """Calculate check digit for UPC/GTIN using GS1 algorithm"""
        if not identifier or not identifier.isdigit():
            raise ValueError("Identifier must contain only digits")
        
        # Remove existing check digit if present
        if len(identifier) in [12, 13, 14]:
            identifier = identifier[:-1]
        
        # Pad to appropriate length
        if len(identifier) == 11:  # UPC-A
            identifier = identifier
        elif len(identifier) == 12:  # EAN-13/GTIN-13
            identifier = identifier
        else:
            raise ValueError("Invalid identifier length")
        
        # Calculate check digit
        odd_sum = sum(int(identifier[i]) for i in range(0, len(identifier), 2))
        even_sum = sum(int(identifier[i]) for i in range(1, len(identifier), 2))
        
        total = odd_sum + (even_sum * 3)
        check_digit = (10 - (total % 10)) % 10
        
        return str(check_digit)
    
    def validate_check_digit(self, identifier: str) -> bool:
        """Validate check digit for UPC/GTIN/GLN"""
        if not identifier or not identifier.isdigit():
            return False
        
        if len(identifier) not in [12, 13, 14]:
            return False
        
        calculated_check = self.calculate_check_digit(identifier[:-1])
        return calculated_check == identifier[-1]
    
    def generate_next_upc(self, last_sequence: Optional[int] = None) -> str:
        """Generate next UPC code using company prefix"""
        if last_sequence is None:
            next_sequence = 1
        else:
            next_sequence = last_sequence + 1
        
        # Format: Company Prefix + Product Code + Check Digit
        product_code_length = 11 - len(self.company_prefix)
        if product_code_length <= 0:
            raise ValueError("Company prefix too long for UPC generation")
        
        product_code = str(next_sequence).zfill(product_code_length)
        upc_without_check = self.company_prefix + product_code
        
        if len(upc_without_check) != 11:
            raise ValueError("Invalid UPC format during generation")
        
        check_digit = self.calculate_check_digit(upc_without_check)
        upc = upc_without_check + check_digit
        
        return upc
    
    def generate_next_gln(self, last_sequence: Optional[int] = None) -> str:
        """Generate next GLN using company prefix"""
        if last_sequence is None:
            next_sequence = 1
        else:
            next_sequence = last_sequence + 1
        
        # Format: Company Prefix + Location Reference + Check Digit
        location_ref_length = 12 - len(self.company_prefix)
        if location_ref_length <= 0:
            raise ValueError("Company prefix too long for GLN generation")
        
        location_reference = str(next_sequence).zfill(location_ref_length)
        gln_without_check = self.company_prefix + location_reference
        
        if len(gln_without_check) != 12:
            raise ValueError("Invalid GLN format during generation")
        
        check_digit = self.calculate_check_digit(gln_without_check)
        gln = gln_without_check + check_digit
        
        return gln
    
    async def register_gtin_with_gs1(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register GTIN with GS1 US Data Hub"""
        endpoint = f"{self.base_url}/api/v1/myproduct"
        
        # Prepare GS1 product data format
        gs1_data = {
            "gtin": product_data["gtin"],
            "brandName1": product_data.get("brand_name", "")[:70],
            "brandNameLanguage1": "ENG",
            "productDescription1": product_data.get("product_description", "")[:200],
            "productDescriptionLanguage1": "ENG",
            "industryType": "Entertainment",
            "productType": "Digital Music"
        }
        
        # Add optional fields
        if product_data.get("release_date"):
            gs1_data["releaseDate"] = product_data["release_date"].isoformat()
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    endpoint,
                    headers=self.headers,
                    json=gs1_data
                )
                response.raise_for_status()
                
                logger.info(f"Successfully registered GTIN {product_data['gtin']} with GS1")
                return response.json()
                
        except httpx.HTTPStatusError as e:
            logger.error(f"GS1 API error registering GTIN: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error registering GTIN: {str(e)}")
            raise
    
    async def register_gln_with_gs1(self, location_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register GLN with GS1 US Data Hub"""
        endpoint = f"{self.base_url}/api/v1/location"
        
        # Prepare GS1 location data format
        gs1_data = {
            "gln": location_data["gln"],
            "organizationName": {
                "language": "ENG",
                "value": location_data.get("organization_name", "")[:255]
            },
            "locationName": {
                "language": "ENG",
                "value": location_data.get("location_name", "")[:255]
            },
            "streetAddress": location_data.get("street_address", "")[:255],
            "addressLocality": location_data.get("address_locality", "")[:100],
            "addressRegion": location_data.get("address_region", "")[:100],
            "postalCode": location_data.get("postal_code", "")[:20],
            "countryCode": location_data.get("country_code", "US"),
            "glnType": location_data.get("gln_type", "Legal Entity"),
            "supplyChainRole": location_data.get("supply_chain_role", ""),
            "industry": location_data.get("industry", "Entertainment")
        }
        
        # Add optional hierarchy fields
        if location_data.get("parent_gln"):
            gs1_data["parentGln"] = location_data["parent_gln"]
        
        if location_data.get("entity_gln"):
            gs1_data["entityGln"] = location_data["entity_gln"]
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    endpoint,
                    headers=self.headers,
                    json=gs1_data
                )
                response.raise_for_status()
                
                logger.info(f"Successfully registered GLN {location_data['gln']} with GS1")
                return response.json()
                
        except httpx.HTTPStatusError as e:
            logger.error(f"GS1 API error registering GLN: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error registering GLN: {str(e)}")
            raise
    
    def create_music_release_data(self, title: str, artist_name: str, label_name: str, 
                                 release_date: datetime, **kwargs) -> Dict[str, Any]:
        """Create standardized music release data for GS1 registration"""
        
        # Generate UPC and GTIN
        upc = self.generate_next_upc(kwargs.get("last_sequence"))
        gtin = f"0{upc}"  # Convert UPC-12 to GTIN-13
        
        release_data = {
            "gtin": gtin,
            "upc": upc,
            "title": title,
            "artist_name": artist_name,
            "label_name": label_name,
            "release_date": release_date,
            "brand_name": label_name[:70],
            "product_description": f"{artist_name} - {title}"[:200],
            "genre": kwargs.get("genre"),
            "duration_seconds": kwargs.get("duration_seconds"),
            "isrc": kwargs.get("isrc"),
            "catalog_number": kwargs.get("catalog_number"),
            "distribution_format": kwargs.get("distribution_format", "Digital")
        }
        
        return release_data
    
    def create_location_data(self, location_name: str, organization_name: str, 
                           gln_type: str = "Legal Entity", **kwargs) -> Dict[str, Any]:
        """Create standardized location data for GS1 registration"""
        
        # Generate GLN
        gln = self.generate_next_gln(kwargs.get("last_sequence"))
        
        location_data = {
            "gln": gln,
            "location_name": location_name,
            "organization_name": organization_name,
            "gln_type": gln_type,
            "street_address": kwargs.get("street_address"),
            "address_locality": kwargs.get("address_locality"),
            "address_region": kwargs.get("address_region"),
            "postal_code": kwargs.get("postal_code"),
            "country_code": kwargs.get("country_code", "US"),
            "supply_chain_role": kwargs.get("supply_chain_role"),
            "industry": kwargs.get("industry", "Entertainment"),
            "parent_gln": kwargs.get("parent_gln"),
            "entity_gln": kwargs.get("entity_gln")
        }
        
        return location_data
    
    def get_big_mann_entertainment_info(self) -> Dict[str, str]:
        """Get Big Mann Entertainment business information"""
        return {
            "business_entity": "Big Mann Entertainment",
            "business_owner": "John LeGerron Spivey",
            "ein": "270658077",
            "tin": "12800",
            "industry": "Entertainment",
            "business_type": "Media Distribution"
        }