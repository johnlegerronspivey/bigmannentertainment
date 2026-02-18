"""
Infrastructure Automation Service
Manages Terraform configs, Lambda status, and deployment tracking.
Supports LIVE mode (real AWS/GitHub API calls) with graceful fallback to local file reading.
"""

from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone, timedelta
from typing import Optional
import os
import json
import logging
import boto3
from botocore.exceptions import ClientError, NoCredentialsError, BotoCoreError
from github import Github, GithubException

logger = logging.getLogger(__name__)

_db: Optional[AsyncIOMotorDatabase] = None

INFRA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "infra")
LAMBDA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "lambda")
GH_WORKFLOWS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".github", "workflows")

ENVIRONMENTS = ["dev", "staging", "prod"]

# AWS / GitHub config from env
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
S3_BUCKET = os.environ.get("S3_BUCKET_NAME", "")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPO = os.environ.get("GITHUB_REPO", "")
LAMBDA_FUNCTION_PREFIX = os.environ.get("LAMBDA_FUNCTION_PREFIX", "cve-remediation")


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


def _build_boto3_client(service_name: str):
    """Build a boto3 client, returns None if credentials are missing."""
    try:
        return boto3.client(service_name, region_name=AWS_REGION)
    except (NoCredentialsError, BotoCoreError) as e:
        logger.warning("Cannot create %s client: %s", service_name, e)
        return None


def _build_github_client():
    """Build a PyGitHub client, returns None if token is missing."""
    if not GITHUB_TOKEN:
        return None
    try:
        return Github(GITHUB_TOKEN)
    except Exception as e:
        logger.warning("Cannot create GitHub client: %s", e)
        return None


class IaCService:
    def __init__(self, db):
        self.db = db
        self._lambda_client = _build_boto3_client("lambda")
        self._s3_client = _build_boto3_client("s3")
        self._cw_client = _build_boto3_client("cloudwatch")
        self._gh = _build_github_client()

    # ── connection health ───────────────────────────────────────────
    async def get_live_status(self) -> dict:
        """Check connectivity to AWS Lambda, S3, and GitHub."""
        aws_lambda_ok = False
        aws_lambda_detail = "No credentials"
        aws_s3_ok = False
        aws_s3_detail = "No credentials"
        github_ok = False
        github_detail = "No token"
        github_user = None
        github_repo_name = None

        # AWS Lambda
        if self._lambda_client:
            try:
                resp = self._lambda_client.list_functions(MaxItems=1)
                aws_lambda_ok = True
                total = len(resp.get("Functions", []))
                aws_lambda_detail = f"Connected ({AWS_REGION})"
            except ClientError as e:
                aws_lambda_detail = f"Error: {e.response['Error']['Code']}"
            except Exception as e:
                aws_lambda_detail = f"Error: {str(e)[:80]}"

        # AWS S3
        if self._s3_client:
            try:
                self._s3_client.head_bucket(Bucket=S3_BUCKET) if S3_BUCKET else None
                if S3_BUCKET:
                    aws_s3_ok = True
                    aws_s3_detail = f"Connected ({S3_BUCKET})"
                else:
                    aws_s3_detail = "No S3_BUCKET_NAME configured"
            except ClientError as e:
                code = e.response["Error"]["Code"]
                if code == "404":
                    aws_s3_detail = f"Bucket '{S3_BUCKET}' not found"
                elif code == "403":
                    aws_s3_ok = True
                    aws_s3_detail = f"Connected ({S3_BUCKET}, limited access)"
                else:
                    aws_s3_detail = f"Error: {code}"
            except Exception as e:
                aws_s3_detail = f"Error: {str(e)[:80]}"

        # GitHub
        if self._gh:
            try:
                user = self._gh.get_user()
                github_user = user.login
                github_ok = True
                github_detail = f"Connected as {user.login}"
                if GITHUB_REPO:
                    github_repo_name = GITHUB_REPO
            except GithubException as e:
                github_detail = f"Auth error: {e.data.get('message', str(e))}" if hasattr(e, 'data') and e.data else f"Error: {str(e)[:80]}"
            except Exception as e:
                github_detail = f"Error: {str(e)[:80]}"

        return {
            "aws_lambda": {"connected": aws_lambda_ok, "detail": aws_lambda_detail, "region": AWS_REGION},
            "aws_s3": {"connected": aws_s3_ok, "detail": aws_s3_detail, "bucket": S3_BUCKET},
            "github": {"connected": github_ok, "detail": github_detail, "user": github_user, "repo": github_repo_name},
            "checked_at": datetime.now(timezone.utc).isoformat(),
        }

    # ── live Lambda data ────────────────────────────────────────────
    async def get_lambda_live(self) -> dict:
        """Fetch real Lambda function configurations and CloudWatch metrics."""
        if not self._lambda_client:
            return {"connected": False, "error": "AWS Lambda client not available", "functions": []}

        functions = []
        try:
            paginator = self._lambda_client.get_paginator("list_functions")
            for page in paginator.paginate(MaxItems=50):
                for fn in page.get("Functions", []):
                    fn_data = {
                        "name": fn["FunctionName"],
                        "runtime": fn.get("Runtime", "N/A"),
                        "handler": fn.get("Handler", "N/A"),
                        "memory_mb": fn.get("MemorySize", 0),
                        "timeout": fn.get("Timeout", 0),
                        "code_size_bytes": fn.get("CodeSize", 0),
                        "last_modified": fn.get("LastModified", ""),
                        "state": fn.get("State", "Unknown"),
                        "description": fn.get("Description", ""),
                        "architectures": fn.get("Architectures", []),
                        "layers": [l["Arn"].split(":")[-2] for l in fn.get("Layers", [])],
                    }
                    # Fetch CloudWatch metrics for the last 24h
                    metrics = self._get_lambda_metrics(fn["FunctionName"])
                    fn_data["metrics"] = metrics
                    functions.append(fn_data)
        except ClientError as e:
            return {"connected": True, "error": f"ListFunctions failed: {e.response['Error']['Code']}", "functions": []}
        except Exception as e:
            return {"connected": True, "error": str(e)[:120], "functions": []}

        return {"connected": True, "error": None, "functions": functions, "total": len(functions)}

    def _get_lambda_metrics(self, function_name: str) -> dict:
        """Get CloudWatch metrics for a Lambda function (last 24h)."""
        if not self._cw_client:
            return {}
        now = datetime.now(timezone.utc)
        start = now - timedelta(hours=24)
        metrics_out = {}
        for metric_name, stat in [("Invocations", "Sum"), ("Errors", "Sum"), ("Duration", "Average"), ("Throttles", "Sum")]:
            try:
                resp = self._cw_client.get_metric_statistics(
                    Namespace="AWS/Lambda",
                    MetricName=metric_name,
                    Dimensions=[{"Name": "FunctionName", "Value": function_name}],
                    StartTime=start,
                    EndTime=now,
                    Period=86400,
                    Statistics=[stat],
                )
                dps = resp.get("Datapoints", [])
                if dps:
                    metrics_out[metric_name.lower()] = round(dps[0].get(stat, 0), 2)
                else:
                    metrics_out[metric_name.lower()] = 0
            except Exception:
                metrics_out[metric_name.lower()] = None
        return metrics_out

    # ── live GitHub Actions data ────────────────────────────────────
    async def get_github_runs(self, limit: int = 15) -> dict:
        """Fetch GitHub Actions workflow runs."""
        if not self._gh:
            return {"connected": False, "error": "GitHub token not configured", "runs": []}

        if not GITHUB_REPO:
            # Try to discover repos with workflows
            try:
                user = self._gh.get_user()
                repos = []
                for repo in user.get_repos(sort="updated", direction="desc"):
                    repos.append({"full_name": repo.full_name, "private": repo.private, "updated_at": repo.updated_at.isoformat() if repo.updated_at else None})
                    if len(repos) >= 10:
                        break
                return {
                    "connected": True,
                    "error": "GITHUB_REPO not configured. Set it in .env to see workflow runs.",
                    "runs": [],
                    "available_repos": repos,
                }
            except GithubException as e:
                return {"connected": False, "error": f"GitHub API error: {str(e)[:100]}", "runs": []}

        try:
            repo = self._gh.get_repo(GITHUB_REPO)
            runs_list = []
            for run in repo.get_workflow_runs(status="completed")[:limit]:
                runs_list.append({
                    "id": run.id,
                    "name": run.name,
                    "status": run.status,
                    "conclusion": run.conclusion,
                    "branch": run.head_branch,
                    "event": run.event,
                    "created_at": run.created_at.isoformat() if run.created_at else None,
                    "updated_at": run.updated_at.isoformat() if run.updated_at else None,
                    "run_number": run.run_number,
                    "html_url": run.html_url,
                })
            return {"connected": True, "error": None, "runs": runs_list, "repo": GITHUB_REPO}
        except GithubException as e:
            msg = e.data.get("message", str(e)) if hasattr(e, "data") and e.data else str(e)
            return {"connected": True, "error": f"Repo error: {msg[:100]}", "runs": []}
        except Exception as e:
            return {"connected": False, "error": str(e)[:120], "runs": []}

    # ── live Terraform state from S3 ────────────────────────────────
    async def get_terraform_state(self, environment: str = "dev") -> dict:
        """Read Terraform state file from S3 backend."""
        if not self._s3_client or not S3_BUCKET:
            return {"connected": False, "error": "S3 client or bucket not configured", "resources": []}

        state_key = f"terraform/state/{environment}/terraform.tfstate"
        try:
            obj = self._s3_client.get_object(Bucket=S3_BUCKET, Key=state_key)
            body = obj["Body"].read().decode("utf-8")
            state = json.loads(body)
            resources = []
            for r in state.get("resources", []):
                resources.append({
                    "type": r.get("type", ""),
                    "name": r.get("name", ""),
                    "provider": r.get("provider", ""),
                    "module": r.get("module", ""),
                    "instances": len(r.get("instances", [])),
                })
            return {
                "connected": True,
                "error": None,
                "environment": environment,
                "serial": state.get("serial", 0),
                "terraform_version": state.get("terraform_version", ""),
                "resources": resources,
                "total_resources": len(resources),
            }
        except ClientError as e:
            code = e.response["Error"]["Code"]
            if code == "NoSuchKey":
                return {"connected": True, "error": f"No state file at s3://{S3_BUCKET}/{state_key}", "resources": []}
            return {"connected": True, "error": f"S3 error: {code}", "resources": []}
        except Exception as e:
            return {"connected": False, "error": str(e)[:120], "resources": []}

    # ── existing methods (kept for backward compatibility) ──────────
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

        # Augment with live connection status
        live = await self.get_live_status()

        return {
            "terraform": {"configured": tf_exists, "directory": "infra/"},
            "lambda": {"configured": lambda_exists, "directory": "lambda/"},
            "github_actions": {"configured": workflow_exists, "file": ".github/workflows/build-lambda.yml"},
            "environments": envs,
            "total_deployments": deploy_count,
            "last_deployment": last_deploy,
            "live_connections": live,
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
        await self.db.iac_deployments.insert_one(record)
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
