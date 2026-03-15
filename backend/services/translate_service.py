"""AWS Translate Service - Multi-language content translation."""
import os
import logging
import boto3
from typing import Dict, Any, List
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class TranslateService:
    def __init__(self):
        self.region = os.environ.get("AWS_REGION", "us-east-1")
        self.available = False
        self._client = None
        try:
            self._client = boto3.client(
                "translate",
                aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
                region_name=self.region,
            )
            self._client.list_languages(MaxResults=1)
            self.available = True
        except Exception as e:
            logger.warning(f"Translate init failed: {e}")

    def get_status(self) -> Dict[str, Any]:
        if not self.available:
            return {"available": False}
        return {"available": True, "region": self.region, "service": "Amazon Translate"}

    def translate_text(self, text: str, source_lang: str = "auto", target_lang: str = "es") -> Dict[str, Any]:
        resp = self._client.translate_text(
            Text=text,
            SourceLanguageCode=source_lang,
            TargetLanguageCode=target_lang,
        )
        return {
            "translated_text": resp.get("TranslatedText", ""),
            "source_language": resp.get("SourceLanguageCode", ""),
            "target_language": resp.get("TargetLanguageCode", ""),
        }

    def list_languages(self) -> List[Dict[str, Any]]:
        resp = self._client.list_languages(MaxResults=100)
        return [
            {"code": lang.get("LanguageCode", ""), "name": lang.get("LanguageName", "")}
            for lang in resp.get("Languages", [])
        ]

    def list_terminologies(self) -> List[Dict[str, Any]]:
        resp = self._client.list_terminologies(MaxSize=100)
        return [
            {
                "name": t.get("Name", ""),
                "source_language": t.get("SourceLanguageCode", ""),
                "target_languages": t.get("TargetLanguageCodes", []),
                "size": t.get("SizeBytes", 0),
                "term_count": t.get("TermCount", 0),
            }
            for t in resp.get("TerminologyPropertiesList", [])
        ]

    def list_parallel_data(self) -> List[Dict[str, Any]]:
        resp = self._client.list_parallel_data(MaxResults=50)
        return [
            {
                "name": pd.get("Name", ""),
                "status": pd.get("Status", ""),
                "source_language": pd.get("SourceLanguageCode", ""),
                "target_languages": pd.get("TargetLanguageCodes", []),
            }
            for pd in resp.get("ParallelDataPropertiesList", [])
        ]
