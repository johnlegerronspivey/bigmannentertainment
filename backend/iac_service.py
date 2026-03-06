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
import asyncio
import boto3
from botocore.exceptions import ClientError, NoCredentialsError, BotoCoreError
from github import Github, GithubException

logger = logging.getLogger(__name__)

_db: Optional[AsyncIOMotorDatabase] = None

INFRA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "infra")
INFRA_TF_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "infra-terraform")
INFRA_CDK_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "infra-cdk")
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
        self._rds_client = _build_boto3_client("rds")
        self._gh = _build_github_client()

    # ── connection health ───────────────────────────────────────────
    def _check_live_status_sync(self) -> dict:
        """Synchronous version - check connectivity to AWS Lambda, S3, and GitHub."""
        aws_lambda_ok = False
        aws_lambda_detail = "No credentials"
        aws_s3_ok = False
        aws_s3_detail = "No credentials"
        github_ok = False
        github_detail = "No token"
        github_user = None
        github_repo_name = None

        if self._lambda_client:
            try:
                self._lambda_client.list_functions(MaxItems=1)
                aws_lambda_ok = True
                aws_lambda_detail = f"Connected ({AWS_REGION})"
            except ClientError as e:
                aws_lambda_detail = f"Error: {e.response['Error']['Code']}"
            except Exception as e:
                aws_lambda_detail = f"Error: {str(e)[:80]}"

        if self._s3_client:
            try:
                if S3_BUCKET:
                    self._s3_client.head_bucket(Bucket=S3_BUCKET)
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

    async def get_live_status(self) -> dict:
        return await asyncio.to_thread(self._check_live_status_sync)

    # ── live Lambda data ────────────────────────────────────────────
    def _get_lambda_live_sync(self) -> dict:
        """Synchronous: fetch real Lambda function configurations and CloudWatch metrics."""
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
                        "layers": [layer["Arn"].split(":")[-2] for layer in fn.get("Layers", [])],
                    }
                    metrics = self._get_lambda_metrics(fn["FunctionName"])
                    fn_data["metrics"] = metrics
                    functions.append(fn_data)
        except ClientError as e:
            return {"connected": True, "error": f"ListFunctions failed: {e.response['Error']['Code']}", "functions": []}
        except Exception as e:
            return {"connected": True, "error": str(e)[:120], "functions": []}

        return {"connected": True, "error": None, "functions": functions, "total": len(functions)}

    async def get_lambda_live(self) -> dict:
        return await asyncio.to_thread(self._get_lambda_live_sync)
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
    def _get_github_runs_sync(self, limit: int = 15) -> dict:
        """Synchronous: fetch GitHub Actions workflow runs."""
        if not self._gh:
            return {"connected": False, "error": "GitHub token not configured", "runs": []}

        if not GITHUB_REPO:
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

    async def get_github_runs(self, limit: int = 15) -> dict:
        return await asyncio.to_thread(self._get_github_runs_sync, limit)

    # ── live GitHub repo info ───────────────────────────────────────
    def _get_github_repo_info_sync(self) -> dict:
        """Synchronous: fetch repo info, recent commits, branches, open PRs."""
        if not self._gh:
            return {"connected": False, "error": "GitHub token not configured"}
        if not GITHUB_REPO:
            return {"connected": True, "error": "GITHUB_REPO not configured"}

        try:
            repo = self._gh.get_repo(GITHUB_REPO)
            repo_info = {
                "name": repo.full_name,
                "description": repo.description,
                "default_branch": repo.default_branch,
                "stars": repo.stargazers_count,
                "forks": repo.forks_count,
                "open_issues": repo.open_issues_count,
                "language": repo.language,
                "private": repo.private,
                "size_kb": repo.size,
                "updated_at": repo.updated_at.isoformat() if repo.updated_at else None,
                "created_at": repo.created_at.isoformat() if repo.created_at else None,
            }

            commits = []
            for c in repo.get_commits().get_page(0)[:10]:
                commits.append({
                    "sha": c.sha[:7],
                    "message": c.commit.message.split("\n")[0][:120],
                    "author": c.commit.author.name if c.commit.author else "Unknown",
                    "date": c.commit.author.date.isoformat() if c.commit.author and c.commit.author.date else None,
                    "html_url": c.html_url,
                })

            branches = []
            for b in repo.get_branches().get_page(0)[:20]:
                branches.append({
                    "name": b.name,
                    "protected": b.protected,
                    "sha": b.commit.sha[:7],
                })

            pulls = []
            for pr in repo.get_pulls(state="open", sort="updated", direction="desc").get_page(0)[:10]:
                pulls.append({
                    "number": pr.number,
                    "title": pr.title[:120],
                    "state": pr.state,
                    "author": pr.user.login if pr.user else "Unknown",
                    "created_at": pr.created_at.isoformat() if pr.created_at else None,
                    "updated_at": pr.updated_at.isoformat() if pr.updated_at else None,
                    "html_url": pr.html_url,
                    "labels": [l.name for l in pr.labels],
                    "draft": pr.draft,
                })

            return {
                "connected": True,
                "error": None,
                "repo": repo_info,
                "commits": commits,
                "branches": branches,
                "pulls": pulls,
            }
        except GithubException as e:
            msg = e.data.get("message", str(e)) if hasattr(e, "data") and e.data else str(e)
            return {"connected": False, "error": f"GitHub error: {msg[:100]}"}
        except Exception as e:
            return {"connected": False, "error": str(e)[:120]}

    async def get_github_repo_info(self) -> dict:
        return await asyncio.to_thread(self._get_github_repo_info_sync)

    # ── live S3 artifacts ───────────────────────────────────────────
    def _get_s3_artifacts_sync(self, prefix: str = "", max_keys: int = 50) -> dict:
        """Synchronous: list objects in the S3 bucket."""
        if not self._s3_client or not S3_BUCKET:
            return {"connected": False, "error": "S3 client or bucket not configured", "objects": []}

        try:
            params = {"Bucket": S3_BUCKET, "MaxKeys": max_keys}
            if prefix:
                params["Prefix"] = prefix
            resp = self._s3_client.list_objects_v2(**params)
            objects = []
            for obj in resp.get("Contents", []):
                objects.append({
                    "key": obj["Key"],
                    "size_bytes": obj["Size"],
                    "size_display": self._format_size(obj["Size"]),
                    "last_modified": obj["LastModified"].isoformat() if obj.get("LastModified") else None,
                    "storage_class": obj.get("StorageClass", "STANDARD"),
                })

            total_size = sum(o["size_bytes"] for o in objects)
            return {
                "connected": True,
                "error": None,
                "bucket": S3_BUCKET,
                "prefix": prefix,
                "objects": objects,
                "total_objects": len(objects),
                "total_size": total_size,
                "total_size_display": self._format_size(total_size),
                "is_truncated": resp.get("IsTruncated", False),
            }
        except ClientError as e:
            return {"connected": True, "error": f"S3 error: {e.response['Error']['Code']}", "objects": []}
        except Exception as e:
            return {"connected": False, "error": str(e)[:120], "objects": []}

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

    async def get_s3_artifacts(self, prefix: str = "", max_keys: int = 50) -> dict:
        return await asyncio.to_thread(self._get_s3_artifacts_sync, prefix, max_keys)

    # ── live CloudWatch alarms ──────────────────────────────────────
    def _get_cloudwatch_alarms_sync(self) -> dict:
        """Synchronous: list CloudWatch alarms."""
        if not self._cw_client:
            return {"connected": False, "error": "CloudWatch client not available", "alarms": []}

        try:
            resp = self._cw_client.describe_alarms(MaxRecords=50)
            alarms = []
            for a in resp.get("MetricAlarms", []):
                alarms.append({
                    "name": a["AlarmName"],
                    "state": a["StateValue"],
                    "metric": a.get("MetricName", ""),
                    "namespace": a.get("Namespace", ""),
                    "description": a.get("AlarmDescription", ""),
                    "threshold": a.get("Threshold"),
                    "comparison": a.get("ComparisonOperator", ""),
                    "period": a.get("Period", 0),
                    "evaluation_periods": a.get("EvaluationPeriods", 0),
                    "updated_at": a["StateUpdatedTimestamp"].isoformat() if a.get("StateUpdatedTimestamp") else None,
                })

            composite = []
            for a in resp.get("CompositeAlarms", []):
                composite.append({
                    "name": a["AlarmName"],
                    "state": a["StateValue"],
                    "description": a.get("AlarmDescription", ""),
                    "rule": a.get("AlarmRule", ""),
                    "updated_at": a["StateUpdatedTimestamp"].isoformat() if a.get("StateUpdatedTimestamp") else None,
                })

            alarm_count = sum(1 for a in alarms if a["state"] == "ALARM")
            return {
                "connected": True,
                "error": None,
                "alarms": alarms,
                "composite_alarms": composite,
                "total": len(alarms) + len(composite),
                "in_alarm": alarm_count,
            }
        except ClientError as e:
            return {"connected": True, "error": f"CloudWatch error: {e.response['Error']['Code']}", "alarms": []}
        except Exception as e:
            return {"connected": False, "error": str(e)[:120], "alarms": []}

    async def get_cloudwatch_alarms(self) -> dict:
        return await asyncio.to_thread(self._get_cloudwatch_alarms_sync)

    # ── live Terraform state from S3 ────────────────────────────────
    def _get_terraform_state_sync(self, environment: str = "dev") -> dict:
        """Synchronous: read Terraform state file from S3 backend."""
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

    async def get_terraform_state(self, environment: str = "dev") -> dict:
        return await asyncio.to_thread(self._get_terraform_state_sync, environment)

    # ── Terraform modules structure ─────────────────────────────────
    async def get_terraform_modules(self) -> dict:
        """Scan infra-terraform/modules/ and return module metadata with file contents."""
        modules_dir = os.path.join(INFRA_TF_DIR, "modules")
        envs_dir = os.path.join(INFRA_TF_DIR, "envs")

        if not os.path.isdir(modules_dir):
            return {"exists": False, "error": "infra-terraform/modules/ not found", "modules": [], "environments": []}

        MODULE_DESCRIPTIONS = {
            "cognito": {"description": "User authentication via AWS Cognito", "icon": "shield", "category": "auth"},
            "s3-cloudfront": {"description": "Frontend hosting with S3 + CloudFront CDN", "icon": "globe", "category": "hosting"},
            "dynamodb": {"description": "NoSQL data store for campaigns, creatives, attribution, royalties", "icon": "database", "category": "database"},
            "kinesis": {"description": "Real-time data streaming for impressions", "icon": "activity", "category": "streaming"},
            "lambda": {"description": "Serverless compute for campaign + creative functions", "icon": "zap", "category": "compute"},
            "eventbridge": {"description": "Event routing with custom event bus", "icon": "git-branch", "category": "events"},
            "sns": {"description": "Notification alerts via email subscriptions", "icon": "bell", "category": "notifications"},
            "secrets-manager": {"description": "Secure credential storage for blockchain keys", "icon": "lock", "category": "security"},
            "qldb": {"description": "Immutable ledger for audit trails (optional)", "icon": "book-open", "category": "ledger"},
            "media-convert": {"description": "Video transcoding queue (optional)", "icon": "film", "category": "media"},
            "stepfunctions": {"description": "Workflow orchestration via Step Functions", "icon": "layers", "category": "orchestration"},
            "vpc": {"description": "VPC with public/private subnets, NAT, and IGW", "icon": "globe", "category": "networking"},
        }

        modules = []
        for mod_name in sorted(os.listdir(modules_dir)):
            mod_path = os.path.join(modules_dir, mod_name)
            if not os.path.isdir(mod_path):
                continue

            files = {}
            resources = []
            variables = []
            outputs = []
            for fname in sorted(os.listdir(mod_path)):
                fpath = os.path.join(mod_path, fname)
                if os.path.isfile(fpath) and fname.endswith(".tf"):
                    content = _read_file_safe(fpath)
                    files[fname] = content
                    if content and fname == "main.tf":
                        for line in content.split("\n"):
                            stripped = line.strip()
                            if stripped.startswith("resource "):
                                parts = stripped.split('"')
                                if len(parts) >= 4:
                                    resources.append({"type": parts[1], "name": parts[3]})
                    if content and fname == "variables.tf":
                        for line in content.split("\n"):
                            stripped = line.strip()
                            if stripped.startswith("variable "):
                                var_name = stripped.split('"')[1] if '"' in stripped else ""
                                if var_name:
                                    variables.append(var_name)
                    if content and fname == "outputs.tf":
                        for line in content.split("\n"):
                            stripped = line.strip()
                            if stripped.startswith("output "):
                                out_name = stripped.split('"')[1] if '"' in stripped else ""
                                if out_name:
                                    outputs.append(out_name)

            meta = MODULE_DESCRIPTIONS.get(mod_name, {"description": "", "icon": "box", "category": "other"})
            modules.append({
                "name": mod_name,
                "description": meta["description"],
                "icon": meta["icon"],
                "category": meta["category"],
                "files": files,
                "resources": resources,
                "variables": variables,
                "outputs": outputs,
                "file_count": len(files),
                "resource_count": len(resources),
            })

        environments = []
        if os.path.isdir(envs_dir):
            for env_name in sorted(os.listdir(envs_dir)):
                env_path = os.path.join(envs_dir, env_name)
                if not os.path.isdir(env_path):
                    continue
                env_files = {}
                for fname in sorted(os.listdir(env_path)):
                    fpath = os.path.join(env_path, fname)
                    if os.path.isfile(fpath):
                        env_files[fname] = _read_file_safe(fpath)
                environments.append({
                    "name": env_name,
                    "files": env_files,
                    "file_count": len(env_files),
                })

        top_level_files = {}
        for fname in ["provider.tf", "versions.tf", "variables.tf", "outputs.tf", "README.md"]:
            fpath = os.path.join(INFRA_TF_DIR, fname)
            content = _read_file_safe(fpath)
            if content:
                top_level_files[fname] = content

        return {
            "exists": True,
            "modules": modules,
            "environments": environments,
            "top_level_files": top_level_files,
            "total_modules": len(modules),
            "total_resources": sum(m["resource_count"] for m in modules),
        }

    # ── CDK constructs structure ───────────────────────────────────
    async def get_cdk_constructs(self) -> dict:
        """Scan infra-cdk/ and return construct metadata with file contents."""
        lib_dir = os.path.join(INFRA_CDK_DIR, "lib")
        constructs_dir = os.path.join(lib_dir, "constructs")
        bin_dir = os.path.join(INFRA_CDK_DIR, "bin")

        if not os.path.isdir(INFRA_CDK_DIR):
            return {"exists": False, "error": "infra-cdk/ not found", "constructs": [], "config_files": {}}

        CONSTRUCT_DESCRIPTIONS = {
            "auth": {"description": "Cognito User Pool authentication", "icon": "shield", "category": "auth", "services": ["Cognito UserPool", "UserPoolClient"]},
            "frontend": {"description": "S3 + CloudFront static hosting", "icon": "globe", "category": "hosting", "services": ["S3 Bucket", "CloudFront Distribution"]},
            "api": {"description": "API Gateway with Cognito authorizer", "icon": "server", "category": "api", "services": ["REST API", "CognitoAuthorizer", "LambdaIntegration"]},
            "lambdas": {"description": "Lambda microservices for campaigns, creatives, attribution", "icon": "zap", "category": "compute", "services": ["CampaignHandler", "CreativeHandler", "AttributionHandler", "IAM Role"]},
            "dynamodb": {"description": "NoSQL tables for campaigns, creatives, attribution, royalties", "icon": "database", "category": "database", "services": ["Campaigns Table", "Creatives Table", "Attribution Table", "Royalties Table"]},
            "kinesis": {"description": "Real-time impression data streaming", "icon": "activity", "category": "streaming", "services": ["ImpressionStream"]},
            "eventbridge": {"description": "Event-driven routing with custom bus", "icon": "git-branch", "category": "events", "services": ["DoohEventBus", "CampaignCreatedRule", "ImpressionReceivedRule"]},
            "qldb": {"description": "Immutable audit ledger (optional)", "icon": "book-open", "category": "ledger", "services": ["AuditLedger"]},
        }

        constructs = []
        if os.path.isdir(constructs_dir):
            for fname in sorted(os.listdir(constructs_dir)):
                if not fname.endswith(".ts"):
                    continue
                fpath = os.path.join(constructs_dir, fname)
                content = _read_file_safe(fpath)
                name = fname.replace(".ts", "")
                meta = CONSTRUCT_DESCRIPTIONS.get(name, {"description": "", "icon": "box", "category": "other", "services": []})

                exports = []
                imports_list = []
                if content:
                    for line in content.split("\n"):
                        stripped = line.strip()
                        if stripped.startswith("export class "):
                            cls = stripped.split("export class ")[1].split(" ")[0]
                            exports.append(cls)
                        if stripped.startswith("import "):
                            imports_list.append(stripped)

                constructs.append({
                    "name": name,
                    "file": f"lib/constructs/{fname}",
                    "description": meta["description"],
                    "icon": meta["icon"],
                    "category": meta["category"],
                    "services": meta["services"],
                    "exports": exports,
                    "imports_count": len(imports_list),
                    "code": content,
                    "lines": len(content.split("\n")) if content else 0,
                })

        stack_file = os.path.join(lib_dir, "infra-stack.ts")
        stack_content = _read_file_safe(stack_file)

        entry_file = os.path.join(bin_dir, "infra.ts")
        entry_content = _read_file_safe(entry_file)

        config_files = {}
        for fname in ["package.json", "cdk.json", "tsconfig.json"]:
            fpath = os.path.join(INFRA_CDK_DIR, fname)
            c = _read_file_safe(fpath)
            if c:
                config_files[fname] = c

        return {
            "exists": True,
            "constructs": constructs,
            "stack_file": {"name": "lib/infra-stack.ts", "code": stack_content, "lines": len(stack_content.split("\n")) if stack_content else 0},
            "entry_file": {"name": "bin/infra.ts", "code": entry_content, "lines": len(entry_content.split("\n")) if entry_content else 0},
            "config_files": config_files,
            "total_constructs": len(constructs),
            "total_services": sum(len(c["services"]) for c in constructs),
        }

    # ── live RDS data ──────────────────────────────────────────────
    def _get_rds_instances_sync(self) -> dict:
        """Synchronous: fetch all RDS PostgreSQL instances with their details."""
        if not self._rds_client:
            return {"connected": False, "error": "RDS client not available", "instances": []}

        instances = []
        try:
            paginator = self._rds_client.get_paginator("describe_db_instances")
            for page in paginator.paginate():
                for db in page.get("DBInstances", []):
                    if db.get("Engine", "").startswith("postgres"):
                        instances.append({
                            "db_instance_id": db["DBInstanceIdentifier"],
                            "engine": db["Engine"],
                            "engine_version": db["EngineVersion"],
                            "db_instance_class": db.get("DBInstanceClass", ""),
                            "status": db.get("DBInstanceStatus", ""),
                            "endpoint": db.get("Endpoint", {}).get("Address", ""),
                            "port": db.get("Endpoint", {}).get("Port", 5432),
                            "allocated_storage_gb": db.get("AllocatedStorage", 0),
                            "multi_az": db.get("MultiAZ", False),
                            "storage_type": db.get("StorageType", ""),
                            "auto_minor_version_upgrade": db.get("AutoMinorVersionUpgrade", False),
                            "availability_zone": db.get("AvailabilityZone", ""),
                            "backup_retention_period": db.get("BackupRetentionPeriod", 0),
                            "preferred_maintenance_window": db.get("PreferredMaintenanceWindow", ""),
                            "pending_modified_values": db.get("PendingModifiedValues", {}),
                            "ca_certificate_identifier": db.get("CACertificateIdentifier", ""),
                            "storage_encrypted": db.get("StorageEncrypted", False),
                            "publicly_accessible": db.get("PubliclyAccessible", False),
                            "instance_create_time": db.get("InstanceCreateTime").isoformat() if db.get("InstanceCreateTime") else None,
                        })
        except ClientError as e:
            return {"connected": True, "error": f"DescribeDBInstances failed: {e.response['Error']['Code']}", "instances": []}
        except Exception as e:
            return {"connected": True, "error": str(e)[:200], "instances": []}

        return {"connected": True, "error": None, "instances": instances, "total": len(instances)}

    async def get_rds_instances(self) -> dict:
        return await asyncio.to_thread(self._get_rds_instances_sync)

    def _get_rds_upgrade_targets_sync(self, instance_id: str) -> dict:
        """Synchronous: get valid minor version upgrade targets for a specific RDS instance."""
        if not self._rds_client:
            return {"connected": False, "error": "RDS client not available", "targets": []}

        try:
            # First get the current instance info
            resp = self._rds_client.describe_db_instances(DBInstanceIdentifier=instance_id)
            dbs = resp.get("DBInstances", [])
            if not dbs:
                return {"connected": True, "error": f"Instance '{instance_id}' not found", "targets": []}

            db = dbs[0]
            current_version = db["EngineVersion"]
            engine = db["Engine"]
            current_major = ".".join(current_version.split(".")[:1])  # e.g. "16" from "16.3"

            # Get all available engine versions for the same major version
            targets = []
            paginator = self._rds_client.get_paginator("describe_db_engine_versions")
            for page in paginator.paginate(Engine=engine):
                for ver in page.get("DBEngineVersions", []):
                    ver_str = ver["EngineVersion"]
                    ver_major = ".".join(ver_str.split(".")[:1])
                    # Only include same-major versions that are newer
                    if ver_major == current_major and ver_str > current_version:
                        valid_targets = ver.get("ValidUpgradeTarget", [])
                        targets.append({
                            "engine_version": ver_str,
                            "description": ver.get("DBEngineVersionDescription", ""),
                            "auto_upgrade": ver.get("SupportsGlobalDatabases", False),
                            "status": ver.get("Status", "available"),
                            "is_valid_target": False,
                        })

            # Also check direct valid upgrade targets from the engine version API
            resp2 = self._rds_client.describe_db_engine_versions(
                Engine=engine,
                EngineVersion=current_version
            )
            direct_targets = []
            for ev in resp2.get("DBEngineVersions", []):
                for t in ev.get("ValidUpgradeTarget", []):
                    if not t.get("IsMajorVersionUpgrade", True):
                        direct_targets.append(t["EngineVersion"])

            # Mark which targets are valid direct upgrades
            for t in targets:
                if t["engine_version"] in direct_targets:
                    t["is_valid_target"] = True

            # Add any direct targets not already in the list
            existing_versions = {t["engine_version"] for t in targets}
            for dt_ver in direct_targets:
                if dt_ver not in existing_versions:
                    targets.append({
                        "engine_version": dt_ver,
                        "description": f"PostgreSQL {dt_ver}",
                        "auto_upgrade": False,
                        "status": "available",
                        "is_valid_target": True,
                    })

            # Sort targets by version descending
            targets.sort(key=lambda x: x["engine_version"], reverse=True)

            return {
                "connected": True,
                "error": None,
                "instance_id": instance_id,
                "current_version": current_version,
                "engine": engine,
                "targets": targets,
                "total": len(targets),
            }

        except ClientError as e:
            return {"connected": True, "error": f"RDS error: {e.response['Error']['Code']} - {e.response['Error'].get('Message', '')}", "targets": []}
        except Exception as e:
            return {"connected": True, "error": str(e)[:200], "targets": []}

    async def get_rds_upgrade_targets(self, instance_id: str) -> dict:
        return await asyncio.to_thread(self._get_rds_upgrade_targets_sync, instance_id)

    def _upgrade_rds_instance_sync(self, instance_id: str, target_version: str, apply_immediately: bool = True) -> dict:
        """Synchronous: initiate a minor version upgrade on an RDS instance."""
        if not self._rds_client:
            return {"success": False, "error": "RDS client not available"}

        try:
            resp = self._rds_client.modify_db_instance(
                DBInstanceIdentifier=instance_id,
                EngineVersion=target_version,
                ApplyImmediately=apply_immediately,
                AllowMajorVersionUpgrade=False,
            )
            db = resp.get("DBInstance", {})
            return {
                "success": True,
                "error": None,
                "instance_id": db.get("DBInstanceIdentifier", instance_id),
                "target_version": target_version,
                "apply_immediately": apply_immediately,
                "status": db.get("DBInstanceStatus", ""),
                "pending_modified_values": db.get("PendingModifiedValues", {}),
            }
        except ClientError as e:
            return {"success": False, "error": f"RDS error: {e.response['Error']['Code']} - {e.response['Error'].get('Message', '')}"}
        except Exception as e:
            return {"success": False, "error": str(e)[:200]}

    async def upgrade_rds_instance(self, instance_id: str, target_version: str, apply_immediately: bool = True) -> dict:
        return await asyncio.to_thread(self._upgrade_rds_instance_sync, instance_id, target_version, apply_immediately)

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
                    line.strip() for line in (requirements or "").split("\n") if line.strip() and not line.startswith("#")
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
