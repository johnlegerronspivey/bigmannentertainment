"""Route53 DNS management service for bigmannentertainment.com"""
import os
import logging
import boto3
from typing import Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

DOMAIN = "bigmannentertainment.com"


class Route53Service:
    def __init__(self):
        self.available = False
        self.client = None
        self.hosted_zone_id = None
        try:
            self.client = boto3.client(
                "route53",
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                region_name=os.getenv("AWS_REGION", "us-east-1"),
            )
            self._resolve_hosted_zone()
            self.available = True
            logger.info(f"Route53 service initialized - zone {self.hosted_zone_id}")
        except Exception as e:
            logger.warning(f"Route53 init failed: {e}")

    def _resolve_hosted_zone(self):
        zones = self.client.list_hosted_zones()
        for z in zones["HostedZones"]:
            if z["Name"] == f"{DOMAIN}." and not z.get("Config", {}).get("PrivateZone"):
                self.hosted_zone_id = z["Id"].split("/")[-1]
                return
        raise ValueError(f"No public hosted zone found for {DOMAIN}")

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------
    def list_records(self):
        if not self.available:
            return []
        resp = self.client.list_resource_record_sets(HostedZoneId=self.hosted_zone_id)
        records = []
        for r in resp["ResourceRecordSets"]:
            name = r["Name"].rstrip(".")
            rec = {
                "name": name,
                "type": r["Type"],
                "ttl": r.get("TTL", 300),
                "values": [v["Value"] for v in r.get("ResourceRecords", [])],
            }
            alias = r.get("AliasTarget")
            if alias:
                rec["alias"] = alias["DNSName"].rstrip(".")
                rec["values"] = [rec["alias"]]
            records.append(rec)
        return records

    def get_zone_info(self):
        if not self.available:
            return None
        zone = self.client.get_hosted_zone(Id=self.hosted_zone_id)
        hz = zone["HostedZone"]
        ns = zone.get("DelegationSet", {}).get("NameServers", [])
        return {
            "id": self.hosted_zone_id,
            "name": hz["Name"].rstrip("."),
            "record_count": hz["ResourceRecordSetCount"],
            "name_servers": ns,
        }

    # ------------------------------------------------------------------
    # Write helpers
    # ------------------------------------------------------------------
    def _change_record(self, action: str, name: str, rtype: str, values: list, ttl: int = 300):
        """UPSERT / CREATE / DELETE a single record."""
        rr = [{"Value": v} for v in values]
        self.client.change_resource_record_sets(
            HostedZoneId=self.hosted_zone_id,
            ChangeBatch={
                "Comment": f"Route53 auto-config {datetime.now(timezone.utc).isoformat()}",
                "Changes": [
                    {
                        "Action": action,
                        "ResourceRecordSet": {
                            "Name": name,
                            "Type": rtype,
                            "TTL": ttl,
                            "ResourceRecords": rr,
                        },
                    }
                ],
            },
        )

    def upsert_record(self, name: str, rtype: str, values: list, ttl: int = 300):
        self._change_record("UPSERT", name, rtype, values, ttl)

    def delete_record(self, name: str, rtype: str, values: list, ttl: int = 300):
        self._change_record("DELETE", name, rtype, values, ttl)

    # ------------------------------------------------------------------
    # Auto-configure all required DNS records
    # ------------------------------------------------------------------
    def auto_configure(self, ses_verification_token: str = "", dkim_tokens: list = None):
        """Create/update all recommended DNS records for the domain."""
        if not self.available:
            raise RuntimeError("Route53 not available")

        results = []

        def _try(label, fn):
            try:
                fn()
                results.append({"record": label, "status": "ok"})
            except Exception as e:
                results.append({"record": label, "status": "error", "error": str(e)})

        # 1. SPF (updated: includes WorkMail, strict -all)
        _try(f"TXT {DOMAIN} (SPF)", lambda: self.upsert_record(
            DOMAIN, "TXT",
            ['"v=spf1 include:amazonses.com include:amazonworkmail.com -all"'], 300))

        # 2. DMARC (updated: strict policy with forensic reporting)
        _try(f"TXT _dmarc.{DOMAIN}", lambda: self.upsert_record(
            f"_dmarc.{DOMAIN}", "TXT",
            [f'"v=DMARC1; p=reject; sp=reject; adkim=s; aspf=s; rua=mailto:dmarc-reports@{DOMAIN}; ruf=mailto:dmarc-forensic@{DOMAIN}; pct=100"'],
            300))

        # 3. SES verification TXT (if token provided)
        if ses_verification_token:
            _try(f"TXT _amazonses.{DOMAIN}", lambda: self.upsert_record(
                f"_amazonses.{DOMAIN}", "TXT",
                [f'"{ses_verification_token}"'], 300))

        # 4. DKIM CNAMEs
        for token in (dkim_tokens or []):
            _try(f"CNAME {token}._domainkey (DKIM)", lambda t=token: self.upsert_record(
                f"{t}._domainkey.{DOMAIN}", "CNAME",
                [f"{t}.dkim.amazonses.com"], 300))

        # 5. WWW redirect
        _try(f"CNAME www.{DOMAIN}", lambda: self.upsert_record(
            f"www.{DOMAIN}", "CNAME", [DOMAIN], 300))

        # 6. API subdomain
        _try(f"CNAME api.{DOMAIN}", lambda: self.upsert_record(
            f"api.{DOMAIN}", "CNAME", [DOMAIN], 300))

        # 7. MX for SES inbound
        _try(f"MX {DOMAIN}", lambda: self.upsert_record(
            DOMAIN, "MX", ["10 inbound-smtp.us-east-1.amazonaws.com"], 300))

        # 8. Mail subdomain
        _try(f"CNAME mail.{DOMAIN}", lambda: self.upsert_record(
            f"mail.{DOMAIN}", "CNAME",
            ["inbound-smtp.us-east-1.amazonaws.com"], 300))

        # 9. WorkMail autodiscover
        _try(f"CNAME autodiscover.{DOMAIN}", lambda: self.upsert_record(
            f"autodiscover.{DOMAIN}", "CNAME",
            ["autodiscover.mail.us-east-1.awsapps.com"], 300))

        # 10. MTA-STS
        _try(f"TXT _mta-sts.{DOMAIN}", lambda: self.upsert_record(
            f"_mta-sts.{DOMAIN}", "TXT",
            ['"v=STSv1; id=20260218"'], 300))

        # 11. SMTP TLS Reporting
        _try(f"TXT _smtp._tls.{DOMAIN}", lambda: self.upsert_record(
            f"_smtp._tls.{DOMAIN}", "TXT",
            [f'"v=TLSRPTv1; rua=mailto:tls-reports@{DOMAIN}"'], 300))

        # 12. CAA - Amazon ACM
        _try(f"CAA {DOMAIN} (amazon)", lambda: self.upsert_record(
            DOMAIN, "CAA", ['0 issue "amazon.com"'], 300))

        return results
