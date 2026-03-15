"""AWS Personalize Service - ML-powered content recommendations."""
import os
import logging
import boto3
from typing import Dict, Any, List
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class PersonalizeService:
    def __init__(self):
        self.region = os.environ.get("AWS_REGION", "us-east-1")
        self.available = False
        self._client = None
        self._runtime = None

        try:
            self._client = boto3.client(
                "personalize",
                aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
                region_name=self.region,
            )
            self._runtime = boto3.client(
                "personalize-runtime",
                aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
                region_name=self.region,
            )
            self._client.list_datasets(maxResults=1)
            self.available = True
        except Exception as e:
            logger.warning(f"Personalize init failed: {e}")

    def get_status(self) -> Dict[str, Any]:
        if not self.available:
            return {"available": False}
        return {
            "available": True,
            "region": self.region,
            "service": "AWS Personalize",
        }

    def list_dataset_groups(self) -> List[Dict[str, Any]]:
        if not self.available:
            raise RuntimeError("Personalize not available")
        resp = self._client.list_dataset_groups(maxResults=50)
        return [
            {
                "name": dg.get("name", ""),
                "arn": dg.get("datasetGroupArn", ""),
                "status": dg.get("status", ""),
                "domain": dg.get("domain", ""),
                "created_at": dg.get("creationDateTime", "").isoformat() if dg.get("creationDateTime") else "",
                "updated_at": dg.get("lastUpdatedDateTime", "").isoformat() if dg.get("lastUpdatedDateTime") else "",
            }
            for dg in resp.get("datasetGroups", [])
        ]

    def list_campaigns(self) -> List[Dict[str, Any]]:
        if not self.available:
            raise RuntimeError("Personalize not available")
        resp = self._client.list_campaigns(maxResults=50)
        return [
            {
                "name": c.get("name", ""),
                "arn": c.get("campaignArn", ""),
                "status": c.get("status", ""),
                "created_at": c.get("creationDateTime", "").isoformat() if c.get("creationDateTime") else "",
                "updated_at": c.get("lastUpdatedDateTime", "").isoformat() if c.get("lastUpdatedDateTime") else "",
            }
            for c in resp.get("campaigns", [])
        ]

    def list_solutions(self) -> List[Dict[str, Any]]:
        if not self.available:
            raise RuntimeError("Personalize not available")
        resp = self._client.list_solutions(maxResults=50)
        return [
            {
                "name": s.get("name", ""),
                "arn": s.get("solutionArn", ""),
                "status": s.get("status", ""),
                "recipe_arn": s.get("recipeArn", ""),
                "created_at": s.get("creationDateTime", "").isoformat() if s.get("creationDateTime") else "",
                "updated_at": s.get("lastUpdatedDateTime", "").isoformat() if s.get("lastUpdatedDateTime") else "",
            }
            for s in resp.get("solutions", [])
        ]

    def list_recipes(self) -> List[Dict[str, Any]]:
        if not self.available:
            raise RuntimeError("Personalize not available")
        resp = self._client.list_recipes(maxResults=50)
        return [
            {
                "name": r.get("name", ""),
                "arn": r.get("recipeArn", ""),
                "status": r.get("status", ""),
                "description": r.get("description", ""),
            }
            for r in resp.get("recipes", [])
        ]

    def get_recommendations(self, campaign_arn: str, user_id: str, num_results: int = 10) -> List[Dict[str, Any]]:
        if not self.available or not self._runtime:
            raise RuntimeError("Personalize runtime not available")
        resp = self._runtime.get_recommendations(
            campaignArn=campaign_arn,
            userId=user_id,
            numResults=num_results,
        )
        return [
            {
                "item_id": item.get("itemId", ""),
                "score": round(item.get("score", 0), 4),
            }
            for item in resp.get("itemList", [])
        ]

    def list_datasets(self, dataset_group_arn: str = None) -> List[Dict[str, Any]]:
        if not self.available:
            raise RuntimeError("Personalize not available")
        params = {"maxResults": 50}
        if dataset_group_arn:
            params["datasetGroupArn"] = dataset_group_arn
        resp = self._client.list_datasets(**params)
        return [
            {
                "name": d.get("name", ""),
                "arn": d.get("datasetArn", ""),
                "type": d.get("datasetType", ""),
                "status": d.get("status", ""),
                "created_at": d.get("creationDateTime", "").isoformat() if d.get("creationDateTime") else "",
            }
            for d in resp.get("datasets", [])
        ]

    def list_event_trackers(self, dataset_group_arn: str = None) -> List[Dict[str, Any]]:
        if not self.available:
            raise RuntimeError("Personalize not available")
        params = {"maxResults": 50}
        if dataset_group_arn:
            params["datasetGroupArn"] = dataset_group_arn
        resp = self._client.list_event_trackers(**params)
        return [
            {
                "name": et.get("name", ""),
                "arn": et.get("eventTrackerArn", ""),
                "status": et.get("status", ""),
                "created_at": et.get("creationDateTime", "").isoformat() if et.get("creationDateTime") else "",
            }
            for et in resp.get("eventTrackers", [])
        ]
