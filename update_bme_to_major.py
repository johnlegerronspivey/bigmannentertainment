#!/usr/bin/env python3
"""
Update Big Mann Entertainment to Major Label
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'bigmann_entertainment_production')

async def update_bme_to_major():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        # Find Big Mann Entertainment label
        label = await db.uln_labels.find_one({
            "metadata_profile.name": {"$regex": "Big Mann Entertainment", "$options": "i"}
        })
        
        if not label:
            print("❌ Big Mann Entertainment label not found")
            return
        
        print(f"✅ Found label: {label['metadata_profile']['name']}")
        print(f"   Current type: {label.get('label_type', 'N/A')}")
        print(f"   Global ID: {label['global_id']['id']}")
        
        # Update to major label
        result = await db.uln_labels.update_one(
            {"_id": label["_id"]},
            {
                "$set": {
                    "label_type": "major",
                    "updated_at": asyncio.get_event_loop().time()
                }
            }
        )
        
        if result.modified_count > 0:
            print(f"✅ Successfully updated Big Mann Entertainment to Major Label")
            
            # Verify the change
            updated_label = await db.uln_labels.find_one({"_id": label["_id"]})
            print(f"   New type: {updated_label['label_type']}")
        else:
            print(f"⚠️  No changes made (label might already be major)")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(update_bme_to_major())
