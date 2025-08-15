from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Optional
import motor.motor_asyncio
import os
from datetime import datetime
import jwt

# Database connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = client.big_mann_entertainment

# JWT Configuration
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
ALGORITHM = "HS256"

# Simple authentication dependency
async def get_current_user(request: Request):
    """Simple authentication check"""
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
        
        token = auth_header.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Get user from database
        user = await db.users.find_one({"id": user_id})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=401, detail="Authentication failed")

async def get_admin_user(request: Request):
    """Admin authentication check"""
    user = await get_current_user(request)
    if not user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return user

# Database connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = client.big_mann_entertainment

# Create router
router = APIRouter(prefix="/api/industry", tags=["IPI Numbers"])

# Big Mann Entertainment IPI Numbers
BIG_MANN_IPI_NUMBERS = [
    {
        "ipi_number": "813048171",
        "entity_name": "Big Mann Entertainment",
        "entity_type": "company",
        "role": "publisher",
        "status": "active",
        "territory": "US",
        "contact_info": {
            "address": "1314 Lincoln Heights Street, Alexander City, AL 35010",
            "phone": "334-669-8638",
            "email": "info@bigmannentertainment.com"
        },
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    },
    {
        "ipi_number": "578413032",
        "entity_name": "John LeGerron Spivey",
        "entity_type": "individual",
        "role": "songwriter",
        "status": "active",
        "territory": "US",
        "contact_info": {
            "address": "1314 Lincoln Heights Street, Alexander City, AL 35010",
            "phone": "334-669-8638",
            "email": "john.spivey@bigmannentertainment.com"
        },
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
]

@router.post("/initialize")
async def initialize_industry_connections():
    """Initialize all industry partner connections including IPI numbers"""
    try:
        # Initialize IPI numbers
        for ipi_data in BIG_MANN_IPI_NUMBERS:
            existing = await db.ipi_numbers.find_one({"ipi_number": ipi_data["ipi_number"]})
            if not existing:
                await db.ipi_numbers.insert_one(ipi_data)
        
        return {
            "success": True,
            "message": f"Successfully initialized industry partners including IPI numbers",
            "total_partners": len(BIG_MANN_IPI_NUMBERS),
            "categories": ["ipi_numbers"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize industry connections: {str(e)}")

@router.get("/ipi")
async def get_ipi_numbers(
    entity_type: Optional[str] = None,
    role: Optional[str] = None
):
    """Get all IPI numbers with optional filtering"""
    try:
        query = {}
        if entity_type:
            query["entity_type"] = entity_type
        if role:
            query["role"] = role
        
        cursor = db.ipi_numbers.find(query)
        ipi_numbers = await cursor.to_list(100)
        
        # Remove MongoDB _id field for JSON serialization
        for ipi in ipi_numbers:
            if "_id" in ipi:
                del ipi["_id"]
        
        return {
            "ipi_numbers": ipi_numbers,
            "total_count": len(ipi_numbers),
            "filters_applied": {
                "entity_type": entity_type,
                "role": role
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve IPI numbers: {str(e)}")

@router.get("/ipi/{ipi_number}")
async def get_ipi_number_details(ipi_number: str):
    """Get detailed information about a specific IPI number"""
    try:
        ipi = await db.ipi_numbers.find_one({"ipi_number": ipi_number})
        if not ipi:
            raise HTTPException(status_code=404, detail="IPI number not found")
        
        # Remove MongoDB _id field for JSON serialization
        if "_id" in ipi:
            del ipi["_id"]
        
        return {
            "ipi_number": ipi,
            "message": f"IPI number {ipi_number} details retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve IPI number details: {str(e)}")

@router.get("/ipi/dashboard")
async def get_ipi_dashboard():
    """Get comprehensive IPI dashboard data"""
    try:
        # Get all IPI numbers
        cursor = db.ipi_numbers.find({})
        all_ipis = await cursor.to_list(100)
        
        # Calculate statistics
        total_ipi_numbers = len(all_ipis)
        by_entity_type = {}
        by_role = {}
        
        for ipi in all_ipis:
            entity_type = ipi.get("entity_type", "unknown")
            role = ipi.get("role", "unknown")
            
            by_entity_type[entity_type] = by_entity_type.get(entity_type, 0) + 1
            by_role[role] = by_role.get(role, 0) + 1
        
        # Big Mann Entertainment specific data
        big_mann_data = {
            "company_ipi": "813048171",
            "individual_ipi": "578413032",
            "status": "active"
        }
        
        dashboard_data = {
            "total_ipi_numbers": total_ipi_numbers,
            "by_entity_type": by_entity_type,
            "by_role": by_role,
            "big_mann_entertainment": big_mann_data
        }
        
        return {
            "dashboard": dashboard_data,
            "last_updated": datetime.utcnow().isoformat(),
            "message": "IPI dashboard data retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve IPI dashboard data: {str(e)}")

@router.post("/ipi")
async def add_ipi_number(ipi_data: dict):
    """Add a new IPI number"""
    try:
        # Check if IPI number already exists
        existing = await db.ipi_numbers.find_one({"ipi_number": ipi_data["ipi_number"]})
        if existing:
            raise HTTPException(status_code=400, detail="IPI number already exists")
        
        # Add timestamps
        ipi_data["created_at"] = datetime.utcnow()
        ipi_data["updated_at"] = datetime.utcnow()
        
        await db.ipi_numbers.insert_one(ipi_data)
        
        return {
            "success": True,
            "message": f"Successfully added IPI number {ipi_data['ipi_number']} for {ipi_data['entity_name']}",
            "ipi_number": ipi_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add IPI number: {str(e)}")