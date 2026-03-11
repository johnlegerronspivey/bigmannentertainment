"""
GS1 Profile Service
Generates GS1 identifiers and digital links for assets
"""
import os
import qrcode
import io
import base64
from datetime import datetime
from typing import Optional, Dict
import random
import string
from PIL import Image, ImageDraw

class GS1ProfileService:
    """Service for managing GS1 identifiers and digital links"""
    
    def __init__(self):
        # Get GS1 configuration from environment
        self.company_prefix = os.getenv("GS1_COMPANY_PREFIX", "8600043402")
        self.gln_base = os.getenv("GLOBAL_LOCATION_NUMBER", "0860004340201")
        self.isrc_prefix = os.getenv("ISRC_PREFIX", "QZ9H8")
        self.base_url = os.getenv("GS1_DIGITAL_LINK_BASE", "https://id.gs1.org")
        
    def generate_gtin(self, item_reference: Optional[str] = None) -> str:
        """
        Generate GTIN-13 (EAN-13) identifier
        Format: GS1 Company Prefix + Item Reference + Check Digit
        """
        if not item_reference:
            # Generate random 5-digit item reference
            item_reference = ''.join(random.choices(string.digits, k=5))
        
        # Ensure item reference is 5 digits
        item_reference = item_reference.zfill(5)
        
        # Combine company prefix (7 digits) + item reference (5 digits)
        gtin_without_check = self.company_prefix + item_reference
        
        # Calculate check digit
        check_digit = self._calculate_check_digit(gtin_without_check)
        
        return gtin_without_check + str(check_digit)
    
    def generate_isrc(self, year: Optional[int] = None, designation: Optional[str] = None) -> str:
        """
        Generate ISRC (International Standard Recording Code)
        Format: Country Code (2) + Registrant Code (3) + Year (2) + Designation (5)
        Example: US-BM1-25-00001
        """
        if not year:
            year = datetime.now().year % 100  # Last 2 digits of year
        
        if not designation:
            # Generate random 5-digit designation
            designation = ''.join(random.choices(string.digits, k=5))
        
        designation = designation.zfill(5)
        
        return f"US-{self.isrc_prefix}-{year:02d}-{designation}"
    
    def generate_isan(self, version: int = 0) -> str:
        """
        Generate ISAN (International Standard Audiovisual Number)
        Format: Root (12 hex) + Episode (4 hex) + Check Char + Version (4 hex) + Check Char
        Example: 0000-0000-0000-0000-0-0000-0
        """
        # Generate random root (12 hex digits in groups of 4)
        root_parts = [''.join(random.choices(string.hexdigits.upper()[:16], k=4)) for _ in range(3)]
        root = '-'.join(root_parts)
        
        # Generate episode (4 hex digits)
        episode = ''.join(random.choices(string.hexdigits.upper()[:16], k=4))
        
        # Check character (simplified - would need actual algorithm)
        check1 = random.choice(string.hexdigits.upper()[:16])
        
        # Version (4 hex digits)
        version_hex = f"{version:04X}"
        
        # Second check character
        check2 = random.choice(string.hexdigits.upper()[:16])
        
        return f"{root}-{episode}-{check1}-{version_hex}-{check2}"
    
    def generate_gdti(self, document_type: Optional[str] = None) -> str:
        """
        Generate GDTI (Global Document Type Identifier)
        Format: Company Prefix + Document Type + Serial Number + Check Digit
        """
        if not document_type:
            document_type = ''.join(random.choices(string.digits, k=3))
        
        document_type = document_type.zfill(3)
        
        # Serial number
        serial = ''.join(random.choices(string.digits + string.ascii_uppercase, k=8))
        
        # Base GDTI
        gdti_base = self.company_prefix + document_type
        check_digit = self._calculate_check_digit(gdti_base)
        
        return f"{gdti_base}{check_digit}{serial}"
    
    def generate_gln_for_location(self, location_code: Optional[str] = None) -> str:
        """
        Generate GLN (Global Location Number) for a specific location
        Format: GS1 Company Prefix + Location Reference + Check Digit
        """
        if not location_code:
            location_code = ''.join(random.choices(string.digits, k=5))
        
        location_code = location_code.zfill(5)
        
        gln_without_check = self.company_prefix + location_code
        check_digit = self._calculate_check_digit(gln_without_check)
        
        return gln_without_check + str(check_digit)
    
    def create_digital_link(self, gtin: str, additional_params: Optional[Dict] = None) -> str:
        """
        Create GS1 Digital Link URL
        Format: https://id.gs1.org/01/{GTIN}?key=value
        """
        url = f"{self.base_url}/01/{gtin}"
        
        if additional_params:
            params = '&'.join([f"{k}={v}" for k, v in additional_params.items()])
            url += f"?{params}"
        
        return url
    
    def generate_qr_code(self, data: str, size: int = 300, with_logo: bool = True) -> str:
        """
        Generate QR code image as base64 string with optional BME logo overlay
        Returns: data:image/png;base64,{encoded_image}
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction for logo overlay
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to PIL Image for logo overlay
        if with_logo:
            img = img.convert('RGB')
            img = self._add_logo_to_qr(img)
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    def _add_logo_to_qr(self, qr_img: Image.Image) -> Image.Image:
        """
        Add Big Mann Entertainment logo to center of QR code
        Creates a simple branded logo if logo file doesn't exist
        """
        # Create a simple BME logo if no file exists
        # Get QR code dimensions
        qr_width, qr_height = qr_img.size
        logo_size = qr_width // 5  # Logo takes up 20% of QR code
        
        # Create logo image with purple background and white text
        logo = Image.new('RGB', (logo_size, logo_size), color='#7C3AED')  # Purple color
        draw = ImageDraw.Draw(logo)
        
        # Draw white border
        border_width = 3
        draw.rectangle(
            [border_width, border_width, logo_size - border_width, logo_size - border_width],
            outline='white',
            width=border_width
        )
        
        # Add text "BME" in center (simplified - would need better font handling)
        text = "BME"
        text_bbox = draw.textbbox((0, 0), text)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        text_x = (logo_size - text_width) // 2
        text_y = (logo_size - text_height) // 2
        draw.text((text_x, text_y), text, fill='white')
        
        # Calculate position to center logo on QR code
        logo_pos_x = (qr_width - logo_size) // 2
        logo_pos_y = (qr_height - logo_size) // 2
        
        # Paste logo onto QR code
        qr_img.paste(logo, (logo_pos_x, logo_pos_y))
        
        return qr_img
    
    def generate_qr_code_file(self, data: str, with_logo: bool = True) -> bytes:
        """
        Generate QR code as PNG bytes for download
        Returns: PNG file bytes
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        img = img.convert('RGB')
        
        if with_logo:
            img = self._add_logo_to_qr(img)
        
        # Convert to bytes
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()
    
    def _calculate_check_digit(self, code: str) -> int:
        """
        Calculate GS1 check digit using modulo 10 algorithm
        """
        # Convert to list of integers
        digits = [int(d) for d in code]
        
        # Apply weights: odd positions get 3, even positions get 1 (from right)
        total = 0
        for i, digit in enumerate(reversed(digits)):
            weight = 3 if i % 2 == 0 else 1
            total += digit * weight
        
        # Calculate check digit
        check_digit = (10 - (total % 10)) % 10
        
        return check_digit
    
    def validate_gtin(self, gtin: str) -> bool:
        """Validate GTIN check digit"""
        if not gtin or not gtin.isdigit() or len(gtin) != 13:
            return False
        
        code_without_check = gtin[:-1]
        provided_check = int(gtin[-1])
        calculated_check = self._calculate_check_digit(code_without_check)
        
        return provided_check == calculated_check
    
    def parse_isrc(self, isrc: str) -> Dict:
        """Parse ISRC into components"""
        parts = isrc.split('-')
        if len(parts) != 4:
            return {}
        
        return {
            "country_code": parts[0],
            "registrant_code": parts[1],
            "year": parts[2],
            "designation": parts[3]
        }

# Singleton instance
gs1_service = GS1ProfileService()
