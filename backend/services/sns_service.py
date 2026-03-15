"""AWS SNS Service - Simple Notification Service."""
import os
import logging
import boto3
from typing import Dict, Any, List
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class SNSService:
    def __init__(self):
        self.region = os.environ.get("AWS_REGION", "us-east-1")
        self.available = False
        self._client = None
        try:
            self._client = boto3.client(
                "sns",
                aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
                region_name=self.region,
            )
            self._client.list_topics()
            self.available = True
        except Exception as e:
            logger.warning(f"SNS init failed: {e}")

    def get_status(self) -> Dict[str, Any]:
        if not self.available:
            return {"available": False}
        return {"available": True, "region": self.region, "service": "Amazon SNS"}

    def list_topics(self) -> List[Dict[str, Any]]:
        resp = self._client.list_topics()
        topics = []
        for t in resp.get("Topics", []):
            arn = t.get("TopicArn", "")
            try:
                attrs = self._client.get_topic_attributes(TopicArn=arn)["Attributes"]
                topics.append({
                    "arn": arn,
                    "name": arn.split(":")[-1],
                    "subscriptions_confirmed": int(attrs.get("SubscriptionsConfirmed", 0)),
                    "subscriptions_pending": int(attrs.get("SubscriptionsPending", 0)),
                    "display_name": attrs.get("DisplayName", ""),
                    "policy": bool(attrs.get("Policy")),
                })
            except ClientError:
                topics.append({"arn": arn, "name": arn.split(":")[-1]})
        return topics

    def list_subscriptions(self, topic_arn: str = None) -> List[Dict[str, Any]]:
        if topic_arn:
            resp = self._client.list_subscriptions_by_topic(TopicArn=topic_arn)
        else:
            resp = self._client.list_subscriptions()
        return [
            {
                "arn": s.get("SubscriptionArn", ""),
                "protocol": s.get("Protocol", ""),
                "endpoint": s.get("Endpoint", ""),
                "topic_arn": s.get("TopicArn", ""),
                "owner": s.get("Owner", ""),
            }
            for s in resp.get("Subscriptions", [])
        ]

    def list_platform_applications(self) -> List[Dict[str, Any]]:
        resp = self._client.list_platform_applications()
        return [
            {
                "arn": pa.get("PlatformApplicationArn", ""),
                "name": pa.get("PlatformApplicationArn", "").split("/")[-1] if pa.get("PlatformApplicationArn") else "",
                "enabled": pa.get("Attributes", {}).get("Enabled", "false"),
            }
            for pa in resp.get("PlatformApplications", [])
        ]

    def publish_message(self, topic_arn: str, message: str, subject: str = None) -> Dict[str, Any]:
        kwargs = {"TopicArn": topic_arn, "Message": message}
        if subject:
            kwargs["Subject"] = subject
        resp = self._client.publish(**kwargs)
        return {"message_id": resp.get("MessageId", "")}
