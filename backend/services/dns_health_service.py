"""DNS Health Checker Service — real DNS lookups and health monitoring."""
import socket
import time
import uuid
from datetime import datetime, timezone
from typing import Optional

import dns.resolver
import dns.reversename
import dns.rdatatype

from config.database import db

RECORD_TYPES = ["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA", "SRV", "CAA", "PTR"]


def _resolve(domain: str, rdtype: str, timeout: float = 5.0) -> dict:
    """Perform a single DNS lookup and return structured result."""
    start = time.monotonic()
    try:
        answers = dns.resolver.resolve(domain, rdtype, lifetime=timeout)
        elapsed_ms = round((time.monotonic() - start) * 1000, 2)
        records = []
        for rdata in answers:
            if rdtype == "MX":
                records.append({"priority": rdata.preference, "value": str(rdata.exchange).rstrip(".")})
            elif rdtype == "SOA":
                records.append({
                    "mname": str(rdata.mname).rstrip("."),
                    "rname": str(rdata.rname).rstrip("."),
                    "serial": rdata.serial,
                    "refresh": rdata.refresh,
                    "retry": rdata.retry,
                    "expire": rdata.expire,
                    "minimum": rdata.minimum,
                })
            elif rdtype == "SRV":
                records.append({
                    "priority": rdata.priority,
                    "weight": rdata.weight,
                    "port": rdata.port,
                    "target": str(rdata.target).rstrip("."),
                })
            elif rdtype == "CAA":
                records.append({
                    "flags": rdata.flags,
                    "tag": rdata.tag.decode() if isinstance(rdata.tag, bytes) else str(rdata.tag),
                    "value": rdata.value.decode() if isinstance(rdata.value, bytes) else str(rdata.value),
                })
            else:
                records.append({"value": str(rdata).rstrip(".").strip('"')})
        return {
            "type": rdtype,
            "records": records,
            "count": len(records),
            "ttl": answers.rrset.ttl if answers.rrset else None,
            "response_time_ms": elapsed_ms,
            "status": "ok",
        }
    except dns.resolver.NXDOMAIN:
        return {"type": rdtype, "records": [], "count": 0, "ttl": None,
                "response_time_ms": round((time.monotonic() - start) * 1000, 2),
                "status": "nxdomain", "error": "Domain does not exist"}
    except dns.resolver.NoAnswer:
        return {"type": rdtype, "records": [], "count": 0, "ttl": None,
                "response_time_ms": round((time.monotonic() - start) * 1000, 2),
                "status": "no_answer", "error": f"No {rdtype} records found"}
    except dns.resolver.NoNameservers:
        return {"type": rdtype, "records": [], "count": 0, "ttl": None,
                "response_time_ms": round((time.monotonic() - start) * 1000, 2),
                "status": "no_nameservers", "error": "No nameservers available"}
    except dns.exception.Timeout:
        return {"type": rdtype, "records": [], "count": 0, "ttl": None,
                "response_time_ms": round((time.monotonic() - start) * 1000, 2),
                "status": "timeout", "error": "DNS query timed out"}
    except Exception as e:
        return {"type": rdtype, "records": [], "count": 0, "ttl": None,
                "response_time_ms": round((time.monotonic() - start) * 1000, 2),
                "status": "error", "error": str(e)}


def lookup_domain(domain: str, record_types: Optional[list] = None) -> dict:
    """Lookup DNS records for a domain across specified record types."""
    if not record_types:
        record_types = ["A", "AAAA", "MX", "NS", "TXT", "CNAME"]
    results = {}
    for rt in record_types:
        rt_upper = rt.upper()
        if rt_upper in RECORD_TYPES:
            results[rt_upper] = _resolve(domain, rt_upper)
    return results


def health_check(domain: str) -> dict:
    """Run a comprehensive health check on a domain."""
    checks = {}

    # 1. Basic resolution
    a_result = _resolve(domain, "A")
    checks["a_record"] = {
        "status": "pass" if a_result["status"] == "ok" else "fail",
        "detail": f"{a_result['count']} A record(s) found" if a_result["status"] == "ok" else a_result.get("error", "No A records"),
        "response_time_ms": a_result["response_time_ms"],
    }

    # 2. IPv6 support
    aaaa_result = _resolve(domain, "AAAA")
    checks["ipv6"] = {
        "status": "pass" if aaaa_result["status"] == "ok" else "warn",
        "detail": f"{aaaa_result['count']} AAAA record(s)" if aaaa_result["status"] == "ok" else "No IPv6 (AAAA) records",
        "response_time_ms": aaaa_result["response_time_ms"],
    }

    # 3. Nameserver check
    ns_result = _resolve(domain, "NS")
    ns_count = ns_result["count"]
    checks["nameservers"] = {
        "status": "pass" if ns_count >= 2 else ("warn" if ns_count == 1 else "fail"),
        "detail": f"{ns_count} nameserver(s)" + (" (recommend >= 2)" if ns_count < 2 else ""),
        "response_time_ms": ns_result["response_time_ms"],
        "nameservers": [r.get("value", "") for r in ns_result.get("records", [])],
    }

    # 4. Mail (MX)
    mx_result = _resolve(domain, "MX")
    checks["mail"] = {
        "status": "pass" if mx_result["status"] == "ok" else "info",
        "detail": f"{mx_result['count']} MX record(s)" if mx_result["status"] == "ok" else "No MX records",
        "response_time_ms": mx_result["response_time_ms"],
    }

    # 5. SPF
    txt_result = _resolve(domain, "TXT")
    spf_found = any("v=spf1" in r.get("value", "") for r in txt_result.get("records", []))
    checks["spf"] = {
        "status": "pass" if spf_found else "warn",
        "detail": "SPF record found" if spf_found else "No SPF record (email spoofing risk)",
    }

    # 6. DMARC
    dmarc_result = _resolve(f"_dmarc.{domain}", "TXT")
    dmarc_found = any("v=DMARC1" in r.get("value", "").upper() for r in dmarc_result.get("records", []))
    checks["dmarc"] = {
        "status": "pass" if dmarc_found else "warn",
        "detail": "DMARC record found" if dmarc_found else "No DMARC record",
    }

    # 7. SOA
    soa_result = _resolve(domain, "SOA")
    checks["soa"] = {
        "status": "pass" if soa_result["status"] == "ok" else "fail",
        "detail": "SOA record present" if soa_result["status"] == "ok" else "No SOA record",
        "response_time_ms": soa_result["response_time_ms"],
    }

    # 8. TCP connectivity on port 80/443
    for port, label in [(80, "http"), (443, "https")]:
        start = time.monotonic()
        try:
            s = socket.create_connection((domain, port), timeout=5)
            s.close()
            elapsed = round((time.monotonic() - start) * 1000, 2)
            checks[label] = {"status": "pass", "detail": f"Port {port} open", "response_time_ms": elapsed}
        except Exception:
            elapsed = round((time.monotonic() - start) * 1000, 2)
            checks[label] = {"status": "fail", "detail": f"Port {port} unreachable", "response_time_ms": elapsed}

    # Score
    score_map = {"pass": 10, "warn": 5, "info": 7, "fail": 0}
    total = sum(score_map.get(v["status"], 0) for v in checks.values())
    max_score = len(checks) * 10
    health_pct = round((total / max_score) * 100) if max_score else 0

    return {
        "domain": domain,
        "health_score": health_pct,
        "checks": checks,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


async def save_lookup_history(user_id: str, domain: str, record_types: list, results: dict):
    """Persist a lookup to MongoDB for history."""
    doc = {
        "lookup_id": str(uuid.uuid4()),
        "user_id": user_id,
        "domain": domain,
        "record_types": record_types,
        "result_summary": {
            rt: {"count": v.get("count", 0), "status": v.get("status")}
            for rt, v in results.items()
        },
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.dns_lookup_history.insert_one(doc)


async def get_lookup_history(user_id: str, limit: int = 25):
    """Return recent lookup history for a user."""
    cursor = db.dns_lookup_history.find(
        {"user_id": user_id}, {"_id": 0}
    ).sort("created_at", -1).limit(limit)
    return await cursor.to_list(length=limit)


async def add_monitored_domain(user_id: str, domain: str):
    """Add a domain to the user's monitoring list."""
    existing = await db.dns_monitors.find_one({"user_id": user_id, "domain": domain})
    if existing:
        return None
    doc = {
        "monitor_id": str(uuid.uuid4()),
        "user_id": user_id,
        "domain": domain,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "last_checked": None,
        "last_health_score": None,
    }
    await db.dns_monitors.insert_one(doc)
    doc.pop("_id", None)
    return doc


async def list_monitored_domains(user_id: str):
    """Return all monitored domains for a user."""
    cursor = db.dns_monitors.find({"user_id": user_id}, {"_id": 0})
    return await cursor.to_list(length=100)


async def remove_monitored_domain(user_id: str, monitor_id: str):
    """Remove a domain from monitoring."""
    result = await db.dns_monitors.delete_one({"monitor_id": monitor_id, "user_id": user_id})
    return result.deleted_count > 0


async def refresh_monitor(user_id: str, monitor_id: str):
    """Run a health check on a monitored domain and update its status."""
    doc = await db.dns_monitors.find_one({"monitor_id": monitor_id, "user_id": user_id})
    if not doc:
        return None
    health = health_check(doc["domain"])
    await db.dns_monitors.update_one(
        {"monitor_id": monitor_id},
        {"$set": {
            "last_checked": datetime.now(timezone.utc).isoformat(),
            "last_health_score": health["health_score"],
            "last_checks": {k: {"status": v["status"], "detail": v["detail"]} for k, v in health["checks"].items()},
        }},
    )
    return health
