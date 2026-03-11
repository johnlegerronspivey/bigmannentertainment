"""
Scanner Service - Phase 2: Multi-scanner orchestration, CI/CD pipeline generation, Policy-as-code
Integrates: Trivy, Grype, Syft, Checkov
"""

import asyncio
import json
import logging
import subprocess
import uuid
import os
import shutil
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger("scanner_service")

_scanner_instance = None


def get_scanner_service():
    global _scanner_instance
    if _scanner_instance is None:
        mongo_url = os.environ.get("MONGO_URL")
        db_name = os.environ.get("DB_NAME")
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        _scanner_instance = ScannerService(db)
    return _scanner_instance


def initialize_scanner_service(db):
    global _scanner_instance
    _scanner_instance = ScannerService(db)
    return _scanner_instance


GRYPE_SEVERITY_MAP = {"Critical": "critical", "High": "high", "Medium": "medium", "Low": "low", "Negligible": "info"}
TRIVY_SEVERITY_MAP = {"CRITICAL": "critical", "HIGH": "high", "MEDIUM": "medium", "LOW": "low", "UNKNOWN": "info"}


class ScannerService:
    def __init__(self, db):
        self.db = db
        self.scan_results_col = db["cve_scan_results"]
        self.policy_rules_col = db["cve_policy_rules"]
        self.pipeline_configs_col = db["cve_pipeline_configs"]
        self.cves_col = db["cve_entries"]
        self.audit_col = db["cve_audit_trail"]

    # ═══════════════════════════════════════════════════════════
    # TOOL STATUS
    # ═══════════════════════════════════════════════════════════

    async def get_tool_status(self) -> Dict[str, Any]:
        tools = {}
        for name, cmd in [("trivy", "trivy --version"), ("grype", "grype version"),
                          ("syft", "syft version"), ("checkov", "/root/.venv/bin/checkov --version")]:
            try:
                r = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=10)
                output = (r.stdout.strip() or r.stderr.strip()).split("\n")[0]
                version = output if r.returncode == 0 else None
                tools[name] = {"installed": r.returncode == 0, "version": version}
            except Exception:
                tools[name] = {"installed": False, "version": None}
        return tools

    # ═══════════════════════════════════════════════════════════
    # TRIVY SCANNER
    # ═══════════════════════════════════════════════════════════

    async def run_trivy_fs(self, target: str = "/app", severity_filter: str = "CRITICAL,HIGH,MEDIUM,LOW") -> Dict[str, Any]:
        scan_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        result = {"id": scan_id, "scanner": "trivy", "scan_type": "filesystem",
                  "target": target, "started_at": now, "status": "running"}
        try:
            proc = subprocess.run(
                ["trivy", "fs", target, "--format", "json", "--severity", severity_filter, "--skip-db-update"],
                capture_output=True, text=True, timeout=180
            )
            data = json.loads(proc.stdout) if proc.stdout.strip() else {}
            vulns = []
            for res in data.get("Results", []):
                tgt = res.get("Target", "")
                for v in res.get("Vulnerabilities", []):
                    vulns.append({
                        "id": v.get("VulnerabilityID", ""),
                        "package": v.get("PkgName", ""),
                        "installed_version": v.get("InstalledVersion", ""),
                        "fixed_version": v.get("FixedVersion", ""),
                        "severity": TRIVY_SEVERITY_MAP.get(v.get("Severity", ""), "info"),
                        "title": v.get("Title", ""),
                        "description": v.get("Description", "")[:300],
                        "cvss_score": v.get("CVSS", {}).get("nvd", {}).get("V3Score", 0),
                        "target_file": tgt,
                        "references": v.get("References", [])[:3],
                    })
            result["vulnerabilities"] = vulns
            result["summary"] = self._summarize(vulns)
            result["status"] = "completed"
            result["raw_stderr"] = proc.stderr[:500] if proc.stderr else ""
        except subprocess.TimeoutExpired:
            result["status"] = "timeout"
            result["vulnerabilities"] = []
            result["summary"] = self._summarize([])
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            result["vulnerabilities"] = []
            result["summary"] = self._summarize([])

        result["completed_at"] = datetime.now(timezone.utc).isoformat()
        await self.scan_results_col.insert_one({**result})
        await self._log_audit("trivy_scan", scan_id, f"Trivy FS scan: {len(result.get('vulnerabilities',[]))} vulns on {target}")
        return {k: v for k, v in result.items() if k != "_id"}

    async def run_trivy_iac(self, target: str = "/tmp/test_iac") -> Dict[str, Any]:
        scan_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        result = {"id": scan_id, "scanner": "trivy", "scan_type": "iac",
                  "target": target, "started_at": now, "status": "running"}
        try:
            proc = subprocess.run(
                ["trivy", "config", target, "--format", "json"],
                capture_output=True, text=True, timeout=120
            )
            data = json.loads(proc.stdout) if proc.stdout.strip() else {}
            misconfigs = []
            for res in data.get("Results", []):
                tgt = res.get("Target", "")
                for m in res.get("Misconfigurations", []):
                    misconfigs.append({
                        "id": m.get("ID", ""),
                        "title": m.get("Title", ""),
                        "description": m.get("Description", "")[:300],
                        "severity": TRIVY_SEVERITY_MAP.get(m.get("Severity", ""), "info"),
                        "resolution": m.get("Resolution", ""),
                        "target_file": tgt,
                        "references": m.get("References", [])[:3],
                    })
            result["misconfigurations"] = misconfigs
            result["summary"] = {"total": len(misconfigs),
                                 "critical": sum(1 for m in misconfigs if m["severity"] == "critical"),
                                 "high": sum(1 for m in misconfigs if m["severity"] == "high"),
                                 "medium": sum(1 for m in misconfigs if m["severity"] == "medium"),
                                 "low": sum(1 for m in misconfigs if m["severity"] == "low")}
            result["status"] = "completed"
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            result["misconfigurations"] = []
            result["summary"] = {"total": 0, "critical": 0, "high": 0, "medium": 0, "low": 0}

        result["completed_at"] = datetime.now(timezone.utc).isoformat()
        await self.scan_results_col.insert_one({**result})
        await self._log_audit("trivy_iac_scan", scan_id, f"Trivy IaC scan: {len(result.get('misconfigurations',[]))} misconfigs on {target}")
        return {k: v for k, v in result.items() if k != "_id"}

    # ═══════════════════════════════════════════════════════════
    # GRYPE SCANNER
    # ═══════════════════════════════════════════════════════════

    async def run_grype(self, target: str = "dir:/app/backend") -> Dict[str, Any]:
        scan_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        result = {"id": scan_id, "scanner": "grype", "scan_type": "dependency",
                  "target": target, "started_at": now, "status": "running"}
        try:
            proc = subprocess.run(
                ["grype", target, "--output", "json"],
                capture_output=True, text=True, timeout=180
            )
            data = json.loads(proc.stdout) if proc.stdout.strip() else {}
            vulns = []
            for m in data.get("matches", []):
                vuln = m.get("vulnerability", {})
                art = m.get("artifact", {})
                cvss_entries = vuln.get("cvss", [])
                score = 0
                if cvss_entries:
                    metrics = cvss_entries[0].get("metrics", {})
                    score = metrics.get("baseScore", 0)
                vulns.append({
                    "id": vuln.get("id", ""),
                    "package": art.get("name", ""),
                    "installed_version": art.get("version", ""),
                    "fixed_version": ", ".join(vuln.get("fix", {}).get("versions", [])),
                    "severity": GRYPE_SEVERITY_MAP.get(vuln.get("severity", ""), "info"),
                    "description": vuln.get("description", "")[:300],
                    "cvss_score": score,
                    "data_source": vuln.get("dataSource", ""),
                })
            result["vulnerabilities"] = vulns
            result["summary"] = self._summarize(vulns)
            result["status"] = "completed"
        except subprocess.TimeoutExpired:
            result["status"] = "timeout"
            result["vulnerabilities"] = []
            result["summary"] = self._summarize([])
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            result["vulnerabilities"] = []
            result["summary"] = self._summarize([])

        result["completed_at"] = datetime.now(timezone.utc).isoformat()
        await self.scan_results_col.insert_one({**result})
        await self._log_audit("grype_scan", scan_id, f"Grype scan: {len(result.get('vulnerabilities',[]))} vulns on {target}")
        return {k: v for k, v in result.items() if k != "_id"}

    # ═══════════════════════════════════════════════════════════
    # SYFT SBOM GENERATOR
    # ═══════════════════════════════════════════════════════════

    async def run_syft(self, target: str = "/app", output_format: str = "cyclonedx-json") -> Dict[str, Any]:
        scan_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        result = {"id": scan_id, "scanner": "syft", "scan_type": "sbom",
                  "target": target, "started_at": now, "status": "running"}
        try:
            proc = subprocess.run(
                ["syft", target, "-o", "json"],
                capture_output=True, text=True, timeout=180
            )
            data = json.loads(proc.stdout) if proc.stdout.strip() else {}
            artifacts = data.get("artifacts", [])
            packages = []
            for a in artifacts:
                packages.append({
                    "name": a.get("name", ""),
                    "version": a.get("version", ""),
                    "type": a.get("type", ""),
                    "language": a.get("language", ""),
                    "licenses": [l.get("value", "") for l in a.get("licenses", []) if isinstance(l, dict)][:3],
                    "purl": a.get("purl", ""),
                })
            result["packages"] = packages
            result["summary"] = {
                "total_packages": len(packages),
                "by_type": {},
                "by_language": {},
            }
            for p in packages:
                t = p["type"] or "unknown"
                result["summary"]["by_type"][t] = result["summary"]["by_type"].get(t, 0) + 1
                lang = p["language"] or "unknown"
                result["summary"]["by_language"][lang] = result["summary"]["by_language"].get(lang, 0) + 1
            result["status"] = "completed"
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            result["packages"] = []
            result["summary"] = {"total_packages": 0, "by_type": {}, "by_language": {}}

        result["completed_at"] = datetime.now(timezone.utc).isoformat()
        await self.scan_results_col.insert_one({**result})
        await self._log_audit("syft_scan", scan_id, f"Syft SBOM: {len(result.get('packages',[]))} packages from {target}")
        return {k: v for k, v in result.items() if k != "_id"}

    # ═══════════════════════════════════════════════════════════
    # CHECKOV IAC SCANNER
    # ═══════════════════════════════════════════════════════════

    async def run_checkov(self, target: str = "/tmp/test_iac", framework: str = "all") -> Dict[str, Any]:
        scan_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        result = {"id": scan_id, "scanner": "checkov", "scan_type": "iac",
                  "target": target, "started_at": now, "status": "running"}
        try:
            cmd = ["/root/.venv/bin/checkov", "-d", target, "--output", "json", "--compact"]
            if framework != "all":
                cmd.extend(["--framework", framework])
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            raw = proc.stdout.strip()
            if raw:
                data = json.loads(raw)
                if not isinstance(data, list):
                    data = [data]
            else:
                data = []

            checks = []
            total_passed = 0
            total_failed = 0
            total_skipped = 0
            for block in data:
                total_passed += block.get("summary", {}).get("passed", 0)
                total_failed += block.get("summary", {}).get("failed", 0)
                total_skipped += block.get("summary", {}).get("skipped", 0)
                for check in block.get("results", {}).get("failed_checks", []):
                    sev = "medium"
                    sev_raw = check.get("severity", "")
                    if sev_raw:
                        sev = sev_raw.lower() if sev_raw.lower() in ["critical", "high", "medium", "low"] else "medium"
                    checks.append({
                        "check_id": check.get("check_id", ""),
                        "check_name": check.get("check_type", check.get("check_id", "")),
                        "resource": check.get("resource", ""),
                        "file": check.get("file_path", ""),
                        "guideline": check.get("guideline", ""),
                        "severity": sev,
                        "status": "failed",
                    })
                for check in block.get("results", {}).get("passed_checks", []):
                    checks.append({
                        "check_id": check.get("check_id", ""),
                        "check_name": check.get("check_type", check.get("check_id", "")),
                        "resource": check.get("resource", ""),
                        "file": check.get("file_path", ""),
                        "severity": "info",
                        "status": "passed",
                    })

            result["checks"] = checks
            result["summary"] = {"passed": total_passed, "failed": total_failed, "skipped": total_skipped,
                                 "total": total_passed + total_failed + total_skipped}
            result["status"] = "completed"
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            result["checks"] = []
            result["summary"] = {"passed": 0, "failed": 0, "skipped": 0, "total": 0}

        result["completed_at"] = datetime.now(timezone.utc).isoformat()
        await self.scan_results_col.insert_one({**result})
        await self._log_audit("checkov_scan", scan_id, f"Checkov IaC: {result['summary']['failed']} failed, {result['summary']['passed']} passed on {target}")
        return {k: v for k, v in result.items() if k != "_id"}

    # ═══════════════════════════════════════════════════════════
    # SCAN HISTORY
    # ═══════════════════════════════════════════════════════════

    async def list_scan_results(self, scanner: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        query = {}
        if scanner:
            query["scanner"] = scanner
        results = []
        cursor = self.scan_results_col.find(query, {"_id": 0, "vulnerabilities": 0, "misconfigurations": 0, "packages": 0, "checks": 0}).sort("started_at", -1).limit(limit)
        async for doc in cursor:
            results.append(doc)
        return results

    async def get_scan_result(self, scan_id: str) -> Optional[Dict[str, Any]]:
        doc = await self.scan_results_col.find_one({"id": scan_id}, {"_id": 0})
        return doc

    # ═══════════════════════════════════════════════════════════
    # POLICY-AS-CODE RULES ENGINE
    # ═══════════════════════════════════════════════════════════

    async def create_policy_rule(self, data: Dict[str, Any]) -> Dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        rule = {
            "id": str(uuid.uuid4()),
            "name": data.get("name", ""),
            "description": data.get("description", ""),
            "enabled": data.get("enabled", True),
            "condition_type": data.get("condition_type", "severity_threshold"),
            "condition": data.get("condition", {}),
            "action": data.get("action", "block_deploy"),
            "scope": data.get("scope", "all"),
            "created_at": now,
            "updated_at": now,
        }
        await self.policy_rules_col.insert_one({**rule})
        await self._log_audit("policy_rule_created", rule["id"], f"Policy rule created: {rule['name']}")
        return rule

    async def list_policy_rules(self) -> List[Dict[str, Any]]:
        rules = []
        cursor = self.policy_rules_col.find({}, {"_id": 0}).sort("created_at", -1)
        async for doc in cursor:
            rules.append(doc)
        return rules

    async def update_policy_rule(self, rule_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
        data.pop("id", None)
        data.pop("_id", None)
        result = await self.policy_rules_col.find_one_and_update(
            {"id": rule_id}, {"$set": data}, return_document=True
        )
        if result:
            result.pop("_id", None)
            await self._log_audit("policy_rule_updated", rule_id, f"Policy rule updated: {result.get('name')}")
            return result
        return None

    async def delete_policy_rule(self, rule_id: str) -> bool:
        result = await self.policy_rules_col.delete_one({"id": rule_id})
        if result.deleted_count:
            await self._log_audit("policy_rule_deleted", rule_id, "Policy rule deleted")
            return True
        return False

    async def evaluate_policies(self, scan_result: Dict[str, Any]) -> Dict[str, Any]:
        rules = await self.list_policy_rules()
        evaluation = {"deploy_allowed": True, "rules_evaluated": 0, "rules_triggered": [], "rules_passed": []}

        vulns = scan_result.get("vulnerabilities", [])
        misconfigs = scan_result.get("misconfigurations", [])
        checks = scan_result.get("checks", [])
        summary = scan_result.get("summary", {})

        for rule in rules:
            if not rule.get("enabled", True):
                continue
            evaluation["rules_evaluated"] += 1
            triggered = False
            ctype = rule.get("condition_type", "")
            cond = rule.get("condition", {})

            if ctype == "severity_threshold":
                min_sev = cond.get("min_severity", "critical")
                max_count = cond.get("max_count", 0)
                sev_order = {"critical": 4, "high": 3, "medium": 2, "low": 1, "info": 0}
                min_level = sev_order.get(min_sev, 0)
                matching = sum(1 for v in vulns if sev_order.get(v.get("severity", "info"), 0) >= min_level)
                if matching > max_count:
                    triggered = True

            elif ctype == "package_blocklist":
                blocked = cond.get("packages", [])
                found = [v["package"] for v in vulns if v.get("package") in blocked]
                if found:
                    triggered = True

            elif ctype == "cvss_threshold":
                threshold = cond.get("min_score", 9.0)
                high_cvss = [v for v in vulns if v.get("cvss_score", 0) >= threshold]
                if high_cvss:
                    triggered = True

            elif ctype == "iac_failures":
                max_failures = cond.get("max_failures", 0)
                failed = summary.get("failed", len([c for c in checks if c.get("status") == "failed"]))
                if failed > max_failures:
                    triggered = True

            if triggered:
                evaluation["rules_triggered"].append({"rule_id": rule["id"], "rule_name": rule["name"], "action": rule["action"]})
                if rule.get("action") == "block_deploy":
                    evaluation["deploy_allowed"] = False
            else:
                evaluation["rules_passed"].append({"rule_id": rule["id"], "rule_name": rule["name"]})

        return evaluation

    async def seed_default_rules(self) -> Dict[str, Any]:
        existing = await self.policy_rules_col.count_documents({})
        if existing > 0:
            return {"message": "Rules already exist", "count": existing}

        defaults = [
            {"name": "Block Critical Vulnerabilities", "description": "Block deploy if any critical vulnerability exists",
             "condition_type": "severity_threshold", "condition": {"min_severity": "critical", "max_count": 0}, "action": "block_deploy"},
            {"name": "Block High CVSS (9.0+)", "description": "Block deploy if CVSS score >= 9.0",
             "condition_type": "cvss_threshold", "condition": {"min_score": 9.0}, "action": "block_deploy"},
            {"name": "Warn on High Vulnerabilities", "description": "Warn if more than 5 high-severity vulns",
             "condition_type": "severity_threshold", "condition": {"min_severity": "high", "max_count": 5}, "action": "warn"},
            {"name": "Block IaC Failures", "description": "Block deploy if more than 3 IaC check failures",
             "condition_type": "iac_failures", "condition": {"max_failures": 3}, "action": "block_deploy"},
            {"name": "Blocklist Protected Packages", "description": "Block deploy if blocked packages have vulns",
             "condition_type": "package_blocklist", "condition": {"packages": ["jsonpath", "node-forge", "cryptography"]}, "action": "block_deploy"},
        ]
        for r in defaults:
            await self.create_policy_rule(r)
        return {"message": "Default rules seeded", "count": len(defaults)}

    # ═══════════════════════════════════════════════════════════
    # CI/CD PIPELINE GENERATOR
    # ═══════════════════════════════════════════════════════════

    async def generate_pipeline(self, config: Dict[str, Any]) -> Dict[str, Any]:
        pipeline_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        repo_name = config.get("repo_name", "bigmannentertainment")
        branch = config.get("branch", "main")
        enable_trivy = config.get("enable_trivy", True)
        enable_grype = config.get("enable_grype", True)
        enable_checkov = config.get("enable_checkov", True)
        enable_syft = config.get("enable_syft", True)
        fail_on_critical = config.get("fail_on_critical", True)
        fail_on_high = config.get("fail_on_high", False)
        container_image = config.get("container_image", "")
        terraform_dir = config.get("terraform_dir", "terraform/")
        notify_email = config.get("notify_email", "")

        yaml_content = self._build_github_actions_yaml(
            repo_name=repo_name, branch=branch,
            enable_trivy=enable_trivy, enable_grype=enable_grype,
            enable_checkov=enable_checkov, enable_syft=enable_syft,
            fail_on_critical=fail_on_critical, fail_on_high=fail_on_high,
            container_image=container_image, terraform_dir=terraform_dir,
            notify_email=notify_email,
        )

        pipeline = {
            "id": pipeline_id,
            "repo_name": repo_name,
            "branch": branch,
            "config": config,
            "yaml_content": yaml_content,
            "created_at": now,
        }
        await self.pipeline_configs_col.insert_one({**pipeline})
        await self._log_audit("pipeline_generated", pipeline_id, f"CI/CD pipeline generated for {repo_name}")
        return {k: v for k, v in pipeline.items() if k != "_id"}

    def _build_github_actions_yaml(self, **kwargs) -> str:
        lines = [
            f"name: Security Gates - {kwargs['repo_name']}",
            "",
            "on:",
            "  push:",
            f"    branches: [{kwargs['branch']}]",
            "  pull_request:",
            f"    branches: [{kwargs['branch']}]",
            "  schedule:",
            "    - cron: '0 6 * * 1'  # Weekly Monday 6 AM",
            "",
            "permissions:",
            "  contents: read",
            "  security-events: write",
            "  pull-requests: write",
            "",
            "jobs:",
        ]

        if kwargs.get("enable_syft"):
            lines += [
                "  sbom-generation:",
                "    name: Generate SBOM",
                "    runs-on: ubuntu-latest",
                "    steps:",
                "      - uses: actions/checkout@v4",
                "      - name: Install Syft",
                "        uses: anchore/sbom-action/download-syft@v0",
                "      - name: Generate SBOM",
                "        run: syft . -o cyclonedx-json=sbom.json",
                "      - name: Upload SBOM",
                "        uses: actions/upload-artifact@v4",
                "        with:",
                "          name: sbom",
                "          path: sbom.json",
                "",
            ]

        if kwargs.get("enable_trivy"):
            lines += [
                "  trivy-scan:",
                "    name: Trivy Vulnerability Scan",
                "    runs-on: ubuntu-latest",
                "    steps:",
                "      - uses: actions/checkout@v4",
                "      - name: Run Trivy FS Scan",
                "        uses: aquasecurity/trivy-action@master",
                "        with:",
                "          scan-type: fs",
                "          scan-ref: .",
                "          format: sarif",
                "          output: trivy-results.sarif",
                f"          severity: {'CRITICAL' if kwargs.get('fail_on_critical') else 'CRITICAL,HIGH'}",
                f"          exit-code: {'1' if kwargs.get('fail_on_critical') else '0'}",
                "      - name: Upload Trivy SARIF",
                "        uses: github/codeql-action/upload-sarif@v3",
                "        if: always()",
                "        with:",
                "          sarif_file: trivy-results.sarif",
                "",
            ]

            if kwargs.get("container_image"):
                lines += [
                    "  trivy-container-scan:",
                    "    name: Trivy Container Image Scan",
                    "    runs-on: ubuntu-latest",
                    "    steps:",
                    "      - uses: actions/checkout@v4",
                    "      - name: Build Container Image",
                    "        run: docker build -t scan-target:latest .",
                    "      - name: Run Trivy Image Scan",
                    "        uses: aquasecurity/trivy-action@master",
                    "        with:",
                    "          image-ref: scan-target:latest",
                    "          format: sarif",
                    "          output: trivy-image.sarif",
                    f"          exit-code: {'1' if kwargs.get('fail_on_critical') else '0'}",
                    f"          severity: CRITICAL{',HIGH' if kwargs.get('fail_on_high') else ''}",
                    "      - name: Upload Container SARIF",
                    "        uses: github/codeql-action/upload-sarif@v3",
                    "        if: always()",
                    "        with:",
                    "          sarif_file: trivy-image.sarif",
                    "",
                ]

        if kwargs.get("enable_grype"):
            lines += [
                "  grype-scan:",
                "    name: Grype Dependency Scan",
                "    runs-on: ubuntu-latest",
                "    steps:",
                "      - uses: actions/checkout@v4",
                "      - name: Run Grype Scan",
                "        uses: anchore/scan-action@v4",
                "        id: grype",
                "        with:",
                "          path: .",
                f"          fail-build: {'true' if kwargs.get('fail_on_critical') else 'false'}",
                "          severity-cutoff: critical",
                "          output-format: sarif",
                "      - name: Upload Grype SARIF",
                "        uses: github/codeql-action/upload-sarif@v3",
                "        if: always()",
                "        with:",
                "          sarif_file: ${{ steps.grype.outputs.sarif }}",
                "",
            ]

        if kwargs.get("enable_checkov"):
            tf_dir = kwargs.get("terraform_dir", "terraform/")
            lines += [
                "  checkov-iac-scan:",
                "    name: Checkov IaC Security Scan",
                "    runs-on: ubuntu-latest",
                "    steps:",
                "      - uses: actions/checkout@v4",
                "      - name: Run Checkov",
                "        uses: bridgecrewio/checkov-action@master",
                "        with:",
                f"          directory: {tf_dir}",
                "          framework: terraform",
                "          output_format: sarif",
                "          output_file_path: checkov-results.sarif",
                f"          soft_fail: {'false' if kwargs.get('fail_on_critical') else 'true'}",
                "      - name: Upload Checkov SARIF",
                "        uses: github/codeql-action/upload-sarif@v3",
                "        if: always()",
                "        with:",
                "          sarif_file: checkov-results.sarif",
                "",
            ]

        lines += [
            "  security-gate:",
            "    name: Security Gate Decision",
            "    runs-on: ubuntu-latest",
            "    needs: [" + ", ".join(
                [j for j, e in [
                    ("sbom-generation", kwargs.get("enable_syft")),
                    ("trivy-scan", kwargs.get("enable_trivy")),
                    ("grype-scan", kwargs.get("enable_grype")),
                    ("checkov-iac-scan", kwargs.get("enable_checkov")),
                ] if e]
            ) + "]",
            "    if: always()",
            "    steps:",
            "      - name: Check Security Results",
            "        run: |",
            "          echo 'All security scans completed.'",
            "          echo 'Review SARIF results in GitHub Security tab.'",
        ]

        if kwargs.get("notify_email"):
            lines += [
                "",
                "  notify:",
                "    name: Notify on Failure",
                "    runs-on: ubuntu-latest",
                "    needs: [security-gate]",
                "    if: failure()",
                "    steps:",
                "      - name: Send Notification",
                "        run: |",
                f"          echo 'Security scan failed for {kwargs['repo_name']}. Notify {kwargs['notify_email']}'",
            ]

        return "\n".join(lines)

    async def list_pipelines(self, limit: int = 20) -> List[Dict[str, Any]]:
        results = []
        cursor = self.pipeline_configs_col.find({}, {"_id": 0, "yaml_content": 0}).sort("created_at", -1).limit(limit)
        async for doc in cursor:
            results.append(doc)
        return results

    async def get_pipeline(self, pipeline_id: str) -> Optional[Dict[str, Any]]:
        return await self.pipeline_configs_col.find_one({"id": pipeline_id}, {"_id": 0})

    # ═══════════════════════════════════════════════════════════
    # HELPERS
    # ═══════════════════════════════════════════════════════════

    def _summarize(self, vulns: List[Dict]) -> Dict[str, int]:
        return {
            "total": len(vulns),
            "critical": sum(1 for v in vulns if v.get("severity") == "critical"),
            "high": sum(1 for v in vulns if v.get("severity") == "high"),
            "medium": sum(1 for v in vulns if v.get("severity") == "medium"),
            "low": sum(1 for v in vulns if v.get("severity") == "low"),
        }

    async def _log_audit(self, action: str, target_id: str, message: str, user: str = "system"):
        entry = {
            "id": str(uuid.uuid4()),
            "action": action,
            "target_id": target_id,
            "message": message,
            "user": user,
            "data": {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        await self.audit_col.insert_one({**entry})
