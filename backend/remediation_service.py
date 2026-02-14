"""
Remediation Service - Phase 3: Automated Remediation, GitHub Integration, AWS Inspector
Creates GitHub issues/PRs for vulnerabilities, tracks remediation lifecycle, syncs with AWS Security Hub
"""

import json
import logging
import uuid
import os
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from github import Github, GithubException

logger = logging.getLogger("remediation_service")

_remediation_instance = None


def get_remediation_service():
    global _remediation_instance
    if _remediation_instance is None:
        mongo_url = os.environ.get("MONGO_URL")
        db_name = os.environ.get("DB_NAME")
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        _remediation_instance = RemediationService(db)
    return _remediation_instance


def initialize_remediation_service(db):
    global _remediation_instance
    _remediation_instance = RemediationService(db)
    return _remediation_instance


REMEDIATION_STATES = ["open", "issue_created", "pr_created", "in_review", "merged", "deployed", "verified", "closed", "wont_fix"]

SEVERITY_LABELS = {
    "critical": "severity:critical",
    "high": "severity:high",
    "medium": "severity:medium",
    "low": "severity:low",
    "info": "severity:info",
}

SEVERITY_PRIORITY = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}


class RemediationService:
    def __init__(self, db):
        self.db = db
        self.remediation_col = db["cve_remediation_items"]
        self.github_config_col = db["cve_github_config"]
        self.aws_findings_col = db["cve_aws_findings"]
        self.cves_col = db["cve_entries"]
        self.services_col = db["cve_services"]
        self.audit_col = db["cve_audit_trail"]

    def _get_github(self) -> Optional[Github]:
        token = os.environ.get("GITHUB_TOKEN")
        if not token:
            return None
        from github import Auth
        return Github(auth=Auth.Token(token))

    def _get_repo(self):
        gh = self._get_github()
        if not gh:
            return None, None
        repo_name = os.environ.get("GITHUB_REPO", "")
        if not repo_name:
            return gh, None
        try:
            repo = gh.get_repo(repo_name)
            return gh, repo
        except GithubException as e:
            logger.error(f"GitHub repo access failed: {e}")
            return gh, None

    # ═══════════════════════════════════════════════════════════
    # GITHUB CONFIG
    # ═══════════════════════════════════════════════════════════

    async def get_github_config(self) -> Dict[str, Any]:
        gh, repo = self._get_repo()
        config = {
            "connected": gh is not None,
            "repo_connected": repo is not None,
            "repo_name": os.environ.get("GITHUB_REPO", ""),
            "token_configured": bool(os.environ.get("GITHUB_TOKEN")),
            "write_access": False,
        }
        if repo:
            try:
                config["repo_full_name"] = repo.full_name
                config["repo_url"] = repo.html_url
                config["default_branch"] = repo.default_branch
                config["open_issues_count"] = repo.open_issues_count
                config["repo_private"] = repo.private
                config["write_access"] = repo.permissions.push if repo.permissions else False
            except GithubException:
                config["repo_connected"] = False

        stats = await self._get_remediation_stats()
        config["stats"] = stats
        return config

    async def _get_remediation_stats(self) -> Dict[str, Any]:
        total = await self.remediation_col.count_documents({})
        open_items = await self.remediation_col.count_documents({"status": "open"})
        issues_created = await self.remediation_col.count_documents({"github_issue_number": {"$ne": None}})
        prs_created = await self.remediation_col.count_documents({"github_pr_number": {"$ne": None}})
        merged = await self.remediation_col.count_documents({"status": "merged"})
        closed = await self.remediation_col.count_documents({"status": {"$in": ["closed", "verified"]}})

        by_severity = {}
        for sev in ["critical", "high", "medium", "low", "info"]:
            by_severity[sev] = await self.remediation_col.count_documents({"severity": sev, "status": {"$nin": ["closed", "verified", "wont_fix"]}})

        return {
            "total": total,
            "open": open_items,
            "issues_created": issues_created,
            "prs_created": prs_created,
            "merged": merged,
            "closed": closed,
            "by_severity": by_severity,
        }

    # ═══════════════════════════════════════════════════════════
    # REMEDIATION ITEMS CRUD
    # ═══════════════════════════════════════════════════════════

    async def list_items(self, status: Optional[str] = None, severity: Optional[str] = None,
                         limit: int = 50, skip: int = 0) -> Dict[str, Any]:
        query = {}
        if status:
            query["status"] = status
        if severity:
            query["severity"] = severity
        total = await self.remediation_col.count_documents(query)
        cursor = self.remediation_col.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit)
        items = []
        async for doc in cursor:
            items.append(doc)
        return {"items": items, "total": total, "limit": limit, "skip": skip}

    async def get_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        return await self.remediation_col.find_one({"id": item_id}, {"_id": 0})

    async def update_item_status(self, item_id: str, new_status: str, notes: str = "") -> Optional[Dict[str, Any]]:
        if new_status not in REMEDIATION_STATES:
            return None
        now = datetime.now(timezone.utc).isoformat()
        updates = {"status": new_status, "updated_at": now}
        if notes:
            updates["notes"] = notes
        result = await self.remediation_col.find_one_and_update(
            {"id": item_id}, {"$set": updates}, return_document=True
        )
        if result:
            result.pop("_id", None)
            await self._log_audit("remediation_status_updated", item_id, f"Remediation {item_id} -> {new_status}", {"notes": notes})
        return result

    # ═══════════════════════════════════════════════════════════
    # CREATE GITHUB ISSUE FROM CVE
    # ═══════════════════════════════════════════════════════════

    async def create_github_issue(self, cve_entry_id: str) -> Dict[str, Any]:
        cve = await self.cves_col.find_one({"id": cve_entry_id}, {"_id": 0})
        if not cve:
            cve = await self.cves_col.find_one({"cve_id": cve_entry_id}, {"_id": 0})
        if not cve:
            return {"error": "CVE not found", "success": False}

        gh, repo = self._get_repo()
        if not repo:
            return {"error": "GitHub repository not connected", "success": False}

        existing = await self.remediation_col.find_one({"cve_entry_id": cve.get("id"), "github_issue_number": {"$ne": None}}, {"_id": 0})
        if existing:
            return {"error": f"Issue already exists: #{existing['github_issue_number']}", "success": False, "existing": existing}

        severity = cve.get("severity", "medium")
        cve_id = cve.get("cve_id", "Unknown")
        title = f"[{severity.upper()}] {cve_id}: {cve.get('title', 'Vulnerability detected')}"

        body = self._build_issue_body(cve)
        labels = ["security", "vulnerability", SEVERITY_LABELS.get(severity, "severity:medium")]

        try:
            existing_labels = [l.name for l in repo.get_labels()]
            for label in labels:
                if label not in existing_labels:
                    try:
                        color = {"security": "d73a4a", "vulnerability": "e11d48"}.get(label, "fbca04")
                        repo.create_label(name=label, color=color)
                    except GithubException:
                        pass

            issue = repo.create_issue(title=title, body=body, labels=labels)

            now = datetime.now(timezone.utc).isoformat()
            item = {
                "id": str(uuid.uuid4()),
                "cve_entry_id": cve.get("id"),
                "cve_id": cve_id,
                "severity": severity,
                "title": cve.get("title", ""),
                "affected_package": cve.get("affected_package", ""),
                "affected_version": cve.get("affected_version", ""),
                "fixed_version": cve.get("fixed_version", ""),
                "github_issue_number": issue.number,
                "github_issue_url": issue.html_url,
                "github_pr_number": None,
                "github_pr_url": None,
                "status": "issue_created",
                "assigned_to": cve.get("assigned_to", ""),
                "assigned_team": cve.get("assigned_team", ""),
                "notes": "",
                "source": "manual",
                "created_at": now,
                "updated_at": now,
            }
            await self.remediation_col.insert_one({**item})

            await self.cves_col.update_one({"id": cve.get("id")}, {"$set": {"status": "triaged", "updated_at": now}})
            await self._log_audit("github_issue_created", cve_id, f"GitHub issue #{issue.number} created for {cve_id}", {"issue_url": issue.html_url})

            return {"success": True, "issue_number": issue.number, "issue_url": issue.html_url, "item": item}
        except GithubException as e:
            logger.error(f"GitHub issue creation failed: {e}")
            msg = str(e)
            if "403" in msg:
                msg = "GitHub token lacks write permissions. Update your token's permissions to include 'Issues: Read and write' at github.com/settings/tokens"
            return {"error": msg, "success": False}

    def _build_issue_body(self, cve: Dict) -> str:
        severity = cve.get("severity", "medium").upper()
        emoji = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🔵", "INFO": "⚪"}.get(severity, "⚪")
        body = f"""## {emoji} Security Vulnerability: {cve.get('cve_id', 'N/A')}

**Severity:** {severity} | **CVSS:** {cve.get('cvss_score', 'N/A')}
**Status:** {cve.get('status', 'detected')}

### Description
{cve.get('description', 'No description available.')}

### Affected Component
| Field | Value |
|-------|-------|
| Package | `{cve.get('affected_package', 'N/A')}` |
| Version | `{cve.get('affected_version', 'N/A')}` |
| Fixed In | `{cve.get('fixed_version', 'N/A')}` |

### Affected Services
{', '.join(cve.get('affected_services', [])) or 'None specified'}

### References
{chr(10).join([f'- {ref}' for ref in cve.get('references', [])]) or 'None'}

### Remediation Steps
1. Update `{cve.get('affected_package', 'package')}` to version `{cve.get('fixed_version', 'latest')}`
2. Run security scan to verify fix
3. Deploy to staging and validate
4. Deploy to production

---
*Auto-generated by CVE Management Platform*
"""
        return body

    # ═══════════════════════════════════════════════════════════
    # CREATE GITHUB PR FOR DEPENDENCY BUMP
    # ═══════════════════════════════════════════════════════════

    async def create_github_pr(self, cve_entry_id: str) -> Dict[str, Any]:
        cve = await self.cves_col.find_one({"id": cve_entry_id}, {"_id": 0})
        if not cve:
            cve = await self.cves_col.find_one({"cve_id": cve_entry_id}, {"_id": 0})
        if not cve:
            return {"error": "CVE not found", "success": False}

        gh, repo = self._get_repo()
        if not repo:
            return {"error": "GitHub repository not connected", "success": False}

        pkg = cve.get("affected_package", "")
        fixed_ver = cve.get("fixed_version", "")
        if not pkg or not fixed_ver:
            return {"error": "Missing package name or fixed version for PR generation", "success": False}

        branch_name = f"security/fix-{cve.get('cve_id', 'cve').lower().replace('-', '_')}-{uuid.uuid4().hex[:6]}"
        cve_id = cve.get("cve_id", "Unknown")
        severity = cve.get("severity", "medium")

        try:
            default_branch = repo.default_branch
            base_ref = repo.get_git_ref(f"heads/{default_branch}")
            base_sha = base_ref.object.sha

            repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=base_sha)

            files_to_check = ["requirements.txt", "package.json", "Pipfile", "setup.py", "pyproject.toml"]
            updated_files = []

            for fname in files_to_check:
                try:
                    file_content = repo.get_contents(fname, ref=default_branch)
                    content = file_content.decoded_content.decode("utf-8")

                    new_content = self._bump_dependency(content, pkg, fixed_ver, fname)
                    if new_content != content:
                        repo.update_file(
                            path=fname,
                            message=f"fix: bump {pkg} to {fixed_ver} ({cve_id})",
                            content=new_content,
                            sha=file_content.sha,
                            branch=branch_name,
                        )
                        updated_files.append(fname)
                except Exception:
                    continue

            if not updated_files:
                try:
                    repo.get_git_ref(f"heads/{branch_name}").delete()
                except Exception:
                    pass
                return {"error": f"Could not find {pkg} in any dependency file to update", "success": False}

            pr_title = f"[Security] Bump {pkg} to {fixed_ver} ({cve_id})"
            pr_body = f"""## Security Fix: {cve_id}

**Severity:** {severity.upper()}
**Package:** `{pkg}`
**Current Version:** `{cve.get('affected_version', 'N/A')}`
**Fixed Version:** `{fixed_ver}`

### Changes
{chr(10).join([f'- Updated `{f}`' for f in updated_files])}

### Description
{cve.get('description', 'Dependency version bump to fix security vulnerability.')}

---
*Auto-generated by CVE Management Platform*
"""
            pr = repo.create_pull(
                title=pr_title,
                body=pr_body,
                head=branch_name,
                base=default_branch,
                maintainer_can_modify=True,
            )

            pr.add_to_labels("security", "dependencies")

            now = datetime.now(timezone.utc).isoformat()
            existing = await self.remediation_col.find_one({"cve_entry_id": cve.get("id")}, {"_id": 0})
            if existing:
                await self.remediation_col.update_one(
                    {"id": existing["id"]},
                    {"$set": {"github_pr_number": pr.number, "github_pr_url": pr.html_url, "status": "pr_created", "updated_at": now}}
                )
                item = await self.remediation_col.find_one({"id": existing["id"]}, {"_id": 0})
            else:
                item = {
                    "id": str(uuid.uuid4()),
                    "cve_entry_id": cve.get("id"),
                    "cve_id": cve_id,
                    "severity": severity,
                    "title": cve.get("title", ""),
                    "affected_package": pkg,
                    "affected_version": cve.get("affected_version", ""),
                    "fixed_version": fixed_ver,
                    "github_issue_number": None,
                    "github_issue_url": None,
                    "github_pr_number": pr.number,
                    "github_pr_url": pr.html_url,
                    "status": "pr_created",
                    "assigned_to": cve.get("assigned_to", ""),
                    "assigned_team": cve.get("assigned_team", ""),
                    "notes": "",
                    "source": "manual",
                    "created_at": now,
                    "updated_at": now,
                }
                await self.remediation_col.insert_one({**item})

            await self.cves_col.update_one({"id": cve.get("id")}, {"$set": {"status": "in_progress", "updated_at": now}})
            await self._log_audit("github_pr_created", cve_id, f"PR #{pr.number} for {pkg}@{fixed_ver}", {"pr_url": pr.html_url, "files": updated_files})

            return {"success": True, "pr_number": pr.number, "pr_url": pr.html_url, "updated_files": updated_files, "branch": branch_name, "item": item}
        except GithubException as e:
            logger.error(f"GitHub PR creation failed: {e}")
            msg = str(e)
            if "403" in msg:
                msg = "GitHub token lacks write permissions. Update your token's permissions to include 'Contents: Read and write' and 'Pull requests: Read and write' at github.com/settings/tokens"
            return {"error": msg, "success": False}

    def _bump_dependency(self, content: str, package: str, new_version: str, filename: str) -> str:
        import re
        if filename == "requirements.txt":
            pattern = rf'^({re.escape(package)})\s*[=><~!]+\s*[\d\.\*]+(.*)$'
            replacement = rf'\1>={new_version}\2'
            return re.sub(pattern, replacement, content, flags=re.MULTILINE | re.IGNORECASE)
        elif filename == "package.json":
            pattern = rf'("{re.escape(package)}"\s*:\s*)"[^"]*"'
            replacement = rf'\1"^{new_version}"'
            return re.sub(pattern, replacement, content)
        elif filename == "pyproject.toml":
            pattern = rf'^(\s*"{re.escape(package)})\s*[><=~!]+\s*[\d\.\*]+"(.*)$'
            replacement = rf'\1>={new_version}"\2'
            return re.sub(pattern, replacement, content, flags=re.MULTILINE | re.IGNORECASE)
        return content

    # ═══════════════════════════════════════════════════════════
    # BULK OPERATIONS
    # ═══════════════════════════════════════════════════════════

    async def bulk_create_issues(self, severity_filter: str = "critical", limit: int = 10) -> Dict[str, Any]:
        query = {"status": {"$in": ["detected", "triaged"]}, "severity": severity_filter}
        cursor = self.cves_col.find(query, {"_id": 0}).sort("detected_at", 1).limit(limit)
        results = {"created": [], "skipped": [], "errors": []}
        async for cve in cursor:
            existing = await self.remediation_col.find_one({"cve_entry_id": cve.get("id"), "github_issue_number": {"$ne": None}})
            if existing:
                results["skipped"].append({"cve_id": cve.get("cve_id"), "reason": "issue already exists"})
                continue
            result = await self.create_github_issue(cve.get("id"))
            if result.get("success"):
                results["created"].append({"cve_id": cve.get("cve_id"), "issue_number": result["issue_number"]})
            else:
                results["errors"].append({"cve_id": cve.get("cve_id"), "error": result.get("error")})

        return {"total_processed": len(results["created"]) + len(results["skipped"]) + len(results["errors"]), **results}

    # ═══════════════════════════════════════════════════════════
    # SYNC WITH GITHUB
    # ═══════════════════════════════════════════════════════════

    async def sync_github_status(self) -> Dict[str, Any]:
        gh, repo = self._get_repo()
        if not repo:
            return {"error": "GitHub not connected", "synced": 0}

        synced = 0
        cursor = self.remediation_col.find({"status": {"$nin": ["closed", "verified", "wont_fix"]}}, {"_id": 0})
        async for item in cursor:
            updated = False
            now = datetime.now(timezone.utc).isoformat()

            if item.get("github_pr_number"):
                try:
                    pr = repo.get_pull(item["github_pr_number"])
                    if pr.merged and item["status"] != "merged":
                        await self.remediation_col.update_one(
                            {"id": item["id"]}, {"$set": {"status": "merged", "updated_at": now}}
                        )
                        await self.cves_col.update_one({"id": item.get("cve_entry_id")}, {"$set": {"status": "fixed", "fixed_at": now, "updated_at": now}})
                        updated = True
                    elif pr.state == "closed" and not pr.merged and item["status"] not in ["closed", "wont_fix"]:
                        await self.remediation_col.update_one(
                            {"id": item["id"]}, {"$set": {"status": "closed", "updated_at": now}}
                        )
                        updated = True
                except GithubException:
                    pass

            if item.get("github_issue_number") and not updated:
                try:
                    issue = repo.get_issue(item["github_issue_number"])
                    if issue.state == "closed" and item["status"] not in ["merged", "closed", "verified"]:
                        await self.remediation_col.update_one(
                            {"id": item["id"]}, {"$set": {"status": "closed", "updated_at": now}}
                        )
                        updated = True
                except GithubException:
                    pass

            if updated:
                synced += 1

        return {"synced": synced, "message": f"Synced {synced} remediation items with GitHub"}

    # ═══════════════════════════════════════════════════════════
    # AWS INSPECTOR / SECURITY HUB
    # ═══════════════════════════════════════════════════════════

    async def get_aws_findings(self, limit: int = 50) -> Dict[str, Any]:
        try:
            import boto3
            inspector_client = boto3.client(
                "inspector2",
                region_name=os.environ.get("AWS_REGION", "us-east-1"),
                aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
            )
            response = inspector_client.list_findings(
                maxResults=min(limit, 100),
                filterCriteria={"findingStatus": [{"comparison": "EQUALS", "value": "ACTIVE"}]},
            )
            findings = []
            for f in response.get("findings", []):
                finding = {
                    "id": f.get("findingArn", ""),
                    "title": f.get("title", ""),
                    "description": f.get("description", ""),
                    "severity": f.get("severity", "MEDIUM").lower(),
                    "status": f.get("status", "ACTIVE"),
                    "type": f.get("type", ""),
                    "first_observed": f.get("firstObservedAt", "").isoformat() if f.get("firstObservedAt") else "",
                    "last_observed": f.get("lastObservedAt", "").isoformat() if f.get("lastObservedAt") else "",
                    "resources": [r.get("id", "") for r in f.get("resources", [])],
                    "source": "aws_inspector",
                }
                findings.append(finding)

            return {"findings": findings, "count": len(findings), "source": "aws_inspector"}

        except Exception as e:
            logger.warning(f"AWS Inspector not available: {e}")
            stored = await self.aws_findings_col.find({}, {"_id": 0}).sort("imported_at", -1).limit(limit).to_list(limit)
            return {"findings": stored, "count": len(stored), "source": "cached", "note": f"Live AWS unavailable: {str(e)[:100]}"}

    async def sync_aws_findings(self) -> Dict[str, Any]:
        result = await self.get_aws_findings(limit=100)
        if result.get("source") != "aws_inspector":
            return {"synced": 0, "error": "AWS Inspector not reachable", "note": result.get("note", "")}

        imported = 0
        for finding in result.get("findings", []):
            existing = await self.aws_findings_col.find_one({"id": finding["id"]})
            now = datetime.now(timezone.utc).isoformat()
            if existing:
                await self.aws_findings_col.update_one({"id": finding["id"]}, {"$set": {**finding, "imported_at": now}})
            else:
                await self.aws_findings_col.insert_one({**finding, "imported_at": now})
                imported += 1

                cve_data = {
                    "title": finding["title"],
                    "description": finding["description"],
                    "severity": finding["severity"],
                    "source": "aws_inspector",
                    "tags": ["aws", "inspector"],
                    "references": [finding["id"]],
                }
                await self.cves_col.insert_one({
                    "id": str(uuid.uuid4()),
                    "cve_id": f"AWS-{uuid.uuid4().hex[:8].upper()}",
                    **cve_data,
                    "status": "detected",
                    "cvss_score": 0.0,
                    "affected_package": "",
                    "affected_version": "",
                    "fixed_version": "",
                    "affected_services": [],
                    "assigned_to": "",
                    "assigned_team": "",
                    "exploitability": "unknown",
                    "detected_at": now,
                    "created_at": now,
                    "updated_at": now,
                    "triaged_at": None,
                    "fixed_at": None,
                    "verified_at": None,
                })

        return {"synced": len(result.get("findings", [])), "new_imported": imported}

    async def get_security_hub_summary(self) -> Dict[str, Any]:
        try:
            import boto3
            hub_client = boto3.client(
                "securityhub",
                region_name=os.environ.get("AWS_REGION", "us-east-1"),
                aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
            )
            response = hub_client.get_findings(
                Filters={"WorkflowStatus": [{"Value": "NEW", "Comparison": "EQUALS"}]},
                MaxResults=20,
            )
            findings = []
            for f in response.get("Findings", []):
                findings.append({
                    "id": f.get("Id", ""),
                    "title": f.get("Title", ""),
                    "severity": f.get("Severity", {}).get("Label", "MEDIUM").lower(),
                    "product": f.get("ProductName", ""),
                    "compliance_status": f.get("Compliance", {}).get("Status", ""),
                    "source": "security_hub",
                })

            return {"findings": findings, "count": len(findings), "source": "security_hub"}
        except Exception as e:
            return {"findings": [], "count": 0, "source": "unavailable", "note": str(e)[:100]}

    # ═══════════════════════════════════════════════════════════
    # AUDIT
    # ═══════════════════════════════════════════════════════════

    async def _log_audit(self, action: str, entity_id: str, message: str, data: Optional[Dict] = None):
        entry = {
            "id": str(uuid.uuid4()),
            "action": action,
            "entity_id": entity_id,
            "message": message,
            "data": data or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        await self.audit_col.insert_one({**entry})
