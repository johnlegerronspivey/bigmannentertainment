"""AWS SageMaker Service - ML model training & deployment."""
import os
import logging
import boto3
from typing import Dict, Any, List
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class SageMakerService:
    def __init__(self):
        self.region = os.environ.get("AWS_REGION", "us-east-1")
        self.available = False
        self._client = None
        try:
            self._client = boto3.client(
                "sagemaker",
                aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
                region_name=self.region,
            )
            self._client.list_notebook_instances(MaxResults=1)
            self.available = True
        except ClientError:
            self.available = True  # Access exists but no notebooks
        except Exception as e:
            logger.warning(f"SageMaker init failed: {e}")

    def get_status(self) -> Dict[str, Any]:
        if not self.available:
            return {"available": False}
        return {"available": True, "region": self.region, "service": "Amazon SageMaker"}

    def list_notebook_instances(self) -> List[Dict[str, Any]]:
        resp = self._client.list_notebook_instances(MaxResults=20)
        return [
            {
                "name": nb.get("NotebookInstanceName", ""),
                "status": nb.get("NotebookInstanceStatus", ""),
                "instance_type": nb.get("InstanceType", ""),
                "created_at": nb.get("CreationTime", "").isoformat() if nb.get("CreationTime") else "",
                "url": nb.get("Url", ""),
            }
            for nb in resp.get("NotebookInstances", [])
        ]

    def list_training_jobs(self, max_results: int = 20) -> List[Dict[str, Any]]:
        resp = self._client.list_training_jobs(MaxResults=max_results, SortBy="CreationTime", SortOrder="Descending")
        return [
            {
                "name": j.get("TrainingJobName", ""),
                "status": j.get("TrainingJobStatus", ""),
                "created_at": j.get("CreationTime", "").isoformat() if j.get("CreationTime") else "",
                "training_end": j.get("TrainingEndTime", "").isoformat() if j.get("TrainingEndTime") else "",
            }
            for j in resp.get("TrainingJobSummaries", [])
        ]

    def list_models(self, max_results: int = 20) -> List[Dict[str, Any]]:
        resp = self._client.list_models(MaxResults=max_results, SortBy="CreationTime", SortOrder="Descending")
        return [
            {
                "name": m.get("ModelName", ""),
                "arn": m.get("ModelArn", ""),
                "created_at": m.get("CreationTime", "").isoformat() if m.get("CreationTime") else "",
            }
            for m in resp.get("Models", [])
        ]

    def list_endpoints(self, max_results: int = 20) -> List[Dict[str, Any]]:
        resp = self._client.list_endpoints(MaxResults=max_results, SortBy="CreationTime", SortOrder="Descending")
        return [
            {
                "name": ep.get("EndpointName", ""),
                "status": ep.get("EndpointStatus", ""),
                "arn": ep.get("EndpointArn", ""),
                "created_at": ep.get("CreationTime", "").isoformat() if ep.get("CreationTime") else "",
                "last_modified": ep.get("LastModifiedTime", "").isoformat() if ep.get("LastModifiedTime") else "",
            }
            for ep in resp.get("Endpoints", [])
        ]

    def list_processing_jobs(self, max_results: int = 20) -> List[Dict[str, Any]]:
        resp = self._client.list_processing_jobs(MaxResults=max_results, SortBy="CreationTime", SortOrder="Descending")
        return [
            {
                "name": j.get("ProcessingJobName", ""),
                "status": j.get("ProcessingJobStatus", ""),
                "created_at": j.get("CreationTime", "").isoformat() if j.get("CreationTime") else "",
            }
            for j in resp.get("ProcessingJobSummaries", [])
        ]

    def list_feature_groups(self) -> List[Dict[str, Any]]:
        try:
            resp = self._client.list_feature_groups(MaxResults=20, SortBy="CreationTime", SortOrder="Descending")
            return [
                {
                    "name": fg.get("FeatureGroupName", ""),
                    "status": fg.get("FeatureGroupStatus", ""),
                    "created_at": fg.get("CreationTime", "").isoformat() if fg.get("CreationTime") else "",
                }
                for fg in resp.get("FeatureGroupSummaries", [])
            ]
        except ClientError:
            return []
