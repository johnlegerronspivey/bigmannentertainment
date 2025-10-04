#!/usr/bin/env python3
"""
Update Big Mann Entertainment label details
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'bigmann_entertainment_production')

async def update_label():
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
        print(f"   Global ID: {label['global_id']['id']}")
        
        # Prepare update data
        update_data = {
            "metadata_profile.name": "Big Mann Entertainment",
            "metadata_profile.legal_name": "John LeGerron Spivey",
            "metadata_profile.genre_specialization": ["Hip-Hop", "R&B", "Rap"],
            "metadata_profile.headquarters": "1314 Lincoln Heights Street, Alexander City, Alabama, 35010",
            "metadata_profile.tax_status": "sole_proprietorship",
            "integration_type": "full_integration",
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Update the label
        result = await db.uln_labels.update_one(
            {"_id": label["_id"]},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            print(f"✅ Successfully updated Big Mann Entertainment label")
            print("\n📋 Updated fields:")
            print(f"   • Legal Name: John LeGerron Spivey")
            print(f"   • Genres: Hip-Hop, R&B, Rap")
            print(f"   • Integration: Full Integration")
            print(f"   • Headquarters: 1314 Lincoln Heights Street, Alexander City, Alabama, 35010")
            print(f"   • Tax Status: Sole Proprietorship")
        else:
            print(f"⚠️  No changes made")
        
        # Update owner in associated_entities
        entities = label.get('associated_entities', [])
        owner_found = False
        
        for i, entity in enumerate(entities):
            if entity.get('entity_type') == 'owner' or entity.get('role') == 'Owner':
                # Update existing owner
                await db.uln_labels.update_one(
                    {"_id": label["_id"]},
                    {"$set": {f"associated_entities.{i}.name": "John LeGerron Spivey"}}
                )
                print(f"   • Owner: John LeGerron Spivey (updated)")
                owner_found = True
                break
        
        if not owner_found:
            # Add new owner entity
            import uuid
            owner_entity = {
                "entity_id": str(uuid.uuid4()),
                "entity_type": "owner",
                "name": "John LeGerron Spivey",
                "role": "Owner",
                "permissions": ["full_access"],
                "royalty_share": 0.0,
                "active": True,
                "created_at": datetime.utcnow().isoformat()
            }
            await db.uln_labels.update_one(
                {"_id": label["_id"]},
                {"$push": {"associated_entities": owner_entity}}
            )
            print(f"   • Owner: John LeGerron Spivey (added)")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(update_label())
