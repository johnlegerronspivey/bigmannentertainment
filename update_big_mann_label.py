"""
Script to update Big Mann Entertainment label in ULN
Updates genre and integration type for label ID: 1758F4E9
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

# Database connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'bigmann_entertainment_production')

async def update_big_mann_label():
    """Update Big Mann Entertainment label with new genre and integration"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    uln_labels = db.uln_labels
    
    # The global_id structure in the database
    label_id = "BM-LBL-1758F4E9"
    
    # First, let's find the label
    label = await uln_labels.find_one({"global_id.id": label_id})
    
    if not label:
        print(f"❌ Label with ID {label_id} not found")
        # Try to find by name
        label = await uln_labels.find_one({"metadata_profile.name": "Big Mann Entertainment"})
        if label:
            print(f"✅ Found label by name. ID: {label['global_id']['id']}")
        else:
            print("❌ Big Mann Entertainment label not found in database")
            # List all labels to help debug
            all_labels = await uln_labels.find({}).to_list(length=100)
            print(f"\nFound {len(all_labels)} labels in database:")
            for l in all_labels[:10]:
                print(f"  - {l.get('metadata_profile', {}).get('name', 'Unknown')} (ID: {l.get('global_id', {}).get('id', 'Unknown')})")
            client.close()
            return
    
    current_id = label['global_id']['id']
    current_genres = label.get('metadata_profile', {}).get('genre_specialization', [])
    current_integration = label.get('integration_type', 'Unknown')
    
    print(f"\n📋 Current Label Information:")
    print(f"   Name: {label.get('metadata_profile', {}).get('name', 'Unknown')}")
    print(f"   ID: {current_id}")
    print(f"   Current Genres: {current_genres}")
    print(f"   Current Integration: {current_integration}")
    
    # Update the label
    update_data = {
        "$set": {
            "metadata_profile.genre_specialization": ["Hip-Hop", "R&B", "Rap"],
            "integration_type": "full_integration",
            "updated_at": "2025-01-30T00:00:00"
        }
    }
    
    result = await uln_labels.update_one(
        {"global_id.id": current_id},
        update_data
    )
    
    if result.modified_count > 0:
        print(f"\n✅ Successfully updated Big Mann Entertainment label!")
        print(f"   ✓ Genre updated to: Hip-Hop, R&B, Rap")
        print(f"   ✓ Integration updated to: Full Integration")
        
        # Verify the update
        updated_label = await uln_labels.find_one({"global_id.id": current_id})
        new_genres = updated_label.get('metadata_profile', {}).get('genre_specialization', [])
        new_integration = updated_label.get('integration_type', 'Unknown')
        
        print(f"\n📋 Verified Updated Information:")
        print(f"   New Genres: {new_genres}")
        print(f"   New Integration: {new_integration}")
    else:
        print(f"\n⚠️  No changes made. Label may already have these values.")
    
    client.close()

if __name__ == "__main__":
    print("🚀 Starting Big Mann Entertainment Label Update...")
    print("=" * 60)
    asyncio.run(update_big_mann_label())
    print("=" * 60)
    print("✅ Update process complete!")
