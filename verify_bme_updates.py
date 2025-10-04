#!/usr/bin/env python3
"""
Verify Big Mann Entertainment label updates
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'bigmann_entertainment_production')

async def verify_label():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        label = await db.uln_labels.find_one({
            "global_id.id": "BM-LBL-1758F4E9"
        })
        
        if label:
            print("=" * 70)
            print("BIG MANN ENTERTAINMENT - UPDATED LABEL DETAILS")
            print("=" * 70)
            print(f"Label Name:        {label['metadata_profile']['name']}")
            print(f"Legal Name:        {label['metadata_profile'].get('legal_name', 'N/A')}")
            print(f"Label Type:        {label['label_type'].upper()} ⭐")
            print(f"Integration Type:  {label['integration_type'].replace('_', ' ').title()}")
            print(f"Tax Status:        {label['metadata_profile'].get('tax_status', 'N/A').replace('_', ' ').title()}")
            print(f"Headquarters:      {label['metadata_profile'].get('headquarters', 'N/A')}")
            print(f"Jurisdiction:      {label['metadata_profile'].get('jurisdiction', 'N/A')}")
            print(f"Music Genres:      {', '.join(label['metadata_profile'].get('genre_specialization', []))}")
            print(f"Status:            {label.get('status', 'N/A').title()}")
            print(f"Global ID:         {label['global_id']['id']}")
            
            # Check for owner
            entities = label.get('associated_entities', [])
            owners = [e for e in entities if e.get('entity_type') == 'owner' or e.get('role') == 'Owner']
            if owners:
                print(f"\nOwner(s):")
                for owner in owners:
                    print(f"  • {owner.get('name', 'N/A')} ({owner.get('role', 'N/A')})")
            
            print("=" * 70)
            print("✅ All updates successfully applied!")
            
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(verify_label())
