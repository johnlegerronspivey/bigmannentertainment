"""
Script to update Big Mann Entertainment legal name - remove LLC
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

# Database connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'bigmann_entertainment_production')

async def update_legal_name():
    """Update Big Mann Entertainment legal name to remove LLC"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    uln_labels = db.uln_labels
    
    label_id = "BM-LBL-1758F4E9"
    
    # Find the label
    label = await uln_labels.find_one({"global_id.id": label_id})
    
    if not label:
        print(f"❌ Label with ID {label_id} not found")
        client.close()
        return
    
    current_legal_name = label.get('metadata_profile', {}).get('legal_name', 'N/A')
    
    print(f"\n📋 Current Legal Name: {current_legal_name}")
    
    # Update the legal name
    update_data = {
        "$set": {
            "metadata_profile.legal_name": "Big Mann Entertainment",
            "updated_at": "2025-01-30T01:00:00"
        }
    }
    
    result = await uln_labels.update_one(
        {"global_id.id": label_id},
        update_data
    )
    
    if result.modified_count > 0:
        print(f"✅ Successfully updated legal name!")
        print(f"   Previous: {current_legal_name}")
        print(f"   Updated:  Big Mann Entertainment")
        
        # Verify the update
        updated_label = await uln_labels.find_one({"global_id.id": label_id})
        new_legal_name = updated_label.get('metadata_profile', {}).get('legal_name', 'N/A')
        
        print(f"\n📋 Verified: {new_legal_name}")
    else:
        print(f"\n⚠️  No changes made.")
    
    client.close()

if __name__ == "__main__":
    print("🚀 Updating Big Mann Entertainment Legal Name...")
    print("=" * 60)
    asyncio.run(update_legal_name())
    print("=" * 60)
    print("✅ Update complete!")
