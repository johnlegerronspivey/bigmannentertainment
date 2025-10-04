#!/usr/bin/env python3
"""
Verify Big Mann Entertainment label update
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
import json

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'bigmann_entertainment_production')

async def verify_label():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        label = await db.uln_labels.find_one({
            "metadata_profile.name": {"$regex": "Big Mann Entertainment", "$options": "i"}
        })
        
        if label:
            print("=" * 60)
            print("BIG MANN ENTERTAINMENT LABEL DETAILS")
            print("=" * 60)
            print(f"Name: {label['metadata_profile']['name']}")
            print(f"Legal Name: {label['metadata_profile'].get('legal_name', 'N/A')}")
            print(f"Label Type: {label['label_type']} ⭐")
            print(f"Integration Type: {label['integration_type']}")
            print(f"Global ID: {label['global_id']['id']}")
            print(f"Status: {label.get('status', 'N/A')}")
            print(f"Headquarters: {label['metadata_profile'].get('headquarters', 'N/A')}")
            print(f"Jurisdiction: {label['metadata_profile'].get('jurisdiction', 'N/A')}")
            print(f"Genres: {', '.join(label['metadata_profile'].get('genre_specialization', []))}")
            
            # Check for owner
            entities = label.get('associated_entities', [])
            owner = next((e for e in entities if e.get('entity_type') == 'owner' or e.get('role') == 'Owner'), None)
            if owner:
                print(f"Owner: {owner.get('name', 'N/A')}")
            
            print("=" * 60)
            
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(verify_label())
