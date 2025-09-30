"""
Script to update Big Mann Entertainment label owner to John LeGerron Spivey
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
import uuid

# Database connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'bigmann_entertainment_production')

async def update_label_owner():
    """Update Big Mann Entertainment label to set John LeGerron Spivey as owner"""
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
    
    print(f"\n📋 Current Label Information:")
    print(f"   Name: {label.get('metadata_profile', {}).get('name', 'Unknown')}")
    print(f"   ID: {label['global_id']['id']}")
    
    current_entities = label.get('associated_entities', [])
    print(f"\n👥 Current Associated Entities: {len(current_entities)}")
    for entity in current_entities:
        print(f"   - {entity.get('name', 'Unknown')} ({entity.get('role', 'Unknown')})")
    
    # Create John LeGerron Spivey as the primary owner/CEO
    john_spivey_entity = {
        "entity_id": f"ENTITY-{str(uuid.uuid4())[:8].upper()}",
        "entity_type": "admin",
        "name": "John LeGerron Spivey",
        "role": "CEO & Founder",
        "permissions": [
            "full_access",
            "content_management",
            "financial_management",
            "contract_signing",
            "dao_voting",
            "artist_management"
        ],
        "royalty_share": 1.0,  # 100% ownership
        "jurisdiction": "US",
        "contact_info": {
            "location": "Alexander City, AL",
            "business_entity": "Big Mann Entertainment"
        },
        "active": True,
        "created_at": "2025-01-30T00:00:00"
    }
    
    # Also update metadata profile to include legal owner information
    metadata_update = {
        "legal_name": "Big Mann Entertainment LLC",
        "headquarters": "Alexander City, AL",
        "contact_information": {
            "business_owner": "John LeGerron Spivey",
            "location": "Alexander City, AL",
            "business_email": "contact@bigmannentertainment.com",
            "phone": "+1-555-BME-MUSIC"
        }
    }
    
    # Update the label
    update_data = {
        "$set": {
            "associated_entities": [john_spivey_entity],
            "metadata_profile.legal_name": metadata_update["legal_name"],
            "metadata_profile.headquarters": metadata_update["headquarters"],
            "metadata_profile.contact_information": metadata_update["contact_information"],
            "updated_at": "2025-01-30T00:00:00"
        }
    }
    
    result = await uln_labels.update_one(
        {"global_id.id": label_id},
        update_data
    )
    
    if result.modified_count > 0:
        print(f"\n✅ Successfully updated Big Mann Entertainment label owner!")
        print(f"   ✓ Owner: John LeGerron Spivey")
        print(f"   ✓ Role: CEO & Founder")
        print(f"   ✓ Ownership: 100%")
        print(f"   ✓ Legal Name: {metadata_update['legal_name']}")
        
        # Verify the update
        updated_label = await uln_labels.find_one({"global_id.id": label_id})
        new_entities = updated_label.get('associated_entities', [])
        
        print(f"\n📋 Verified Updated Information:")
        print(f"   Associated Entities: {len(new_entities)}")
        for entity in new_entities:
            print(f"   - {entity.get('name', 'Unknown')} ({entity.get('role', 'Unknown')})")
            print(f"     Permissions: {', '.join(entity.get('permissions', [])[:3])}...")
            print(f"     Ownership: {entity.get('royalty_share', 0) * 100}%")
        
        contact_info = updated_label.get('metadata_profile', {}).get('contact_information', {})
        print(f"\n   Business Owner: {contact_info.get('business_owner', 'N/A')}")
        print(f"   Location: {contact_info.get('location', 'N/A')}")
    else:
        print(f"\n⚠️  No changes made. Label may already have these values.")
    
    client.close()

if __name__ == "__main__":
    print("🚀 Updating Big Mann Entertainment Label Owner...")
    print("=" * 70)
    asyncio.run(update_label_owner())
    print("=" * 70)
    print("✅ Owner update process complete!")
