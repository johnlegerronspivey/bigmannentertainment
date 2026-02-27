"""Authentication endpoints - register, login, password management."""
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
from models.core import User, UserSession, UserCreate, UserLogin, Token, TokenRefresh, ForgotPasswordRequest, ResetPasswordRequest

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

def calculate_upc_check_digit(upc_11_digits: str) -> str:
    """Calculate check digit for UPC code using the standard algorithm"""
    if len(upc_11_digits) != 11:
        raise ValueError("UPC must be 11 digits for check digit calculation")
    
    odd_sum = sum(int(upc_11_digits[i]) for i in range(0, 11, 2))  # Digits at positions 1, 3, 5, 7, 9, 11
    even_sum = sum(int(upc_11_digits[i]) for i in range(1, 11, 2))  # Digits at positions 2, 4, 6, 8, 10
    
    # Corrected UPC-A algorithm: (even_sum * 3) + odd_sum
    total = (even_sum * 3) + odd_sum
    check_digit = (10 - (total % 10)) % 10
    
    return str(check_digit)

# API Endpoints
@router.post("/auth/register", response_model=Token)
async def register_user(user_data: UserCreate, request: Request):
    # Validate email format
    import re
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, user_data.email):
        raise HTTPException(status_code=400, detail="Invalid email format")
    
    # Validate password complexity
    if len(user_data.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
    
    if not re.search(r'[A-Z]', user_data.password):
        raise HTTPException(status_code=400, detail="Password must contain at least one uppercase letter")
    
    if not re.search(r'[a-z]', user_data.password):
        raise HTTPException(status_code=400, detail="Password must contain at least one lowercase letter")
    
    if not re.search(r'\d', user_data.password):
        raise HTTPException(status_code=400, detail="Password must contain at least one number")
    
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Validate age (must be 18+)
    today = datetime.utcnow().date()
    birth_date = user_data.date_of_birth.date() if isinstance(user_data.date_of_birth, datetime) else user_data.date_of_birth
    age = today.year - birth_date.year
    if today < birth_date.replace(year=today.year):
        age -= 1
    
    if age < 18:
        raise HTTPException(status_code=400, detail="Must be 18 or older to register")
    
    # Hash password
    hashed_password = get_password_hash(user_data.password)
    
    # Create user
    user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        business_name=user_data.business_name,
        date_of_birth=user_data.date_of_birth,
        address_line1=user_data.address_line1,
        address_line2=user_data.address_line2,
        city=user_data.city,
        state_province=user_data.state_province,
        postal_code=user_data.postal_code,
        country=user_data.country,
        is_active=True,
        is_verified=False,
        role="user"
    )
    
    # Store user in database
    user_dict = user.dict()
    user_dict["password_hash"] = hashed_password
    
    await db.users.insert_one(user_dict)
    
    # Send welcome email
    try:
        await _get_email_service().send_welcome_email(user.email, user.full_name)
    except Exception as e:
        print(f"Failed to send welcome email: {str(e)}")
        # Don't fail registration if email fails
    
    # Log activity
    await log_activity(user.id, "register", "user", user.id, {"email": user.email}, request)
    
    # Create tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id, "email": user.email, "role": user.role},
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token()
    
    # Create session
    session = UserSession(
        user_id=user.id,
        session_token=access_token,
        refresh_token=refresh_token,
        expires_at=datetime.utcnow() + access_token_expires,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host
    )
    
    await db.user_sessions.insert_one(session.dict())
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user
    )

@router.post("/auth/login", response_model=Token)
async def login_user(login_data: UserLogin, request: Request):
    # Find user
    user_doc = await db.users.find_one({"email": login_data.email})
    if not user_doc:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Remove MongoDB _id field to prevent ObjectId serialization issues
    if "_id" in user_doc:
        del user_doc["_id"]
    
    user = User(**user_doc)
    
    # Check if account is locked
    if user.locked_until and user.locked_until > datetime.utcnow():
        raise HTTPException(status_code=423, detail="Account is temporarily locked due to too many failed attempts")
    
    # Verify password
    password_hash = user_doc.get("password_hash")
    if not password_hash:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not verify_password(login_data.password, password_hash):
        # Increment failed attempts
        failed_attempts = user.failed_login_attempts + 1
        locked_until = None
        
        if failed_attempts >= MAX_LOGIN_ATTEMPTS:
            locked_until = datetime.utcnow() + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
        
        await db.users.update_one(
            {"id": user.id},
            {
                "$set": {
                    "failed_login_attempts": failed_attempts,
                    "locked_until": locked_until
                }
            }
        )
        
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Check if account is active
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")
    
    # Reset failed attempts on successful login
    await db.users.update_one(
        {"id": user.id},
        {
            "$set": {
                "failed_login_attempts": 0,
                "locked_until": None,
                "last_login": datetime.utcnow(),
                "login_count": user.login_count + 1
            }
        }
    )
    
    # Log activity
    await log_activity(user.id, "login", "user", user.id, {"method": "password"}, request)
    
    # Create tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id, "email": user.email, "role": user.role},
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token()
    
    # Create session
    session = UserSession(
        user_id=user.id,
        session_token=access_token,
        refresh_token=refresh_token,
        expires_at=datetime.utcnow() + access_token_expires,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host
    )
    
    await db.user_sessions.insert_one(session.dict())
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user
    )

@router.get("/auth/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@router.get("/auth/profile")
async def get_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "business_name": current_user.business_name,
        "date_of_birth": current_user.date_of_birth,
        "address_line1": current_user.address_line1,
        "address_line2": current_user.address_line2,
        "city": current_user.city,
        "state_province": current_user.state_province,
        "postal_code": current_user.postal_code,
        "country": current_user.country,
        "is_active": current_user.is_active,
        "is_admin": current_user.is_admin,
        "is_verified": current_user.is_verified,
        "role": current_user.role,
        "account_status": current_user.account_status,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at
    }

@router.post("/auth/refresh", response_model=Token)
async def refresh_token(refresh_data: TokenRefresh, request: Request):
    # Find session by refresh token
    session_doc = await db.user_sessions.find_one({
        "refresh_token": refresh_data.refresh_token,
        "is_active": True
    })
    
    if not session_doc:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    session = UserSession(**session_doc)
    
    # Check if session has expired
    if session.expires_at < datetime.utcnow():
        await db.user_sessions.update_one(
            {"id": session.id},
            {"$set": {"is_active": False}}
        )
        raise HTTPException(status_code=401, detail="Session has expired")
    
    # Get user
    user_doc = await db.users.find_one({"id": session.user_id})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Remove MongoDB _id field to prevent ObjectId serialization issues
    if "_id" in user_doc:
        del user_doc["_id"]
    
    user = User(**user_doc)
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")
    
    # Create new tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id, "email": user.email, "role": user.role},
        expires_delta=access_token_expires
    )
    new_refresh_token = create_refresh_token()
    
    # Update session
    await db.user_sessions.update_one(
        {"id": session.id},
        {
            "$set": {
                "session_token": access_token,
                "refresh_token": new_refresh_token,
                "expires_at": datetime.utcnow() + access_token_expires,
                "last_accessed": datetime.utcnow()
            }
        }
    )
    
    # Log activity
    await log_activity(user.id, "token_refresh", "user", user.id, {}, request)
    
    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user
    )

@router.post("/auth/logout")
async def logout_user(current_user: User = Depends(get_current_user), request: Request = None):
    # Deactivate all user sessions
    await db.user_sessions.update_many(
        {"user_id": current_user.id, "is_active": True},
        {"$set": {"is_active": False}}
    )
    
    # Log activity
    if request:
        await log_activity(current_user.id, "logout", "user", current_user.id, {}, request)
    
    return {"message": "Successfully logged out"}

@router.post("/auth/forgot-password")
async def forgot_password(request_data: ForgotPasswordRequest, request: Request):
    # Find user
    user_doc = await db.users.find_one({"email": request_data.email})
    if not user_doc:
        # Don't reveal if email exists or not
        return {"message": "If the email exists, a reset link has been sent"}
    
    # Remove MongoDB _id field to prevent ObjectId serialization issues
    if "_id" in user_doc:
        del user_doc["_id"]
    
    user = User(**user_doc)
    
    # Generate reset token
    reset_token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=PASSWORD_RESET_TOKEN_EXPIRE_HOURS)
    
    # Store reset token
    await db.users.update_one(
        {"id": user.id},
        {
            "$set": {
                "password_reset_token": reset_token,
                "password_reset_expires": expires_at
            }
        }
    )
    
    # Log activity
    await log_activity(user.id, "password_reset_requested", "user", user.id, {"email": user.email}, request)
    
    # Send password reset email
    try:
        email_sent = await _get_email_service().send_password_reset_email(user.email, reset_token, user.full_name)
        if email_sent:
            return {"message": "If the email exists, a reset link has been sent"}
        else:
            # Fallback to development mode if email fails
            reset_url = f"{os.environ.get('FRONTEND_URL', 'http://localhost:3000')}/reset-password?token={reset_token}"
            return {
                "message": "Email service unavailable. Please use the development reset link below.",
                "reset_token": reset_token,
                "reset_url": reset_url,
                "expires_in_hours": PASSWORD_RESET_TOKEN_EXPIRE_HOURS,
                "instructions": "Email service is currently unavailable. Use the reset URL below for testing purposes."
            }
    except Exception as e:
        print(f"Email service error: {str(e)}")
        # Fallback to development mode if email fails
        reset_url = f"{os.environ.get('FRONTEND_URL', 'http://localhost:3000')}/reset-password?token={reset_token}"
        return {
            "message": "Email service unavailable. Please use the development reset link below.",
            "reset_token": reset_token,
            "reset_url": reset_url,
            "expires_in_hours": PASSWORD_RESET_TOKEN_EXPIRE_HOURS,
            "instructions": "Email service is currently unavailable. Use the reset URL below for testing purposes."
        }

@router.post("/auth/reset-password")
async def reset_password(reset_data: ResetPasswordRequest, request: Request):
    # Find user by reset token
    user_doc = await db.users.find_one({
        "password_reset_token": reset_data.token,
        "password_reset_expires": {"$gt": datetime.utcnow()}
    })
    
    if not user_doc:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    
    # Remove MongoDB _id field to prevent ObjectId serialization issues
    if "_id" in user_doc:
        del user_doc["_id"]
    
    user = User(**user_doc)
    
    # Hash new password
    hashed_password = get_password_hash(reset_data.new_password)
    
    # Update password and clear reset token
    await db.users.update_one(
        {"id": user.id},
        {
            "$set": {
                "password_hash": hashed_password,
                "failed_login_attempts": 0,
                "locked_until": None
            },
            "$unset": {
                "password_reset_token": "",
                "password_reset_expires": ""
            }
        }
    )
    
    # Deactivate all sessions
    await db.user_sessions.update_many(
        {"user_id": user.id},
        {"$set": {"is_active": False}}
    )
    
    # Log activity
    await log_activity(user.id, "password_reset_completed", "user", user.id, {}, request)
    
    return {"message": "Password has been reset successfully"}


