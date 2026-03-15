"""AWS SQS Service - Simple Queue Service."""
import os
import logging
import boto3
from typing import Dict, Any, List
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class SQSService:
    def __init__(self):
        self.region = os.environ.get("AWS_REGION", "us-east-1")
        self.available = False
        self._client = None
        try:
            self._client = boto3.client(
                "sqs",
                aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
                region_name=self.region,
            )
            self._client.list_queues(MaxResults=1)
            self.available = True
        except Exception as e:
            logger.warning(f"SQS init failed: {e}")

    def get_status(self) -> Dict[str, Any]:
        if not self.available:
            return {"available": False}
        return {"available": True, "region": self.region, "service": "Amazon SQS"}

    def list_queues(self) -> List[Dict[str, Any]]:
        resp = self._client.list_queues(MaxResults=100)
        queues = []
        for url in resp.get("QueueUrls", []):
            try:
                attrs = self._client.get_queue_attributes(
                    QueueUrl=url,
                    AttributeNames=["All"],
                )["Attributes"]
                queues.append({
                    "url": url,
                    "name": url.split("/")[-1],
                    "arn": attrs.get("QueueArn", ""),
                    "messages_available": int(attrs.get("ApproximateNumberOfMessages", 0)),
                    "messages_in_flight": int(attrs.get("ApproximateNumberOfMessagesNotVisible", 0)),
                    "messages_delayed": int(attrs.get("ApproximateNumberOfMessagesDelayed", 0)),
                    "visibility_timeout": int(attrs.get("VisibilityTimeout", 30)),
                    "retention_seconds": int(attrs.get("MessageRetentionPeriod", 345600)),
                    "is_fifo": url.endswith(".fifo"),
                    "created": attrs.get("CreatedTimestamp", ""),
                })
            except ClientError:
                queues.append({"url": url, "name": url.split("/")[-1]})
        return queues

    def get_queue_attributes(self, queue_url: str) -> Dict[str, Any]:
        resp = self._client.get_queue_attributes(
            QueueUrl=queue_url, AttributeNames=["All"]
        )
        attrs = resp.get("Attributes", {})
        return {
            "url": queue_url,
            "name": queue_url.split("/")[-1],
            "arn": attrs.get("QueueArn", ""),
            "messages_available": int(attrs.get("ApproximateNumberOfMessages", 0)),
            "messages_in_flight": int(attrs.get("ApproximateNumberOfMessagesNotVisible", 0)),
            "visibility_timeout": int(attrs.get("VisibilityTimeout", 30)),
            "max_message_size": int(attrs.get("MaximumMessageSize", 262144)),
            "retention_seconds": int(attrs.get("MessageRetentionPeriod", 345600)),
            "delay_seconds": int(attrs.get("DelaySeconds", 0)),
            "receive_wait_seconds": int(attrs.get("ReceiveMessageWaitTimeSeconds", 0)),
            "redrive_policy": attrs.get("RedrivePolicy", ""),
        }

    def list_dead_letter_queues(self, queue_arn: str) -> List[Dict[str, Any]]:
        try:
            resp = self._client.list_dead_letter_source_queues(QueueUrl=queue_arn)
            return [{"url": url, "name": url.split("/")[-1]} for url in resp.get("queueUrls", [])]
        except ClientError:
            return []

    def send_message(self, queue_url: str, message_body: str, delay_seconds: int = 0) -> Dict[str, Any]:
        resp = self._client.send_message(
            QueueUrl=queue_url, MessageBody=message_body, DelaySeconds=delay_seconds
        )
        return {"message_id": resp.get("MessageId", ""), "md5": resp.get("MD5OfMessageBody", "")}

    def purge_queue(self, queue_url: str) -> Dict[str, Any]:
        self._client.purge_queue(QueueUrl=queue_url)
        return {"purged": True, "queue_url": queue_url}
