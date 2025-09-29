"""
Migration Script: Convert Existing Labels to ULN System
======================================================

This script migrates existing record labels from the industry_models system
to the new Unified Label Network (ULN) system with enhanced features:
- Global Label IDs
- Smart contract bindings  
- Cross-label content sharing capabilities
- DAO governance integration
- Multi-jurisdiction compliance
"""

import asyncio
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from typing import Dict, Any, List
import uuid

# Add backend directory to path for imports
sys.path.append('/app/backend')

from uln_models import (
    ULNLabel, LabelType, IntegrationType, LabelMetadataProfile, 
    GlobalLabelID, TerritoryJurisdiction, AssociatedEntity
)
from uln_service import ULNService

# Database connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/bigmann')
client = AsyncIOMotorClient(MONGO_URL)
db = client.bigmann

class LabelMigrationService:
    """Service to migrate existing labels to ULN system"""
    
    def __init__(self):
        self.uln_service = ULNService()
        self.migration_stats = {
            "total_processed": 0,
            "successful_migrations": 0,
            "failed_migrations": 0,
            "skipped_existing": 0,
            "errors": []
        }
    
    async def migrate_all_labels(self):
        """Migrate all existing labels to ULN system"""
        print("🚀 Starting migration of existing labels to ULN system...")
        
        try:
            # Get existing record labels from industry partners
            existing_labels = await self._get_existing_labels()
            
            if not existing_labels:
                print("❌ No existing labels found to migrate")
                return self.migration_stats
            
            print(f"📊 Found {len(existing_labels)} labels to migrate")
            
            # Migrate each label
            for label_data in existing_labels:
                await self._migrate_single_label(label_data)
            
            # Print migration summary
            await self._print_migration_summary()
            
            return self.migration_stats
            
        except Exception as e:
            print(f"❌ Migration failed: {str(e)}")
            self.migration_stats["errors"].append(f"General migration error: {str(e)}")
            return self.migration_stats
    
    async def _get_existing_labels(self) -> List[Dict[str, Any]]:
        """Get existing labels from industry models"""
        try:
            # Try to import and get labels from industry service
            try:
                from industry_service import IndustryService
                industry_service = IndustryService()
                result = await industry_service.get_record_labels()
                
                if result.get("success"):
                    labels = []
                    
                    # Process major labels
                    for label in result.get("major_labels", []):
                        labels.append({
                            **label,
                            "label_type": "major",
                            "source": "industry_partners"
                        })
                    
                    # Process independent labels
                    for label in result.get("independent_labels", []):
                        labels.append({
                            **label,
                            "label_type": "independent", 
                            "source": "industry_partners"
                        })
                    
                    return labels
                
            except ImportError:
                print("⚠️ Industry service not available, using fallback data")
            
            # Fallback: get from industry_models directly
            fallback_labels = await self._get_labels_from_industry_models()
            if fallback_labels:
                return fallback_labels
                
            # Final fallback: use mock data
            return self._get_mock_labels()
            
        except Exception as e:
            print(f"⚠️ Error getting existing labels: {str(e)}")
            return []
    
    async def _get_labels_from_industry_models(self) -> List[Dict[str, Any]]:
        """Fallback method to get labels from industry_models.py"""
        try:
            from industry_models import ENTERTAINMENT_INDUSTRY_PARTNERS
            
            labels = []
            record_labels = ENTERTAINMENT_INDUSTRY_PARTNERS.get("record_labels", {})
            
            for label_id, label_data in record_labels.items():
                labels.append({
                    "id": label_id,
                    "name": label_data.get("name", label_id),
                    "label_type": label_data.get("label_type", "independent"),
                    "integration_type": label_data.get("integration_type", "distribution_only"),
                    "founded": label_data.get("founded"),
                    "headquarters": label_data.get("headquarters", "Unknown"),
                    "parent": label_data.get("parent"),
                    "genre_focus": label_data.get("genre_focus"),
                    "territories": label_data.get("territories", ["US"]),
                    "source": "industry_models"
                })
            
            return labels
            
        except ImportError:
            print("⚠️ Cannot import industry_models, using mock data")
            return self._get_mock_labels()
    
    def _get_mock_labels(self) -> List[Dict[str, Any]]:
        """Generate mock labels for testing migration"""
        return [
            {
                "id": "atlantic_records",
                "name": "Atlantic Records",
                "label_type": "major",
                "integration_type": "full_integration",
                "founded": "1947",
                "headquarters": "New York, NY, USA",
                "parent": "Warner Music Group",
                "territories": ["US", "UK", "EU"],
                "source": "mock_data"
            },
            {
                "id": "def_jam_recordings",
                "name": "Def Jam Recordings", 
                "label_type": "major",
                "integration_type": "full_integration",
                "founded": "1984",
                "headquarters": "New York, NY, USA",
                "parent": "Universal Music Group",
                "territories": ["US", "UK", "EU"],
                "source": "mock_data"
            },
            {
                "id": "indie_collective",
                "name": "Independent Artist Collective",
                "label_type": "independent",
                "integration_type": "api_partner",
                "founded": "2020",
                "headquarters": "Los Angeles, CA, USA",
                "genre_focus": "Alternative Rock",
                "territories": ["US", "CA"],
                "source": "mock_data"
            }
        ]
    
    async def _migrate_single_label(self, label_data: Dict[str, Any]):
        """Migrate a single label to ULN system"""
        try:
            self.migration_stats["total_processed"] += 1
            label_name = label_data.get("name", "Unknown Label")
            
            print(f"📝 Migrating: {label_name}")
            
            # Check if already migrated
            existing_uln_label = await db.uln_labels.find_one({
                "metadata_profile.name": label_name
            })
            
            if existing_uln_label:
                print(f"⏭️ Skipping {label_name} - already exists in ULN")
                self.migration_stats["skipped_existing"] += 1
                return
            
            # Create ULN label
            uln_label = await self._convert_to_uln_label(label_data)
            
            # Store in database using prepared data
            label_dict = uln_label.dict()
            label_dict = self.uln_service._prepare_for_mongo(label_dict)
            
            result = await db.uln_labels.insert_one(label_dict)
            
            if result.inserted_id:
                print(f"✅ Successfully migrated: {label_name} -> {uln_label.global_id.id}")
                self.migration_stats["successful_migrations"] += 1
                
                # Create audit trail entry
                await self.uln_service._create_audit_entry(
                    action_type="label_migrated",
                    actor_id="migration_system",
                    actor_type="system",
                    resource_type="label",
                    resource_id=uln_label.global_id.id,
                    action_description=f"Migrated existing label {label_name} to ULN system",
                    changes_made={
                        "source": label_data.get("source", "unknown"),
                        "migration_timestamp": datetime.utcnow().isoformat()
                    }
                )
            else:
                raise Exception("Failed to insert into database")
            
        except Exception as e:
            error_msg = f"Failed to migrate {label_data.get('name', 'Unknown')}: {str(e)}"
            print(f"❌ {error_msg}")
            self.migration_stats["failed_migrations"] += 1
            self.migration_stats["errors"].append(error_msg)
    
    async def _convert_to_uln_label(self, label_data: Dict[str, Any]) -> ULNLabel:
        """Convert existing label data to ULN format"""
        
        # Determine label type
        label_type = LabelType.MAJOR if label_data.get("label_type") == "major" else LabelType.INDEPENDENT
        
        # Determine integration type
        integration_mapping = {
            "full_integration": IntegrationType.FULL_INTEGRATION,
            "api_partner": IntegrationType.API_PARTNER,
            "distribution_only": IntegrationType.DISTRIBUTION_ONLY,
            "metadata_sync": IntegrationType.METADATA_SYNC,
            "content_sharing": IntegrationType.CONTENT_SHARING
        }
        integration_type = integration_mapping.get(
            label_data.get("integration_type", "distribution_only"),
            IntegrationType.DISTRIBUTION_ONLY
        )
        
        # Determine jurisdiction
        territories = label_data.get("territories", ["US"])
        primary_territory = territories[0] if territories else "US"
        
        jurisdiction_mapping = {
            "US": TerritoryJurisdiction.US,
            "UK": TerritoryJurisdiction.UK,
            "EU": TerritoryJurisdiction.EU,
            "CA": TerritoryJurisdiction.CA,
            "AU": TerritoryJurisdiction.AU,
            "JP": TerritoryJurisdiction.JP
        }
        jurisdiction = jurisdiction_mapping.get(primary_territory, TerritoryJurisdiction.US)
        
        # Create metadata profile
        metadata_profile = LabelMetadataProfile(
            name=label_data.get("name", "Unknown Label"),
            legal_name=label_data.get("legal_name"),
            jurisdiction=jurisdiction,
            tax_status="corporation",  # Default
            founded_date=self._parse_date(label_data.get("founded")),
            headquarters=label_data.get("headquarters", "Unknown"),
            contact_information={
                "migrated_from": label_data.get("source", "unknown"),
                "original_id": label_data.get("id", "unknown")
            },
            genre_specialization=[label_data.get("genre_focus")] if label_data.get("genre_focus") else [],
            territories_of_operation=territories,
            industry_affiliations=[label_data.get("parent")] if label_data.get("parent") else []
        )
        
        # Create associated entities (would be populated later with actual data)
        associated_entities = []
        if label_data.get("parent"):
            # Add parent company as associated entity
            associated_entities.append(AssociatedEntity(
                entity_id=str(uuid.uuid4()),
                entity_type="parent_company",
                name=label_data["parent"],
                role="parent",
                permissions=["governance", "financial_oversight"],
                royalty_share=0.0  # Parent company doesn't get direct royalty share
            ))
        
        # Create ULN label
        uln_label = ULNLabel(
            global_id=GlobalLabelID(),
            label_type=label_type,
            integration_type=integration_type,
            metadata_profile=metadata_profile,
            associated_entities=associated_entities,
            status="active",
            onboarding_completed=False,  # Will be completed during onboarding
            compliance_verified=False   # Will be verified separately
        )
        
        return uln_label
    
    def _parse_date(self, date_str: str) -> datetime.date:
        """Parse date string to date object"""
        if not date_str:
            return None
        
        try:
            # Try different date formats
            if len(date_str) == 4:  # Just year
                return datetime(int(date_str), 1, 1).date()
            elif "-" in date_str:
                return datetime.fromisoformat(date_str).date()
            else:
                return datetime(int(date_str), 1, 1).date()
        except (ValueError, TypeError):
            return None
    
    async def _print_migration_summary(self):
        """Print comprehensive migration summary"""
        stats = self.migration_stats
        
        print("\n" + "="*60)
        print("🎯 MIGRATION COMPLETE - SUMMARY REPORT")
        print("="*60)
        print(f"📊 Total Labels Processed: {stats['total_processed']}")
        print(f"✅ Successful Migrations: {stats['successful_migrations']}")
        print(f"⏭️ Skipped (Already Exist): {stats['skipped_existing']}")
        print(f"❌ Failed Migrations: {stats['failed_migrations']}")
        
        if stats['successful_migrations'] > 0:
            success_rate = (stats['successful_migrations'] / stats['total_processed']) * 100
            print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if stats['errors']:
            print("\n🚨 ERRORS ENCOUNTERED:")
            for error in stats['errors']:
                print(f"   • {error}")
        
        print("\n🎉 Migration process completed!")
        print("="*60)
    
    async def verify_migration(self):
        """Verify migration was successful"""
        print("\n🔍 Verifying migration...")
        
        try:
            # Count ULN labels
            uln_count = await db.uln_labels.count_documents({})
            major_count = await db.uln_labels.count_documents({"label_type": "major"})
            independent_count = await db.uln_labels.count_documents({"label_type": "independent"})
            
            print(f"📊 ULN Labels in Database: {uln_count}")
            print(f"   • Major Labels: {major_count}")
            print(f"   • Independent Labels: {independent_count}")
            
            # Check recent migrations
            recent_migrations = await db.uln_audit_trail.count_documents({
                "action_type": "label_migrated"
            })
            print(f"🔄 Migration Audit Entries: {recent_migrations}")
            
            # Sample a few labels to verify structure
            sample_labels = await db.uln_labels.find({}).limit(3).to_list(length=None)
            
            print(f"\n📋 Sample Migrated Labels:")
            for label in sample_labels:
                global_id = label.get("global_id", {}).get("id", "Unknown")
                name = label.get("metadata_profile", {}).get("name", "Unknown")
                label_type = label.get("label_type", "Unknown")
                print(f"   • {name} ({label_type}) - ID: {global_id}")
            
            return {
                "total_uln_labels": uln_count,
                "major_labels": major_count,
                "independent_labels": independent_count,
                "migration_audit_entries": recent_migrations
            }
            
        except Exception as e:
            print(f"❌ Verification failed: {str(e)}")
            return None

async def main():
    """Main migration function"""
    print("🌐 ULN Label Migration System")
    print("=" * 50)
    
    migration_service = LabelMigrationService()
    
    # Run migration
    migration_stats = await migration_service.migrate_all_labels()
    
    # Verify migration
    verification_results = await migration_service.verify_migration()
    
    # Print final status
    if migration_stats["successful_migrations"] > 0:
        print(f"\n🎉 SUCCESS: {migration_stats['successful_migrations']} labels migrated to ULN system")
        
        if verification_results:
            print("\n📊 ULN System Status:")
            print(f"   • Total Labels: {verification_results['total_uln_labels']}")
            print(f"   • Major Labels: {verification_results['major_labels']}")
            print(f"   • Independent Labels: {verification_results['independent_labels']}")
            print(f"   • Audit Trail Entries: {verification_results['migration_audit_entries']}")
        
        print("\n🚀 ULN system is ready for:")
        print("   • Cross-label content sharing")  
        print("   • Multi-label royalty distribution")
        print("   • DAO governance integration")
        print("   • Smart contract deployment")
        print("   • Blockchain integration")
        
    else:
        print("\n⚠️ No labels were successfully migrated")
        if migration_stats["errors"]:
            print("Please check the errors above and try again")
    
    # Close database connection
    client.close()

if __name__ == "__main__":
    asyncio.run(main())