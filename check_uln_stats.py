#!/usr/bin/env python3
"""
Check ULN Statistics
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'bigmann_entertainment_production')

async def check_stats():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        total_labels = await db.uln_labels.count_documents({})
        major_labels = await db.uln_labels.count_documents({"label_type": "major"})
        independent_labels = await db.uln_labels.count_documents({"label_type": "independent"})
        
        print("=" * 60)
        print("ULN LABEL STATISTICS")
        print("=" * 60)
        print(f"Total Labels: {total_labels}")
        print(f"Major Labels: {major_labels} 🏢")
        print(f"Independent Labels: {independent_labels} 🎵")
        print("=" * 60)
        
        # List all major labels
        major_label_docs = await db.uln_labels.find({"label_type": "major"}).to_list(length=None)
        print("\nMAJOR LABELS:")
        for label in major_label_docs:
            name = label['metadata_profile']['name']
            global_id = label['global_id']['id']
            print(f"  • {name} ({global_id})")
        
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(check_stats())
