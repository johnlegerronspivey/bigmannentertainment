#!/usr/bin/env python3
"""
Initialize the industry partners database with all record labels
"""
import asyncio
import sys
import os
sys.path.append('/app/backend')

from motor.motor_asyncio import AsyncIOMotorClient
from industry_models import ENTERTAINMENT_INDUSTRY_PARTNERS, RecordLabel
import logging

# Database connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/bigmann')

async def initialize_record_labels():
    """Initialize the database with all record labels"""
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(MONGO_URL)
        db = client.bigmann
        
        print("🔄 Connecting to database...")
        
        # Clear existing industry partners (optional - comment out to keep existing data)
        # await db.industry_partners.delete_many({"category": "record_label"})
        # print("🗑️ Cleared existing record labels")
        
        # Initialize counters
        major_count = 0
        independent_count = 0
        total_inserted = 0
        
        # Add record labels from ENTERTAINMENT_INDUSTRY_PARTNERS
        if "record_labels" in ENTERTAINMENT_INDUSTRY_PARTNERS:
            print("📊 Found record labels data in ENTERTAINMENT_INDUSTRY_PARTNERS")
            
            for tier, labels in ENTERTAINMENT_INDUSTRY_PARTNERS["record_labels"].items():
                print(f"🏷️ Processing {tier} labels: {len(labels)} labels")
                
                for label_data in labels:
                    # Check if label already exists
                    existing_label = await db.industry_partners.find_one({
                        "name": label_data["name"],
                        "category": "record_label"
                    })
                    
                    if not existing_label:
                        # Create RecordLabel object
                        label = RecordLabel(
                            category="record_label",
                            tier=tier,
                            **label_data
                        )
                        
                        # Insert into database
                        result = await db.industry_partners.insert_one(label.dict())
                        
                        if result.inserted_id:
                            print(f"✅ Added {tier} label: {label_data['name']}")
                            total_inserted += 1
                            if tier == "major":
                                major_count += 1
                            else:
                                independent_count += 1
                        else:
                            print(f"❌ Failed to add: {label_data['name']}")
                    else:
                        print(f"⏭️ Label already exists: {label_data['name']}")
        
        # Verify the data was inserted
        total_labels = await db.industry_partners.count_documents({"category": "record_label"})
        major_labels = await db.industry_partners.count_documents({
            "category": "record_label", 
            "tier": "major"
        })
        independent_labels = await db.industry_partners.count_documents({
            "category": "record_label", 
            "tier": "independent"
        })
        
        print("\n📊 DATABASE INITIALIZATION SUMMARY:")
        print(f"✅ Total labels inserted this run: {total_inserted}")
        print(f"📈 Major labels inserted: {major_count}")
        print(f"🎵 Independent labels inserted: {independent_count}")
        print(f"\n📊 TOTAL DATABASE CONTENTS:")
        print(f"🏢 Total record labels in database: {total_labels}")
        print(f"📈 Major labels in database: {major_labels}")
        print(f"🎵 Independent labels in database: {independent_labels}")
        
        # Show some sample labels
        print("\n🔍 SAMPLE MAJOR LABELS:")
        async for label in db.industry_partners.find({"category": "record_label", "tier": "major"}).limit(5):
            print(f"   • {label['name']} (Founded: {label.get('founded', 'Unknown')})")
        
        print("\n🔍 SAMPLE INDEPENDENT LABELS:")
        async for label in db.industry_partners.find({"category": "record_label", "tier": "independent"}).limit(5):
            print(f"   • {label['name']} (Genre: {label.get('genre_focus', 'Various')})")
        
        print(f"\n🎉 Record labels database initialization completed successfully!")
        print(f"🌐 All {total_labels} record labels are now connected to the labels dashboard!")
        
        # Close database connection
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Error initializing record labels: {str(e)}")
        return False

if __name__ == "__main__":
    print("🏢 Big Mann Entertainment - Record Labels Database Initialization")
    print("=" * 70)
    
    # Run the initialization
    success = asyncio.run(initialize_record_labels())
    
    if success:
        print("\n✅ SUCCESS: All major and independent record labels have been connected!")
        print("🔗 The labels dashboard is now fully operational with comprehensive label data.")
        sys.exit(0)
    else:
        print("\n❌ FAILED: Record labels initialization encountered errors.")
        sys.exit(1)