"""AWS Transcribe Service - Auto-generate captions & subtitles for media content."""
import os
import logging
import uuid
import json
import boto3
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class TranscribeService:
    def __init__(self):
        self.region = os.environ.get("AWS_REGION", "us-east-1")
        self.s3_bucket = os.environ.get("S3_BUCKET_NAME")
        self.cloudfront_domain = os.environ.get("CLOUDFRONT_DOMAIN", "cdn.bigmannentertainment.com")
        self.available = False
        try:
            self.client = boto3.client(
                "transcribe",
                aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
                region_name=self.region,
            )
            self.s3_client = boto3.client(
                "s3",
                aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
                region_name=self.region,
            )
            self.available = True
        except Exception as e:
            logger.warning(f"Transcribe init failed: {e}")

    # ------------------------------------------------------------------
    # Supported languages
    # ------------------------------------------------------------------
    LANGUAGES = {
        "en-US": "English (US)",
        "en-GB": "English (UK)",
        "es-US": "Spanish (US)",
        "es-ES": "Spanish (Spain)",
        "fr-FR": "French",
        "de-DE": "German",
        "it-IT": "Italian",
        "pt-BR": "Portuguese (Brazil)",
        "ja-JP": "Japanese",
        "ko-KR": "Korean",
        "zh-CN": "Chinese (Simplified)",
        "hi-IN": "Hindi",
        "ar-SA": "Arabic",
    }

    # ------------------------------------------------------------------
    # Start transcription
    # ------------------------------------------------------------------
    def start_transcription(
        self,
        s3_input_key: str,
        user_id: str,
        language_code: str = "en-US",
        enable_subtitles: bool = True,
        subtitle_formats: Optional[List[str]] = None,
        identify_language: bool = False,
    ) -> Dict[str, Any]:
        if not self.available:
            raise RuntimeError("Transcribe service not available")

        job_name = f"bme-{user_id[:8]}-{uuid.uuid4().hex[:8]}"
        media_uri = f"s3://{self.s3_bucket}/{s3_input_key}"
        output_key = f"transcriptions/{user_id}/{job_name}/"

        kwargs: Dict[str, Any] = {
            "TranscriptionJobName": job_name,
            "Media": {"MediaFileUri": media_uri},
            "OutputBucketName": self.s3_bucket,
            "OutputKey": output_key,
            "Tags": [
                {"Key": "Project", "Value": "BigMannEntertainment"},
                {"Key": "User", "Value": user_id},
            ],
        }

        if identify_language:
            kwargs["IdentifyLanguage"] = True
        else:
            kwargs["LanguageCode"] = language_code

        if enable_subtitles:
            formats = subtitle_formats or ["vtt", "srt"]
            kwargs["Subtitles"] = {"Formats": [f.upper() for f in formats], "OutputStartIndex": 1}

        resp = self.client.start_transcription_job(**kwargs)
        job = resp["TranscriptionJob"]

        return {
            "job_name": job["TranscriptionJobName"],
            "status": job["TranscriptionJobStatus"],
            "language": language_code if not identify_language else "auto-detect",
            "media_uri": media_uri,
            "output_key": output_key,
            "subtitles_enabled": enable_subtitles,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    # ------------------------------------------------------------------
    # Get job result
    # ------------------------------------------------------------------
    def get_job(self, job_name: str) -> Dict[str, Any]:
        if not self.available:
            raise RuntimeError("Transcribe service not available")

        resp = self.client.get_transcription_job(TranscriptionJobName=job_name)
        job = resp["TranscriptionJob"]
        status = job["TranscriptionJobStatus"]

        result: Dict[str, Any] = {
            "job_name": job_name,
            "status": status,
            "language": job.get("LanguageCode", "unknown"),
            "media_uri": job.get("Media", {}).get("MediaFileUri"),
        }

        if status == "COMPLETED":
            transcript_uri = job.get("Transcript", {}).get("TranscriptFileUri", "")
            result["transcript_uri"] = transcript_uri

            # Build subtitle URLs
            subtitles = job.get("Subtitles", {})
            subtitle_uris = subtitles.get("SubtitleFileUris", [])
            result["subtitle_files"] = []
            for uri in subtitle_uris:
                # Extract S3 key
                s3_key = uri.split(f"{self.s3_bucket}/", 1)[-1] if self.s3_bucket in uri else uri
                result["subtitle_files"].append({
                    "uri": uri,
                    "cdn_url": f"https://{self.cloudfront_domain}/{s3_key}",
                    "format": "SRT" if ".srt" in uri.lower() else "VTT" if ".vtt" in uri.lower() else "unknown",
                })

            # Fetch transcript text
            result["transcript_text"] = self._fetch_transcript_text(job)

            # Identified language
            if job.get("IdentifiedLanguageScore"):
                result["identified_language_score"] = job["IdentifiedLanguageScore"]

        elif status == "FAILED":
            result["failure_reason"] = job.get("FailureReason", "Unknown error")

        if "CreationTime" in job:
            result["created_at"] = job["CreationTime"].isoformat()
        if "CompletionTime" in job:
            result["completed_at"] = job["CompletionTime"].isoformat()

        return result

    def _fetch_transcript_text(self, job: dict) -> Optional[str]:
        """Download the JSON transcript from S3 and extract plain text."""
        try:
            transcript_uri = job.get("Transcript", {}).get("TranscriptFileUri", "")
            if not transcript_uri:
                return None
            # Parse S3 key from URI
            if self.s3_bucket in transcript_uri:
                s3_key = transcript_uri.split(f"{self.s3_bucket}/", 1)[-1]
            else:
                return None

            obj = self.s3_client.get_object(Bucket=self.s3_bucket, Key=s3_key)
            data = json.loads(obj["Body"].read().decode("utf-8"))
            transcripts = data.get("results", {}).get("transcripts", [])
            return " ".join(t.get("transcript", "") for t in transcripts) if transcripts else None
        except Exception as e:
            logger.error(f"Failed to fetch transcript text: {e}")
            return None

    # ------------------------------------------------------------------
    # List jobs
    # ------------------------------------------------------------------
    def list_jobs(self, status: Optional[str] = None, max_results: int = 20) -> List[Dict[str, Any]]:
        if not self.available:
            raise RuntimeError("Transcribe service not available")

        kwargs: Dict[str, Any] = {"MaxResults": max_results}
        if status:
            kwargs["Status"] = status
        kwargs["JobNameContains"] = "bme-"

        resp = self.client.list_transcription_jobs(**kwargs)
        jobs = []
        for j in resp.get("TranscriptionJobSummaries", []):
            jobs.append({
                "job_name": j["TranscriptionJobName"],
                "status": j["TranscriptionJobStatus"],
                "language": j.get("LanguageCode", "unknown"),
                "created_at": j["CreationTime"].isoformat() if "CreationTime" in j else None,
                "completed_at": j["CompletionTime"].isoformat() if "CompletionTime" in j else None,
                "failure_reason": j.get("FailureReason"),
            })
        return jobs

    # ------------------------------------------------------------------
    # Delete job
    # ------------------------------------------------------------------
    def delete_job(self, job_name: str) -> bool:
        try:
            self.client.delete_transcription_job(TranscriptionJobName=job_name)
            return True
        except Exception as e:
            logger.error(f"Delete transcription job failed: {e}")
            return False

    # ------------------------------------------------------------------
    # Service info
    # ------------------------------------------------------------------
    def get_status(self) -> Dict[str, Any]:
        if not self.available:
            return {"available": False, "error": "Transcribe client not initialized"}
        try:
            self.client.list_transcription_jobs(MaxResults=1)
            return {"available": True, "region": self.region, "languages": len(self.LANGUAGES)}
        except Exception as e:
            return {"available": False, "error": str(e)}

    def get_languages(self) -> Dict[str, str]:
        return self.LANGUAGES
