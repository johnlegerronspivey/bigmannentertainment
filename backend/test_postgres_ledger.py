import asyncio
import logging
import os
from dotenv import load_dotenv

# Force load env to ensure we get the right URL
load_dotenv("/app/backend/.env")

from qldb_service import initialize_qldb_service
from qldb_models import CreateDisputeRequest, DisputeType, Priority

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_qldb_service():
    print("--- Testing Emergent Ledger on AWS Aurora ---")
    
    # 1. Initialize Service
    print("Initializing service...")
    service = initialize_qldb_service()
    
    # Wait a bit for schema init task
    await asyncio.sleep(2)
    
    # 2. Check Health (Connectivity)
    print("Checking health...")
    health = await service.check_health()
    print(f"Health Status: {health}")
    
    if health['status'] != 'healthy':
        print("Health check failed. Aborting.")
        return

    # 3. Create Dispute
    print("Creating Dispute...")
    req = CreateDisputeRequest(
        type=DisputeType.COPYRIGHT,
        priority=Priority.HIGH,
        title="Test Dispute from Script",
        description="Testing the new Postgres Ledger driver",
        amount_disputed=1000.0,
        currency="USD",
        claimant_name="Test User",
        claimant_email="test@example.com"
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

    # 5. Verify Chain
    print("Verifying Chain Integrity...")
    integrity = await service.verify_chain_integrity()
    print(f"Integrity Report: {integrity}")

if __name__ == "__main__":
    asyncio.run(test_qldb_service())
