"""
Extract inline code from server.py into modular files.
Uses exact line ranges from manual analysis.
"""

def read_lines(path):
    with open(path) as f:
        return f.readlines()

def write_file(path, content):
    with open(path, 'w') as f:
        f.write(content)
    print(f"  Created {path} ({content.count(chr(10))} lines)")

lines = read_lines('/app/backend/server.py')

def get_range(start, end):
    """Get lines (1-indexed, inclusive)"""
    return ''.join(lines[start-1:end])

# ============================================================
# 1. services/distribution_svc.py (lines 1362-1542)
# ============================================================
content = '''"""Distribution service - content distribution across 119+ platforms."""
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import HTTPException
from config.database import db
from config.platforms import DISTRIBUTION_PLATFORMS
from models.core import ContentDistribution

''' + get_range(1362, 1542) + '\n'
write_file('/app/backend/services/distribution_svc.py', content)

# ============================================================
# 2. services/email_svc.py (lines 1545-2254: first SESService + EmailService + init)
# ============================================================
content = '''"""Email services - SES with SMTP fallback, branded email templates."""
import os
import re
import logging
import boto3
from datetime import datetime
from typing import Optional
from botocore.exceptions import ClientError, NoCredentialsError

''' + get_range(1545, 2254) + '\n'
write_file('/app/backend/services/email_svc.py', content)

# ============================================================
# 3. services/s3_svc.py (lines 2257-2434: S3Service)
# ============================================================
content = '''"""AWS S3 service for media file storage."""
import os
import logging
from datetime import datetime
from typing import List, Optional
import boto3
from fastapi import HTTPException, UploadFile
from botocore.exceptions import ClientError

''' + get_range(2257, 2434) + '\n'
write_file('/app/backend/services/s3_svc.py', content)

# ============================================================
# 4. services/ses_transactional_svc.py (lines 2436-2746: second SESService + EmailNotificationService + inits)
# ============================================================
content = '''"""AWS SES transactional email service + enhanced notification service."""
import os
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
import boto3
from botocore.exceptions import ClientError
from services.email_svc import EmailService

''' + get_range(2436, 2746) + '\n'
write_file('/app/backend/services/ses_transactional_svc.py', content)

# ============================================================
# 5. services/aws_media_svc.py (lines 6323-6544: CloudFront + Lambda + Rekognition + inits)
# ============================================================
content = '''"""AWS media processing services - CloudFront CDN, Lambda, Rekognition."""
import os
import json
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
import boto3

''' + get_range(6323, 6544) + '\n'
write_file('/app/backend/services/aws_media_svc.py', content)

# ============================================================
# 6. routes/licensing_routes.py (lines 457-658)
# ============================================================
content = '''"""Licensing and rights compliance endpoints."""
import uuid
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter
from config.database import db

router = APIRouter(tags=["Licensing"])

''' + get_range(457, 658) + '\n'
# Replace @api_router with @router
content = content.replace('@api_router.', '@router.')
write_file('/app/backend/routes/licensing_routes.py', content)

# ============================================================
# 7. routes/agency_routes.py (lines 668-1291)
# ============================================================
content = '''"""Agency onboarding endpoints - registration, KYC, talent, contracts."""
import uuid
import hashlib
from datetime import datetime, timezone
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, File, Form, UploadFile
from config.database import db
from auth.service import get_current_user
from models.core import User
from models.agency import (
    VerificationStatus, AgencyRegistrationRequest,
    TalentCreationRequest, LicenseContractRequest,
)

agency_router = APIRouter(prefix="/agency", tags=["Agency Onboarding"])

''' + get_range(671, 1291) + '\n'
write_file('/app/backend/routes/agency_routes.py', content)

# ============================================================
# 8. routes/admin_routes.py (lines 1295-1360 + 5430-5691)
# ============================================================
content = '''"""Admin endpoints - notifications, user management, content moderation."""
from datetime import datetime, timezone
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Form
from config.database import db
from auth.service import get_current_user, get_current_admin_user
from models.core import User, MediaContent
from models.agency import NotificationRequest

router = APIRouter(tags=["Admin"])

''' + get_range(1295, 1360) + '\n' + get_range(5430, 5691) + '\n'
content = content.replace('@api_router.', '@router.')
write_file('/app/backend/routes/admin_routes.py', content)

# ============================================================
# 9. routes/auth_routes.py (lines 2748-3168: UPC helper + auth endpoints)
# ============================================================
content = '''"""Authentication endpoints - register, login, password management."""
import re
import uuid
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Request
from config.database import db
from config.settings import settings
from auth.service import (
    verify_password, get_password_hash, create_access_token,
    create_refresh_token, get_current_user, log_activity,
)
from models.core import User, UserCreate, UserLogin, Token, TokenRefresh, ForgotPasswordRequest, ResetPasswordRequest

router = APIRouter(tags=["Authentication"])

# Import email service lazily to avoid circular imports
def _get_email_service():
    from services.email_svc import email_service
    return email_service

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS
MAX_LOGIN_ATTEMPTS = settings.MAX_LOGIN_ATTEMPTS
LOCKOUT_DURATION_MINUTES = settings.LOCKOUT_DURATION_MINUTES
PASSWORD_RESET_TOKEN_EXPIRE_HOURS = settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS

''' + get_range(2748, 3168) + '\n'
content = content.replace('@api_router.', '@router.')
# Fix email_service references to use lazy import
content = content.replace('email_service.send_password_reset_email', '_get_email_service().send_password_reset_email')
content = content.replace('email_service.send_welcome_email', '_get_email_service().send_welcome_email')
write_file('/app/backend/routes/auth_routes.py', content)

# ============================================================
# 10. routes/dao_routes.py (lines 3169-3318)
# ============================================================
content = '''"""DAO and Smart Contract endpoints."""
from datetime import datetime, timezone
from fastapi import APIRouter
from config.database import db
from dao_smart_contracts import dao_contract_manager

router = APIRouter(tags=["DAO"])

''' + get_range(3169, 3318) + '\n'
content = content.replace('@api_router.', '@router.')
write_file('/app/backend/routes/dao_routes.py', content)

# ============================================================
# 11. routes/health_routes.py (lines 3319-3612 + 5691-5823)
# ============================================================
content = '''"""Service health check endpoints."""
import os
from datetime import datetime, timezone
from typing import Dict, Any
from fastapi import APIRouter
from config.database import db

router = APIRouter(tags=["Health Checks"])

''' + get_range(3319, 3612) + '\n' + get_range(5691, 5822) + '\n'
content = content.replace('@api_router.', '@router.')
write_file('/app/backend/routes/health_routes.py', content)

# ============================================================
# 12. routes/business_routes.py (lines 3614-3843)
# ============================================================
content = '''"""Business identifiers endpoints - UPC, ISRC, GLN generation."""
import uuid
import hashlib
import random
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from config.database import db
from config.settings import settings
from auth.service import get_current_user
from models.core import User, ProductIdentifier

router = APIRouter(tags=["Business"])

UPC_COMPANY_PREFIX = settings.UPC_COMPANY_PREFIX
GLOBAL_LOCATION_NUMBER = settings.GLOBAL_LOCATION_NUMBER
ISRC_PREFIX = settings.ISRC_PREFIX
PUBLISHER_NUMBER = settings.PUBLISHER_NUMBER
BUSINESS_EIN = settings.BUSINESS_EIN
BUSINESS_ADDRESS = settings.BUSINESS_ADDRESS
BUSINESS_PHONE = settings.BUSINESS_PHONE
BUSINESS_NAICS_CODE = settings.BUSINESS_NAICS_CODE
BUSINESS_TIN = settings.BUSINESS_TIN
BUSINESS_LEGAL_NAME = settings.BUSINESS_LEGAL_NAME
PRINCIPAL_NAME = settings.PRINCIPAL_NAME
IPI_BUSINESS = settings.IPI_BUSINESS
IPI_PRINCIPAL = settings.IPI_PRINCIPAL
IPN_NUMBER = settings.IPN_NUMBER
DPID = settings.DPID

''' + get_range(3614, 3843) + '\n'
content = content.replace('@api_router.', '@router.')
write_file('/app/backend/routes/business_routes.py', content)

# ============================================================
# 13. routes/media_routes.py (lines 3845-4366)
# ============================================================
content = '''"""Media management endpoints - upload, library, CRUD, search."""
import os
import uuid
import hashlib
import aiofiles
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, File, Form, UploadFile
from config.database import db
from auth.service import get_current_user
from models.core import User, MediaContent

router = APIRouter(tags=["Media"])

''' + get_range(3845, 4366) + '\n'
content = content.replace('@api_router.', '@router.')
write_file('/app/backend/routes/media_routes.py', content)

# ============================================================
# 14. routes/aws_routes.py (lines 4367-5020 + 5823-5993)
# ============================================================
content = '''"""AWS endpoints - S3 uploads, SES email, CDN, media processing."""
import os
import json
import uuid
import hashlib
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, File, Form, UploadFile, Request
from config.database import db
from auth.service import get_current_user
from models.core import User

router = APIRouter(tags=["AWS"])

# Lazy service imports to avoid circular dependencies
def _get_s3_service():
    from services.s3_svc import S3Service
    return S3Service()

def _get_ses_service():
    from services.ses_transactional_svc import ses_service
    return ses_service

''' + get_range(4367, 5020) + '\n' + get_range(5823, 5993) + '\n'
content = content.replace('@api_router.', '@router.')
write_file('/app/backend/routes/aws_routes.py', content)

# ============================================================
# 15. routes/distribution_routes.py (lines 5021-5430)
# ============================================================
content = '''"""Distribution endpoints - platform management, content distribution."""
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from config.database import db
from config.platforms import DISTRIBUTION_PLATFORMS
from auth.service import get_current_user
from models.core import User

router = APIRouter(tags=["Distribution"])

''' + get_range(5021, 5429) + '\n'
content = content.replace('@api_router.', '@router.')
write_file('/app/backend/routes/distribution_routes.py', content)

# ============================================================
# 16. routes/system_routes.py (lines 6035-6317 + webhook + misc)
# ============================================================
content = '''"""System endpoints - health, status, performance, webhooks."""
import os
import logging
from datetime import datetime, timezone
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Request
from config.database import db
from config.platforms import DISTRIBUTION_PLATFORMS
from config.settings import settings
from auth.service import get_current_user
from models.core import User

router = APIRouter(tags=["System"])

BUSINESS_LEGAL_NAME = settings.BUSINESS_LEGAL_NAME
PRINCIPAL_NAME = settings.PRINCIPAL_NAME
BUSINESS_EIN = settings.BUSINESS_EIN
BUSINESS_NAICS_CODE = settings.BUSINESS_NAICS_CODE

''' + get_range(6035, 6317) + '\n'
content = content.replace('@api_router.', '@router.')
write_file('/app/backend/routes/system_routes.py', content)

print("\n=== All files extracted successfully ===")
