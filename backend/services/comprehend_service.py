"""AWS Comprehend Service - Natural Language Processing & Sentiment Analysis."""
import os
import logging
import boto3
from typing import Dict, Any, List
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class ComprehendService:
    def __init__(self):
        self.region = os.environ.get("AWS_REGION", "us-east-1")
        self.available = False
        self._client = None

        try:
            self._client = boto3.client(
                "comprehend",
                aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
                region_name=self.region,
            )
            self._client.list_endpoints(MaxResults=1)
            self.available = True
        except Exception as e:
            logger.warning(f"Comprehend init failed: {e}")

    def get_status(self) -> Dict[str, Any]:
        if not self.available:
            return {"available": False}
        return {
            "available": True,
            "region": self.region,
            "service": "AWS Comprehend",
        }

    def detect_sentiment(self, text: str, language: str = "en") -> Dict[str, Any]:
        if not self.available:
            raise RuntimeError("Comprehend not available")
        resp = self._client.detect_sentiment(Text=text, LanguageCode=language)
        return {
            "sentiment": resp.get("Sentiment", ""),
            "scores": {
                "positive": round(resp["SentimentScore"].get("Positive", 0), 4),
                "negative": round(resp["SentimentScore"].get("Negative", 0), 4),
                "neutral": round(resp["SentimentScore"].get("Neutral", 0), 4),
                "mixed": round(resp["SentimentScore"].get("Mixed", 0), 4),
            },
        }

    def detect_entities(self, text: str, language: str = "en") -> List[Dict[str, Any]]:
        if not self.available:
            raise RuntimeError("Comprehend not available")
        resp = self._client.detect_entities(Text=text, LanguageCode=language)
        return [
            {
                "text": e.get("Text", ""),
                "type": e.get("Type", ""),
                "score": round(e.get("Score", 0), 4),
                "begin_offset": e.get("BeginOffset", 0),
                "end_offset": e.get("EndOffset", 0),
            }
            for e in resp.get("Entities", [])
        ]

    def detect_key_phrases(self, text: str, language: str = "en") -> List[Dict[str, Any]]:
        if not self.available:
            raise RuntimeError("Comprehend not available")
        resp = self._client.detect_key_phrases(Text=text, LanguageCode=language)
        return [
            {
                "text": p.get("Text", ""),
                "score": round(p.get("Score", 0), 4),
                "begin_offset": p.get("BeginOffset", 0),
                "end_offset": p.get("EndOffset", 0),
            }
            for p in resp.get("KeyPhrases", [])
        ]

    def detect_language(self, text: str) -> List[Dict[str, Any]]:
        if not self.available:
            raise RuntimeError("Comprehend not available")
        resp = self._client.detect_dominant_language(Text=text)
        return [
            {
                "language_code": l.get("LanguageCode", ""),
                "score": round(l.get("Score", 0), 4),
            }
            for l in resp.get("Languages", [])
        ]

    def detect_pii(self, text: str, language: str = "en") -> List[Dict[str, Any]]:
        if not self.available:
            raise RuntimeError("Comprehend not available")
        resp = self._client.detect_pii_entities(Text=text, LanguageCode=language)
        return [
            {
                "type": e.get("Type", ""),
                "score": round(e.get("Score", 0), 4),
                "begin_offset": e.get("BeginOffset", 0),
                "end_offset": e.get("EndOffset", 0),
            }
            for e in resp.get("Entities", [])
        ]

    def detect_syntax(self, text: str, language: str = "en") -> List[Dict[str, Any]]:
        if not self.available:
            raise RuntimeError("Comprehend not available")
        resp = self._client.detect_syntax(Text=text, LanguageCode=language)
        return [
            {
                "token_id": t.get("TokenId", 0),
                "text": t.get("Text", ""),
                "part_of_speech": t.get("PartOfSpeech", {}).get("Tag", ""),
                "score": round(t.get("PartOfSpeech", {}).get("Score", 0), 4),
                "begin_offset": t.get("BeginOffset", 0),
                "end_offset": t.get("EndOffset", 0),
            }
            for t in resp.get("SyntaxTokens", [])
        ]

    def batch_detect_sentiment(self, texts: List[str], language: str = "en") -> List[Dict[str, Any]]:
        if not self.available:
            raise RuntimeError("Comprehend not available")
        resp = self._client.batch_detect_sentiment(TextList=texts, LanguageCode=language)
        results = []
        for r in resp.get("ResultList", []):
            results.append({
                "index": r.get("Index", 0),
                "sentiment": r.get("Sentiment", ""),
                "scores": {
                    "positive": round(r["SentimentScore"].get("Positive", 0), 4),
                    "negative": round(r["SentimentScore"].get("Negative", 0), 4),
                    "neutral": round(r["SentimentScore"].get("Neutral", 0), 4),
                    "mixed": round(r["SentimentScore"].get("Mixed", 0), 4),
                },
            })
        return results

    def list_endpoints(self) -> List[Dict[str, Any]]:
        if not self.available:
            raise RuntimeError("Comprehend not available")
        resp = self._client.list_endpoints(MaxResults=10)
        return [
            {
                "arn": ep.get("EndpointArn", ""),
                "status": ep.get("Status", ""),
                "model_arn": ep.get("ModelArn", ""),
                "desired_units": ep.get("DesiredInferenceUnits", 0),
                "current_units": ep.get("CurrentInferenceUnits", 0),
                "created_at": ep.get("CreationTime", "").isoformat() if ep.get("CreationTime") else "",
            }
            for ep in resp.get("EndpointPropertiesList", [])
        ]
