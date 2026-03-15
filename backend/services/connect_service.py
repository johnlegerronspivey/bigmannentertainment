"""Amazon Connect Service - Cloud contact center management."""
import os
import logging
import boto3
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class ConnectService:
    def __init__(self):
        self.region = os.environ.get("AWS_REGION", "us-east-1")
        self.available = False
        self._client = None

        try:
            self._client = boto3.client(
                "connect",
                aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
                region_name=self.region,
            )
            self._client.list_instances(MaxResults=1)
            self.available = True
        except Exception as e:
            logger.warning(f"Connect init failed: {e}")

    def get_status(self) -> Dict[str, Any]:
        if not self.available:
            return {"available": False}
        try:
            resp = self._client.list_instances(MaxResults=1)
            instance_count = len(resp.get("InstanceSummaryList", []))
            return {
                "available": True,
                "region": self.region,
                "service": "Amazon Connect",
                "instances_found": instance_count,
            }
        except Exception as e:
            return {"available": False, "error": str(e)}

    # ------------------------------------------------------------------
    # Instances
    # ------------------------------------------------------------------
    def list_instances(self) -> List[Dict[str, Any]]:
        if not self.available:
            raise RuntimeError("Connect not available")
        resp = self._client.list_instances(MaxResults=10)
        instances = []
        for inst in resp.get("InstanceSummaryList", []):
            instances.append({
                "instance_id": inst.get("Id", ""),
                "arn": inst.get("Arn", ""),
                "instance_alias": inst.get("InstanceAlias", ""),
                "identity_management_type": inst.get("IdentityManagementType", ""),
                "instance_status": inst.get("InstanceStatus", ""),
                "inbound_calls_enabled": inst.get("InboundCallsEnabled", False),
                "outbound_calls_enabled": inst.get("OutboundCallsEnabled", False),
                "created_time": inst.get("CreatedTime", "").isoformat() if hasattr(inst.get("CreatedTime", ""), "isoformat") else str(inst.get("CreatedTime", "")),
            })
        return instances

    def describe_instance(self, instance_id: str) -> Dict[str, Any]:
        if not self.available:
            raise RuntimeError("Connect not available")
        resp = self._client.describe_instance(InstanceId=instance_id)
        inst = resp.get("Instance", {})
        return {
            "instance_id": inst.get("Id", ""),
            "arn": inst.get("Arn", ""),
            "instance_alias": inst.get("InstanceAlias", ""),
            "identity_management_type": inst.get("IdentityManagementType", ""),
            "instance_status": inst.get("InstanceStatus", ""),
            "inbound_calls_enabled": inst.get("InboundCallsEnabled", False),
            "outbound_calls_enabled": inst.get("OutboundCallsEnabled", False),
            "service_role": inst.get("ServiceRole", ""),
            "status_reason": inst.get("StatusReason", {}).get("Message", ""),
            "created_time": inst.get("CreatedTime", "").isoformat() if hasattr(inst.get("CreatedTime", ""), "isoformat") else str(inst.get("CreatedTime", "")),
        }

    # ------------------------------------------------------------------
    # Queues
    # ------------------------------------------------------------------
    def list_queues(self, instance_id: str) -> List[Dict[str, Any]]:
        if not self.available:
            raise RuntimeError("Connect not available")
        resp = self._client.list_queues(InstanceId=instance_id, QueueTypes=["STANDARD"], MaxResults=50)
        queues = []
        for q in resp.get("QueueSummaryList", []):
            queues.append({
                "queue_id": q.get("Id", ""),
                "arn": q.get("Arn", ""),
                "name": q.get("Name", ""),
                "queue_type": q.get("QueueType", ""),
                "last_modified_time": q.get("LastModifiedTime", "").isoformat() if hasattr(q.get("LastModifiedTime", ""), "isoformat") else str(q.get("LastModifiedTime", "")),
                "last_modified_region": q.get("LastModifiedRegion", ""),
            })
        return queues

    def describe_queue(self, instance_id: str, queue_id: str) -> Dict[str, Any]:
        if not self.available:
            raise RuntimeError("Connect not available")
        resp = self._client.describe_queue(InstanceId=instance_id, QueueId=queue_id)
        q = resp.get("Queue", {})
        return {
            "queue_id": q.get("QueueId", ""),
            "arn": q.get("QueueArn", ""),
            "name": q.get("Name", ""),
            "description": q.get("Description", ""),
            "queue_type": q.get("Type", ""),
            "status": q.get("Status", ""),
            "max_contacts": q.get("MaxContacts", 0),
            "hours_of_operation_id": q.get("HoursOfOperationId", ""),
        }

    # ------------------------------------------------------------------
    # Contact Flows
    # ------------------------------------------------------------------
    def list_contact_flows(self, instance_id: str) -> List[Dict[str, Any]]:
        if not self.available:
            raise RuntimeError("Connect not available")
        resp = self._client.list_contact_flows(InstanceId=instance_id, MaxResults=50)
        flows = []
        for f in resp.get("ContactFlowSummaryList", []):
            flows.append({
                "flow_id": f.get("Id", ""),
                "arn": f.get("Arn", ""),
                "name": f.get("Name", ""),
                "contact_flow_type": f.get("ContactFlowType", ""),
                "contact_flow_state": f.get("ContactFlowState", ""),
                "contact_flow_status": f.get("ContactFlowStatus", ""),
                "last_modified_time": f.get("LastModifiedTime", "").isoformat() if hasattr(f.get("LastModifiedTime", ""), "isoformat") else str(f.get("LastModifiedTime", "")),
            })
        return flows

    # ------------------------------------------------------------------
    # Hours of Operation
    # ------------------------------------------------------------------
    def list_hours_of_operation(self, instance_id: str) -> List[Dict[str, Any]]:
        if not self.available:
            raise RuntimeError("Connect not available")
        resp = self._client.list_hours_of_operations(InstanceId=instance_id, MaxResults=50)
        hours = []
        for h in resp.get("HoursOfOperationSummaryList", []):
            hours.append({
                "hours_id": h.get("Id", ""),
                "arn": h.get("Arn", ""),
                "name": h.get("Name", ""),
                "last_modified_time": h.get("LastModifiedTime", "").isoformat() if hasattr(h.get("LastModifiedTime", ""), "isoformat") else str(h.get("LastModifiedTime", "")),
                "last_modified_region": h.get("LastModifiedRegion", ""),
            })
        return hours

    def describe_hours_of_operation(self, instance_id: str, hours_id: str) -> Dict[str, Any]:
        if not self.available:
            raise RuntimeError("Connect not available")
        resp = self._client.describe_hours_of_operation(InstanceId=instance_id, HoursOfOperationId=hours_id)
        h = resp.get("HoursOfOperation", {})
        config = []
        for c in h.get("Config", []):
            config.append({
                "day": c.get("Day", ""),
                "start_time": f"{c.get('StartTime', {}).get('Hours', 0):02d}:{c.get('StartTime', {}).get('Minutes', 0):02d}",
                "end_time": f"{c.get('EndTime', {}).get('Hours', 0):02d}:{c.get('EndTime', {}).get('Minutes', 0):02d}",
            })
        return {
            "hours_id": h.get("HoursOfOperationId", ""),
            "arn": h.get("HoursOfOperationArn", ""),
            "name": h.get("Name", ""),
            "description": h.get("Description", ""),
            "time_zone": h.get("TimeZone", ""),
            "config": config,
        }

    # ------------------------------------------------------------------
    # Users
    # ------------------------------------------------------------------
    def list_users(self, instance_id: str) -> List[Dict[str, Any]]:
        if not self.available:
            raise RuntimeError("Connect not available")
        resp = self._client.list_users(InstanceId=instance_id, MaxResults=50)
        users = []
        for u in resp.get("UserSummaryList", []):
            users.append({
                "user_id": u.get("Id", ""),
                "arn": u.get("Arn", ""),
                "username": u.get("Username", ""),
                "last_modified_time": u.get("LastModifiedTime", "").isoformat() if hasattr(u.get("LastModifiedTime", ""), "isoformat") else str(u.get("LastModifiedTime", "")),
                "last_modified_region": u.get("LastModifiedRegion", ""),
            })
        return users

    def describe_user(self, instance_id: str, user_id: str) -> Dict[str, Any]:
        if not self.available:
            raise RuntimeError("Connect not available")
        resp = self._client.describe_user(InstanceId=instance_id, UserId=user_id)
        u = resp.get("User", {})
        identity = u.get("IdentityInfo", {})
        phone = u.get("PhoneConfig", {})
        return {
            "user_id": u.get("Id", ""),
            "arn": u.get("Arn", ""),
            "username": u.get("Username", ""),
            "first_name": identity.get("FirstName", ""),
            "last_name": identity.get("LastName", ""),
            "email": identity.get("Email", ""),
            "phone_type": phone.get("PhoneType", ""),
            "auto_accept": phone.get("AutoAccept", False),
            "after_contact_work_time_limit": phone.get("AfterContactWorkTimeLimit", 0),
            "routing_profile_id": u.get("RoutingProfileId", ""),
            "security_profile_ids": u.get("SecurityProfileIds", []),
        }

    # ------------------------------------------------------------------
    # Routing Profiles
    # ------------------------------------------------------------------
    def list_routing_profiles(self, instance_id: str) -> List[Dict[str, Any]]:
        if not self.available:
            raise RuntimeError("Connect not available")
        resp = self._client.list_routing_profiles(InstanceId=instance_id, MaxResults=50)
        profiles = []
        for p in resp.get("RoutingProfileSummaryList", []):
            profiles.append({
                "routing_profile_id": p.get("Id", ""),
                "arn": p.get("Arn", ""),
                "name": p.get("Name", ""),
                "last_modified_time": p.get("LastModifiedTime", "").isoformat() if hasattr(p.get("LastModifiedTime", ""), "isoformat") else str(p.get("LastModifiedTime", "")),
                "last_modified_region": p.get("LastModifiedRegion", ""),
            })
        return profiles
