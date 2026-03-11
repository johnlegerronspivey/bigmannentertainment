"""
Audit Trail Service
Handles immutable logging, audit trails, metadata snapshots, and compliance tracking
"""

import asyncio
import json
import logging
import hashlib
import hmac
import secrets
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import uuid
from collections import defaultdict

from audit_models import (
    ImmutableAuditLog, MetadataSnapshot, UploadAuditLog, ValidationAuditLog,
    RightsCheckAuditLog, AuditLogQuery, AuditReport, RealTimeAlert,
    AuditStatistics, AuditEventType, AuditSeverity, AuditOutcome
)

logger = logging.getLogger(__name__)

class AuditService:
    """Service for comprehensive audit trail and logging"""
    
    def __init__(self, mongo_db=None):
        self.mongo_db = mongo_db
        self.audit_secret_key = secrets.token_hex(32)  # For HMAC signatures
        self.alert_rules = self._initialize_alert_rules()
        
    async def log_audit_event(self, event_type: AuditEventType, event_name: str,
                            event_description: str, user_context: Dict[str, Any] = None,
                            resource_context: Dict[str, Any] = None,
                            event_data: Dict[str, Any] = None,
                            severity: AuditSeverity = AuditSeverity.INFO,
                            outcome: AuditOutcome = AuditOutcome.SUCCESS) -> str:
        """Log an immutable audit event"""
        
        try:
            # Get the previous log hash for chain integrity
            previous_hash = await self._get_latest_log_hash()
            
            # Create audit log entry
            audit_log = ImmutableAuditLog(
                event_type=event_type,
                event_name=event_name,
                event_description=event_description,
                severity=severity,
                outcome=outcome,
                event_data=event_data or {},
                previous_log_hash=previous_hash
            )
            
            # Add user context if provided
            if user_context:
                audit_log.user_id = user_context.get("user_id")
                audit_log.user_email = user_context.get("user_email")
                audit_log.user_role = user_context.get("user_role")
                audit_log.session_id = user_context.get("session_id")
                audit_log.ip_address = user_context.get("ip_address")
                audit_log.user_agent = user_context.get("user_agent")
            
            # Add resource context if provided
            if resource_context:
                audit_log.resource_type = resource_context.get("resource_type")
                audit_log.resource_id = resource_context.get("resource_id")
                audit_log.resource_name = resource_context.get("resource_name")
                audit_log.content_id = resource_context.get("content_id")
                audit_log.isrc = resource_context.get("isrc")
                audit_log.upc = resource_context.get("upc")
                audit_log.filename = resource_context.get("filename")
                audit_log.file_size = resource_context.get("file_size")
                audit_log.file_type = resource_context.get("file_type")
            
            # Generate digital signature for integrity
            audit_log.digital_signature = self._generate_signature(audit_log)
            
            # Store in database
            await self._store_audit_log(audit_log)
            
            # Check for alert conditions
            await self._check_alert_conditions(audit_log)
            
            logger.info(f"Audit event logged: {event_type.value} - {event_name}")
            return audit_log.log_id
            
        except Exception as e:
            logger.error(f"Failed to log audit event: {str(e)}")
            return None
    
    async def create_metadata_snapshot(self, content_id: str, user_id: str,
                                     metadata_state: Dict[str, Any],
                                     trigger_event: str = "manual",
                                     trigger_reason: str = None) -> str:
        """Create timestamped metadata snapshot for compliance"""
        
        try:
            # Get previous snapshot hash for chain integrity
            previous_hash = await self._get_latest_snapshot_hash(content_id)
            
            # Create snapshot
            snapshot = MetadataSnapshot(
                content_id=content_id,
                user_id=user_id,
                metadata_state=metadata_state,
                trigger_event=trigger_event,
                trigger_reason=trigger_reason,
                previous_snapshot_hash=previous_hash
            )
            
            # Extract key identifiers from metadata
            if metadata_state:
                snapshot.isrc = metadata_state.get("isrc")
                snapshot.upc = metadata_state.get("upc")
                snapshot.filename = metadata_state.get("filename", "unknown")
                
            # Generate snapshot hash
            snapshot.snapshot_hash = snapshot.generate_snapshot_hash()
            
            # Store snapshot
            await self._store_metadata_snapshot(snapshot)
            
            # Log the snapshot creation
            await self.log_audit_event(
                event_type=AuditEventType.METADATA_UPDATE,
                event_name="Metadata Snapshot Created",
                event_description=f"Metadata snapshot created for content {content_id}",
                user_context={"user_id": user_id},
                resource_context={"content_id": content_id, "resource_type": "content"},
                event_data={
                    "snapshot_id": snapshot.snapshot_id,
                    "trigger_event": trigger_event,
                    "metadata_fields": list(metadata_state.keys()) if metadata_state else []
                }
            )
            
            logger.info(f"Metadata snapshot created: {snapshot.snapshot_id}")
            return snapshot.snapshot_id
            
        except Exception as e:
            logger.error(f"Failed to create metadata snapshot: {str(e)}")
            return None
    
    async def log_upload_event(self, upload_data: Dict[str, Any]) -> str:
        """Log comprehensive upload audit trail"""
        
        try:
            # Create main audit log
            audit_log_id = await self.log_audit_event(
                event_type=AuditEventType.UPLOAD,
                event_name="File Upload",
                event_description=f"File uploaded: {upload_data.get('filename', 'unknown')}",
                user_context=upload_data.get("user_context", {}),
                resource_context=upload_data.get("resource_context", {}),
                event_data=upload_data.get("event_data", {}),
                outcome=AuditOutcome.SUCCESS if upload_data.get("success", True) else AuditOutcome.FAILURE
            )
            
            # Create detailed upload log
            upload_log = UploadAuditLog(
                audit_log_id=audit_log_id,
                content_id=upload_data.get("content_id"),
                user_id=upload_data.get("user_id"),
                original_filename=upload_data.get("original_filename"),
                final_filename=upload_data.get("final_filename"),
                file_size=upload_data.get("file_size", 0),
                file_type=upload_data.get("file_type", "unknown"),
                mime_type=upload_data.get("mime_type"),
                upload_method=upload_data.get("upload_method", "direct"),
                upload_duration_ms=upload_data.get("upload_duration_ms"),
                file_hash_md5=upload_data.get("file_hash_md5"),
                file_hash_sha256=upload_data.get("file_hash_sha256"),
                initial_metadata=upload_data.get("initial_metadata", {}),
                storage_provider=upload_data.get("storage_provider", "s3"),
                storage_bucket=upload_data.get("storage_bucket"),
                storage_key=upload_data.get("storage_key"),
                storage_url=upload_data.get("storage_url"),
                upload_status=upload_data.get("upload_status", "completed"),
                upload_started=upload_data.get("upload_started", datetime.now()),
                upload_completed=upload_data.get("upload_completed", datetime.now())
            )
            
            # Store detailed upload log
            await self._store_upload_log(upload_log)
            
            # Create initial metadata snapshot
            if upload_data.get("initial_metadata"):
                await self.create_metadata_snapshot(
                    content_id=upload_data.get("content_id"),
                    user_id=upload_data.get("user_id"),
                    metadata_state=upload_data.get("initial_metadata"),
                    trigger_event="upload",
                    trigger_reason="Initial upload metadata"
                )
            
            logger.info(f"Upload audit logged: {upload_log.upload_id}")
            return upload_log.upload_id
            
        except Exception as e:
            logger.error(f"Failed to log upload event: {str(e)}")
            return None
    
    async def log_validation_event(self, validation_data: Dict[str, Any]) -> str:
        """Log comprehensive validation audit trail"""
        
        try:
            # Create main audit log
            outcome = AuditOutcome.SUCCESS if validation_data.get("validation_status") == "passed" else AuditOutcome.FAILURE
            severity = AuditSeverity.ERROR if outcome == AuditOutcome.FAILURE else AuditSeverity.INFO
            
            audit_log_id = await self.log_audit_event(
                event_type=AuditEventType.VALIDATION,
                event_name="Metadata Validation",
                event_description=f"Validation performed for content {validation_data.get('content_id')}",
                user_context=validation_data.get("user_context", {}),
                resource_context=validation_data.get("resource_context", {}),
                event_data=validation_data.get("event_data", {}),
                severity=severity,
                outcome=outcome
            )
            
            # Create detailed validation log
            validation_log = ValidationAuditLog(
                audit_log_id=audit_log_id,
                content_id=validation_data.get("content_id"),
                user_id=validation_data.get("user_id"),
                validation_type=validation_data.get("validation_type", "metadata"),
                validation_format=validation_data.get("validation_format", "json"),
                input_metadata=validation_data.get("input_metadata", {}),
                validation_rules=validation_data.get("validation_rules", []),
                validation_config=validation_data.get("validation_config", {}),
                validation_status=validation_data.get("validation_status", "pending"),
                validation_score=validation_data.get("validation_score"),
                confidence_score=validation_data.get("confidence_score"),
                field_results=validation_data.get("field_results", {}),
                validation_errors=validation_data.get("validation_errors", []),
                validation_warnings=validation_data.get("validation_warnings", []),
                validation_info=validation_data.get("validation_info", []),
                duplicate_check_performed=validation_data.get("duplicate_check_performed", False),
                duplicates_found=validation_data.get("duplicates_found", []),
                duplicate_identifiers=validation_data.get("duplicate_identifiers", []),
                business_rules_applied=validation_data.get("business_rules_applied", []),
                business_rule_violations=validation_data.get("business_rule_violations", []),
                validation_duration_ms=validation_data.get("validation_duration_ms", 0.0),
                rules_processed=validation_data.get("rules_processed", 0),
                fields_validated=validation_data.get("fields_validated", 0),
                validation_started=validation_data.get("validation_started", datetime.now()),
                validation_completed=validation_data.get("validation_completed", datetime.now())
            )
            
            # Store detailed validation log
            await self._store_validation_log(validation_log)
            
            # Create metadata snapshot after validation
            if validation_data.get("input_metadata"):
                await self.create_metadata_snapshot(
                    content_id=validation_data.get("content_id"),
                    user_id=validation_data.get("user_id"),
                    metadata_state={
                        **validation_data.get("input_metadata", {}),
                        "validation_status": validation_data.get("validation_status"),
                        "validation_score": validation_data.get("validation_score"),
                        "validation_timestamp": datetime.now().isoformat()
                    },
                    trigger_event="validation",
                    trigger_reason=f"Validation {validation_data.get('validation_status', 'completed')}"
                )
            
            logger.info(f"Validation audit logged: {validation_log.validation_id}")
            return validation_log.validation_id
            
        except Exception as e:
            logger.error(f"Failed to log validation event: {str(e)}")
            return None
    
    async def log_rights_check_event(self, rights_data: Dict[str, Any]) -> str:
        """Log comprehensive rights check audit trail"""
        
        try:
            # Create main audit log
            outcome = AuditOutcome.SUCCESS if rights_data.get("overall_status") == "compliant" else AuditOutcome.FAILURE
            severity = AuditSeverity.WARNING if outcome == AuditOutcome.FAILURE else AuditSeverity.INFO
            
            audit_log_id = await self.log_audit_event(
                event_type=AuditEventType.RIGHTS_CHECK,
                event_name="Rights Compliance Check",
                event_description=f"Rights check performed for content {rights_data.get('content_id')}",
                user_context=rights_data.get("user_context", {}),
                resource_context=rights_data.get("resource_context", {}),
                event_data=rights_data.get("event_data", {}),
                severity=severity,
                outcome=outcome
            )
            
            # Create detailed rights check log
            rights_log = RightsCheckAuditLog(
                audit_log_id=audit_log_id,
                content_id=rights_data.get("content_id"),
                user_id=rights_data.get("user_id"),
                check_type=rights_data.get("check_type", "comprehensive"),
                check_scope=rights_data.get("check_scope", "global"),
                isrc=rights_data.get("isrc"),
                title=rights_data.get("title"),
                artist=rights_data.get("artist"),
                territory_codes=rights_data.get("territory_codes", []),
                usage_rights=rights_data.get("usage_rights", []),
                rights_holders=rights_data.get("rights_holders", []),
                target_territories=rights_data.get("target_territories", []),
                target_usage_types=rights_data.get("target_usage_types", []),
                overall_status=rights_data.get("overall_status", "unknown"),
                overall_score=rights_data.get("overall_score"),
                territory_results=rights_data.get("territory_results", {}),
                territory_violations=rights_data.get("territory_violations", []),
                territory_warnings=rights_data.get("territory_warnings", []),
                usage_results=rights_data.get("usage_results", {}),
                usage_violations=rights_data.get("usage_violations", []),
                usage_warnings=rights_data.get("usage_warnings", []),
                expiry_checks=rights_data.get("expiry_checks", []),
                embargo_checks=rights_data.get("embargo_checks", []),
                expired_rights=rights_data.get("expired_rights", []),
                active_embargos=rights_data.get("active_embargos", []),
                compliance_frameworks=rights_data.get("compliance_frameworks", []),
                compliance_violations=rights_data.get("compliance_violations", []),
                check_duration_ms=rights_data.get("check_duration_ms", 0.0),
                territories_checked=rights_data.get("territories_checked", 0),
                usage_types_checked=rights_data.get("usage_types_checked", 0),
                check_started=rights_data.get("check_started", datetime.now()),
                check_completed=rights_data.get("check_completed", datetime.now())
            )
            
            # Store detailed rights check log
            await self._store_rights_check_log(rights_log)
            
            # Create metadata snapshot after rights check
            snapshot_metadata = {
                "isrc": rights_data.get("isrc"),
                "title": rights_data.get("title"),
                "artist": rights_data.get("artist"),
                "rights_status": rights_data.get("overall_status"),
                "rights_score": rights_data.get("overall_score"),
                "territory_compliance": rights_data.get("territory_results", {}),
                "usage_compliance": rights_data.get("usage_results", {}),
                "rights_check_timestamp": datetime.now().isoformat()
            }
            
            await self.create_metadata_snapshot(
                content_id=rights_data.get("content_id"),
                user_id=rights_data.get("user_id"),
                metadata_state=snapshot_metadata,
                trigger_event="rights_check",
                trigger_reason=f"Rights check {rights_data.get('overall_status', 'completed')}"
            )
            
            logger.info(f"Rights check audit logged: {rights_log.rights_check_id}")
            return rights_log.rights_check_id
            
        except Exception as e:
            logger.error(f"Failed to log rights check event: {str(e)}")
            return None
    
    async def query_audit_logs(self, query: AuditLogQuery, user_role: str = "user",
                             user_id: str = None) -> Dict[str, Any]:
        """Query audit logs with proper access control"""
        
        try:
            if self.mongo_db is None:
                return {"logs": [], "total": 0}
            
            # Build MongoDB query based on access control
            mongo_query = {}
            
            # Apply access control
            if user_role == "content_owner" and user_id:
                # Content owners only see their own logs
                mongo_query["user_id"] = user_id
            elif user_role == "admin":
                # Admins see all platform activity (no additional filter)
                pass
            elif user_role == "super_admin":
                # Super admins get full audit access (no additional filter)
                pass
            else:
                # Regular users see only their own logs
                if user_id:
                    mongo_query["user_id"] = user_id
                else:
                    return {"logs": [], "total": 0}  # No access without user_id
            
            # Apply query filters
            if query.start_date:
                mongo_query["timestamp"] = {"$gte": query.start_date}
            if query.end_date:
                if "timestamp" in mongo_query:
                    mongo_query["timestamp"]["$lte"] = query.end_date
                else:
                    mongo_query["timestamp"] = {"$lte": query.end_date}
            
            if query.event_types:
                mongo_query["event_type"] = {"$in": [et.value for et in query.event_types]}
            
            if query.severities:
                mongo_query["severity"] = {"$in": [s.value for s in query.severities]}
            
            if query.outcomes:
                mongo_query["outcome"] = {"$in": [o.value for o in query.outcomes]}
            
            if query.user_ids:
                if "user_id" in mongo_query:
                    # Intersect with existing user_id filter
                    if mongo_query["user_id"] in query.user_ids:
                        mongo_query["user_id"] = {"$in": query.user_ids}
                    else:
                        # No intersection, return empty
                        return {"logs": [], "total": 0}
                else:
                    mongo_query["user_id"] = {"$in": query.user_ids}
            
            if query.resource_ids:
                mongo_query["resource_id"] = {"$in": query.resource_ids}
            
            if query.content_ids:
                mongo_query["content_id"] = {"$in": query.content_ids}
            
            if query.search_text:
                mongo_query["$text"] = {"$search": query.search_text}
            
            # Get total count
            total_count = await self.mongo_db["audit_logs"].count_documents(mongo_query)
            
            # Get paginated results
            sort_direction = -1 if query.sort_order == "desc" else 1
            cursor = self.mongo_db["audit_logs"].find(mongo_query) \
                .sort(query.sort_by, sort_direction) \
                .skip(query.offset) \
                .limit(query.limit)
            
            logs_data = await cursor.to_list(length=query.limit)
            
            # Remove MongoDB _id and convert to audit log objects
            logs = []
            for log_data in logs_data:
                log_data.pop("_id", None)
                logs.append(log_data)
            
            return {
                "logs": logs,
                "total": total_count,
                "limit": query.limit,
                "offset": query.offset
            }
            
        except Exception as e:
            logger.error(f"Failed to query audit logs: {str(e)}")
            return {"logs": [], "total": 0}
    
    async def get_metadata_snapshots(self, content_id: str, user_id: str = None,
                                   user_role: str = "user") -> List[Dict[str, Any]]:
        """Get metadata snapshots for content with access control"""
        
        try:
            if self.mongo_db is None:
                return []
            
            # Build query with access control
            query = {"content_id": content_id}
            
            # Apply access control
            if user_role == "content_owner" and user_id:
                query["user_id"] = user_id
            elif user_role in ["admin", "super_admin"]:
                # Admins can see all snapshots
                pass
            else:
                # Regular users need to be the owner
                if user_id:
                    query["user_id"] = user_id
                else:
                    return []
            
            # Get snapshots sorted by timestamp
            cursor = self.mongo_db["metadata_snapshots"].find(query) \
                .sort("snapshot_timestamp", -1)
            
            snapshots_data = await cursor.to_list(length=None)
            
            # Remove MongoDB _id
            snapshots = []
            for snapshot_data in snapshots_data:
                snapshot_data.pop("_id", None)
                snapshots.append(snapshot_data)
            
            return snapshots
            
        except Exception as e:
            logger.error(f"Failed to get metadata snapshots: {str(e)}")
            return []
    
    async def generate_audit_report(self, report_config: AuditReport, user_role: str = "user",
                                  user_id: str = None) -> Dict[str, Any]:
        """Generate comprehensive audit report with access control"""
        
        try:
            # Query audit logs based on report configuration
            query_result = await self.query_audit_logs(
                report_config.query, user_role, user_id
            )
            
            # Generate statistics
            stats = await self._generate_report_statistics(query_result["logs"])
            
            # Prepare report data
            report_data = {
                "report_id": report_config.report_id,
                "report_name": report_config.report_name,
                "report_type": report_config.report_type,
                "generated_by": report_config.generated_by,
                "generated_at": report_config.generated_at,
                "query_parameters": report_config.query.dict(),
                "total_records": query_result["total"],
                "statistics": stats,
                "logs": query_result["logs"] if report_config.report_type == "detailed" else []
            }
            
            # Add metadata snapshots if requested
            if report_config.include_metadata_snapshots:
                snapshots = []
                content_ids = list(set([log.get("content_id") for log in query_result["logs"] if log.get("content_id")]))
                for content_id in content_ids:
                    content_snapshots = await self.get_metadata_snapshots(content_id, user_id, user_role)
                    snapshots.extend(content_snapshots)
                report_data["metadata_snapshots"] = snapshots
            
            return report_data
            
        except Exception as e:
            logger.error(f"Failed to generate audit report: {str(e)}")
            return {"error": str(e)}
    
    async def create_real_time_alert(self, alert_type: str, severity: AuditSeverity,
                                   title: str, message: str, event_context: Dict[str, Any] = None) -> str:
        """Create real-time alert for suspicious activities"""
        
        try:
            alert = RealTimeAlert(
                alert_type=alert_type,
                severity=severity,
                title=title,
                message=message,
                event_type=event_context.get("event_type", AuditEventType.SYSTEM_EVENT),
                resource_type=event_context.get("resource_type"),
                resource_id=event_context.get("resource_id"),
                user_id=event_context.get("user_id"),
                related_log_ids=event_context.get("related_log_ids", []),
                related_content_ids=event_context.get("related_content_ids", [])
            )
            
            # Store alert
            await self._store_real_time_alert(alert)
            
            # Send notifications (implement notification channels as needed)
            await self._send_alert_notifications(alert)
            
            logger.warning(f"Real-time alert created: {alert.title}")
            return alert.alert_id
            
        except Exception as e:
            logger.error(f"Failed to create real-time alert: {str(e)}")
            return None
    
    # Private helper methods
    
    async def _get_latest_log_hash(self) -> Optional[str]:
        """Get the hash of the most recent audit log for chain integrity"""
        try:
            if self.mongo_db is None:
                return None
                
            latest_log = await self.mongo_db["audit_logs"].find_one(
                {}, sort=[("timestamp", -1)]
            )
            return latest_log.get("log_hash") if latest_log else None
        except Exception:
            return None
    
    async def _get_latest_snapshot_hash(self, content_id: str) -> Optional[str]:
        """Get the hash of the most recent snapshot for content"""
        try:
            if self.mongo_db is None:
                return None
                
            latest_snapshot = await self.mongo_db["metadata_snapshots"].find_one(
                {"content_id": content_id}, sort=[("snapshot_timestamp", -1)]
            )
            return latest_snapshot.get("snapshot_hash") if latest_snapshot else None
        except Exception:
            return None
    
    def _generate_signature(self, audit_log: ImmutableAuditLog) -> str:
        """Generate HMAC signature for log integrity"""
        message = f"{audit_log.log_id}:{audit_log.timestamp.isoformat()}:{audit_log.log_hash}"
        return hmac.new(
            self.audit_secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
    
    async def _store_audit_log(self, audit_log: ImmutableAuditLog):
        """Store audit log in database"""
        if self.mongo_db is None:
            return
            
        try:
            log_dict = audit_log.dict()
            log_dict["_id"] = audit_log.log_id
            await self.mongo_db["audit_logs"].insert_one(log_dict)
        except Exception as e:
            logger.error(f"Failed to store audit log: {str(e)}")
    
    async def _store_metadata_snapshot(self, snapshot: MetadataSnapshot):
        """Store metadata snapshot in database"""
        if self.mongo_db is None:
            return
            
        try:
            snapshot_dict = snapshot.dict()
            snapshot_dict["_id"] = snapshot.snapshot_id
            await self.mongo_db["metadata_snapshots"].insert_one(snapshot_dict)
        except Exception as e:
            logger.error(f"Failed to store metadata snapshot: {str(e)}")
    
    async def _store_upload_log(self, upload_log: UploadAuditLog):
        """Store detailed upload log"""
        if self.mongo_db is None:
            return
            
        try:
            log_dict = upload_log.dict()
            log_dict["_id"] = upload_log.upload_id
            await self.mongo_db["upload_audit_logs"].insert_one(log_dict)
        except Exception as e:
            logger.error(f"Failed to store upload log: {str(e)}")
    
    async def _store_validation_log(self, validation_log: ValidationAuditLog):
        """Store detailed validation log"""
        if self.mongo_db is None:
            return
            
        try:
            log_dict = validation_log.dict()
            log_dict["_id"] = validation_log.validation_id
            await self.mongo_db["validation_audit_logs"].insert_one(log_dict)
        except Exception as e:
            logger.error(f"Failed to store validation log: {str(e)}")
    
    async def _store_rights_check_log(self, rights_log: RightsCheckAuditLog):
        """Store detailed rights check log"""
        if self.mongo_db is None:
            return
            
        try:
            log_dict = rights_log.dict()
            log_dict["_id"] = rights_log.rights_check_id
            await self.mongo_db["rights_check_audit_logs"].insert_one(log_dict)
        except Exception as e:
            logger.error(f"Failed to store rights check log: {str(e)}")
    
    async def _store_real_time_alert(self, alert: RealTimeAlert):
        """Store real-time alert"""
        if self.mongo_db is None:
            return
            
        try:
            alert_dict = alert.dict()
            alert_dict["_id"] = alert.alert_id
            await self.mongo_db["real_time_alerts"].insert_one(alert_dict)
        except Exception as e:
            logger.error(f"Failed to store real-time alert: {str(e)}")
    
    def _initialize_alert_rules(self) -> Dict[str, Any]:
        """Initialize alert rules for suspicious activity detection"""
        return {
            "failed_logins": {"threshold": 5, "window_minutes": 15},
            "validation_failures": {"threshold": 10, "window_minutes": 30},
            "rights_violations": {"threshold": 3, "window_minutes": 60},
            "upload_failures": {"threshold": 5, "window_minutes": 10},
            "admin_actions": {"threshold": 20, "window_minutes": 60},
            "data_exports": {"threshold": 5, "window_minutes": 60}
        }
    
    async def _check_alert_conditions(self, audit_log: ImmutableAuditLog):
        """Check if audit log triggers any alert conditions"""
        try:
            # Check for suspicious patterns
            if audit_log.severity == AuditSeverity.ERROR and audit_log.event_type == AuditEventType.LOGIN:
                await self._check_failed_login_pattern(audit_log)
            
            elif audit_log.outcome == AuditOutcome.FAILURE and audit_log.event_type == AuditEventType.VALIDATION:
                await self._check_validation_failure_pattern(audit_log)
            
            elif audit_log.event_type == AuditEventType.RIGHTS_CHECK and audit_log.outcome == AuditOutcome.FAILURE:
                await self._check_rights_violation_pattern(audit_log)
                
        except Exception as e:
            logger.error(f"Failed to check alert conditions: {str(e)}")
    
    async def _check_failed_login_pattern(self, audit_log: ImmutableAuditLog):
        """Check for suspicious failed login patterns"""
        # Implementation for failed login detection
        pass
    
    async def _check_validation_failure_pattern(self, audit_log: ImmutableAuditLog):
        """Check for suspicious validation failure patterns"""
        # Implementation for validation failure detection
        pass
    
    async def _check_rights_violation_pattern(self, audit_log: ImmutableAuditLog):
        """Check for suspicious rights violation patterns"""
        # Implementation for rights violation detection
        pass
    
    async def _send_alert_notifications(self, alert: RealTimeAlert):
        """Send alert notifications through configured channels"""
        # Implementation for notification sending (email, slack, etc.)
        logger.info(f"Alert notification: {alert.title} - {alert.message}")
    
    async def _generate_report_statistics(self, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate statistics for audit report"""
        if not logs:
            return {}
        
        # Count events by type
        events_by_type = defaultdict(int)
        events_by_severity = defaultdict(int)
        events_by_outcome = defaultdict(int)
        
        for log in logs:
            events_by_type[log.get("event_type", "unknown")] += 1
            events_by_severity[log.get("severity", "unknown")] += 1
            events_by_outcome[log.get("outcome", "unknown")] += 1
        
        return {
            "total_events": len(logs),
            "events_by_type": dict(events_by_type),
            "events_by_severity": dict(events_by_severity),
            "events_by_outcome": dict(events_by_outcome),
            "date_range": {
                "start": min([log.get("timestamp") for log in logs if log.get("timestamp")], default=None),
                "end": max([log.get("timestamp") for log in logs if log.get("timestamp")], default=None)
            }
        }