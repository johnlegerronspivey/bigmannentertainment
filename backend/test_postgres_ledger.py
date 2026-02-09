import asyncio
import logging
import os
from dotenv import load_dotenv

load_dotenv("/app/backend/.env")

from qldb_service import initialize_qldb_service
from qldb_models import CreateDisputeRequest, DisputeType, Priority

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_qldb_service():
    print("--- Testing Standard PostgreSQL Dispute Service ---")
    
    # 1. Initialize Service
    print("Initializing service...")
    try:
        service = initialize_qldb_service()
        await service.manager.initialize() 
    except Exception as e:
        print(f"❌ Initialization Failed: {e}")
        return

    # 2. Check Health
    print("Checking health...")
    health = await service.check_health()
    print(f"Health Status: {health}")
    
    if health['status'] != 'healthy':
        print("Health check failed. Aborting.")
        return

    # 3. Create Dispute
    print("Creating Dispute...")
    req = CreateDisputeRequest(
        type=DisputeType.ROYALTY_DISPUTE,
        priority=Priority.HIGH,
        title="Standard SQL Dispute",
        description="Testing standard PostgreSQL storage without ledger features",
        amount_disputed=750.0,
        currency="USD",
        claimant_name="SQL User",
        claimant_email="sql@example.com"
    )
    
    try:
        dispute = await service.create_dispute(req)
        print(f"✅ Dispute Created: {dispute.dispute_number} (ID: {dispute.id})")
    except Exception as e:
        print(f"❌ Failed to create dispute: {e}")
        return

    # 4. Fetch Dispute
    print("Fetching Dispute...")
    fetched = await service.get_dispute(dispute.id)
    if fetched:
        print(f"✅ Fetched Dispute: {fetched.title}")
    else:
        print("❌ Failed to fetch dispute")

if __name__ == "__main__":
    asyncio.run(test_qldb_service())
