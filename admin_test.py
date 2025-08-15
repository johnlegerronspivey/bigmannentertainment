#!/usr/bin/env python3
"""
Admin functionality test for Big Mann Entertainment
"""

import requests
import json
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import os
from dotenv import load_dotenv
from pathlib import Path

# Configuration
BASE_URL = "https://mediaempire-auth.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@bigmannentertainment.com"
ADMIN_PASSWORD = "AdminBigMann2025!"

async def create_admin_user():
    """Create an admin user in the database"""
    ROOT_DIR = Path('/app/backend')
    load_dotenv(ROOT_DIR / '.env')
    
    client = AsyncIOMotorClient(os.environ['MONGO_URL'])
    db = client[os.environ['DB_NAME']]
    
    # Check if admin already exists
    existing_admin = await db.users.find_one({"email": ADMIN_EMAIL})
    if existing_admin:
        print("Admin user already exists")
        client.close()
        return
    
    # Create admin user directly in database
    from passlib.context import CryptContext
    import uuid
    from datetime import datetime
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_password = pwd_context.hash(ADMIN_PASSWORD)
    
    admin_user = {
        "id": str(uuid.uuid4()),
        "email": ADMIN_EMAIL,
        "full_name": "Admin User",
        "business_name": "Big Mann Entertainment",
        "is_active": True,
        "is_admin": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    await db.users.insert_one(admin_user)
    await db.user_credentials.insert_one({
        "user_id": admin_user["id"],
        "email": ADMIN_EMAIL,
        "hashed_password": hashed_password
    })
    
    print("Admin user created successfully")
    client.close()

def test_admin_analytics():
    """Test admin analytics access"""
    # Login as admin
    login_data = {
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"❌ Admin login failed: {response.status_code}")
        return False
    
    data = response.json()
    admin_token = data['access_token']
    
    # Test analytics dashboard
    headers = {'Authorization': f'Bearer {admin_token}'}
    response = requests.get(f"{BASE_URL}/analytics/dashboard", headers=headers)
    
    if response.status_code == 200:
        analytics_data = response.json()
        print("✅ Admin analytics access successful")
        print(f"   Stats: {analytics_data.get('stats', {})}")
        return True
    else:
        print(f"❌ Admin analytics failed: {response.status_code}")
        return False

if __name__ == "__main__":
    print("Creating admin user...")
    asyncio.run(create_admin_user())
    
    print("Testing admin analytics...")
    success = test_admin_analytics()
    
    if success:
        print("✅ Admin functionality test passed")
    else:
        print("❌ Admin functionality test failed")