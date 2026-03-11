#!/usr/bin/env python3
"""
Test ULN Service Directly
=========================

Test the ULN service methods directly to debug the directory issue
"""

import asyncio
import os
import sys
sys.path.append('/app/backend')

from uln_service import ULNService

async def test_uln_service():
    """Test ULN service methods directly"""
    print("🔍 TESTING ULN SERVICE DIRECTLY")
    print("=" * 50)
    
    service = ULNService()
    
    # Test 1: Check if labels exist in database
    print("📊 Checking labels in database...")
    try:
        label_count = await service.uln_labels.count_documents({})
        active_count = await service.uln_labels.count_documents({"status": "active"})
        print(f"   Total labels: {label_count}")
        print(f"   Active labels: {active_count}")
        
        # Get a sample label
        sample_label = await service.uln_labels.find_one({})
        if sample_label:
            sample_label.pop("_id", None)
            print(f"   Sample label: {sample_label.get('metadata_profile', {}).get('name', 'Unknown')}")
            print(f"   Sample status: {sample_label.get('status', 'Unknown')}")
            print(f"   Sample type: {sample_label.get('label_type', 'Unknown')}")
        else:
            print(f"   ❌ No labels found in database")
            return
    except Exception as e:
        print(f"   ❌ Database error: {str(e)}")
        return
    
    # Test 2: Test get_label_directory method
    print(f"\n📁 Testing get_label_directory method...")
    try:
        result = await service.get_label_directory()
        print(f"   Success: {result.get('success')}")
        
        if result.get('success'):
            labels = result.get('labels', [])
            label_hub_entries = result.get('label_hub_entries', [])
            total_labels = result.get('total_labels', 0)
            
            print(f"   Labels: {len(labels)}")
            print(f"   Label Hub Entries: {len(label_hub_entries)}")
            print(f"   Total Labels: {total_labels}")
            
            if labels:
                print(f"   Sample label from result:")
                sample = labels[0]
                print(f"      Name: {sample.get('name', 'Unknown')}")
                print(f"      Type: {sample.get('label_type', 'Unknown')}")
                print(f"      Global ID: {sample.get('global_id', 'Unknown')}")
        else:
            print(f"   ❌ Service returned success=false")
            print(f"   Error: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"   ❌ Service method error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Test get_label_by_id method
    print(f"\n🏷️ Testing get_label_by_id method...")
    try:
        # Get the first label's ID
        first_label = await service.uln_labels.find_one({})
        if first_label:
            global_id = first_label.get('global_id', {}).get('id')
            if global_id:
                label = await service.get_label_by_id(global_id)
                if label:
                    print(f"   ✅ Found label: {label.get('metadata_profile', {}).get('name', 'Unknown')}")
                else:
                    print(f"   ❌ Label not found by ID: {global_id}")
            else:
                print(f"   ❌ No global ID found in first label")
        else:
            print(f"   ❌ No labels to test with")
    except Exception as e:
        print(f"   ❌ get_label_by_id error: {str(e)}")
    
    # Test 4: Test dashboard stats
    print(f"\n📊 Testing get_uln_dashboard_stats method...")
    try:
        result = await service.get_uln_dashboard_stats()
        print(f"   Success: {result.get('success')}")
        
        if result.get('success'):
            stats = result.get('dashboard_stats', {})
            print(f"   Total Labels: {stats.get('total_labels', 0)}")
            print(f"   Major Labels: {stats.get('major_labels', 0)}")
            print(f"   Independent Labels: {stats.get('independent_labels', 0)}")
        else:
            print(f"   ❌ Dashboard stats failed: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"   ❌ Dashboard stats error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_uln_service())