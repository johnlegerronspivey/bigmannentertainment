"""AWS WorkMail Service - Business email management."""
import os
import logging
import boto3
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class WorkMailService:
    def __init__(self):
        self.region = os.environ.get("AWS_REGION", "us-east-1")
        self.available = False
        self._client = None

        try:
            self._client = boto3.client(
                "workmail",
                aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
                region_name=self.region,
            )
            self._client.list_organizations(MaxResults=1)
            self.available = True
        except Exception as e:
            logger.warning(f"WorkMail init failed: {e}")

    def get_status(self) -> Dict[str, Any]:
        if not self.available:
            return {"available": False}
        try:
            resp = self._client.list_organizations(MaxResults=1)
            org_count = len(resp.get("OrganizationSummaries", []))
            return {
                "available": True,
                "region": self.region,
                "service": "Amazon WorkMail",
                "organizations_found": org_count,
            }
        except Exception as e:
            return {"available": False, "error": str(e)}

    # ------------------------------------------------------------------
    # Organizations
    # ------------------------------------------------------------------
    def list_organizations(self, max_results: int = 50) -> List[Dict[str, Any]]:
        if not self.available:
            raise RuntimeError("WorkMail not available")
        resp = self._client.list_organizations(MaxResults=max_results)
        orgs = []
        for o in resp.get("OrganizationSummaries", []):
            orgs.append({
                "organization_id": o["OrganizationId"],
                "alias": o.get("Alias", ""),
                "default_mail_domain": o.get("DefaultMailDomain", ""),
                "error_message": o.get("ErrorMessage", ""),
                "state": o.get("State", "Unknown"),
            })
        return orgs

    def describe_organization(self, organization_id: str) -> Dict[str, Any]:
        if not self.available:
            raise RuntimeError("WorkMail not available")
        resp = self._client.describe_organization(OrganizationId=organization_id)
        return {
            "organization_id": resp.get("OrganizationId", ""),
            "alias": resp.get("Alias", ""),
            "default_mail_domain": resp.get("DefaultMailDomain", ""),
            "state": resp.get("State", ""),
            "directory_id": resp.get("DirectoryId", ""),
            "directory_type": resp.get("DirectoryType", ""),
            "completed_date": resp.get("CompletedDate", ""),
            "error_message": resp.get("ErrorMessage", ""),
        }

    # ------------------------------------------------------------------
    # Users
    # ------------------------------------------------------------------
    def list_users(self, organization_id: str, max_results: int = 50) -> List[Dict[str, Any]]:
        if not self.available:
            raise RuntimeError("WorkMail not available")
        resp = self._client.list_users(
            OrganizationId=organization_id, MaxResults=max_results
        )
        users = []
        for u in resp.get("Users", []):
            users.append({
                "entity_id": u.get("Id", ""),
                "name": u.get("Name", ""),
                "email": u.get("Email", ""),
                "state": u.get("State", ""),
                "user_role": u.get("UserRole", ""),
                "enabled_date": str(u.get("EnabledDate", "")),
                "disabled_date": str(u.get("DisabledDate", "")),
            })
        return users

    def create_user(self, organization_id: str, name: str, display_name: str,
                    password: str) -> Dict[str, Any]:
        if not self.available:
            raise RuntimeError("WorkMail not available")
        resp = self._client.create_user(
            OrganizationId=organization_id,
            Name=name,
            DisplayName=display_name,
            Password=password,
        )
        return {
            "user_id": resp["UserId"],
            "name": name,
            "display_name": display_name,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    def register_to_workmail(self, organization_id: str, entity_id: str,
                             email: str) -> bool:
        if not self.available:
            raise RuntimeError("WorkMail not available")
        try:
            self._client.register_to_work_mail(
                OrganizationId=organization_id,
                EntityId=entity_id,
                Email=email,
            )
            return True
        except Exception as e:
            logger.error(f"Register user failed: {e}")
            return False

    def deregister_from_workmail(self, organization_id: str,
                                 entity_id: str) -> bool:
        if not self.available:
            raise RuntimeError("WorkMail not available")
        try:
            self._client.deregister_from_work_mail(
                OrganizationId=organization_id, EntityId=entity_id
            )
            return True
        except Exception as e:
            logger.error(f"Deregister user failed: {e}")
            return False

    def delete_user(self, organization_id: str, user_id: str) -> bool:
        if not self.available:
            raise RuntimeError("WorkMail not available")
        try:
            self._client.delete_user(
                OrganizationId=organization_id, UserId=user_id
            )
            return True
        except Exception as e:
            logger.error(f"Delete user failed: {e}")
            return False

    # ------------------------------------------------------------------
    # Groups
    # ------------------------------------------------------------------
    def list_groups(self, organization_id: str, max_results: int = 50) -> List[Dict[str, Any]]:
        if not self.available:
            raise RuntimeError("WorkMail not available")
        resp = self._client.list_groups(
            OrganizationId=organization_id, MaxResults=max_results
        )
        groups = []
        for g in resp.get("Groups", []):
            groups.append({
                "entity_id": g.get("Id", ""),
                "name": g.get("Name", ""),
                "email": g.get("Email", ""),
                "state": g.get("State", ""),
                "enabled_date": str(g.get("EnabledDate", "")),
                "disabled_date": str(g.get("DisabledDate", "")),
            })
        return groups
