"""AWS EventBridge Service - Event-driven workflow automation."""
import os
import logging
import boto3
from typing import Dict, Any, List
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class EventBridgeService:
    def __init__(self):
        self.region = os.environ.get("AWS_REGION", "us-east-1")
        self.available = False
        self._client = None
        try:
            self._client = boto3.client(
                "events",
                aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
                region_name=self.region,
            )
            self._client.list_event_buses(Limit=1)
            self.available = True
        except Exception as e:
            logger.warning(f"EventBridge init failed: {e}")

    def get_status(self) -> Dict[str, Any]:
        if not self.available:
            return {"available": False}
        return {"available": True, "region": self.region, "service": "Amazon EventBridge"}

    def list_event_buses(self) -> List[Dict[str, Any]]:
        resp = self._client.list_event_buses(Limit=50)
        return [
            {
                "name": eb.get("Name", ""),
                "arn": eb.get("Arn", ""),
                "policy": bool(eb.get("Policy")),
            }
            for eb in resp.get("EventBuses", [])
        ]

    def list_rules(self, event_bus_name: str = "default") -> List[Dict[str, Any]]:
        resp = self._client.list_rules(EventBusName=event_bus_name, Limit=50)
        return [
            {
                "name": r.get("Name", ""),
                "arn": r.get("Arn", ""),
                "state": r.get("State", ""),
                "description": r.get("Description", ""),
                "schedule": r.get("ScheduleExpression", ""),
                "event_pattern": r.get("EventPattern", ""),
                "event_bus_name": r.get("EventBusName", ""),
            }
            for r in resp.get("Rules", [])
        ]

    def list_targets(self, rule_name: str, event_bus_name: str = "default") -> List[Dict[str, Any]]:
        resp = self._client.list_targets_by_rule(Rule=rule_name, EventBusName=event_bus_name, Limit=50)
        return [
            {
                "id": t.get("Id", ""),
                "arn": t.get("Arn", ""),
                "role_arn": t.get("RoleArn", ""),
                "input": t.get("Input", ""),
            }
            for t in resp.get("Targets", [])
        ]

    def list_archives(self) -> List[Dict[str, Any]]:
        resp = self._client.list_archives(Limit=50)
        return [
            {
                "name": a.get("ArchiveName", ""),
                "state": a.get("State", ""),
                "event_source_arn": a.get("EventSourceArn", ""),
                "retention_days": a.get("RetentionDays", 0),
                "event_count": a.get("EventCount", 0),
                "size_bytes": a.get("SizeBytes", 0),
                "created_at": a.get("CreationTime", "").isoformat() if a.get("CreationTime") else "",
            }
            for a in resp.get("Archives", [])
        ]

    def list_connections(self) -> List[Dict[str, Any]]:
        resp = self._client.list_connections(Limit=50)
        return [
            {
                "name": c.get("Name", ""),
                "state": c.get("ConnectionState", ""),
                "auth_type": c.get("AuthorizationType", ""),
                "created_at": c.get("CreationTime", "").isoformat() if c.get("CreationTime") else "",
            }
            for c in resp.get("Connections", [])
        ]

    def list_api_destinations(self) -> List[Dict[str, Any]]:
        resp = self._client.list_api_destinations(Limit=50)
        return [
            {
                "name": a.get("Name", ""),
                "state": a.get("ApiDestinationState", ""),
                "endpoint": a.get("InvocationEndpoint", ""),
                "http_method": a.get("HttpMethod", ""),
                "invocation_rate": a.get("InvocationRateLimitPerSecond", 0),
            }
            for a in resp.get("ApiDestinations", [])
        ]
