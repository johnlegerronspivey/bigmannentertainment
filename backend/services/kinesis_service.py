"""AWS Kinesis Service - Real-time data streaming & analytics."""
import os
import logging
import boto3
from typing import Dict, Any, List
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class KinesisService:
    def __init__(self):
        self.region = os.environ.get("AWS_REGION", "us-east-1")
        self.available = False
        self._client = None
        self._firehose = None
        self._analytics = None
        try:
            self._client = boto3.client(
                "kinesis",
                aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
                region_name=self.region,
            )
            self._client.list_streams(Limit=1)
            self.available = True
            self._firehose = boto3.client(
                "firehose",
                aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
                region_name=self.region,
            )
        except Exception as e:
            logger.warning(f"Kinesis init failed: {e}")

    def get_status(self) -> Dict[str, Any]:
        if not self.available:
            return {"available": False}
        return {"available": True, "region": self.region, "service": "Amazon Kinesis"}

    def list_streams(self) -> List[Dict[str, Any]]:
        resp = self._client.list_streams(Limit=50)
        streams = []
        for name in resp.get("StreamNames", []):
            try:
                desc = self._client.describe_stream_summary(StreamName=name)
                summary = desc.get("StreamDescriptionSummary", {})
                streams.append({
                    "name": name,
                    "status": summary.get("StreamStatus", ""),
                    "shard_count": summary.get("OpenShardCount", 0),
                    "retention_hours": summary.get("RetentionPeriodHours", 0),
                    "encryption": summary.get("EncryptionType", "NONE"),
                    "arn": summary.get("StreamARN", ""),
                })
            except ClientError:
                streams.append({"name": name, "status": "UNKNOWN"})
        return streams

    def list_firehose_streams(self) -> List[Dict[str, Any]]:
        if not self._firehose:
            return []
        try:
            resp = self._firehose.list_delivery_streams(Limit=50)
            streams = []
            for name in resp.get("DeliveryStreamNames", []):
                try:
                    desc = self._firehose.describe_delivery_stream(DeliveryStreamName=name)
                    ds = desc.get("DeliveryStreamDescription", {})
                    streams.append({
                        "name": name,
                        "status": ds.get("DeliveryStreamStatus", ""),
                        "type": ds.get("DeliveryStreamType", ""),
                        "arn": ds.get("DeliveryStreamARN", ""),
                        "created_at": ds.get("CreateTimestamp", "").isoformat() if ds.get("CreateTimestamp") else "",
                    })
                except ClientError:
                    streams.append({"name": name, "status": "UNKNOWN"})
            return streams
        except ClientError:
            return []

    def describe_stream(self, stream_name: str) -> Dict[str, Any]:
        resp = self._client.describe_stream_summary(StreamName=stream_name)
        s = resp.get("StreamDescriptionSummary", {})
        return {
            "name": s.get("StreamName", ""),
            "arn": s.get("StreamARN", ""),
            "status": s.get("StreamStatus", ""),
            "shard_count": s.get("OpenShardCount", 0),
            "retention_hours": s.get("RetentionPeriodHours", 0),
            "encryption": s.get("EncryptionType", "NONE"),
            "enhanced_monitoring": [
                m.get("ShardLevelMetrics", [])
                for m in s.get("EnhancedMonitoring", [])
            ],
        }

    def get_stream_metrics(self, stream_name: str) -> Dict[str, Any]:
        """Get basic stream shard info as proxy metrics."""
        resp = self._client.describe_stream_summary(StreamName=stream_name)
        s = resp.get("StreamDescriptionSummary", {})
        return {
            "stream_name": stream_name,
            "open_shards": s.get("OpenShardCount", 0),
            "retention_hours": s.get("RetentionPeriodHours", 0),
            "consumers": s.get("ConsumerCount", 0),
        }
