"""AWS Pinpoint Service - Marketing campaigns and audience engagement."""
import os
import logging
import boto3
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class PinpointService:
    def __init__(self):
        self.region = os.environ.get("AWS_REGION", "us-east-1")
        self.available = False
        self._client = None

        try:
            self._client = boto3.client(
                "pinpoint",
                aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
                region_name=self.region,
            )
            self._client.get_apps(PageSize="1")
            self.available = True
        except Exception as e:
            logger.warning(f"Pinpoint init failed: {e}")

    def get_status(self) -> Dict[str, Any]:
        if not self.available:
            return {"available": False}
        try:
            resp = self._client.get_apps(PageSize="1")
            app_count = len(resp.get("ApplicationsResponse", {}).get("Item", []))
            return {
                "available": True,
                "region": self.region,
                "service": "Amazon Pinpoint",
                "applications_found": app_count,
            }
        except Exception as e:
            return {"available": False, "error": str(e)}

    # ------------------------------------------------------------------
    # Applications (Projects)
    # ------------------------------------------------------------------
    def list_applications(self) -> List[Dict[str, Any]]:
        if not self.available:
            raise RuntimeError("Pinpoint not available")
        resp = self._client.get_apps(PageSize="50")
        apps = []
        for a in resp.get("ApplicationsResponse", {}).get("Item", []):
            apps.append({
                "application_id": a["Id"],
                "name": a["Name"],
                "arn": a.get("Arn", ""),
                "tags": a.get("tags", {}),
                "creation_date": a.get("CreationDate", ""),
            })
        return apps

    def create_application(self, name: str, tags: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        if not self.available:
            raise RuntimeError("Pinpoint not available")
        params = {"CreateApplicationRequest": {"Name": name}}
        if tags:
            params["CreateApplicationRequest"]["tags"] = tags
        resp = self._client.create_app(**params)
        app_resp = resp["ApplicationResponse"]
        return {
            "application_id": app_resp["Id"],
            "name": app_resp["Name"],
            "arn": app_resp.get("Arn", ""),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    def get_application(self, application_id: str) -> Dict[str, Any]:
        if not self.available:
            raise RuntimeError("Pinpoint not available")
        resp = self._client.get_app(ApplicationId=application_id)
        a = resp["ApplicationResponse"]
        return {
            "application_id": a["Id"],
            "name": a["Name"],
            "arn": a.get("Arn", ""),
            "tags": a.get("tags", {}),
            "creation_date": a.get("CreationDate", ""),
        }

    def delete_application(self, application_id: str) -> bool:
        if not self.available:
            raise RuntimeError("Pinpoint not available")
        try:
            self._client.delete_app(ApplicationId=application_id)
            return True
        except Exception as e:
            logger.error(f"Delete app failed: {e}")
            return False

    # ------------------------------------------------------------------
    # Segments
    # ------------------------------------------------------------------
    def list_segments(self, application_id: str) -> List[Dict[str, Any]]:
        if not self.available:
            raise RuntimeError("Pinpoint not available")
        resp = self._client.get_segments(ApplicationId=application_id, PageSize="50")
        segments = []
        for s in resp.get("SegmentsResponse", {}).get("Item", []):
            segments.append({
                "segment_id": s["Id"],
                "name": s["Name"],
                "segment_type": s.get("SegmentType", ""),
                "version": s.get("Version", 0),
                "creation_date": s.get("CreationDate", ""),
                "last_modified_date": s.get("LastModifiedDate", ""),
            })
        return segments

    def create_segment(self, application_id: str, name: str,
                       dimension_criteria: Optional[Dict] = None) -> Dict[str, Any]:
        if not self.available:
            raise RuntimeError("Pinpoint not available")
        segment_request = {"Name": name, "SegmentGroups": {}}
        if dimension_criteria:
            segment_request["Dimensions"] = dimension_criteria

        resp = self._client.create_segment(
            ApplicationId=application_id,
            WriteSegmentRequest=segment_request,
        )
        seg = resp["SegmentResponse"]
        return {
            "segment_id": seg["Id"],
            "name": seg["Name"],
            "segment_type": seg.get("SegmentType", ""),
            "application_id": seg["ApplicationId"],
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    def delete_segment(self, application_id: str, segment_id: str) -> bool:
        if not self.available:
            raise RuntimeError("Pinpoint not available")
        try:
            self._client.delete_segment(
                ApplicationId=application_id, SegmentId=segment_id
            )
            return True
        except Exception as e:
            logger.error(f"Delete segment failed: {e}")
            return False

    # ------------------------------------------------------------------
    # Campaigns
    # ------------------------------------------------------------------
    def list_campaigns(self, application_id: str) -> List[Dict[str, Any]]:
        if not self.available:
            raise RuntimeError("Pinpoint not available")
        resp = self._client.get_campaigns(ApplicationId=application_id, PageSize="50")
        campaigns = []
        for c in resp.get("CampaignsResponse", {}).get("Item", []):
            campaigns.append({
                "campaign_id": c["Id"],
                "name": c.get("Name", ""),
                "state": c.get("State", {}).get("CampaignStatus", ""),
                "segment_id": c.get("SegmentId", ""),
                "segment_version": c.get("SegmentVersion", 0),
                "creation_date": c.get("CreationDate", ""),
                "last_modified_date": c.get("LastModifiedDate", ""),
                "description": c.get("Description", ""),
            })
        return campaigns

    def create_campaign(self, application_id: str, name: str, segment_id: str,
                        message_config: Dict, description: str = "",
                        schedule: Optional[Dict] = None) -> Dict[str, Any]:
        if not self.available:
            raise RuntimeError("Pinpoint not available")

        campaign_request = {
            "Name": name,
            "SegmentId": segment_id,
            "MessageConfiguration": message_config,
        }
        if description:
            campaign_request["Description"] = description
        if schedule:
            campaign_request["Schedule"] = schedule
        else:
            campaign_request["Schedule"] = {
                "StartTime": "IMMEDIATE",
                "Frequency": "ONCE",
            }

        resp = self._client.create_campaign(
            ApplicationId=application_id,
            WriteCampaignRequest=campaign_request,
        )
        c = resp["CampaignResponse"]
        return {
            "campaign_id": c["Id"],
            "name": c.get("Name", ""),
            "state": c.get("State", {}).get("CampaignStatus", ""),
            "segment_id": c.get("SegmentId", ""),
            "application_id": c["ApplicationId"],
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    def get_campaign(self, application_id: str, campaign_id: str) -> Dict[str, Any]:
        if not self.available:
            raise RuntimeError("Pinpoint not available")
        resp = self._client.get_campaign(
            ApplicationId=application_id, CampaignId=campaign_id
        )
        c = resp["CampaignResponse"]
        return {
            "campaign_id": c["Id"],
            "name": c.get("Name", ""),
            "state": c.get("State", {}).get("CampaignStatus", ""),
            "segment_id": c.get("SegmentId", ""),
            "description": c.get("Description", ""),
            "creation_date": c.get("CreationDate", ""),
            "last_modified_date": c.get("LastModifiedDate", ""),
        }

    def delete_campaign(self, application_id: str, campaign_id: str) -> bool:
        if not self.available:
            raise RuntimeError("Pinpoint not available")
        try:
            self._client.delete_campaign(
                ApplicationId=application_id, CampaignId=campaign_id
            )
            return True
        except Exception as e:
            logger.error(f"Delete campaign failed: {e}")
            return False

    # ------------------------------------------------------------------
    # Direct Messaging
    # ------------------------------------------------------------------
    def send_email_message(self, application_id: str, to_address: str,
                           subject: str, html_body: str,
                           from_address: str) -> Dict[str, Any]:
        if not self.available:
            raise RuntimeError("Pinpoint not available")
        resp = self._client.send_messages(
            ApplicationId=application_id,
            MessageRequest={
                "Addresses": {
                    to_address: {"ChannelType": "EMAIL"}
                },
                "MessageConfiguration": {
                    "EmailMessage": {
                        "FromAddress": from_address,
                        "SimpleEmail": {
                            "Subject": {"Charset": "UTF-8", "Data": subject},
                            "HtmlPart": {"Charset": "UTF-8", "Data": html_body},
                        },
                    }
                },
            },
        )
        result = resp.get("MessageResponse", {}).get("Result", {})
        delivery = result.get(to_address, {}).get("MessageId", "")
        status = result.get(to_address, {}).get("DeliveryStatus", "UNKNOWN")
        return {
            "message_id": delivery,
            "delivery_status": status,
            "to_address": to_address,
        }

    def send_sms_message(self, application_id: str, phone_number: str,
                         body: str, message_type: str = "TRANSACTIONAL") -> Dict[str, Any]:
        if not self.available:
            raise RuntimeError("Pinpoint not available")
        resp = self._client.send_messages(
            ApplicationId=application_id,
            MessageRequest={
                "Addresses": {
                    phone_number: {"ChannelType": "SMS"}
                },
                "MessageConfiguration": {
                    "SMSMessage": {
                        "Body": body,
                        "MessageType": message_type,
                    }
                },
            },
        )
        result = resp.get("MessageResponse", {}).get("Result", {})
        delivery = result.get(phone_number, {}).get("MessageId", "")
        status = result.get(phone_number, {}).get("DeliveryStatus", "UNKNOWN")
        return {
            "message_id": delivery,
            "delivery_status": status,
            "phone_number": phone_number,
        }
