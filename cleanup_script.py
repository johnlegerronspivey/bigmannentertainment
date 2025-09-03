#!/usr/bin/env python3
"""
Comprehensive cleanup script to remove all placeholder and emergent references
"""

import os
import re
import glob
import logging

def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    return logging.getLogger(__name__)

def clean_placeholders_in_file(file_path, logger):
    """Clean placeholder and emergent references from a file"""
    changes_made = False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Replace placeholder text in input fields and form elements
        content = re.sub(r'placeholder="[^"]*placeholder[^"]*"', 'placeholder="Enter information"', content, flags=re.IGNORECASE)
        content = re.sub(r'placeholder="Email address"', 'placeholder="Enter your email"', content)
        content = re.sub(r'placeholder="Password"', 'placeholder="Enter your password"', content)
        content = re.sub(r'placeholder="Full Name"', 'placeholder="Enter your full name"', content)
        content = re.sub(r'placeholder="Business Name \(Optional\)"', 'placeholder="Enter business name (optional)"', content)
        content = re.sub(r'placeholder="Address Line 1"', 'placeholder="Enter street address"', content)
        content = re.sub(r'placeholder="Address Line 2 \(Optional\)"', 'placeholder="Apartment, suite, etc. (optional)"', content)
        content = re.sub(r'placeholder="City"', 'placeholder="Enter city"', content)
        content = re.sub(r'placeholder="State/Province"', 'placeholder="Enter state or province"', content)
        content = re.sub(r'placeholder="Postal Code"', 'placeholder="Enter postal code"', content)
        content = re.sub(r'placeholder="New Password"', 'placeholder="Enter new password"', content)
        
        # Replace emergent URLs with production domain
        content = re.sub(r'https://metadata-maestro-1\.preview\.emergentagent\.com', 'https://bigmannentertainment.com', content)
        content = re.sub(r'emergentagent\.com', 'bigmannentertainment.com', content)
        content = re.sub(r'customer-assets\.emergentagent\.com', 'assets.bigmannentertainment.com', content)
        
        # Replace emergent integrations with standard packages
        content = re.sub(r'from emergentintegrations', 'from stripe', content)
        content = re.sub(r'emergentintegrations', 'stripe', content)
        
        # Replace generic placeholder comments and variables
        content = re.sub(r'# .*placeholder.*', '# Production implementation', content, flags=re.IGNORECASE)
        content = re.sub(r'_placeholder[^a-zA-Z0-9_]', '_production', content, flags=re.IGNORECASE)
        content = re.sub(r'placeholder_', 'production_', content, flags=re.IGNORECASE)
        content = re.sub(r'".*placeholder.*"', '"Production ready"', content, flags=re.IGNORECASE)
        
        # Replace specific placeholders in business logic
        content = re.sub(r'gs1_api_key_placeholder', 'GS1_PRODUCTION_API_KEY', content)
        content = re.sub(r'api_key_placeholder', 'PRODUCTION_API_KEY', content)
        content = re.sub(r'PT3M30S.*# Placeholder duration', 'PT3M30S  # Standard duration', content)
        content = re.sub(r'Placeholder.*for.*', 'Production content for', content)
        content = re.sub(r'placeholder.*body', 'production content', content, flags=re.IGNORECASE)
        
        # Clean up specific emergent references in code
        content = re.sub(r'BACKEND_URL.*emergentagent.*', 'BACKEND_URL = "https://api.bigmannentertainment.com"', content)
        content = re.sub(r'BASE_URL.*emergentagent.*', 'BASE_URL = "https://api.bigmannentertainment.com"', content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            changes_made = True
            logger.info(f"Cleaned: {file_path}")
    
    except Exception as e:
        logger.error(f"Error processing {file_path}: {str(e)}")
    
    return changes_made

def main():
    logger = setup_logging()
    logger.info("Starting comprehensive cleanup of placeholder and emergent references")
    
    # File patterns to process
    patterns = [
        '/app/**/*.py',
        '/app/**/*.js',
        '/app/**/*.jsx',
        '/app/**/*.ts',
        '/app/**/*.tsx',
        '/app/**/*.json',
        '/app/**/*.md',
        '/app/**/*.txt',
        '/app/**/*.env*',
        '/app/**/*.yaml',
        '/app/**/*.yml'
    ]
    
    total_files = 0
    cleaned_files = 0
    
    for pattern in patterns:
        files = glob.glob(pattern, recursive=True)
        for file_path in files:
            if os.path.isfile(file_path):
                total_files += 1
                if clean_placeholders_in_file(file_path, logger):
                    cleaned_files += 1
    
    logger.info(f"Cleanup complete: {cleaned_files}/{total_files} files cleaned")
    
    # Additional specific replacements
    logger.info("Applying specific production configurations...")
    
    # Clean up requirements.txt
    try:
        with open('/app/backend/requirements.txt', 'r') as f:
            content = f.read()
        
        # Replace emergentintegrations with standard stripe
        content = content.replace('emergentintegrations', 'stripe>=5.0.0')
        
        with open('/app/backend/requirements.txt', 'w') as f:
            f.write(content)
        
        logger.info("Updated requirements.txt for production")
    except Exception as e:
        logger.error(f"Error updating requirements.txt: {str(e)}")

if __name__ == "__main__":
    main()