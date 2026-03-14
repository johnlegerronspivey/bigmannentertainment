"""AWS WAF Service - Web Application Firewall management."""
import os
import logging
import boto3
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class WAFService:
    def __init__(self):
        self.region = os.environ.get("AWS_REGION", "us-east-1")
        self.available = False
        self._client = None

        try:
            self._client = boto3.client(
                "wafv2",
                aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
                region_name=self.region,
            )
            self._client.list_web_acls(Scope="REGIONAL", Limit=1)
            self.available = True
        except Exception as e:
            logger.warning(f"WAF init failed: {e}")

    def get_status(self) -> Dict[str, Any]:
        if not self.available:
            return {"available": False}
        try:
            regional = self._client.list_web_acls(Scope="REGIONAL", Limit=1)
            regional_count = len(regional.get("WebACLs", []))
            return {
                "available": True,
                "region": self.region,
                "service": "AWS WAF v2",
                "web_acls_found": regional_count,
            }
        except Exception as e:
            return {"available": False, "error": str(e)}

    # ------------------------------------------------------------------
    # Web ACLs
    # ------------------------------------------------------------------
    def list_web_acls(self, scope: str = "REGIONAL", limit: int = 50) -> List[Dict[str, Any]]:
        if not self.available:
            raise RuntimeError("WAF not available")
        resp = self._client.list_web_acls(Scope=scope, Limit=limit)
        acls = []
        for a in resp.get("WebACLs", []):
            acls.append({
                "name": a.get("Name", ""),
                "id": a.get("Id", ""),
                "arn": a.get("ARN", ""),
                "description": a.get("Description", ""),
                "lock_token": a.get("LockToken", ""),
            })
        return acls

    def get_web_acl(self, name: str, acl_id: str, scope: str = "REGIONAL") -> Dict[str, Any]:
        if not self.available:
            raise RuntimeError("WAF not available")
        resp = self._client.get_web_acl(Name=name, Id=acl_id, Scope=scope)
        acl = resp.get("WebACL", {})
        return {
            "name": acl.get("Name", ""),
            "id": acl.get("Id", ""),
            "arn": acl.get("ARN", ""),
            "description": acl.get("Description", ""),
            "capacity": acl.get("Capacity", 0),
            "default_action": "allow" if "Allow" in acl.get("DefaultAction", {}) else "block",
            "rules_count": len(acl.get("Rules", [])),
            "rules": [
                {
                    "name": r.get("Name", ""),
                    "priority": r.get("Priority", 0),
                    "action": "allow" if "Allow" in r.get("Action", {}) else ("block" if "Block" in r.get("Action", {}) else "count"),
                }
                for r in acl.get("Rules", [])
            ],
            "visibility_config": acl.get("VisibilityConfig", {}),
            "lock_token": resp.get("LockToken", ""),
        }

    def create_web_acl(self, name: str, scope: str = "REGIONAL",
                       default_action: str = "allow",
                       description: str = "") -> Dict[str, Any]:
        if not self.available:
            raise RuntimeError("WAF not available")
        action = {"Allow": {}} if default_action == "allow" else {"Block": {}}
        resp = self._client.create_web_acl(
            Name=name,
            Scope=scope,
            DefaultAction=action,
            Description=description or f"Web ACL created by Big Mann Entertainment",
            Rules=[],
            VisibilityConfig={
                "SampledRequestsEnabled": True,
                "CloudWatchMetricsEnabled": True,
                "MetricName": name.replace("-", "").replace("_", ""),
            },
            Tags=[
                {"Key": "Project", "Value": "BigMannEntertainment"},
                {"Key": "ManagedBy", "Value": "Platform"},
            ],
        )
        summary = resp.get("Summary", {})
        return {
            "name": summary.get("Name", name),
            "id": summary.get("Id", ""),
            "arn": summary.get("ARN", ""),
            "lock_token": summary.get("LockToken", ""),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    def delete_web_acl(self, name: str, acl_id: str, lock_token: str,
                       scope: str = "REGIONAL") -> bool:
        if not self.available:
            raise RuntimeError("WAF not available")
        try:
            self._client.delete_web_acl(
                Name=name, Id=acl_id, Scope=scope, LockToken=lock_token
            )
            return True
        except Exception as e:
            logger.error(f"Delete web ACL failed: {e}")
            return False

    # ------------------------------------------------------------------
    # IP Sets
    # ------------------------------------------------------------------
    def list_ip_sets(self, scope: str = "REGIONAL", limit: int = 50) -> List[Dict[str, Any]]:
        if not self.available:
            raise RuntimeError("WAF not available")
        resp = self._client.list_ip_sets(Scope=scope, Limit=limit)
        sets = []
        for s in resp.get("IPSets", []):
            sets.append({
                "name": s.get("Name", ""),
                "id": s.get("Id", ""),
                "arn": s.get("ARN", ""),
                "description": s.get("Description", ""),
                "lock_token": s.get("LockToken", ""),
            })
        return sets

    def create_ip_set(self, name: str, addresses: List[str],
                      ip_version: str = "IPV4",
                      scope: str = "REGIONAL",
                      description: str = "") -> Dict[str, Any]:
        if not self.available:
            raise RuntimeError("WAF not available")
        resp = self._client.create_ip_set(
            Name=name,
            Scope=scope,
            Description=description or f"IP set managed by Big Mann Entertainment",
            IPAddressVersion=ip_version,
            Addresses=addresses,
            Tags=[
                {"Key": "Project", "Value": "BigMannEntertainment"},
            ],
        )
        summary = resp.get("Summary", {})
        return {
            "name": summary.get("Name", name),
            "id": summary.get("Id", ""),
            "arn": summary.get("ARN", ""),
            "lock_token": summary.get("LockToken", ""),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    def get_ip_set(self, name: str, ip_set_id: str, scope: str = "REGIONAL") -> Dict[str, Any]:
        if not self.available:
            raise RuntimeError("WAF not available")
        resp = self._client.get_ip_set(Name=name, Id=ip_set_id, Scope=scope)
        ip_set = resp.get("IPSet", {})
        return {
            "name": ip_set.get("Name", ""),
            "id": ip_set.get("Id", ""),
            "arn": ip_set.get("ARN", ""),
            "description": ip_set.get("Description", ""),
            "ip_version": ip_set.get("IPAddressVersion", ""),
            "addresses": ip_set.get("Addresses", []),
            "lock_token": resp.get("LockToken", ""),
        }

    def delete_ip_set(self, name: str, ip_set_id: str, lock_token: str,
                      scope: str = "REGIONAL") -> bool:
        if not self.available:
            raise RuntimeError("WAF not available")
        try:
            self._client.delete_ip_set(
                Name=name, Id=ip_set_id, Scope=scope, LockToken=lock_token
            )
            return True
        except Exception as e:
            logger.error(f"Delete IP set failed: {e}")
            return False

    # ------------------------------------------------------------------
    # Rule Groups
    # ------------------------------------------------------------------
    def list_rule_groups(self, scope: str = "REGIONAL", limit: int = 50) -> List[Dict[str, Any]]:
        if not self.available:
            raise RuntimeError("WAF not available")
        resp = self._client.list_rule_groups(Scope=scope, Limit=limit)
        groups = []
        for g in resp.get("RuleGroups", []):
            groups.append({
                "name": g.get("Name", ""),
                "id": g.get("Id", ""),
                "arn": g.get("ARN", ""),
                "description": g.get("Description", ""),
                "lock_token": g.get("LockToken", ""),
            })
        return groups

    def list_available_managed_rule_groups(self, scope: str = "REGIONAL") -> List[Dict[str, Any]]:
        if not self.available:
            raise RuntimeError("WAF not available")
        resp = self._client.list_available_managed_rule_groups(Scope=scope)
        groups = []
        for g in resp.get("ManagedRuleGroups", []):
            groups.append({
                "vendor": g.get("VendorName", ""),
                "name": g.get("Name", ""),
                "description": g.get("Description", ""),
            })
        return groups

    # ------------------------------------------------------------------
    # Resource Associations
    # ------------------------------------------------------------------
    def list_resources_for_web_acl(self, web_acl_arn: str) -> List[str]:
        if not self.available:
            raise RuntimeError("WAF not available")
        try:
            resp = self._client.list_resources_for_web_acl(WebACLArn=web_acl_arn)
            return resp.get("ResourceArns", [])
        except Exception as e:
            logger.error(f"List resources for web ACL failed: {e}")
            return []
