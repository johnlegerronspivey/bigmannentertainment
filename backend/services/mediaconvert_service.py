"""AWS MediaConvert Service - Transcode media for multi-platform distribution."""
import os
import logging
import boto3
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class MediaConvertService:
    def __init__(self):
        self.region = os.environ.get("AWS_REGION", "us-east-1")
        self.s3_bucket = os.environ.get("S3_BUCKET_NAME")
        self.cloudfront_domain = os.environ.get("CLOUDFRONT_DOMAIN", "cdn.bigmannentertainment.com")
        self._endpoint_url = None
        self._client = None
        self.available = False

        try:
            self._sts = boto3.client(
                "sts",
                aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
                region_name=self.region,
            )
            self._account_id = self._sts.get_caller_identity()["Account"]
            self._mc_base = boto3.client(
                "mediaconvert",
                aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
                region_name=self.region,
            )
            self._iam = boto3.client(
                "iam",
                aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
                region_name=self.region,
            )
            self.available = True
        except Exception as e:
            logger.warning(f"MediaConvert init failed: {e}")

    # ------------------------------------------------------------------
    # Endpoint discovery
    # ------------------------------------------------------------------
    def _get_endpoint(self) -> str:
        if self._endpoint_url:
            return self._endpoint_url
        try:
            resp = self._mc_base.describe_endpoints(MaxResults=20)
            endpoints = resp.get("Endpoints", [])
            if endpoints:
                self._endpoint_url = endpoints[0]["Url"]
                return self._endpoint_url
        except Exception as e:
            logger.error(f"Endpoint discovery failed: {e}")
        raise RuntimeError("Could not discover MediaConvert endpoint")

    def _get_client(self):
        if self._client:
            return self._client
        endpoint = self._get_endpoint()
        self._client = boto3.client(
            "mediaconvert",
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
            region_name=self.region,
            endpoint_url=endpoint,
        )
        return self._client

    # ------------------------------------------------------------------
    # IAM role
    # ------------------------------------------------------------------
    def _ensure_role(self) -> str:
        role_name = "BigMannMediaConvertRole"
        try:
            resp = self._iam.get_role(RoleName=role_name)
            return resp["Role"]["Arn"]
        except self._iam.exceptions.NoSuchEntityException:
            pass

        trust_policy = (
            '{"Version":"2012-10-17","Statement":[{"Effect":"Allow",'
            '"Principal":{"Service":"mediaconvert.amazonaws.com"},'
            '"Action":"sts:AssumeRole"}]}'
        )
        resp = self._iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=trust_policy,
            Description="MediaConvert access to S3 for Big Mann Entertainment",
        )
        role_arn = resp["Role"]["Arn"]

        self._iam.attach_role_policy(
            RoleName=role_name,
            PolicyArn="arn:aws:iam::aws:policy/AmazonS3FullAccess",
        )
        self._iam.attach_role_policy(
            RoleName=role_name,
            PolicyArn="arn:aws:iam::aws:policy/AmazonAPIGatewayInvokeFullAccess",
        )
        import time
        time.sleep(10)  # IAM propagation
        return role_arn

    # ------------------------------------------------------------------
    # Presets
    # ------------------------------------------------------------------
    PRESETS: Dict[str, Dict[str, Any]] = {
        "youtube_hd": {
            "label": "YouTube HD 1080p",
            "container": "MP4",
            "video": {"Codec": "H_264", "Width": 1920, "Height": 1080, "RateControlMode": "QVBR", "MaxBitrate": 8000000},
            "audio": {"Codec": "AAC", "Bitrate": 192000, "SampleRate": 48000, "Channels": 2},
        },
        "tiktok_vertical": {
            "label": "TikTok Vertical 1080x1920",
            "container": "MP4",
            "video": {"Codec": "H_264", "Width": 1080, "Height": 1920, "RateControlMode": "QVBR", "MaxBitrate": 4000000},
            "audio": {"Codec": "AAC", "Bitrate": 128000, "SampleRate": 44100, "Channels": 2},
        },
        "instagram_square": {
            "label": "Instagram Square 1080x1080",
            "container": "MP4",
            "video": {"Codec": "H_264", "Width": 1080, "Height": 1080, "RateControlMode": "QVBR", "MaxBitrate": 3500000},
            "audio": {"Codec": "AAC", "Bitrate": 128000, "SampleRate": 44100, "Channels": 2},
        },
        "twitter_hd": {
            "label": "Twitter/X HD 1280x720",
            "container": "MP4",
            "video": {"Codec": "H_264", "Width": 1280, "Height": 720, "RateControlMode": "QVBR", "MaxBitrate": 5000000},
            "audio": {"Codec": "AAC", "Bitrate": 128000, "SampleRate": 48000, "Channels": 2},
        },
        "hls_adaptive": {
            "label": "HLS Adaptive Streaming",
            "container": "M3U8",
            "video": {"Codec": "H_264", "Width": 1920, "Height": 1080, "RateControlMode": "QVBR", "MaxBitrate": 8000000},
            "audio": {"Codec": "AAC", "Bitrate": 128000, "SampleRate": 48000, "Channels": 2},
        },
        "audio_mp3": {
            "label": "MP3 Audio (320kbps)",
            "container": "RAW",
            "audio": {"Codec": "MP3", "Bitrate": 320000, "SampleRate": 44100, "Channels": 2},
        },
        "audio_aac": {
            "label": "AAC Audio (256kbps)",
            "container": "MP4",
            "audio": {"Codec": "AAC", "Bitrate": 256000, "SampleRate": 48000, "Channels": 2},
        },
    }

    # ------------------------------------------------------------------
    # Submit job
    # ------------------------------------------------------------------
    def submit_job(self, s3_input_key: str, preset_key: str, user_id: str) -> Dict[str, Any]:
        if not self.available:
            raise RuntimeError("MediaConvert not available")

        preset = self.PRESETS.get(preset_key)
        if not preset:
            raise ValueError(f"Unknown preset: {preset_key}. Options: {list(self.PRESETS.keys())}")

        client = self._get_client()
        role_arn = self._ensure_role()

        input_uri = f"s3://{self.s3_bucket}/{s3_input_key}"
        output_prefix = f"s3://{self.s3_bucket}/transcoded/{user_id}/{preset_key}/"

        # Build output group
        video_desc = preset.get("video")
        audio_desc = preset.get("audio", {})
        container = preset.get("container", "MP4")

        output_settings: Dict[str, Any] = {"ContainerSettings": {"Container": container}}
        if video_desc:
            codec = video_desc["Codec"]
            output_settings["VideoDescription"] = {
                "Width": video_desc.get("Width", 1920),
                "Height": video_desc.get("Height", 1080),
                "CodecSettings": {
                    "Codec": codec,
                    "H264Settings": {
                        "RateControlMode": video_desc.get("RateControlMode", "QVBR"),
                        "MaxBitrate": video_desc.get("MaxBitrate", 5000000),
                        "QvbrSettings": {"QvbrQualityLevel": 8},
                    },
                },
            }
        if audio_desc:
            acodec = audio_desc.get("Codec", "AAC")
            audio_codec_key = f"{acodec.capitalize()}Settings" if acodec != "MP3" else "Mp3Settings"
            if acodec == "AAC":
                audio_codec_key = "AacSettings"
                audio_codec_val = {
                    "Bitrate": audio_desc.get("Bitrate", 128000),
                    "SampleRate": audio_desc.get("SampleRate", 48000),
                    "CodingMode": "CODING_MODE_2_0" if audio_desc.get("Channels", 2) == 2 else "CODING_MODE_1_0",
                    "RateControlMode": "CBR",
                }
            elif acodec == "MP3":
                audio_codec_key = "Mp3Settings"
                audio_codec_val = {
                    "Bitrate": audio_desc.get("Bitrate", 320000),
                    "SampleRate": audio_desc.get("SampleRate", 44100),
                    "Channels": audio_desc.get("Channels", 2),
                    "RateControlMode": "CBR",
                }
            else:
                audio_codec_key = "AacSettings"
                audio_codec_val = {"Bitrate": 128000}

            output_settings["AudioDescriptions"] = [
                {"CodecSettings": {"Codec": acodec, audio_codec_key: audio_codec_val}}
            ]

        job_settings = {
            "Inputs": [{"FileInput": input_uri, "AudioSelectors": {"Audio Selector 1": {"DefaultSelection": "DEFAULT"}}}],
            "OutputGroups": [
                {
                    "Name": f"BME-{preset_key}",
                    "OutputGroupSettings": {
                        "Type": "FILE_GROUP_OUTPUT_GROUP_SETTINGS",
                        "FileGroupSettings": {"Destination": output_prefix},
                    },
                    "Outputs": [output_settings],
                }
            ],
        }

        resp = client.create_job(
            Role=role_arn,
            Settings=job_settings,
            UserMetadata={"user_id": user_id, "preset": preset_key, "source": s3_input_key},
            Tags={"Project": "BigMannEntertainment", "User": user_id},
        )

        job = resp["Job"]
        return {
            "job_id": job["Id"],
            "status": job["Status"],
            "preset": preset_key,
            "input_key": s3_input_key,
            "output_prefix": output_prefix.replace(f"s3://{self.s3_bucket}/", ""),
            "created_at": job["CreatedAt"].isoformat() if hasattr(job["CreatedAt"], "isoformat") else str(job["CreatedAt"]),
        }

    # ------------------------------------------------------------------
    # Job status
    # ------------------------------------------------------------------
    def get_job(self, job_id: str) -> Dict[str, Any]:
        client = self._get_client()
        resp = client.get_job(Id=job_id)
        job = resp["Job"]
        output_files = []
        if job["Status"] == "COMPLETE":
            for og in job.get("Settings", {}).get("OutputGroups", []):
                dest = og.get("OutputGroupSettings", {}).get("FileGroupSettings", {}).get("Destination", "")
                dest_key = dest.replace(f"s3://{self.s3_bucket}/", "")
                output_files.append({
                    "s3_prefix": dest_key,
                    "cdn_url": f"https://{self.cloudfront_domain}/{dest_key}",
                })
        return {
            "job_id": job["Id"],
            "status": job["Status"],
            "progress": job.get("JobPercentComplete", 0),
            "error_message": job.get("ErrorMessage"),
            "output_files": output_files,
            "created_at": job["CreatedAt"].isoformat() if hasattr(job["CreatedAt"], "isoformat") else str(job["CreatedAt"]),
            "user_metadata": job.get("UserMetadata", {}),
        }

    def list_jobs(self, status: str = "SUBMITTED", max_results: int = 20) -> List[Dict[str, Any]]:
        client = self._get_client()
        kwargs = {"MaxResults": max_results, "Order": "DESCENDING", "Queue": f"arn:aws:mediaconvert:{self.region}:{self._account_id}:queues/Default"}
        if status:
            kwargs["Status"] = status
        resp = client.list_jobs(**kwargs)
        jobs = []
        for j in resp.get("Jobs", []):
            jobs.append({
                "job_id": j["Id"],
                "status": j["Status"],
                "progress": j.get("JobPercentComplete", 0),
                "created_at": j["CreatedAt"].isoformat() if hasattr(j["CreatedAt"], "isoformat") else str(j["CreatedAt"]),
                "user_metadata": j.get("UserMetadata", {}),
            })
        return jobs

    # ------------------------------------------------------------------
    # Get endpoint info
    # ------------------------------------------------------------------
    def get_endpoint_info(self) -> Dict[str, Any]:
        try:
            endpoint = self._get_endpoint()
            return {"available": True, "endpoint": endpoint, "region": self.region}
        except Exception as e:
            return {"available": False, "error": str(e)}

    def get_presets(self) -> Dict[str, Dict[str, str]]:
        return {k: {"label": v["label"], "container": v["container"]} for k, v in self.PRESETS.items()}
