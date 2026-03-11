"""
Enhanced validation utilities
Provides comprehensive input validation with detailed error messages
"""
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, validator, ValidationError


class ValidationError(Exception):
    """Custom validation error with user-friendly messages"""
    def __init__(self, field: str, message: str, suggestions: Optional[List[str]] = None):
        self.field = field
        self.message = message
        self.suggestions = suggestions or []
        super().__init__(self.message)
    
    def to_dict(self):
        return {
            'field': self.field,
            'message': self.message,
            'suggestions': self.suggestions
        }


class Validator:
    """Comprehensive validator with detailed error messages"""
    
    @staticmethod
    def validate_email(email: str) -> tuple[bool, str]:
        """Validate email format with helpful error messages"""
        if not email:
            return False, "Email address is required"
        
        if len(email) > 255:
            return False, "Email address is too long (max 255 characters)"
        
        # Basic email regex
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return False, "Invalid email format. Example: user@example.com"
        
        return True, "Valid"
    
    @staticmethod
    def validate_password(password: str) -> tuple[bool, str, List[str]]:
        """Validate password strength with specific requirements"""
        suggestions = []
        
        if not password:
            return False, "Password is required", []
        
        if len(password) < 8:
            suggestions.append("Use at least 8 characters")
        
        if not re.search(r'[A-Z]', password):
            suggestions.append("Include at least one uppercase letter")
        
        if not re.search(r'[a-z]', password):
            suggestions.append("Include at least one lowercase letter")
        
        if not re.search(r'[0-9]', password):
            suggestions.append("Include at least one number")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            suggestions.append("Include at least one special character")
        
        if suggestions:
            return False, "Password does not meet security requirements", suggestions
        
        return True, "Strong password", []
    
    @staticmethod
    def validate_url(url: str, schemes: List[str] = ['http', 'https']) -> tuple[bool, str]:
        """Validate URL format"""
        if not url:
            return False, "URL is required"
        
        # Simple URL validation
        url_pattern = r'^(https?|ftp)://[^\s/$.?#].[^\s]*$'
        if not re.match(url_pattern, url, re.IGNORECASE):
            return False, f"Invalid URL format. Must start with {' or '.join(schemes)}://"
        
        return True, "Valid URL"
    
    @staticmethod
    def validate_phone(phone: str) -> tuple[bool, str]:
        """Validate phone number"""
        if not phone:
            return False, "Phone number is required"
        
        # Remove common formatting characters
        digits_only = re.sub(r'[^\d+]', '', phone)
        
        if len(digits_only) < 10:
            return False, "Phone number too short (minimum 10 digits)"
        
        if len(digits_only) > 15:
            return False, "Phone number too long (maximum 15 digits)"
        
        return True, "Valid phone number"
    
    @staticmethod
    def validate_file_size(size_bytes: int, max_mb: int = 100) -> tuple[bool, str]:
        """Validate file size"""
        max_bytes = max_mb * 1024 * 1024
        
        if size_bytes > max_bytes:
            size_mb = size_bytes / (1024 * 1024)
            return False, f"File too large ({size_mb:.2f}MB). Maximum size is {max_mb}MB"
        
        return True, "Valid file size"
    
    @staticmethod
    def validate_file_type(filename: str, allowed_extensions: List[str]) -> tuple[bool, str]:
        """Validate file extension"""
        if not filename:
            return False, "Filename is required"
        
        extension = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
        
        if not extension:
            return False, "File must have an extension"
        
        if extension not in allowed_extensions:
            return False, f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        
        return True, "Valid file type"
    
    @staticmethod
    def validate_date_range(start_date: datetime, end_date: datetime) -> tuple[bool, str]:
        """Validate date range"""
        if start_date >= end_date:
            return False, "Start date must be before end date"
        
        # Check if date range is reasonable (not more than 10 years)
        diff_days = (end_date - start_date).days
        if diff_days > 3650:  # 10 years
            return False, "Date range too large (maximum 10 years)"
        
        return True, "Valid date range"
    
    @staticmethod
    def validate_pagination(page: int, page_size: int) -> tuple[bool, str]:
        """Validate pagination parameters"""
        if page < 1:
            return False, "Page number must be at least 1"
        
        if page_size < 1:
            return False, "Page size must be at least 1"
        
        if page_size > 100:
            return False, "Page size too large (maximum 100)"
        
        return True, "Valid pagination"
    
    @staticmethod
    def sanitize_input(text: str, max_length: int = 1000) -> str:
        """Sanitize user input to prevent injection attacks"""
        if not text:
            return ""
        
        # Remove potentially dangerous characters
        sanitized = text.strip()
        
        # Remove null bytes
        sanitized = sanitized.replace('\x00', '')
        
        # Limit length
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized
    
    @staticmethod
    def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> List[ValidationError]:
        """Validate that all required fields are present"""
        errors = []
        
        for field in required_fields:
            if field not in data or data[field] is None or data[field] == '':
                errors.append(
                    ValidationError(
                        field=field,
                        message=f"{field.replace('_', ' ').title()} is required",
                        suggestions=[f"Please provide a value for {field}"]
                    )
                )
        
        return errors


class EnhancedValidator:
    """Combined validator for complex validation scenarios"""
    
    @staticmethod
    def validate_user_registration(data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate user registration data"""
        errors = []
        
        # Email validation
        if 'email' in data:
            is_valid, message = Validator.validate_email(data['email'])
            if not is_valid:
                errors.append({
                    'field': 'email',
                    'message': message,
                    'value': data['email']
                })
        else:
            errors.append({
                'field': 'email',
                'message': 'Email is required'
            })
        
        # Password validation
        if 'password' in data:
            is_valid, message, suggestions = Validator.validate_password(data['password'])
            if not is_valid:
                errors.append({
                    'field': 'password',
                    'message': message,
                    'suggestions': suggestions
                })
        else:
            errors.append({
                'field': 'password',
                'message': 'Password is required'
            })
        
        # Name validation
        if 'full_name' in data:
            if len(data['full_name'].strip()) < 2:
                errors.append({
                    'field': 'full_name',
                    'message': 'Full name must be at least 2 characters',
                    'value': data['full_name']
                })
        else:
            errors.append({
                'field': 'full_name',
                'message': 'Full name is required'
            })
        
        return errors
    
    @staticmethod
    def validate_media_upload(data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate media upload data"""
        errors = []
        
        # Title validation
        if not data.get('title') or len(data['title'].strip()) < 3:
            errors.append({
                'field': 'title',
                'message': 'Title must be at least 3 characters',
                'suggestions': ['Provide a descriptive title for your media']
            })
        
        # Category validation
        valid_categories = ['music', 'video', 'image', 'podcast', 'other']
        if data.get('category') not in valid_categories:
            errors.append({
                'field': 'category',
                'message': 'Invalid category',
                'suggestions': [f'Choose from: {", ".join(valid_categories)}']
            })
        
        # Price validation
        if 'price' in data:
            try:
                price = float(data['price'])
                if price < 0:
                    errors.append({
                        'field': 'price',
                        'message': 'Price cannot be negative',
                        'suggestions': ['Enter a price of 0 or higher']
                    })
                if price > 10000:
                    errors.append({
                        'field': 'price',
                        'message': 'Price seems too high',
                        'suggestions': ['Maximum price is $10,000']
                    })
            except (ValueError, TypeError):
                errors.append({
                    'field': 'price',
                    'message': 'Price must be a valid number'
                })
        
        return errors
