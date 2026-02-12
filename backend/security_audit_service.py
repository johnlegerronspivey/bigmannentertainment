"""
Security Audit Service - Automated dependency vulnerability monitoring
"""

import asyncio
import json
import logging
import subprocess
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
import os

logger = logging.getLogger("security_audit_service")

FRONTEND_DIR = "/app/frontend"
BACKEND_DIR = "/app/backend"

_service_instance = None


def get_security_audit_service():
    global _service_instance
    if _service_instance is None:
        mongo_url = os.environ.get("MONGO_URL")
        db_name = os.environ.get("DB_NAME")
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        _service_instance = SecurityAuditService(db)
    return _service_instance


class SecurityAuditService:
    def __init__(self, db):
        self.db = db
        self.collection = db["security_audits"]
        self._cache: Optional[Dict[str, Any]] = None
        self._cache_time: Optional[datetime] = None
        self._cache_ttl = 300  # 5 min cache

    async def run_frontend_audit(self) -> Dict[str, Any]:
        """Run yarn audit on frontend dependencies."""
        try:
            proc = await asyncio.create_subprocess_exec(
                "yarn", "audit", "--json",
                cwd=FRONTEND_DIR,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=120)
            return self._parse_yarn_audit(stdout.decode("utf-8", errors="replace"))
        except asyncio.TimeoutError:
            return {"error": "Frontend audit timed out", "vulnerabilities": [], "summary": {}}
        except Exception as e:
            return {"error": str(e), "vulnerabilities": [], "summary": {}}

    def _parse_yarn_audit(self, raw: str) -> Dict[str, Any]:
        vulnerabilities: List[Dict[str, Any]] = []
        summary: Dict[str, Any] = {}

        for line in raw.strip().splitlines():
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                if data.get("type") == "auditAdvisory":
                    adv = data["data"]["advisory"]
                    vulnerabilities.append({
                        "module": adv.get("module_name", "unknown"),
                        "severity": adv.get("severity", "unknown"),
                        "title": adv.get("title", ""),
                        "url": adv.get("url", ""),
                        "patched_versions": adv.get("patched_versions", ""),
                        "vulnerable_versions": adv.get("vulnerable_versions", ""),
                        "cwe": adv.get("cwe", ""),
                        "recommendation": adv.get("recommendation", ""),
                    })
                elif data.get("type") == "auditSummary":
                    s = data["data"]
                    summary = {
                        "total_dependencies": s.get("totalDependencies", 0),
                        "vulnerabilities": s.get("vulnerabilities", {}),
                    }
            except (json.JSONDecodeError, KeyError):
                continue

        # Deduplicate
        seen = set()
        unique = []
        for v in vulnerabilities:
            key = f"{v['module']}|{v['title']}"
            if key not in seen:
                seen.add(key)
                unique.append(v)

        sev_order = {"critical": 0, "high": 1, "moderate": 2, "low": 3, "info": 4}
        unique.sort(key=lambda x: sev_order.get(x["severity"], 5))

        return {"vulnerabilities": unique, "summary": summary}

    async def run_backend_audit(self) -> Dict[str, Any]:
        """Run pip-audit on backend Python dependencies."""
        pip_audit_path = "/root/.venv/bin/pip-audit"
        try:
            proc = await asyncio.create_subprocess_exec(
                pip_audit_path, "--format", "json", "--progress-spinner", "off",
                cwd=BACKEND_DIR,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=120)
            return self._parse_pip_audit(stdout.decode("utf-8", errors="replace"))
        except FileNotFoundError:
            # pip-audit not installed — try safety
            return await self._run_safety_check()
        except asyncio.TimeoutError:
            return {"error": "Backend audit timed out", "vulnerabilities": [], "summary": {}}
        except Exception as e:
            return {"error": str(e), "vulnerabilities": [], "summary": {}}

    def _parse_pip_audit(self, raw: str) -> Dict[str, Any]:
        vulnerabilities: List[Dict[str, Any]] = []
        try:
            data = json.loads(raw)
            deps = data if isinstance(data, list) else data.get("dependencies", [])
            for dep in deps:
                for vuln in dep.get("vulns", []):
                    vulnerabilities.append({
                        "module": dep.get("name", "unknown"),
                        "installed_version": dep.get("version", "unknown"),
                        "severity": vuln.get("fix_versions", ["unknown"])[0] if vuln.get("fix_versions") else "unknown",
                        "title": vuln.get("id", ""),
                        "description": vuln.get("description", ""),
                        "url": f"https://osv.dev/vulnerability/{vuln.get('id', '')}",
                        "fix_versions": vuln.get("fix_versions", []),
                    })
        except (json.JSONDecodeError, KeyError):
            pass

        return {
            "vulnerabilities": vulnerabilities,
            "summary": {"total_vulnerabilities": len(vulnerabilities)},
        }

    async def _run_safety_check(self) -> Dict[str, Any]:
        """Fallback: use safety check."""
        try:
            proc = await asyncio.create_subprocess_exec(
                "safety", "check", "--json",
                cwd=BACKEND_DIR,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=120)
            raw = stdout.decode("utf-8", errors="replace")
            vulns = []
            try:
                data = json.loads(raw)
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, list) and len(item) >= 5:
                            vulns.append({
                                "module": item[0],
                                "installed_version": item[2],
                                "severity": "unknown",
                                "title": item[4],
                                "url": "",
                                "fix_versions": [],
                            })
            except json.JSONDecodeError:
                pass
            return {"vulnerabilities": vulns, "summary": {"total_vulnerabilities": len(vulns)}}
        except Exception:
            return {
                "vulnerabilities": [],
                "summary": {"total_vulnerabilities": 0},
                "note": "Neither pip-audit nor safety installed. Install with: pip install pip-audit",
            }

    async def run_full_audit(self, force: bool = False) -> Dict[str, Any]:
        """Run full audit on both frontend and backend."""
        now = datetime.now(timezone.utc)

        # Return cache if fresh
        if not force and self._cache and self._cache_time:
            age = (now - self._cache_time).total_seconds()
            if age < self._cache_ttl:
                return {**self._cache, "cached": True, "cache_age_seconds": int(age)}

        frontend_result, backend_result = await asyncio.gather(
            self.run_frontend_audit(),
            self.run_backend_audit(),
        )

        fe_vulns = frontend_result.get("vulnerabilities", [])
        be_vulns = backend_result.get("vulnerabilities", [])
        fe_summary = frontend_result.get("summary", {})
        fe_vuln_counts = fe_summary.get("vulnerabilities", {})

        total_critical = fe_vuln_counts.get("critical", 0)
        total_high = fe_vuln_counts.get("high", 0)
        total_moderate = fe_vuln_counts.get("moderate", 0)
        total_low = fe_vuln_counts.get("low", 0)

        # Add backend counts
        for v in be_vulns:
            sev = v.get("severity", "").lower()
            if sev == "critical":
                total_critical += 1
            elif sev == "high":
                total_high += 1
            elif sev in ("moderate", "medium"):
                total_moderate += 1
            else:
                total_low += 1

        total_vulns = len(fe_vulns) + len(be_vulns)
        score = 100
        score -= total_critical * 25
        score -= total_high * 15
        score -= total_moderate * 5
        score -= total_low * 1
        score = max(0, score)

        if score >= 90:
            grade = "A"
        elif score >= 75:
            grade = "B"
        elif score >= 60:
            grade = "C"
        elif score >= 40:
            grade = "D"
        else:
            grade = "F"

        result = {
            "timestamp": now.isoformat(),
            "security_score": score,
            "grade": grade,
            "total_dependencies": fe_summary.get("total_dependencies", 0),
            "total_vulnerabilities": total_vulns,
            "severity_breakdown": {
                "critical": total_critical,
                "high": total_high,
                "moderate": total_moderate,
                "low": total_low,
            },
            "frontend": {
                "vulnerabilities": fe_vulns,
                "total_dependencies": fe_summary.get("total_dependencies", 0),
                "vulnerability_counts": fe_vuln_counts,
            },
            "backend": {
                "vulnerabilities": be_vulns,
                "total_vulnerabilities": len(be_vulns),
                "note": backend_result.get("note", ""),
            },
            "cached": False,
        }

        # Save to MongoDB
        audit_record = {
            "timestamp": now.isoformat(),
            "security_score": score,
            "grade": grade,
            "total_vulnerabilities": total_vulns,
            "severity_breakdown": result["severity_breakdown"],
            "frontend_vuln_count": len(fe_vulns),
            "backend_vuln_count": len(be_vulns),
            "total_dependencies": fe_summary.get("total_dependencies", 0),
        }
        await self.collection.insert_one(audit_record)

        self._cache = result
        self._cache_time = now

        return result

    async def get_audit_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get previous audit results."""
        cursor = self.collection.find(
            {}, {"_id": 0}
        ).sort("timestamp", -1).limit(limit)
        return await cursor.to_list(length=limit)
