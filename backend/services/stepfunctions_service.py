"""AWS Step Functions Service - Workflow orchestration."""
import os
import logging
import boto3
from typing import Dict, Any, List
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class StepFunctionsService:
    def __init__(self):
        self.region = os.environ.get("AWS_REGION", "us-east-1")
        self.available = False
        self._client = None
        try:
            self._client = boto3.client(
                "stepfunctions",
                aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
                region_name=self.region,
            )
            self._client.list_state_machines(maxResults=1)
            self.available = True
        except Exception as e:
            logger.warning(f"Step Functions init failed: {e}")

    def get_status(self) -> Dict[str, Any]:
        if not self.available:
            return {"available": False}
        return {"available": True, "region": self.region, "service": "AWS Step Functions"}

    def list_state_machines(self, max_results: int = 50) -> List[Dict[str, Any]]:
        resp = self._client.list_state_machines(maxResults=max_results)
        return [
            {
                "name": sm.get("name", ""),
                "arn": sm.get("stateMachineArn", ""),
                "type": sm.get("type", "STANDARD"),
                "created_at": sm.get("creationDate", "").isoformat() if sm.get("creationDate") else "",
            }
            for sm in resp.get("stateMachines", [])
        ]

    def describe_state_machine(self, arn: str) -> Dict[str, Any]:
        resp = self._client.describe_state_machine(stateMachineArn=arn)
        return {
            "name": resp.get("name", ""),
            "arn": resp.get("stateMachineArn", ""),
            "status": resp.get("status", ""),
            "type": resp.get("type", ""),
            "definition": resp.get("definition", ""),
            "role_arn": resp.get("roleArn", ""),
            "created_at": resp.get("creationDate", "").isoformat() if resp.get("creationDate") else "",
        }

    def list_executions(self, state_machine_arn: str, max_results: int = 20, status_filter: str = None) -> List[Dict[str, Any]]:
        kwargs = {"stateMachineArn": state_machine_arn, "maxResults": max_results}
        if status_filter:
            kwargs["statusFilter"] = status_filter
        resp = self._client.list_executions(**kwargs)
        return [
            {
                "name": ex.get("name", ""),
                "arn": ex.get("executionArn", ""),
                "status": ex.get("status", ""),
                "started_at": ex.get("startDate", "").isoformat() if ex.get("startDate") else "",
                "stopped_at": ex.get("stopDate", "").isoformat() if ex.get("stopDate") else "",
            }
            for ex in resp.get("executions", [])
        ]

    def describe_execution(self, execution_arn: str) -> Dict[str, Any]:
        resp = self._client.describe_execution(executionArn=execution_arn)
        return {
            "name": resp.get("name", ""),
            "arn": resp.get("executionArn", ""),
            "status": resp.get("status", ""),
            "input": resp.get("input", ""),
            "output": resp.get("output", ""),
            "started_at": resp.get("startDate", "").isoformat() if resp.get("startDate") else "",
            "stopped_at": resp.get("stopDate", "").isoformat() if resp.get("stopDate") else "",
        }

    def list_activities(self) -> List[Dict[str, Any]]:
        resp = self._client.list_activities(maxResults=50)
        return [
            {
                "name": a.get("name", ""),
                "arn": a.get("activityArn", ""),
                "created_at": a.get("creationDate", "").isoformat() if a.get("creationDate") else "",
            }
            for a in resp.get("activities", [])
        ]
