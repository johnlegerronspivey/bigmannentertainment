"""Amazon QuickSight Service - Business Intelligence & Visual Dashboards."""
import os
import logging
import boto3
from typing import Dict, Any, List
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class QuickSightService:
    def __init__(self):
        self.region = os.environ.get("AWS_REGION", "us-east-1")
        self.account_id = None
        self.available = False
        self._client = None

        try:
            sts = boto3.client(
                "sts",
                aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
                region_name=self.region,
            )
            self.account_id = sts.get_caller_identity()["Account"]
            self._client = boto3.client(
                "quicksight",
                aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
                region_name=self.region,
            )
            self._client.list_dashboards(AwsAccountId=self.account_id, MaxResults=1)
            self.available = True
        except Exception as e:
            logger.warning(f"QuickSight init failed: {e}")

    def get_status(self) -> Dict[str, Any]:
        if not self.available:
            return {"available": False}
        return {
            "available": True,
            "region": self.region,
            "service": "Amazon QuickSight",
            "account_id": self.account_id,
        }

    def list_dashboards(self) -> List[Dict[str, Any]]:
        if not self.available:
            raise RuntimeError("QuickSight not available")
        resp = self._client.list_dashboards(AwsAccountId=self.account_id, MaxResults=50)
        return [
            {
                "id": d.get("DashboardId", ""),
                "name": d.get("Name", ""),
                "arn": d.get("Arn", ""),
                "version": d.get("PublishedVersionNumber", 0),
                "status": d.get("DashboardId", "") and "ACTIVE",
                "created_at": d.get("CreatedTime", "").isoformat() if d.get("CreatedTime") else "",
                "updated_at": d.get("LastPublishedTime", "").isoformat() if d.get("LastPublishedTime") else "",
            }
            for d in resp.get("DashboardSummaryList", [])
        ]

    def list_datasets(self) -> List[Dict[str, Any]]:
        if not self.available:
            raise RuntimeError("QuickSight not available")
        resp = self._client.list_data_sets(AwsAccountId=self.account_id, MaxResults=50)
        return [
            {
                "id": ds.get("DataSetId", ""),
                "name": ds.get("Name", ""),
                "arn": ds.get("Arn", ""),
                "import_mode": ds.get("ImportMode", ""),
                "row_count": ds.get("RowLevelPermissionDataSet", {}).get("Arn", ""),
                "created_at": ds.get("CreatedTime", "").isoformat() if ds.get("CreatedTime") else "",
            }
            for ds in resp.get("DataSetSummaries", [])
        ]

    def list_data_sources(self) -> List[Dict[str, Any]]:
        if not self.available:
            raise RuntimeError("QuickSight not available")
        resp = self._client.list_data_sources(AwsAccountId=self.account_id, MaxResults=50)
        return [
            {
                "id": src.get("DataSourceId", ""),
                "name": src.get("Name", ""),
                "arn": src.get("Arn", ""),
                "type": src.get("Type", ""),
                "status": src.get("Status", ""),
                "created_at": src.get("CreatedTime", "").isoformat() if src.get("CreatedTime") else "",
            }
            for src in resp.get("DataSources", [])
        ]

    def list_analyses(self) -> List[Dict[str, Any]]:
        if not self.available:
            raise RuntimeError("QuickSight not available")
        resp = self._client.list_analyses(AwsAccountId=self.account_id, MaxResults=50)
        return [
            {
                "id": a.get("AnalysisId", ""),
                "name": a.get("Name", ""),
                "arn": a.get("Arn", ""),
                "status": a.get("Status", ""),
                "created_at": a.get("CreatedTime", "").isoformat() if a.get("CreatedTime") else "",
            }
            for a in resp.get("AnalysisSummaryList", [])
        ]

    def describe_dashboard(self, dashboard_id: str) -> Dict[str, Any]:
        if not self.available:
            raise RuntimeError("QuickSight not available")
        resp = self._client.describe_dashboard(
            AwsAccountId=self.account_id, DashboardId=dashboard_id
        )
        d = resp.get("Dashboard", {})
        return {
            "id": d.get("DashboardId", ""),
            "name": d.get("Name", ""),
            "arn": d.get("Arn", ""),
            "version_number": d.get("Version", {}).get("VersionNumber", 0),
            "status": d.get("Version", {}).get("Status", ""),
            "created_at": d.get("CreatedTime", "").isoformat() if d.get("CreatedTime") else "",
            "updated_at": d.get("LastUpdatedTime", "").isoformat() if d.get("LastUpdatedTime") else "",
            "sheets": [
                {"id": s.get("SheetId", ""), "name": s.get("Name", "")}
                for s in d.get("Version", {}).get("Sheets", [])
            ],
        }

    def get_dashboard_embed_url(self, dashboard_id: str) -> str:
        if not self.available:
            raise RuntimeError("QuickSight not available")
        resp = self._client.get_dashboard_embed_url(
            AwsAccountId=self.account_id,
            DashboardId=dashboard_id,
            IdentityType="IAM",
            SessionLifetimeInMinutes=600,
            UndoRedoDisabled=False,
            ResetDisabled=False,
        )
        return resp.get("EmbedUrl", "")
