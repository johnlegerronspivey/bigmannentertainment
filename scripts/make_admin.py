#!/usr/bin/env python3
"""
Make a user admin for testing purposes
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
import sys

async def make_user_admin(email: str):
    """Make a user admin"""
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'bigmann_entertainment_production')
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    try:
        # Find the user
        user = await db.users.find_one({"email": email})
        if not user:
            print(f"User {email} not found")
            return False
        
        # Update user to admin
        result = await db.users.update_one(
            {"email": email},
            {"$set": {"is_admin": True, "role": "admin"}}
        )
        
        if result.modified_count > 0:
            print(f"✅ User {email} is now an admin")
            return True
        else:
            print(f"❌ Failed to make {email} admin")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        await client.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python make_admin.py <email>")
        sys.exit(1)
    
    email = sys.argv[1]
    asyncio.run(make_user_admin(email))