"""AWS Secrets Manager Service - Secure secret storage and rotation."""
import os
import logging
import json
import boto3
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class SecretsManagerService:
    def __init__(self):
        self.region = os.environ.get("AWS_REGION", "us-east-1")
        self.available = False
        self._client = None

        try:
            self._client = boto3.client(
                "secretsmanager",
                aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
                region_name=self.region,
            )
            self._client.list_secrets(MaxResults=1)
            self.available = True
        except Exception as e:
            logger.warning(f"Secrets Manager init failed: {e}")

    def get_status(self) -> Dict[str, Any]:
        if not self.available:
            return {"available": False}
        try:
            resp = self._client.list_secrets(MaxResults=1)
            return {
                "available": True,
                "region": self.region,
                "service": "AWS Secrets Manager",
                "secrets_found": len(resp.get("SecretList", [])),
            }
        except Exception as e:
            return {"available": False, "error": str(e)}

    # ------------------------------------------------------------------
    # Secrets CRUD
    # ------------------------------------------------------------------
    def list_secrets(self, max_results: int = 50) -> List[Dict[str, Any]]:
        if not self.available:
            raise RuntimeError("Secrets Manager not available")
        resp = self._client.list_secrets(MaxResults=max_results)
        secrets = []
        for s in resp.get("SecretList", []):
            secrets.append({
                "name": s.get("Name", ""),
                "arn": s.get("ARN", ""),
                "description": s.get("Description", ""),
                "created_date": s.get("CreatedDate", "").isoformat() if hasattr(s.get("CreatedDate", ""), "isoformat") else str(s.get("CreatedDate", "")),
                "last_changed_date": s.get("LastChangedDate", "").isoformat() if hasattr(s.get("LastChangedDate", ""), "isoformat") else str(s.get("LastChangedDate", "")),
                "last_accessed_date": s.get("LastAccessedDate", "").isoformat() if hasattr(s.get("LastAccessedDate", ""), "isoformat") else str(s.get("LastAccessedDate", "")),
                "rotation_enabled": s.get("RotationEnabled", False),
                "tags": {t["Key"]: t["Value"] for t in s.get("Tags", [])},
            })
        return secrets

    def describe_secret(self, secret_id: str) -> Dict[str, Any]:
        if not self.available:
            raise RuntimeError("Secrets Manager not available")
        s = self._client.describe_secret(SecretId=secret_id)
        return {
            "name": s.get("Name", ""),
            "arn": s.get("ARN", ""),
            "description": s.get("Description", ""),
            "created_date": s.get("CreatedDate", "").isoformat() if hasattr(s.get("CreatedDate", ""), "isoformat") else str(s.get("CreatedDate", "")),
            "last_changed_date": s.get("LastChangedDate", "").isoformat() if hasattr(s.get("LastChangedDate", ""), "isoformat") else str(s.get("LastChangedDate", "")),
            "last_accessed_date": s.get("LastAccessedDate", "").isoformat() if hasattr(s.get("LastAccessedDate", ""), "isoformat") else str(s.get("LastAccessedDate", "")),
            "rotation_enabled": s.get("RotationEnabled", False),
            "rotation_lambda_arn": s.get("RotationLambdaARN", ""),
            "rotation_rules": s.get("RotationRules", {}),
            "version_ids": s.get("VersionIdsToStages", {}),
            "tags": {t["Key"]: t["Value"] for t in s.get("Tags", [])},
        }

    def create_secret(self, name: str, secret_value: str,
                      description: str = "",
                      is_json: bool = False) -> Dict[str, Any]:
        if not self.available:
            raise RuntimeError("Secrets Manager not available")
        kwargs = {
            "Name": name,
            "Description": description or f"Secret managed by Big Mann Entertainment",
            "Tags": [
                {"Key": "Project", "Value": "BigMannEntertainment"},
                {"Key": "ManagedBy", "Value": "Platform"},
            ],
        }
        if is_json:
            kwargs["SecretString"] = secret_value
        else:
            kwargs["SecretString"] = secret_value

        resp = self._client.create_secret(**kwargs)
        return {
            "name": resp.get("Name", name),
            "arn": resp.get("ARN", ""),
            "version_id": resp.get("VersionId", ""),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    def update_secret(self, secret_id: str, secret_value: str,
                      description: Optional[str] = None) -> Dict[str, Any]:
        if not self.available:
            raise RuntimeError("Secrets Manager not available")
        kwargs = {"SecretId": secret_id, "SecretString": secret_value}
        if description is not None:
            kwargs["Description"] = description
        resp = self._client.update_secret(**kwargs)
        return {
            "name": resp.get("Name", ""),
            "arn": resp.get("ARN", ""),
            "version_id": resp.get("VersionId", ""),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

    def delete_secret(self, secret_id: str, force: bool = False) -> bool:
        if not self.available:
            raise RuntimeError("Secrets Manager not available")
        try:
            kwargs = {"SecretId": secret_id}
            if force:
                kwargs["ForceDeleteWithoutRecovery"] = True
            else:
                kwargs["RecoveryWindowInDays"] = 7
            self._client.delete_secret(**kwargs)
            return True
        except Exception as e:
            logger.error(f"Delete secret failed: {e}")
            return False

    def get_secret_value(self, secret_id: str) -> Dict[str, Any]:
        """Get the actual secret value. Use with caution - returns plaintext."""
        if not self.available:
            raise RuntimeError("Secrets Manager not available")
        resp = self._client.get_secret_value(SecretId=secret_id)
        value = resp.get("SecretString", "")
        is_json = False
        try:
            json.loads(value)
            is_json = True
        except (json.JSONDecodeError, TypeError):
            pass
        return {
            "name": resp.get("Name", ""),
            "arn": resp.get("ARN", ""),
            "version_id": resp.get("VersionId", ""),
            "is_json": is_json,
            "key_count": len(json.loads(value)) if is_json else 0,
        }

    def rotate_secret(self, secret_id: str, rotation_lambda_arn: str = "",
                      days: int = 30) -> Dict[str, Any]:
        if not self.available:
            raise RuntimeError("Secrets Manager not available")
        kwargs = {
            "SecretId": secret_id,
            "RotationRules": {"AutomaticallyAfterDays": days},
        }
        if rotation_lambda_arn:
            kwargs["RotationLambdaARN"] = rotation_lambda_arn
        resp = self._client.rotate_secret(**kwargs)
        return {
            "name": resp.get("Name", ""),
            "arn": resp.get("ARN", ""),
            "version_id": resp.get("VersionId", ""),
            "rotated_at": datetime.now(timezone.utc).isoformat(),
        }

    def tag_secret(self, secret_id: str, tags: Dict[str, str]) -> bool:
        if not self.available:
            raise RuntimeError("Secrets Manager not available")
        try:
            tag_list = [{"Key": k, "Value": v} for k, v in tags.items()]
            self._client.tag_resource(SecretId=secret_id, Tags=tag_list)
            return True
        except Exception as e:
            logger.error(f"Tag secret failed: {e}")
            return False
