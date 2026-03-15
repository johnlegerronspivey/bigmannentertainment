"""Amazon Managed Blockchain Service - Blockchain network management."""
import os
import logging
import boto3
from typing import Dict, Any, List
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class ManagedBlockchainService:
    def __init__(self):
        self.region = os.environ.get("AWS_REGION", "us-east-1")
        self.available = False
        self._client = None

        try:
            self._client = boto3.client(
                "managedblockchain",
                aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
                region_name=self.region,
            )
            self._client.list_networks(MaxResults=1)
            self.available = True
        except Exception as e:
            logger.warning(f"Managed Blockchain init failed: {e}")

    def get_status(self) -> Dict[str, Any]:
        if not self.available:
            return {"available": False}
        return {
            "available": True,
            "region": self.region,
            "service": "Amazon Managed Blockchain",
        }

    def list_networks(self) -> List[Dict[str, Any]]:
        if not self.available:
            raise RuntimeError("Managed Blockchain not available")
        resp = self._client.list_networks(MaxResults=20)
        return [
            {
                "id": n.get("Id", ""),
                "name": n.get("Name", ""),
                "framework": n.get("Framework", ""),
                "framework_version": n.get("FrameworkVersion", ""),
                "status": n.get("Status", ""),
                "description": n.get("Description", ""),
                "created_at": n.get("CreationDate", "").isoformat() if n.get("CreationDate") else "",
            }
            for n in resp.get("Networks", [])
        ]

    def get_network(self, network_id: str) -> Dict[str, Any]:
        if not self.available:
            raise RuntimeError("Managed Blockchain not available")
        resp = self._client.get_network(NetworkId=network_id)
        n = resp.get("Network", {})
        voting = n.get("VotingPolicy", {}).get("ApprovalThresholdPolicy", {})
        framework_attrs = n.get("FrameworkAttributes", {})
        return {
            "id": n.get("Id", ""),
            "name": n.get("Name", ""),
            "framework": n.get("Framework", ""),
            "framework_version": n.get("FrameworkVersion", ""),
            "status": n.get("Status", ""),
            "description": n.get("Description", ""),
            "voting_policy": {
                "threshold_percentage": voting.get("ThresholdPercentage", 0),
                "proposal_duration": voting.get("ProposalDurationInHours", 0),
                "threshold_comparator": voting.get("ThresholdComparator", ""),
            },
            "framework_attributes": {
                "ordering_service": framework_attrs.get("Fabric", {}).get("OrderingServiceEndpoint", ""),
                "edition": framework_attrs.get("Fabric", {}).get("Edition", ""),
            } if "Fabric" in framework_attrs else {},
            "created_at": n.get("CreationDate", "").isoformat() if n.get("CreationDate") else "",
        }

    def list_members(self, network_id: str) -> List[Dict[str, Any]]:
        if not self.available:
            raise RuntimeError("Managed Blockchain not available")
        resp = self._client.list_members(NetworkId=network_id, MaxResults=20)
        return [
            {
                "id": m.get("Id", ""),
                "name": m.get("Name", ""),
                "status": m.get("Status", ""),
                "is_owned": m.get("IsOwned", False),
                "description": m.get("Description", ""),
                "created_at": m.get("CreationDate", "").isoformat() if m.get("CreationDate") else "",
            }
            for m in resp.get("Members", [])
        ]

    def list_nodes(self, network_id: str, member_id: str) -> List[Dict[str, Any]]:
        if not self.available:
            raise RuntimeError("Managed Blockchain not available")
        resp = self._client.list_nodes(
            NetworkId=network_id, MemberId=member_id, MaxResults=20
        )
        return [
            {
                "id": node.get("Id", ""),
                "status": node.get("Status", ""),
                "instance_type": node.get("InstanceType", ""),
                "availability_zone": node.get("AvailabilityZone", ""),
                "created_at": node.get("CreationDate", "").isoformat() if node.get("CreationDate") else "",
            }
            for node in resp.get("Nodes", [])
        ]

    def get_node(self, network_id: str, member_id: str, node_id: str) -> Dict[str, Any]:
        if not self.available:
            raise RuntimeError("Managed Blockchain not available")
        resp = self._client.get_node(
            NetworkId=network_id, MemberId=member_id, NodeId=node_id
        )
        node = resp.get("Node", {})
        return {
            "id": node.get("Id", ""),
            "network_id": node.get("NetworkId", ""),
            "member_id": node.get("MemberId", ""),
            "status": node.get("Status", ""),
            "instance_type": node.get("InstanceType", ""),
            "availability_zone": node.get("AvailabilityZone", ""),
            "framework_attributes": node.get("FrameworkAttributes", {}),
            "log_publishing": node.get("LogPublishingConfiguration", {}),
            "state_db": node.get("StateDB", ""),
            "created_at": node.get("CreationDate", "").isoformat() if node.get("CreationDate") else "",
        }

    def list_proposals(self, network_id: str) -> List[Dict[str, Any]]:
        if not self.available:
            raise RuntimeError("Managed Blockchain not available")
        resp = self._client.list_proposals(NetworkId=network_id, MaxResults=20)
        return [
            {
                "id": p.get("ProposalId", ""),
                "status": p.get("Status", ""),
                "description": p.get("Description", ""),
                "proposed_by_member_id": p.get("ProposedByMemberId", ""),
                "proposed_by_member_name": p.get("ProposedByMemberName", ""),
                "expiration_date": p.get("ExpirationDate", "").isoformat() if p.get("ExpirationDate") else "",
                "created_at": p.get("CreationDate", "").isoformat() if p.get("CreationDate") else "",
            }
            for p in resp.get("Proposals", [])
        ]

    def list_accessors(self) -> List[Dict[str, Any]]:
        if not self.available:
            raise RuntimeError("Managed Blockchain not available")
        resp = self._client.list_accessors(MaxResults=20)
        return [
            {
                "id": a.get("Id", ""),
                "type": a.get("Type", ""),
                "status": a.get("Status", ""),
                "arn": a.get("Arn", ""),
                "network_type": a.get("NetworkType", ""),
                "created_at": a.get("CreationDate", "").isoformat() if a.get("CreationDate") else "",
            }
            for a in resp.get("Accessors", [])
        ]
