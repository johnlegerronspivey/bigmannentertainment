"""AWS Elemental MediaPackage - Video origination & packaging for distribution."""
import os
import logging
import boto3
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class MediaPackageService:
    def __init__(self):
        self.region = os.environ.get("AWS_REGION", "us-east-1")
        self.available = False
        self._client = None

        try:
            self._client = boto3.client(
                "mediapackage",
                aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
                region_name=self.region,
            )
            # Quick availability check
            self._client.list_channels(MaxResults=1)
            self.available = True
        except Exception as e:
            logger.warning(f"MediaPackage init failed: {e}")

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------
    def get_status(self) -> Dict[str, Any]:
        if not self.available:
            return {"available": False}
        try:
            return {
                "available": True,
                "region": self.region,
                "service": "AWS Elemental MediaPackage",
            }
        except Exception as e:
            return {"available": False, "error": str(e)}

    # ------------------------------------------------------------------
    # Channels (origin endpoints ingest HLS/DASH from encoders)
    # ------------------------------------------------------------------
    def create_channel(self, channel_id: str, description: str = "") -> Dict[str, Any]:
        if not self.available:
            raise RuntimeError("MediaPackage not available")

        resp = self._client.create_channel(
            Id=channel_id,
            Description=description or f"Big Mann Entertainment - {channel_id}",
            Tags={"Project": "BigMannEntertainment"},
        )

        ingest = resp.get("HlsIngest", {}).get("IngestEndpoints", [])
        endpoints = []
        for ep in ingest:
            endpoints.append({
                "id": ep.get("Id", ""),
                "url": ep.get("Url", ""),
                "username": ep.get("Username", ""),
                "password": ep.get("Password", ""),
            })

        return {
            "id": resp["Id"],
            "arn": resp["Arn"],
            "description": resp.get("Description", ""),
            "ingest_endpoints": endpoints,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    def list_channels(self, max_results: int = 50) -> List[Dict[str, Any]]:
        if not self.available:
            raise RuntimeError("MediaPackage not available")

        resp = self._client.list_channels(MaxResults=max_results)
        channels = []
        for ch in resp.get("Channels", []):
            ingest = ch.get("HlsIngest", {}).get("IngestEndpoints", [])
            channels.append({
                "id": ch["Id"],
                "arn": ch["Arn"],
                "description": ch.get("Description", ""),
                "ingest_endpoint_count": len(ingest),
                "tags": ch.get("Tags", {}),
            })
        return channels

    def get_channel(self, channel_id: str) -> Dict[str, Any]:
        if not self.available:
            raise RuntimeError("MediaPackage not available")

        resp = self._client.describe_channel(Id=channel_id)
        ingest = resp.get("HlsIngest", {}).get("IngestEndpoints", [])
        endpoints = []
        for ep in ingest:
            endpoints.append({
                "id": ep.get("Id", ""),
                "url": ep.get("Url", ""),
                "username": ep.get("Username", ""),
                "password": ep.get("Password", ""),
            })

        return {
            "id": resp["Id"],
            "arn": resp["Arn"],
            "description": resp.get("Description", ""),
            "ingest_endpoints": endpoints,
            "tags": resp.get("Tags", {}),
        }

    def delete_channel(self, channel_id: str) -> bool:
        if not self.available:
            raise RuntimeError("MediaPackage not available")
        try:
            self._client.delete_channel(Id=channel_id)
            return True
        except Exception as e:
            logger.error(f"Delete channel failed: {e}")
            return False

    # ------------------------------------------------------------------
    # Origin Endpoints (viewer-facing HLS, DASH, MSS, CMAF)
    # ------------------------------------------------------------------
    PACKAGING_FORMATS = {
        "hls": {
            "label": "HLS (HTTP Live Streaming)",
            "description": "Apple HLS - widest device support",
        },
        "dash": {
            "label": "DASH (Dynamic Adaptive Streaming)",
            "description": "MPEG-DASH - standard for adaptive bitrate",
        },
        "mss": {
            "label": "MSS (Microsoft Smooth Streaming)",
            "description": "Smooth Streaming for Microsoft platforms",
        },
        "cmaf": {
            "label": "CMAF (Common Media Application Format)",
            "description": "Low-latency CMAF with chunked transfer",
        },
    }

    def create_origin_endpoint(self, channel_id: str, endpoint_id: str,
                                packaging_format: str = "hls",
                                start_over_window: int = 86400,
                                time_delay: int = 0,
                                description: str = "") -> Dict[str, Any]:
        if not self.available:
            raise RuntimeError("MediaPackage not available")

        params: Dict[str, Any] = {
            "ChannelId": channel_id,
            "Id": endpoint_id,
            "Description": description or f"{packaging_format.upper()} endpoint for {channel_id}",
            "StartoverWindowSeconds": start_over_window,
            "TimeDelaySeconds": time_delay,
            "Tags": {"Project": "BigMannEntertainment"},
        }

        # Set packaging config based on format
        if packaging_format == "hls":
            params["HlsPackage"] = {
                "SegmentDurationSeconds": 6,
                "PlaylistWindowSeconds": 60,
                "PlaylistType": "EVENT",
            }
        elif packaging_format == "dash":
            params["DashPackage"] = {
                "SegmentDurationSeconds": 6,
                "ManifestWindowSeconds": 60,
            }
        elif packaging_format == "mss":
            params["MssPackage"] = {
                "SegmentDurationSeconds": 6,
                "ManifestWindowSeconds": 60,
            }
        elif packaging_format == "cmaf":
            params["CmafPackage"] = {
                "SegmentDurationSeconds": 6,
                "HlsManifests": [{"Id": f"{endpoint_id}-hls", "PlaylistWindowSeconds": 60}],
            }

        resp = self._client.create_origin_endpoint(**params)

        return {
            "id": resp["Id"],
            "arn": resp["Arn"],
            "channel_id": resp["ChannelId"],
            "url": resp.get("Url", ""),
            "description": resp.get("Description", ""),
            "packaging_format": packaging_format,
            "startover_window": resp.get("StartoverWindowSeconds", 0),
            "time_delay": resp.get("TimeDelaySeconds", 0),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    def list_origin_endpoints(self, channel_id: Optional[str] = None,
                               max_results: int = 50) -> List[Dict[str, Any]]:
        if not self.available:
            raise RuntimeError("MediaPackage not available")

        params: Dict[str, Any] = {"MaxResults": max_results}
        if channel_id:
            params["ChannelId"] = channel_id

        resp = self._client.list_origin_endpoints(**params)
        endpoints = []
        for ep in resp.get("OriginEndpoints", []):
            # Detect packaging format
            pkg_fmt = "unknown"
            if ep.get("HlsPackage"):
                pkg_fmt = "hls"
            elif ep.get("DashPackage"):
                pkg_fmt = "dash"
            elif ep.get("MssPackage"):
                pkg_fmt = "mss"
            elif ep.get("CmafPackage"):
                pkg_fmt = "cmaf"

            endpoints.append({
                "id": ep["Id"],
                "arn": ep["Arn"],
                "channel_id": ep["ChannelId"],
                "url": ep.get("Url", ""),
                "packaging_format": pkg_fmt,
                "description": ep.get("Description", ""),
                "tags": ep.get("Tags", {}),
            })
        return endpoints

    def get_origin_endpoint(self, endpoint_id: str) -> Dict[str, Any]:
        if not self.available:
            raise RuntimeError("MediaPackage not available")

        resp = self._client.describe_origin_endpoint(Id=endpoint_id)

        pkg_fmt = "unknown"
        if resp.get("HlsPackage"):
            pkg_fmt = "hls"
        elif resp.get("DashPackage"):
            pkg_fmt = "dash"
        elif resp.get("MssPackage"):
            pkg_fmt = "mss"
        elif resp.get("CmafPackage"):
            pkg_fmt = "cmaf"

        return {
            "id": resp["Id"],
            "arn": resp["Arn"],
            "channel_id": resp["ChannelId"],
            "url": resp.get("Url", ""),
            "packaging_format": pkg_fmt,
            "description": resp.get("Description", ""),
            "startover_window": resp.get("StartoverWindowSeconds", 0),
            "time_delay": resp.get("TimeDelaySeconds", 0),
            "tags": resp.get("Tags", {}),
        }

    def delete_origin_endpoint(self, endpoint_id: str) -> bool:
        if not self.available:
            raise RuntimeError("MediaPackage not available")
        try:
            self._client.delete_origin_endpoint(Id=endpoint_id)
            return True
        except Exception as e:
            logger.error(f"Delete origin endpoint failed: {e}")
            return False

    def get_packaging_formats(self) -> Dict[str, Dict[str, str]]:
        return self.PACKAGING_FORMATS
