"""AWS Neptune Service - Graph database for social connections."""
import os
import logging
import boto3
from typing import Dict, Any, List
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class NeptuneService:
    def __init__(self):
        self.region = os.environ.get("AWS_REGION", "us-east-1")
        self.available = False
        self._client = None
        try:
            self._client = boto3.client(
                "neptune",
                aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
                region_name=self.region,
            )
            self._client.describe_db_clusters(MaxRecords=20)
            self.available = True
        except Exception as e:
            logger.warning(f"Neptune init failed: {e}")

    def get_status(self) -> Dict[str, Any]:
        if not self.available:
            return {"available": False}
        return {"available": True, "region": self.region, "service": "Amazon Neptune"}

    def list_clusters(self) -> List[Dict[str, Any]]:
        resp = self._client.describe_db_clusters(MaxRecords=100)
        return [
            {
                "id": c.get("DBClusterIdentifier", ""),
                "status": c.get("Status", ""),
                "engine": c.get("Engine", ""),
                "engine_version": c.get("EngineVersion", ""),
                "endpoint": c.get("Endpoint", ""),
                "reader_endpoint": c.get("ReaderEndpoint", ""),
                "port": c.get("Port", 0),
                "multi_az": c.get("MultiAZ", False),
                "storage_encrypted": c.get("StorageEncrypted", False),
                "members": len(c.get("DBClusterMembers", [])),
            }
            for c in resp.get("DBClusters", [])
        ]

    def list_instances(self) -> List[Dict[str, Any]]:
        resp = self._client.describe_db_instances(MaxRecords=100)
        return [
            {
                "id": i.get("DBInstanceIdentifier", ""),
                "status": i.get("DBInstanceStatus", ""),
                "class": i.get("DBInstanceClass", ""),
                "engine": i.get("Engine", ""),
                "engine_version": i.get("EngineVersion", ""),
                "endpoint": i.get("Endpoint", {}).get("Address", "") if i.get("Endpoint") else "",
                "port": i.get("Endpoint", {}).get("Port", 0) if i.get("Endpoint") else 0,
                "availability_zone": i.get("AvailabilityZone", ""),
                "cluster_id": i.get("DBClusterIdentifier", ""),
            }
            for i in resp.get("DBInstances", [])
        ]

    def list_cluster_snapshots(self) -> List[Dict[str, Any]]:
        resp = self._client.describe_db_cluster_snapshots(MaxRecords=50)
        return [
            {
                "id": s.get("DBClusterSnapshotIdentifier", ""),
                "cluster_id": s.get("DBClusterIdentifier", ""),
                "status": s.get("Status", ""),
                "engine": s.get("Engine", ""),
                "snapshot_type": s.get("SnapshotType", ""),
                "storage_encrypted": s.get("StorageEncrypted", False),
                "created_at": s.get("SnapshotCreateTime", "").isoformat() if s.get("SnapshotCreateTime") else "",
            }
            for s in resp.get("DBClusterSnapshots", [])
        ]

    def list_parameter_groups(self) -> List[Dict[str, Any]]:
        resp = self._client.describe_db_cluster_parameter_groups(MaxRecords=50)
        return [
            {
                "name": pg.get("DBClusterParameterGroupName", ""),
                "family": pg.get("DBParameterGroupFamily", ""),
                "description": pg.get("Description", ""),
            }
            for pg in resp.get("DBClusterParameterGroups", [])
        ]

    def list_subnet_groups(self) -> List[Dict[str, Any]]:
        resp = self._client.describe_db_subnet_groups(MaxRecords=50)
        return [
            {
                "name": sg.get("DBSubnetGroupName", ""),
                "description": sg.get("DBSubnetGroupDescription", ""),
                "vpc_id": sg.get("VpcId", ""),
                "status": sg.get("SubnetGroupStatus", ""),
                "subnets": len(sg.get("Subnets", [])),
            }
            for sg in resp.get("DBSubnetGroups", [])
        ]
