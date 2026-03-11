"""
Content Removal Service
Core business logic for content takedown and removal management
"""

import os
import logging
import uuid
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timezone, timedelta
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import asyncio
import json
import hashlib
import hmac
from xml.etree import ElementTree as ET
from jinja2 import Template
import aiofiles
import aiohttp

from content_removal_models import (
    RemovalRequest, RemovalRequestCreate, RemovalRequestUpdate,
    RemovalStatus, RemovalUrgency, RemovalReason, PlatformRemovalStatus,
    PlatformRemovalResult, DDEXTakedownMessage, DisputeRequest,
    RemovalAnalytics, ComplianceReport, RemovalEvidence
)

logger = logging.getLogger(__name__)

class ContentRemovalService:
    """Service for managing content removal requests and operations"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.content_removal_requests
        self.disputes_collection = db.removal_disputes
        self.ddex_messages_collection = db.ddex_takedown_messages
        self.evidence_collection = db.removal_evidence
        self.analytics_collection = db.removal_analytics
        
        # Platform configurations from main server
        self.distribution_platforms = self._load_distribution_platforms()
        
        # DDEX configuration
        self.ddex_ftp_configs = self._load_ddex_configurations()
        
    def _load_distribution_platforms(self) -> Dict[str, Any]:
        """Load distribution platform configurations"""
        # This would be imported from the main server configuration
        # For now, we'll use a subset of key platforms
        return {
            "spotify": {
                "name": "Spotify",
                "type": "music_streaming",
                "takedown_method": "ddex_ern",
                "api_endpoint": "https://api.spotify.com/v1",
                "ddex_ftp_host": "ftp.spotify.com",
                "supports_takedown": True
            },
            "apple_music": {
                "name": "Apple Music", 
                "type": "music_streaming",
                "takedown_method": "ddex_ern",
                "api_endpoint": "https://api.music.apple.com/v1",
                "ddex_ftp_host": "ftp.apple.com",
                "supports_takedown": True
            },
            "youtube": {
                "name": "YouTube",
                "type": "social_media",
                "takedown_method": "api_call",
                "api_endpoint": "https://www.googleapis.com/youtube/v3",
                "supports_takedown": True
            },
            "instagram": {
                "name": "Instagram",
                "type": "social_media", 
                "takedown_method": "graph_api",
                "api_endpoint": "https://graph.facebook.com/v18.0",
                "supports_takedown": True
            },
            "tiktok": {
                "name": "TikTok",
                "type": "social_media",
                "takedown_method": "api_call",
                "api_endpoint": "https://open-api.tiktok.com",
                "supports_takedown": True
            }
        }
    
    def _load_ddex_configurations(self) -> Dict[str, Any]:
        """Load DDEX FTP and delivery configurations"""
        return {
            "default": {
                "message_sender": "BigMannEntertainment",
                "sender_party_id": "BME001",
                "sender_name": "Big Mann Entertainment",
                "sender_owner": "John LeGerron Spivey",
                "namespace": "http://ddex.net/xml/ern/382",
                "schema_version": "3.8.2"
            },
            "credentials": {
                # These would come from environment variables
                "username": os.getenv("DDEX_USERNAME", ""),
                "password": os.getenv("DDEX_PASSWORD", "")
            }
        }
    
    async def create_removal_request(
        self, 
        request_data: RemovalRequestCreate, 
        requester_id: str,
        requester_role: str = "creator"
    ) -> RemovalRequest:
        """Create a new content removal request"""
        
        # Validate content exists and requester has permission
        content_info = await self._validate_content_and_permissions(
            request_data.content_id, requester_id, requester_role
        )
        
        # Create removal request
        removal_request = RemovalRequest(
            content_id=request_data.content_id,
            content_title=content_info.get("title", "Unknown"),
            content_type=content_info.get("type", "unknown"),
            artist_name=content_info.get("artist_name"),
            release_id=content_info.get("release_id"),
            isrc_code=content_info.get("isrc_code"),
            upc_code=content_info.get("upc_code"),
            reason=request_data.reason,
            urgency=request_data.urgency,
            description=request_data.description,
            requested_by=requester_id,
            requester_role=requester_role,
            target_platforms=request_data.target_platforms,
            territory_scope=request_data.territory_scope,
            effective_date=request_data.effective_date or datetime.now(timezone.utc),
            legal_notice_ref=request_data.legal_notice_ref
        )
        
        # Auto-approve for admin/legal requests
        if requester_role in ["admin", "super_admin", "legal"]:
            removal_request.status = RemovalStatus.APPROVED
            removal_request.approved_by = requester_id
            removal_request.approved_at = datetime.now(timezone.utc)
        
        # Store in database
        await self.collection.insert_one(removal_request.dict())
        
        # Log activity
        await self._log_removal_activity(
            removal_request.id, 
            "request_created",
            f"Removal request created by {requester_role}",
            requester_id
        )
        
        # If auto-approved, start processing
        if removal_request.status == RemovalStatus.APPROVED:
            await self._start_removal_processing(removal_request)
        
        return removal_request
    
    async def approve_removal_request(
        self, 
        request_id: str, 
        approver_id: str,
        notes: Optional[str] = None
    ) -> RemovalRequest:
        """Approve a removal request (admin only)"""
        
        # Get and validate request
        request_doc = await self.collection.find_one({"id": request_id})
        if not request_doc:
            raise ValueError("Removal request not found")
        
        if request_doc["status"] != RemovalStatus.PENDING:
            raise ValueError("Request is not in pending status")
        
        # Update request
        update_data = {
            "status": RemovalStatus.APPROVED,
            "approved_by": approver_id,
            "approved_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        if notes:
            update_data["metadata.approval_notes"] = notes
        
        await self.collection.update_one(
            {"id": request_id}, 
            {"$set": update_data}
        )
        
        # Get updated request
        updated_doc = await self.collection.find_one({"id": request_id})
        removal_request = RemovalRequest(**updated_doc)
        
        # Log activity
        await self._log_removal_activity(
            request_id,
            "request_approved", 
            f"Request approved by admin: {notes or 'No notes'}",
            approver_id
        )
        
        # Start processing
        await self._start_removal_processing(removal_request)
        
        return removal_request
    
    async def reject_removal_request(
        self,
        request_id: str,
        rejector_id: str, 
        reason: str
    ) -> RemovalRequest:
        """Reject a removal request (admin only)"""
        
        # Update request
        await self.collection.update_one(
            {"id": request_id},
            {"$set": {
                "status": RemovalStatus.REJECTED,
                "rejection_reason": reason,
                "approved_by": rejector_id,
                "approved_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }}
        )
        
        # Get updated request
        updated_doc = await self.collection.find_one({"id": request_id})
        
        # Log activity
        await self._log_removal_activity(
            request_id,
            "request_rejected",
            f"Request rejected: {reason}",
            rejector_id
        )
        
        return RemovalRequest(**updated_doc)
    
    async def _start_removal_processing(self, removal_request: RemovalRequest):
        """Start the removal processing workflow"""
        
        # Update status to in progress
        await self.collection.update_one(
            {"id": removal_request.id},
            {"$set": {
                "status": RemovalStatus.IN_PROGRESS,
                "updated_at": datetime.now(timezone.utc)
            }}
        )
        
        # Suspend royalties if needed
        if removal_request.reason in [
            RemovalReason.RIGHTS_REVOKED,
            RemovalReason.LICENSING_EXPIRED,
            RemovalReason.COPYRIGHT_DISPUTE
        ]:
            await self._suspend_royalty_payments(removal_request)
        
        # Process platform removals
        platforms_to_process = removal_request.target_platforms
        if not platforms_to_process:
            # If no specific platforms, remove from all applicable platforms
            platforms_to_process = list(self.distribution_platforms.keys())
        
        # Create tasks for each platform
        platform_tasks = []
        for platform_id in platforms_to_process:
            if platform_id in self.distribution_platforms:
                task = self._process_platform_removal(removal_request, platform_id)
                platform_tasks.append(task)
        
        # Execute platform removals concurrently
        if platform_tasks:
            await asyncio.gather(*platform_tasks, return_exceptions=True)
        
        # Check if all removals completed
        await self._check_removal_completion(removal_request.id)
    
    async def _process_platform_removal(
        self,
        removal_request: RemovalRequest, 
        platform_id: str
    ):
        """Process removal for a specific platform"""
        
        platform_config = self.distribution_platforms[platform_id]
        result = PlatformRemovalResult(
            platform_id=platform_id,
            platform_name=platform_config["name"],
            status=PlatformRemovalStatus.PROCESSING
        )
        
        try:
            # Determine removal method
            takedown_method = platform_config.get("takedown_method", "manual")
            
            if takedown_method == "ddex_ern":
                success = await self._process_ddex_takedown(removal_request, platform_id)
            elif takedown_method == "api_call":
                success = await self._process_api_takedown(removal_request, platform_id)
            elif takedown_method == "graph_api":
                success = await self._process_graph_api_takedown(removal_request, platform_id)
            else:
                # Manual process - mark as pending manual action
                success = False
                result.error_message = "Manual removal required"
            
            if success:
                result.status = PlatformRemovalStatus.COMPLETED
                result.completed_at = datetime.now(timezone.utc)
            else:
                result.status = PlatformRemovalStatus.FAILED
                if not result.error_message:
                    result.error_message = "Removal processing failed"
                    
        except Exception as e:
            logger.error(f"Platform removal failed for {platform_id}: {str(e)}")
            result.status = PlatformRemovalStatus.FAILED
            result.error_message = str(e)
        
        # Update request with platform result
        await self.collection.update_one(
            {"id": removal_request.id},
            {
                "$push": {"platform_results": result.dict()},
                "$set": {"updated_at": datetime.now(timezone.utc)}
            }
        )
        
        # Log platform result
        await self._log_removal_activity(
            removal_request.id,
            f"platform_{result.status.value}",
            f"{platform_config['name']}: {result.status.value}",
            "system"
        )
    
    async def _process_ddex_takedown(
        self,
        removal_request: RemovalRequest,
        platform_id: str
    ) -> bool:
        """Process DDEX ERN takedown message"""
        
        try:
            # Generate DDEX XML
            xml_content = await self._generate_ddex_takedown_xml(
                removal_request, platform_id
            )
            
            # Create DDEX message record
            ddex_message = DDEXTakedownMessage(
                removal_request_id=removal_request.id,
                message_recipient=platform_id,
                release_id=removal_request.release_id or removal_request.content_id,
                takedown_reason=removal_request.reason.value,
                effective_date=removal_request.effective_date,
                territory_code=removal_request.territory_scope,
                xml_content=xml_content
            )
            
            # Store DDEX message
            await self.ddex_messages_collection.insert_one(ddex_message.dict())
            
            # Attempt delivery (FTP or API)
            delivery_success = await self._deliver_ddex_message(
                ddex_message, platform_id
            )
            
            # Update delivery status
            await self.ddex_messages_collection.update_one(
                {"id": ddex_message.id},
                {"$set": {
                    "delivery_status": "sent" if delivery_success else "failed",
                    "sent_at": datetime.now(timezone.utc) if delivery_success else None,
                    "delivery_attempts": 1,
                    "last_attempt_at": datetime.now(timezone.utc)
                }}
            )
            
            return delivery_success
            
        except Exception as e:
            logger.error(f"DDEX takedown failed for {platform_id}: {str(e)}")
            return False
    
    async def _generate_ddex_takedown_xml(
        self,
        removal_request: RemovalRequest,
        platform_id: str
    ) -> str:
        """Generate DDEX ERN takedown XML message"""
        
        # DDEX ERN Takedown XML template
        xml_template = """<?xml version="1.0" encoding="UTF-8"?>
<ern:NewReleaseMessage 
    xmlns:ern="http://ddex.net/xml/ern/382"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://ddex.net/xml/ern/382 http://ddex.net/xml/ern/382/ern-main.xsd"
    MessageSchemaVersionId="ern/382">
    
    <MessageHeader>
        <MessageThreadId>{{ message_thread_id }}</MessageThreadId>
        <MessageId>{{ message_id }}</MessageId>
        <MessageFileName>{{ message_filename }}</MessageFileName>
        <MessageSender>
            <PartyId>{{ sender_party_id }}</PartyId>
            <PartyName>
                <FullName>{{ sender_name }}</FullName>
            </PartyName>
        </MessageSender>
        <MessageRecipient>
            <PartyId>{{ recipient_party_id }}</PartyId>
            <PartyName>
                <FullName>{{ recipient_name }}</FullName>
            </PartyName>
        </MessageRecipient>
        <MessageCreatedDateTime>{{ created_datetime }}</MessageCreatedDateTime>
        <MessageAuditTrail>
            <AuditTrailEntry>{{ audit_trail_entry }}</AuditTrailEntry>
        </MessageAuditTrail>
    </MessageHeader>

    <UpdateIndicator>OriginalMessage</UpdateIndicator>
    
    <Deal>
        <DealReference>
            <DealId>{{ deal_id }}</DealId>
        </DealReference>
        <DealTerms>
            <TerritoryCode>{{ territory_code }}</TerritoryCode>
            <ValidityPeriod>
                <StartDate>{{ start_date }}</StartDate>
                <EndDate>{{ end_date }}</EndDate>
            </ValidityPeriod>
            <CarrierType>{{ carrier_type }}</CarrierType>
        </DealTerms>
    </Deal>
    
    <ReleaseTakedown>
        <ReleaseId>
            <ProprietaryId Namespace="BigMannEntertainment">{{ release_id }}</ProprietaryId>
            {% if isrc_code %}
            <ISRC>{{ isrc_code }}</ISRC>
            {% endif %}
            {% if upc_code %}
            <UPC>{{ upc_code }}</UPC>
            {% endif %}
        </ReleaseId>
        <ReleaseTitle>{{ release_title }}</ReleaseTitle>
        <TakedownReason>{{ takedown_reason }}</TakedownReason>
        <TakedownEffectiveDate>{{ effective_date }}</TakedownEffectiveDate>
        <TerritoryCode>{{ territory_code }}</TerritoryCode>
        {% if legal_notice_ref %}
        <LegalNoticeReference>{{ legal_notice_ref }}</LegalNoticeReference>
        {% endif %}
    </ReleaseTakedown>
    
</ern:NewReleaseMessage>"""
        
        # Prepare template variables
        now = datetime.now(timezone.utc)
        message_id = f"BME_TAKEDOWN_{removal_request.id}_{int(now.timestamp())}"
        
        template_vars = {
            "message_thread_id": f"BME_THREAD_{removal_request.id}",
            "message_id": message_id,
            "message_filename": f"{message_id}.xml",
            "sender_party_id": "BME001",
            "sender_name": "Big Mann Entertainment (John LeGerron Spivey)",
            "recipient_party_id": platform_id.upper(),
            "recipient_name": self.distribution_platforms[platform_id]["name"],
            "created_datetime": now.isoformat(),
            "audit_trail_entry": f"Removal requested by {removal_request.requester_role}: {removal_request.reason.value}",
            "deal_id": f"BME_DEAL_{removal_request.content_id}",
            "territory_code": removal_request.territory_scope,
            "start_date": "2020-01-01",  # Original deal start
            "end_date": removal_request.effective_date.strftime("%Y-%m-%d"),
            "carrier_type": "All",
            "release_id": removal_request.release_id or removal_request.content_id,
            "isrc_code": removal_request.isrc_code,
            "upc_code": removal_request.upc_code,
            "release_title": removal_request.content_title,
            "takedown_reason": removal_request.description,
            "effective_date": removal_request.effective_date.strftime("%Y-%m-%d"),
            "legal_notice_ref": removal_request.legal_notice_ref
        }
        
        # Render template
        template = Template(xml_template)
        xml_content = template.render(**template_vars)
        
        return xml_content
    
    async def _deliver_ddex_message(
        self,
        ddex_message: DDEXTakedownMessage,
        platform_id: str
    ) -> bool:
        """Deliver DDEX message to platform (FTP or API)"""
        
        try:
            platform_config = self.distribution_platforms[platform_id]
            
            if "ddex_ftp_host" in platform_config:
                # FTP delivery
                return await self._deliver_via_ftp(ddex_message, platform_config)
            else:
                # API delivery (mock for now)
                logger.info(f"DDEX message delivered via API to {platform_id}")
                return True
                
        except Exception as e:
            logger.error(f"DDEX delivery failed for {platform_id}: {str(e)}")
            return False
    
    async def _deliver_via_ftp(
        self,
        ddex_message: DDEXTakedownMessage,
        platform_config: Dict[str, Any]
    ) -> bool:
        """Deliver DDEX message via FTP"""
        
        # For production, this would use actual FTP client
        # For now, we'll simulate the delivery
        try:
            logger.info(f"Simulating FTP delivery to {platform_config['ddex_ftp_host']}")
            
            # Save XML to file
            filename = f"takedown_{ddex_message.id}.xml"
            file_path = f"/app/uploads/ddex_messages/{filename}"
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Write XML content
            async with aiofiles.open(file_path, 'w') as f:
                await f.write(ddex_message.xml_content)
            
            logger.info(f"DDEX takedown message saved to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"FTP delivery simulation failed: {str(e)}")
            return False
    
    async def _process_api_takedown(
        self,
        removal_request: RemovalRequest,
        platform_id: str
    ) -> bool:
        """Process API-based takedown (YouTube, TikTok, etc.)"""
        
        try:
            platform_config = self.distribution_platforms[platform_id]
            
            # Mock API call for takedown
            # In production, this would make actual API calls
            logger.info(f"Processing API takedown for {platform_id}")
            
            # Simulate API response
            await asyncio.sleep(1)  # Simulate API call delay
            
            # Mock success (would be based on actual API response)
            return True
            
        except Exception as e:
            logger.error(f"API takedown failed for {platform_id}: {str(e)}")
            return False
    
    async def _process_graph_api_takedown(
        self,
        removal_request: RemovalRequest,
        platform_id: str
    ) -> bool:
        """Process Facebook Graph API takedown (Instagram, Facebook)"""
        
        try:
            # Mock Graph API call
            logger.info(f"Processing Graph API takedown for {platform_id}")
            
            # Simulate API response
            await asyncio.sleep(1)
            
            return True
            
        except Exception as e:
            logger.error(f"Graph API takedown failed for {platform_id}: {str(e)}")
            return False
    
    async def _suspend_royalty_payments(self, removal_request: RemovalRequest):
        """Suspend royalty payments for removed content"""
        
        try:
            # Update removal request with royalty suspension
            await self.collection.update_one(
                {"id": removal_request.id},
                {"$set": {
                    "royalty_suspended": True,
                    "royalty_suspension_date": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                }}
            )
            
            # Log royalty suspension
            await self._log_removal_activity(
                removal_request.id,
                "royalty_suspended",
                "Royalty payments suspended due to content removal",
                "system"
            )
            
            logger.info(f"Royalty payments suspended for content {removal_request.content_id}")
            
        except Exception as e:
            logger.error(f"Failed to suspend royalty payments: {str(e)}")
    
    async def _check_removal_completion(self, request_id: str):
        """Check if all platform removals are complete"""
        
        # Get current request
        request_doc = await self.collection.find_one({"id": request_id})
        if not request_doc:
            return
        
        platform_results = request_doc.get("platform_results", [])
        
        # Check if all platforms are processed
        all_completed = True
        any_failed = False
        
        for result in platform_results:
            if result["status"] in [PlatformRemovalStatus.PENDING, PlatformRemovalStatus.PROCESSING]:
                all_completed = False
                break
            elif result["status"] == PlatformRemovalStatus.FAILED:
                any_failed = True
        
        if all_completed:
            # Determine final status
            final_status = RemovalStatus.FAILED if any_failed else RemovalStatus.COMPLETED
            
            # Update request
            await self.collection.update_one(
                {"id": request_id},
                {"$set": {
                    "status": final_status,
                    "completed_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                }}
            )
            
            # Log completion
            await self._log_removal_activity(
                request_id,
                "removal_completed",
                f"Removal process completed with status: {final_status.value}",
                "system"
            )
    
    async def _validate_content_and_permissions(
        self,
        content_id: str,
        requester_id: str, 
        requester_role: str
    ) -> Dict[str, Any]:
        """Validate content exists and requester has permission"""
        
        # Check if content exists (mock for now)
        # In production, this would query the actual content database
        content_info = {
            "id": content_id,
            "title": f"Content {content_id}",
            "type": "audio",
            "artist_name": "Test Artist",
            "owner_id": requester_id,  # Mock ownership
            "release_id": f"REL_{content_id}",
            "isrc_code": f"QZ9H8{content_id[-6:]}",
            "upc_code": f"860004340{content_id[-4:]}"
        }
        
        # Check permissions
        if requester_role in ["admin", "super_admin", "legal"]:
            # Admins can remove any content
            return content_info
        elif requester_role == "creator":
            # Creators can only remove their own content
            if content_info.get("owner_id") == requester_id:
                return content_info
            else:
                raise ValueError("Permission denied: You can only remove your own content")
        else:
            raise ValueError("Invalid requester role")
    
    async def _log_removal_activity(
        self,
        request_id: str,
        activity_type: str,
        description: str,
        actor_id: str
    ):
        """Log removal activity for audit trail"""
        
        activity_log = {
            "id": str(uuid.uuid4()),
            "request_id": request_id,
            "activity_type": activity_type,
            "description": description,
            "actor_id": actor_id,
            "timestamp": datetime.now(timezone.utc)
        }
        
        # Store in audit collection
        await self.db.removal_activity_logs.insert_one(activity_log)
    
    async def get_removal_requests(
        self,
        user_id: str,
        user_role: str,
        status: Optional[RemovalStatus] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[RemovalRequest]:
        """Get removal requests for user"""
        
        # Build query
        query = {}
        
        if user_role not in ["admin", "super_admin"]:
            # Non-admins can only see their own requests
            query["requested_by"] = user_id
        
        if status:
            query["status"] = status.value
        
        # Execute query
        cursor = self.collection.find(query).sort("created_at", -1).skip(offset).limit(limit)
        docs = await cursor.to_list(length=limit)
        
        return [RemovalRequest(**doc) for doc in docs]
    
    async def get_removal_request(self, request_id: str) -> Optional[RemovalRequest]:
        """Get specific removal request"""
        
        doc = await self.collection.find_one({"id": request_id})
        if doc:
            return RemovalRequest(**doc)
        return None
    
    async def generate_analytics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> RemovalAnalytics:
        """Generate removal analytics"""
        
        # Default to last 30 days
        if not end_date:
            end_date = datetime.now(timezone.utc)
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Build date filter
        date_filter = {
            "created_at": {
                "$gte": start_date,
                "$lte": end_date
            }
        }
        
        # Aggregate statistics
        pipeline = [
            {"$match": date_filter},
            {"$group": {
                "_id": None,
                "total_requests": {"$sum": 1},
                "pending_requests": {
                    "$sum": {"$cond": [{"$eq": ["$status", "pending"]}, 1, 0]}
                },
                "approved_requests": {
                    "$sum": {"$cond": [{"$eq": ["$status", "approved"]}, 1, 0]}
                },
                "completed_requests": {
                    "$sum": {"$cond": [{"$eq": ["$status", "completed"]}, 1, 0]}
                },
                "disputed_requests": {
                    "$sum": {"$cond": [{"$eq": ["$status", "disputed"]}, 1, 0]}
                },
                "reasons": {"$push": "$reason"},
                "platforms": {"$push": "$target_platforms"}
            }}
        ]
        
        result = await self.collection.aggregate(pipeline).to_list(length=1)
        
        if result:
            data = result[0]
            
            # Count by reason
            requests_by_reason = {}
            for reason in data.get("reasons", []):
                requests_by_reason[reason] = requests_by_reason.get(reason, 0) + 1
            
            # Count by platform
            requests_by_platform = {}
            for platform_list in data.get("platforms", []):
                for platform in platform_list:
                    requests_by_platform[platform] = requests_by_platform.get(platform, 0) + 1
            
            return RemovalAnalytics(
                total_requests=data.get("total_requests", 0),
                pending_requests=data.get("pending_requests", 0),
                approved_requests=data.get("approved_requests", 0),
                completed_requests=data.get("completed_requests", 0),
                disputed_requests=data.get("disputed_requests", 0),
                requests_by_reason=requests_by_reason,
                requests_by_platform=requests_by_platform
            )
        
        return RemovalAnalytics()