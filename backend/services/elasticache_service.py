"""AWS ElastiCache Service - Redis/Memcached caching layer."""
import os
import logging
import boto3
from typing import Dict, Any, List
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class ElastiCacheService:
    def __init__(self):
        self.region = os.environ.get("AWS_REGION", "us-east-1")
        self.available = False
        self._client = None
        try:
            self._client = boto3.client(
                "elasticache",
                aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
                region_name=self.region,
            )
            self._client.describe_cache_clusters(MaxRecords=20)
            self.available = True
        except Exception as e:
            logger.warning(f"ElastiCache init failed: {e}")

    def get_status(self) -> Dict[str, Any]:
        if not self.available:
            return {"available": False}
        return {"available": True, "region": self.region, "service": "Amazon ElastiCache"}

    def list_clusters(self) -> List[Dict[str, Any]]:
        resp = self._client.describe_cache_clusters(MaxRecords=100, ShowCacheNodeInfo=True)
        return [
            {
                "id": c.get("CacheClusterId", ""),
                "status": c.get("CacheClusterStatus", ""),
                "engine": c.get("Engine", ""),
                "engine_version": c.get("EngineVersion", ""),
                "node_type": c.get("CacheNodeType", ""),
                "num_nodes": c.get("NumCacheNodes", 0),
                "availability_zone": c.get("PreferredAvailabilityZone", ""),
                "created_at": c.get("CacheClusterCreateTime", "").isoformat() if c.get("CacheClusterCreateTime") else "",
            }
            for c in resp.get("CacheClusters", [])
        ]

    def list_replication_groups(self) -> List[Dict[str, Any]]:
        resp = self._client.describe_replication_groups(MaxRecords=100)
        return [
            {
                "id": rg.get("ReplicationGroupId", ""),
                "description": rg.get("Description", ""),
                "status": rg.get("Status", ""),
                "cluster_enabled": rg.get("ClusterEnabled", False),
                "automatic_failover": rg.get("AutomaticFailover", ""),
                "multi_az": rg.get("MultiAZ", ""),
                "member_clusters": rg.get("MemberClusters", []),
                "node_groups": len(rg.get("NodeGroups", [])),
            }
            for rg in resp.get("ReplicationGroups", [])
        ]

    def list_snapshots(self) -> List[Dict[str, Any]]:
        resp = self._client.describe_snapshots(MaxRecords=50)
        return [
            {
                "name": s.get("SnapshotName", ""),
                "status": s.get("SnapshotStatus", ""),
                "source": s.get("SnapshotSource", ""),
                "cache_cluster_id": s.get("CacheClusterId", ""),
                "engine": s.get("Engine", ""),
                "engine_version": s.get("EngineVersion", ""),
                "node_type": s.get("CacheNodeType", ""),
                "num_nodes": s.get("NumCacheNodes", 0),
            }
            for s in resp.get("Snapshots", [])
        ]

    def list_reserved_nodes(self) -> List[Dict[str, Any]]:
        try:
            resp = self._client.describe_reserved_cache_nodes(MaxRecords=50)
            return [
                {
                    "id": rn.get("ReservedCacheNodeId", ""),
                    "node_type": rn.get("CacheNodeType", ""),
                    "duration": rn.get("Duration", 0),
                    "count": rn.get("CacheNodeCount", 0),
                    "state": rn.get("State", ""),
                    "offering_type": rn.get("OfferingType", ""),
                }
                for rn in resp.get("ReservedCacheNodes", [])
            ]
        except ClientError:
            return []

    def list_subnet_groups(self) -> List[Dict[str, Any]]:
        resp = self._client.describe_cache_subnet_groups(MaxRecords=50)
        return [
            {
                "name": sg.get("CacheSubnetGroupName", ""),
                "description": sg.get("CacheSubnetGroupDescription", ""),
                "vpc_id": sg.get("VpcId", ""),
                "subnets": len(sg.get("Subnets", [])),
            }
            for sg in resp.get("CacheSubnetGroups", [])
        ]
