"""
Infrastructure Automation Service
Manages Terraform configs, Lambda status, and deployment tracking.
"""

from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone
from typing import Optional
import os
import json

_db: Optional[AsyncIOMotorDatabase] = None

INFRA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "infra")
LAMBDA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "lambda")
GH_WORKFLOWS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".github", "workflows")

ENVIRONMENTS = ["dev", "staging", "prod"]


def initialize_iac_service(db: AsyncIOMotorDatabase):
    global _db
    _db = db
    return True


def get_iac_service():
    return IaCService(_db)


def _read_file_safe(path: str) -> Optional[str]:
    try:
        with open(path, "r") as f:
            return f.read()
    except Exception:
        return None


def _parse_tfvars(content: str) -> dict:
    result = {}
    if not content:
        return result
    for line in content.strip().split("\n"):
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("tags"):
            break
        key, val = line.split("=", 1)
        result[key.strip()] = val.strip().strip('"')
    return result


class IaCService:
    def __init__(self, db):
        self.db = db

    async def get_overview(self) -> dict:
        tf_exists = os.path.isfile(os.path.join(INFRA_DIR, "main.tf"))
        lambda_exists = os.path.isfile(os.path.join(LAMBDA_DIR, "remediation_lambda.py"))
        workflow_exists = os.path.isfile(os.path.join(GH_WORKFLOWS_DIR, "build-lambda.yml"))

        envs = []
        for env_name in ENVIRONMENTS:
            path = os.path.join(INFRA_DIR, "environments", f"{env_name}.tfvars")
            exists = os.path.isfile(path)
            envs.append({"name": env_name, "configured": exists})

        deploy_count = await self.db.iac_deployments.count_documents({})
        last_deploy = await self.db.iac_deployments.find_one(
            {}, sort=[("deployed_at", -1)], projection={"_id": 0}
        )

        return {
            "terraform": {"configured": tf_exists, "directory": "infra/"},
            "lambda": {"configured": lambda_exists, "directory": "lambda/"},
            "github_actions": {"configured": workflow_exists, "file": ".github/workflows/build-lambda.yml"},
            "environments": envs,
            "total_deployments": deploy_count,
            "last_deployment": last_deploy,
        }

    async def get_terraform_configs(self) -> dict:
        main_tf = _read_file_safe(os.path.join(INFRA_DIR, "main.tf"))
        variables_tf = _read_file_safe(os.path.join(INFRA_DIR, "variables.tf"))
        outputs_tf = _read_file_safe(os.path.join(INFRA_DIR, "outputs.tf"))

        env_configs = {}
        for env_name in ENVIRONMENTS:
            path = os.path.join(INFRA_DIR, "environments", f"{env_name}.tfvars")
            raw = _read_file_safe(path)
            env_configs[env_name] = {
                "exists": raw is not None,
                "parsed": _parse_tfvars(raw) if raw else {},
                "raw": raw,
            }

        return {
            "main_tf": main_tf,
            "variables_tf": variables_tf,
            "outputs_tf": outputs_tf,
            "environments": env_configs,
        }

    async def get_lambda_config(self) -> dict:
        handler_code = _read_file_safe(os.path.join(LAMBDA_DIR, "remediation_lambda.py"))
        requirements = _read_file_safe(os.path.join(LAMBDA_DIR, "requirements.txt"))
        package_script = _read_file_safe(os.path.join(LAMBDA_DIR, "package.sh"))

        return {
            "handler": {
                "file": "lambda/remediation_lambda.py",
                "exists": handler_code is not None,
                "lines": len(handler_code.split("\n")) if handler_code else 0,
            },
            "requirements": {
                "file": "lambda/requirements.txt",
                "content": requirements,
                "packages": [
                    l.strip() for l in (requirements or "").split("\n") if l.strip() and not l.startswith("#")
                ],
            },
            "package_script": {
                "file": "lambda/package.sh",
                "exists": package_script is not None,
            },
            "runtime": "python3.12",
            "handler_entry": "remediation_lambda.handler",
            "timeout": 60,
            "memory_mb": 256,
        }

    async def get_workflow_config(self) -> dict:
        workflow_path = os.path.join(GH_WORKFLOWS_DIR, "build-lambda.yml")
        content = _read_file_safe(workflow_path)
        return {
            "file": ".github/workflows/build-lambda.yml",
            "exists": content is not None,
            "content": content,
        }

    async def get_deployments(self, limit: int = 20) -> list:
        cursor = self.db.iac_deployments.find(
            {}, {"_id": 0}
        ).sort("deployed_at", -1).limit(limit)
        return await cursor.to_list(length=limit)

    async def record_deployment(self, data: dict) -> dict:
        record = {
            "environment": data["environment"],
            "component": data.get("component", "lambda"),
            "version": data.get("version", ""),
            "status": data.get("status", "success"),
            "deployed_by": data.get("deployed_by", "manual"),
            "notes": data.get("notes", ""),
            "deployed_at": datetime.now(timezone.utc).isoformat(),
        }
        result = await self.db.iac_deployments.insert_one(record)
        record.pop("_id", None)
        return record

    async def get_deployment_commands(self, environment: str) -> dict:
        return {
            "environment": environment,
            "steps": [
                {
                    "title": "1. Package Lambda",
                    "command": "chmod +x lambda/package.sh && ./lambda/package.sh",
                    "description": "Builds remediation.zip with handler and dependencies",
                },
                {
                    "title": "2. Upload to S3",
                    "command": f"aws s3 cp lambda/remediation.zip s3://model-agency-assets/remediation-{environment}.zip",
                    "description": f"Uploads artifact for {environment} environment",
                },
                {
                    "title": "3. Initialize Terraform",
                    "command": "cd infra && terraform init",
                    "description": "Initializes Terraform with S3 backend",
                },
                {
                    "title": "4. Select workspace",
                    "command": f"terraform workspace select {environment} || terraform workspace new {environment}",
                    "description": f"Switches to {environment} workspace",
                },
                {
                    "title": "5. Plan changes",
                    "command": f"terraform plan -var-file=./environments/{environment}.tfvars",
                    "description": "Preview infrastructure changes before applying",
                },
                {
                    "title": "6. Apply changes",
                    "command": f"terraform apply -var-file=./environments/{environment}.tfvars -auto-approve",
                    "description": "Deploy infrastructure to AWS",
                },
            ],
        }
