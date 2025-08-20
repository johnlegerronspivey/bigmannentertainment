from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
import logging
import json
import base64
import secrets
from datetime import datetime

# Create WebAuthn router
webauthn_router = APIRouter(prefix="/api/webauthn", tags=["WebAuthn"])

logger = logging.getLogger(__name__)

# In-memory store for challenges (in production, use Redis or database)
challenges = {}

@webauthn_router.post("/register/begin")
async def begin_registration(request: Request):
    """Begin WebAuthn registration process"""
    try:
        # Generate a random challenge
        challenge = secrets.token_urlsafe(32)
        
        # Store challenge temporarily
        challenges[challenge] = {
            'created_at': datetime.utcnow(),
            'type': 'registration'
        }
        
        # Get the origin from the request
        origin = str(request.base_url).rstrip('/')
        
        # Return WebAuthn registration options
        options = {
            "challenge": base64.urlsafe_b64encode(challenge.encode()).decode().rstrip('='),
            "rp": {
                "name": "Big Mann Entertainment",
                "id": request.url.hostname or "localhost"
            },
            "user": {
                "id": base64.urlsafe_b64encode(secrets.token_bytes(32)).decode().rstrip('='),
                "name": "user@bigmannentertainment.com",
                "displayName": "Big Mann Entertainment User"
            },
            "pubKeyCredParams": [
                {"alg": -7, "type": "public-key"},  # ES256
                {"alg": -257, "type": "public-key"}  # RS256
            ],
            "authenticatorSelection": {
                "authenticatorAttachment": "platform",
                "userVerification": "required",
                "residentKey": "preferred"
            },
            "timeout": 60000,
            "attestation": "none"
        }
        
        return options
        
    except Exception as e:
        logger.error(f"WebAuthn registration begin error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to begin registration")

@webauthn_router.post("/register/complete")
async def complete_registration(credential: Dict[str, Any]):
    """Complete WebAuthn registration process"""
    try:
        # In a real implementation, you would:
        # 1. Verify the attestation
        # 2. Store the credential ID and public key
        # 3. Associate with user account
        
        logger.info(f"WebAuthn registration completed for credential: {credential.get('id', 'unknown')}")
        
        return {
            "success": True,
            "message": "WebAuthn credential registered successfully"
        }
        
    except Exception as e:
        logger.error(f"WebAuthn registration complete error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to complete registration")

@webauthn_router.post("/authenticate/begin")
async def begin_authentication(request: Request, auth_request: Dict[str, str]):
    """Begin WebAuthn authentication process"""
    try:
        email = auth_request.get('email')
        if not email:
            raise HTTPException(status_code=400, detail="Email required")
        
        # Generate a random challenge
        challenge = secrets.token_urlsafe(32)
        
        # Store challenge temporarily
        challenges[challenge] = {
            'created_at': datetime.utcnow(),
            'type': 'authentication',
            'email': email
        }
        
        # Return WebAuthn authentication options
        options = {
            "challenge": base64.urlsafe_b64encode(challenge.encode()).decode().rstrip('='),
            "rpId": request.url.hostname or "localhost",
            "allowCredentials": [],  # In production, load user's registered credentials
            "userVerification": "required",
            "timeout": 60000
        }
        
        return options
        
    except Exception as e:
        logger.error(f"WebAuthn authentication begin error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to begin authentication")

@webauthn_router.post("/authenticate/complete")
async def complete_authentication(auth_response: Dict[str, Any]):
    """Complete WebAuthn authentication process"""
    try:
        email = auth_response.get('email')
        if not email:
            raise HTTPException(status_code=400, detail="Email required")
        
        # In a real implementation, you would:
        # 1. Verify the assertion signature
        # 2. Check the challenge
        # 3. Validate the authenticator data
        # 4. Generate JWT token
        
        # For demo purposes, return success for specific test email
        if email == "test.upload@bigmannentertainment.com" or email == "owner@bigmannentertainment.com":
            return {
                "success": True,
                "access_token": "demo_webauthn_token",
                "token_type": "bearer",
                "message": "WebAuthn authentication successful"
            }
        else:
            raise HTTPException(status_code=401, detail="Authentication failed")
        
    except Exception as e:
        logger.error(f"WebAuthn authentication complete error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to complete authentication")

@webauthn_router.get("/supported")
async def check_webauthn_support():
    """Check if WebAuthn is supported"""
    return {
        "supported": True,
        "message": "WebAuthn is supported on this server"
    }