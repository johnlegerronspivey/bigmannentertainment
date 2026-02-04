import asyncio
import sys
import os

# Add backend to path
sys.path.append('/app/backend')

from qldb_service import initialize_qldb_service
from qldb_models import CreateDisputeRequest, DisputeType, Priority

async def test_mock_qldb():
    print("Initializing QLDB Service (Mock Mode)...")
    # Force MOCK env just in case, though manager has it hardcoded
    os.environ['QLDB_LEDGER_NAME'] = 'test-ledger'
    
    service = initialize_qldb_service()
    
    # Check Health
    health = await service.check_health()
    print(f"Health Check: {health}")
    
    if health['status'] != 'healthy':
        print("❌ Health check failed")
        return

    # Create Dispute
    print("\nCreating Dispute...")
    req = CreateDisputeRequest(
        title="Test Dispute",
        description="This is a test dispute",
        amount_disputed=100.0,
        currency="USD",
        type=DisputeType.PAYMENT_DISPUTE,
        priority=Priority.HIGH,
        claimant_name="Test User",
        claimant_email="test@example.com",
        respondent_name="Respondent User",
        respondent_email="resp@example.com"
    )
    
    dispute = await service.create_dispute(req)
    print(f"✅ Dispute Created: {dispute.dispute_number}")
    
    # Get Dispute
    print(f"Fetching Dispute {dispute.dispute_number}...")
    fetched = await service.get_dispute(dispute.dispute_number)
    
    if fetched and fetched.title == "Test Dispute":
        print("✅ Dispute Fetched Successfully")
    else:
        print("❌ Failed to fetch dispute")

if __name__ == "__main__":
    asyncio.run(test_mock_qldb())
