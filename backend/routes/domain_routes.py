"""Domain configuration and Route53 DNS management endpoints."""
import os
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, Request
from config.database import db
from auth.service import get_current_user
from models.core import User
from services.ses_transactional_svc import SESService
from services.aws_media_svc import CloudFrontService
from services.route53_svc import Route53Service

router = APIRouter(tags=["Domain & DNS"])

ses_service = SESService()
cloudfront_service = CloudFrontService()
route53_service = Route53Service()


def _get_required_dns_records(domain: str):
    """Build the list of recommended DNS records."""
    cloudfront_dist = os.getenv("CLOUDFRONT_DISTRIBUTION_ID", "")
    cloudfront_domain = os.getenv("CLOUDFRONT_DOMAIN", f"cdn.{domain}")
    return [
        # ── Core Website Records ────────────────────────────────────
        {
            "type": "A",
            "name": domain,
            "value": "ALIAS to CloudFront or ELB endpoint",
            "purpose": "Main website - apex domain routing",
            "priority": "required",
        },
        {
            "type": "AAAA",
            "name": domain,
            "value": "ALIAS to CloudFront or ELB endpoint (IPv6)",
            "purpose": "IPv6 support for main website",
            "priority": "required",
        },
        {
            "type": "CNAME",
            "name": f"www.{domain}",
            "value": domain,
            "purpose": "WWW redirect to apex domain",
            "priority": "required",
        },
        {
            "type": "CNAME",
            "name": f"api.{domain}",
            "value": domain,
            "purpose": "API subdomain for backend services",
            "priority": "required",
        },
        {
            "type": "CNAME",
            "name": f"app.{domain}",
            "value": domain,
            "purpose": "Web application subdomain",
            "priority": "recommended",
        },
        {
            "type": "CNAME",
            "name": f"staging.{domain}",
            "value": domain,
            "purpose": "Staging environment subdomain",
            "priority": "recommended",
        },

        # ── CDN / CloudFront ────────────────────────────────────────
        {
            "type": "CNAME",
            "name": f"cdn.{domain}",
            "value": f"{cloudfront_dist}.cloudfront.net" if cloudfront_dist else cloudfront_domain,
            "purpose": "CDN / CloudFront media delivery",
            "priority": "required",
        },

        # ── Email Authentication (SPF, DKIM, DMARC, BIMI) ──────────
        {
            "type": "TXT",
            "name": domain,
            "value": "v=spf1 include:amazonses.com include:amazonworkmail.com -all",
            "purpose": "SPF - Authorized email senders (SES + WorkMail)",
            "priority": "required",
        },
        {
            "type": "TXT",
            "name": f"_dmarc.{domain}",
            "value": f"v=DMARC1; p=reject; sp=reject; adkim=s; aspf=s; rua=mailto:dmarc-reports@{domain}; ruf=mailto:dmarc-forensic@{domain}; pct=100",
            "purpose": "DMARC - Strict email policy with aggregate + forensic reporting",
            "priority": "required",
        },
        {
            "type": "CNAME",
            "name": f"<token1>._domainkey.{domain}",
            "value": "<token1>.dkim.amazonses.com",
            "purpose": "DKIM - Email signature verification (key 1 of 3)",
            "priority": "required",
        },
        {
            "type": "CNAME",
            "name": f"<token2>._domainkey.{domain}",
            "value": "<token2>.dkim.amazonses.com",
            "purpose": "DKIM - Email signature verification (key 2 of 3)",
            "priority": "required",
        },
        {
            "type": "CNAME",
            "name": f"<token3>._domainkey.{domain}",
            "value": "<token3>.dkim.amazonses.com",
            "purpose": "DKIM - Email signature verification (key 3 of 3)",
            "priority": "required",
        },
        {
            "type": "TXT",
            "name": f"default._bimi.{domain}",
            "value": f"v=BIMI1; l=https://cdn.{domain}/assets/bimi-logo.svg",
            "purpose": "BIMI - Brand logo in email clients (requires VMC certificate)",
            "priority": "recommended",
        },

        # ── SES & WorkMail ──────────────────────────────────────────
        {
            "type": "TXT",
            "name": f"_amazonses.{domain}",
            "value": "<ses-verification-token>",
            "purpose": "SES domain ownership verification",
            "priority": "required",
        },
        {
            "type": "MX",
            "name": domain,
            "value": "10 inbound-smtp.us-east-1.amazonaws.com",
            "purpose": "Email receiving via SES inbound",
            "priority": "required",
        },
        {
            "type": "CNAME",
            "name": f"mail.{domain}",
            "value": "inbound-smtp.us-east-1.amazonaws.com",
            "purpose": "Mail subdomain for email routing",
            "priority": "recommended",
        },
        {
            "type": "CNAME",
            "name": f"autodiscover.{domain}",
            "value": "autodiscover.mail.us-east-1.awsapps.com",
            "purpose": "WorkMail auto-discover for Outlook/mobile clients",
            "priority": "recommended",
        },

        # ── MTA-STS & TLS Reporting ────────────────────────────────
        {
            "type": "TXT",
            "name": f"_mta-sts.{domain}",
            "value": "v=STSv1; id=20260218",
            "purpose": "MTA-STS - Enforce TLS for inbound email",
            "priority": "recommended",
        },
        {
            "type": "CNAME",
            "name": f"mta-sts.{domain}",
            "value": domain,
            "purpose": "MTA-STS policy host (serves /.well-known/mta-sts.txt)",
            "priority": "recommended",
        },
        {
            "type": "TXT",
            "name": f"_smtp._tls.{domain}",
            "value": f"v=TLSRPTv1; rua=mailto:tls-reports@{domain}",
            "purpose": "SMTP TLS Reporting - receive TLS failure reports",
            "priority": "recommended",
        },

        # ── SSL / Certificate Authority ─────────────────────────────
        {
            "type": "CAA",
            "name": domain,
            "value": '0 issue "amazon.com"',
            "purpose": "CAA - Authorize Amazon ACM to issue SSL certificates",
            "priority": "required",
        },
        {
            "type": "CAA",
            "name": domain,
            "value": '0 issue "letsencrypt.org"',
            "purpose": "CAA - Authorize Let's Encrypt as backup SSL issuer",
            "priority": "recommended",
        },
        {
            "type": "CAA",
            "name": domain,
            "value": '0 iodef "mailto:security@' + domain + '"',
            "purpose": "CAA - Report unauthorized certificate issuance attempts",
            "priority": "recommended",
        },

        # ── Service Discovery ───────────────────────────────────────
        {
            "type": "SRV",
            "name": f"_sip._tls.{domain}",
            "value": f"10 5 443 sip.{domain}",
            "purpose": "SIP/TLS service discovery for Amazon Connect VoIP",
            "priority": "optional",
        },
        {
            "type": "SRV",
            "name": f"_submission._tcp.{domain}",
            "value": "10 5 587 email-smtp.us-east-1.amazonaws.com",
            "purpose": "SMTP submission service discovery for email clients",
            "priority": "optional",
        },
        {
            "type": "NAPTR",
            "name": domain,
            "value": '10 100 "S" "SIP+D2T" "" _sip._tcp.' + domain,
            "purpose": "NAPTR - SIP over TCP service routing for VoIP/Connect",
            "priority": "optional",
        },
        {
            "type": "NAPTR",
            "name": domain,
            "value": '20 100 "S" "SIP+D2U" "" _sip._udp.' + domain,
            "purpose": "NAPTR - SIP over UDP fallback for VoIP/Connect",
            "priority": "optional",
        },

        # ── Verification & Ownership ───────────────────────────────
        {
            "type": "TXT",
            "name": domain,
            "value": "google-site-verification=<your-verification-code>",
            "purpose": "Google Search Console - site ownership verification",
            "priority": "optional",
        },
        {
            "type": "TXT",
            "name": domain,
            "value": "apple-domain-verification=<your-apple-token>",
            "purpose": "Apple - domain verification for Apple Business/Pay",
            "priority": "optional",
        },
        {
            "type": "TXT",
            "name": domain,
            "value": "facebook-domain-verification=<your-fb-token>",
            "purpose": "Facebook/Meta - domain verification for Business Suite",
            "priority": "optional",
        },

        # ── Status & Monitoring ─────────────────────────────────────
        {
            "type": "CNAME",
            "name": f"status.{domain}",
            "value": domain,
            "purpose": "Status page subdomain for service health monitoring",
            "priority": "optional",
        },
    ]


# ============================================================
# Domain Configuration Endpoints
# ============================================================

@router.get("/domain/status")
async def get_domain_status():
    """Get domain configuration status for bigmannentertainment.com"""
    domain = "bigmannentertainment.com"
    status = {
        "domain": domain,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "ses": {"status": "unknown"},
        "dns_records": [],
        "cloudfront": {"status": "unknown"},
    }

    # Check SES domain identity
    if ses_service.ses_available:
        try:
            identities = ses_service.ses_client.list_identities(IdentityType="Domain")
            domain_identities = identities.get("Identities", [])
            if domain in domain_identities:
                attrs = ses_service.ses_client.get_identity_verification_attributes(
                    Identities=[domain]
                )
                ver = attrs.get("VerificationAttributes", {}).get(domain, {})
                status["ses"] = {
                    "status": ver.get("VerificationStatus", "NotStarted"),
                    "domain_registered": True,
                }
            else:
                status["ses"] = {"status": "NotStarted", "domain_registered": False}
        except Exception as e:
            status["ses"] = {"status": "error", "error": str(e)}

    # Check CloudFront
    if cloudfront_service.cloudfront_available:
        status["cloudfront"] = {
            "status": "configured",
            "domain": cloudfront_service.distribution_domain,
        }
    else:
        status["cloudfront"] = {"status": "not_configured"}

    # Required DNS records
    status["dns_records"] = _get_required_dns_records(domain)

    # Route53 status
    if route53_service.available:
        zone = route53_service.get_zone_info()
        status["route53"] = {
            "status": "connected",
            "zone_id": zone["id"] if zone else None,
            "record_count": zone["record_count"] if zone else 0,
            "name_servers": zone["name_servers"] if zone else [],
        }
    else:
        status["route53"] = {"status": "unavailable"}

    return status


@router.post("/domain/ses/verify")
async def verify_ses_domain(current_user: User = Depends(get_current_user)):
    """Initiate SES domain identity verification for bigmannentertainment.com"""
    domain = "bigmannentertainment.com"
    if not ses_service.ses_available:
        raise HTTPException(status_code=503, detail="SES service unavailable")
    try:
        result = ses_service.ses_client.verify_domain_identity(Domain=domain)
        verification_token = result.get("VerificationToken", "")

        dkim = ses_service.ses_client.verify_domain_dkim(Domain=domain)
        dkim_tokens = dkim.get("DkimTokens", [])

        dns_records = [
            {
                "type": "TXT",
                "name": f"_amazonses.{domain}",
                "value": verification_token,
                "purpose": "SES Domain Verification",
            }
        ]
        for token in dkim_tokens:
            dns_records.append({
                "type": "CNAME",
                "name": f"{token}._domainkey.{domain}",
                "value": f"{token}.dkim.amazonses.com",
                "purpose": "DKIM Email Authentication",
            })

        dns_records.append({
            "type": "TXT",
            "name": domain,
            "value": "v=spf1 include:amazonses.com ~all",
            "purpose": "SPF Email Authentication",
        })

        dns_records.append({
            "type": "TXT",
            "name": f"_dmarc.{domain}",
            "value": "v=DMARC1; p=quarantine; rua=mailto:dmarc@bigmannentertainment.com",
            "purpose": "DMARC Policy",
        })

        return {
            "status": "verification_initiated",
            "domain": domain,
            "dns_records_to_add": dns_records,
            "instructions": (
                "Add these DNS records to your domain registrar. "
                "Verification typically takes 1-72 hours after records propagate."
            ),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SES domain verification failed: {str(e)}")


@router.get("/domain/ses/check")
async def check_ses_domain_verification(current_user: User = Depends(get_current_user)):
    """Check SES domain verification status"""
    domain = "bigmannentertainment.com"
    if not ses_service.ses_available:
        raise HTTPException(status_code=503, detail="SES service unavailable")
    try:
        attrs = ses_service.ses_client.get_identity_verification_attributes(
            Identities=[domain]
        )
        ver = attrs.get("VerificationAttributes", {}).get(domain, {})
        dkim_attrs = ses_service.ses_client.get_identity_dkim_attributes(
            Identities=[domain]
        )
        dkim = dkim_attrs.get("DkimAttributes", {}).get(domain, {})
        return {
            "domain": domain,
            "verification_status": ver.get("VerificationStatus", "NotStarted"),
            "dkim_enabled": dkim.get("DkimEnabled", False),
            "dkim_verification_status": dkim.get("DkimVerificationStatus", "NotStarted"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/domain/dns-guide")
async def get_dns_configuration_guide():
    """Get complete DNS configuration guide for bigmannentertainment.com"""
    domain = "bigmannentertainment.com"
    return {
        "domain": domain,
        "required_records": _get_required_dns_records(domain),
        "instructions": {
            "step_1": "Log into your domain registrar (GoDaddy, Namecheap, Route53, etc.)",
            "step_2": "Navigate to DNS management for bigmannentertainment.com",
            "step_3": "Add each DNS record listed below",
            "step_4": "Wait 1-48 hours for DNS propagation",
            "step_5": "Use /api/domain/ses/check to verify email domain",
            "step_6": "Use /api/domain/status to verify all services",
        },
    }


# ============================================================
# Route53 DNS Management Endpoints
# ============================================================

@router.get("/route53/zone")
async def get_route53_zone():
    """Get Route53 hosted zone info for bigmannentertainment.com"""
    if not route53_service.available:
        raise HTTPException(status_code=503, detail="Route53 service unavailable")
    info = route53_service.get_zone_info()
    if not info:
        raise HTTPException(status_code=404, detail="Hosted zone not found")
    return info


@router.get("/route53/records")
async def list_route53_records():
    """List all DNS records in the hosted zone"""
    if not route53_service.available:
        raise HTTPException(status_code=503, detail="Route53 service unavailable")
    return {"records": route53_service.list_records()}


@router.post("/route53/record")
async def upsert_route53_record(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    """Create or update a DNS record"""
    if not route53_service.available:
        raise HTTPException(status_code=503, detail="Route53 service unavailable")
    body = await request.json()
    name = body.get("name", "")
    rtype = body.get("type", "")
    values = body.get("values", [])
    ttl = body.get("ttl", 300)
    if not name or not rtype or not values:
        raise HTTPException(status_code=400, detail="name, type, and values are required")
    try:
        route53_service.upsert_record(name, rtype, values, ttl)
        return {"status": "ok", "action": "UPSERT", "name": name, "type": rtype}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/route53/record")
async def delete_route53_record(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    """Delete a DNS record"""
    if not route53_service.available:
        raise HTTPException(status_code=503, detail="Route53 service unavailable")
    body = await request.json()
    name = body.get("name", "")
    rtype = body.get("type", "")
    values = body.get("values", [])
    ttl = body.get("ttl", 300)
    if not name or not rtype or not values:
        raise HTTPException(status_code=400, detail="name, type, and values are required")
    try:
        route53_service.delete_record(name, rtype, values, ttl)
        return {"status": "ok", "action": "DELETE", "name": name, "type": rtype}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/route53/auto-configure")
async def auto_configure_dns(current_user: User = Depends(get_current_user)):
    """Auto-configure all required DNS records (SES, DKIM, SPF, DMARC, WWW, MX)"""
    if not route53_service.available:
        raise HTTPException(status_code=503, detail="Route53 service unavailable")

    domain = "bigmannentertainment.com"
    ses_token = ""
    dkim_tokens = []

    if ses_service.ses_available:
        try:
            result = ses_service.ses_client.verify_domain_identity(Domain=domain)
            ses_token = result.get("VerificationToken", "")
            dkim = ses_service.ses_client.verify_domain_dkim(Domain=domain)
            dkim_tokens = dkim.get("DkimTokens", [])
        except Exception as e:
            logging.warning(f"SES token fetch failed: {e}")

    try:
        results = route53_service.auto_configure(ses_token, dkim_tokens)
        succeeded = sum(1 for r in results if r["status"] == "ok")
        failed = sum(1 for r in results if r["status"] == "error")
        return {
            "status": "completed",
            "domain": domain,
            "total": len(results),
            "succeeded": succeeded,
            "failed": failed,
            "results": results,
            "message": f"Auto-configured {succeeded}/{len(results)} DNS records. DNS propagation may take up to 48 hours.",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
