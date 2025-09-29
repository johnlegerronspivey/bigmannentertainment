"""
ULN Authentication Module
========================

Provides authentication utilities for ULN endpoints without circular imports
"""

import os
import jwt
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from datetime import datetime

# Database connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'bigmann_entertainment_production') 
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# JWT Configuration
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
ALGORITHM = "HS256"

security = HTTPBearer()

class User:
    def __init__(self, **data):
        self.id = data.get('id')
        self.email = data.get('email')
        self.is_admin = data.get('is_admin', False)
        self.role = data.get('role', 'user')
        self.full_name = data.get('full_name', '')

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current authenticated user for ULN endpoints"""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    
    # Find user in database
    user = await db.users.find_one({"id": user_id})
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Remove MongoDB _id field to avoid serialization issues
    user.pop("_id", None)
    return User(**user)

async def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current admin user for ULN endpoints"""
    if not current_user.is_admin and current_user.role not in ["admin", "moderator", "super_admin"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user

# Export database instance
__all__ = ['get_current_user', 'get_current_admin_user', 'User', 'db']