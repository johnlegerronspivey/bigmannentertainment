"""AWS Interactive Video Service (IVS) - Low-latency live streaming."""
import os
import logging
import boto3
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class IVSService:
    def __init__(self):
        self.region = os.environ.get("AWS_REGION", "us-east-1")
        self.available = False
        self._client = None

        try:
            self._client = boto3.client(
                "ivs",
                aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
                region_name=self.region,
            )
            # Quick availability check
            self._client.list_channels(maxResults=1)
            self.available = True
        except Exception as e:
            logger.warning(f"IVS init failed: {e}")

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------
    def get_status(self) -> Dict[str, Any]:
        if not self.available:
            return {"available": False}
        try:
            channels = self._client.list_channels(maxResults=1)
            return {
                "available": True,
                "region": self.region,
                "service": "Amazon Interactive Video Service",
            }
        except Exception as e:
            return {"available": False, "error": str(e)}

    # ------------------------------------------------------------------
    # Channels
    # ------------------------------------------------------------------
    def create_channel(self, name: str, channel_type: str = "STANDARD",
                       latency_mode: str = "LOW", authorized: bool = False,
                       tags: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        if not self.available:
            raise RuntimeError("IVS not available")

        params: Dict[str, Any] = {
            "name": name,
            "type": channel_type,
            "latencyMode": latency_mode,
            "authorized": authorized,
        }
        if tags:
            params["tags"] = tags

        resp = self._client.create_channel(**params)
        channel = resp["channel"]
        stream_key = resp["streamKey"]

        return {
            "channel_arn": channel["arn"],
            "channel_name": channel["name"],
            "ingest_endpoint": channel["ingestEndpoint"],
            "playback_url": channel["playbackUrl"],
            "stream_key_arn": stream_key["arn"],
            "stream_key_value": stream_key["value"],
            "latency_mode": channel["latencyMode"],
            "type": channel["type"],
            "authorized": channel.get("authorized", False),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    def list_channels(self, max_results: int = 50) -> List[Dict[str, Any]]:
        if not self.available:
            raise RuntimeError("IVS not available")

        resp = self._client.list_channels(maxResults=max_results)
        channels = []
        for ch in resp.get("channels", []):
            channels.append({
                "channel_arn": ch["arn"],
                "channel_name": ch["name"],
                "latency_mode": ch["latencyMode"],
                "authorized": ch.get("authorized", False),
                "tags": ch.get("tags", {}),
            })
        return channels

    def get_channel(self, channel_arn: str) -> Dict[str, Any]:
        if not self.available:
            raise RuntimeError("IVS not available")

        resp = self._client.get_channel(arn=channel_arn)
        ch = resp["channel"]
        return {
            "channel_arn": ch["arn"],
            "channel_name": ch["name"],
            "ingest_endpoint": ch["ingestEndpoint"],
            "playback_url": ch["playbackUrl"],
            "latency_mode": ch["latencyMode"],
            "type": ch["type"],
            "authorized": ch.get("authorized", False),
            "recording_configuration_arn": ch.get("recordingConfigurationArn", ""),
            "tags": ch.get("tags", {}),
        }

    def delete_channel(self, channel_arn: str) -> bool:
        if not self.available:
            raise RuntimeError("IVS not available")
        try:
            self._client.delete_channel(arn=channel_arn)
            return True
        except Exception as e:
            logger.error(f"Delete channel failed: {e}")
            return False

    # ------------------------------------------------------------------
    # Streams
    # ------------------------------------------------------------------
    def get_stream(self, channel_arn: str) -> Optional[Dict[str, Any]]:
        if not self.available:
            raise RuntimeError("IVS not available")
        try:
            resp = self._client.get_stream(channelArn=channel_arn)
            s = resp["stream"]
            return {
                "channel_arn": s["channelArn"],
                "state": s["state"],
                "health": s["health"],
                "viewer_count": s.get("viewerCount", 0),
                "start_time": s["startTime"].isoformat() if hasattr(s.get("startTime"), "isoformat") else str(s.get("startTime", "")),
            }
        except ClientError as e:
            if e.response["Error"]["Code"] == "ChannelNotBroadcasting":
                return None
            raise

    def stop_stream(self, channel_arn: str) -> bool:
        if not self.available:
            raise RuntimeError("IVS not available")
        try:
            self._client.stop_stream(channelArn=channel_arn)
            return True
        except Exception as e:
            logger.error(f"Stop stream failed: {e}")
            return False

    def list_streams(self, max_results: int = 50) -> List[Dict[str, Any]]:
        if not self.available:
            raise RuntimeError("IVS not available")

        resp = self._client.list_streams(maxResults=max_results)
        streams = []
        for s in resp.get("streams", []):
            streams.append({
                "channel_arn": s["channelArn"],
                "state": s["state"],
                "health": s["health"],
                "viewer_count": s.get("viewerCount", 0),
                "start_time": s["startTime"].isoformat() if hasattr(s.get("startTime"), "isoformat") else str(s.get("startTime", "")),
            })
        return streams

    # ------------------------------------------------------------------
    # Stream Keys
    # ------------------------------------------------------------------
    def list_stream_keys(self, channel_arn: str) -> List[Dict[str, Any]]:
        if not self.available:
            raise RuntimeError("IVS not available")

        resp = self._client.list_stream_keys(channelArn=channel_arn, maxResults=50)
        keys = []
        for k in resp.get("streamKeys", []):
            keys.append({
                "arn": k["arn"],
                "channel_arn": k["channelArn"],
            })
        return keys

    def create_stream_key(self, channel_arn: str) -> Dict[str, Any]:
        if not self.available:
            raise RuntimeError("IVS not available")

        resp = self._client.create_stream_key(channelArn=channel_arn)
        sk = resp["streamKey"]
        return {
            "arn": sk["arn"],
            "channel_arn": sk["channelArn"],
            "value": sk["value"],
        }

    # ------------------------------------------------------------------
    # Recording Configuration
    # ------------------------------------------------------------------
    def list_recording_configs(self) -> List[Dict[str, Any]]:
        if not self.available:
            raise RuntimeError("IVS not available")

        resp = self._client.list_recording_configurations(maxResults=50)
        configs = []
        for rc in resp.get("recordingConfigurations", []):
            configs.append({
                "arn": rc["arn"],
                "name": rc.get("name", ""),
                "state": rc["state"],
                "destination_bucket": rc.get("destinationConfiguration", {}).get("s3", {}).get("bucketName", ""),
            })
        return configs
