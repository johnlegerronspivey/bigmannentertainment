"""
Initialize Profile System
Run this to set up PostgreSQL tables and seed data
"""
import asyncio
import os
from pg_database import init_db, Base, async_engine
from profile_models import *
from sqlalchemy.ext.asyncio import AsyncSession
from gs1_profile_service import gs1_service

async def initialize_profile_system():
    """Initialize the profile system"""
    print("🚀 Initializing Creator Profile System...")
    
    # Create all tables
    print("📊 Creating PostgreSQL tables...")
    await init_db()
    
    print("✅ Profile system initialized successfully!")
    print("")
    print("📝 Next steps:")
    print("1. Set POSTGRES_URL in .env file")
    print("2. Restart backend: sudo supervisorctl restart backend")
    print("3. Access profiles at: /api/profile/{username}")
    print("")
    print("🔧 Configuration:")
    print(f"   Company Prefix: {gs1_service.company_prefix}")
    print(f"   GLN Base: {gs1_service.gln_base}")
    print(f"   ISRC Prefix: {gs1_service.isrc_prefix}")

if __name__ == "__main__":
    asyncio.run(initialize_profile_system())
