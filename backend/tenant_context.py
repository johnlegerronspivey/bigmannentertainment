"""
Tenant Context — FastAPI dependency for extracting tenant_id from the authenticated user.
Provides both required and optional variants.
"""

from typing import Optional
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

import jwt
from config.database import db
from config.settings import settings

_optional_security = HTTPBearer(auto_error=False)


async def get_optional_tenant_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_optional_security),
) -> Optional[str]:
    """Extract tenant_id from bearer token if present, else return None."""
    if not credentials:
        return None
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        user_id = payload.get("sub")
        if not user_id:
            return None
        user = await db.users.find_one({"id": user_id}, {"_id": 0, "tenant_id": 1})
        if user:
            return user.get("tenant_id") or None
    except Exception:
        pass
    return None


async def get_required_tenant_id(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
) -> str:
    """Extract tenant_id from bearer token; raises 401/403 if missing."""
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = await db.users.find_one({"id": user_id}, {"_id": 0, "tenant_id": 1})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    tenant_id = user.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=403, detail="User not assigned to a tenant")
    return tenant_id
