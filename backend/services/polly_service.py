"""AWS Polly Service - Text-to-speech for audio content."""
import os
import logging
import boto3
from typing import Dict, Any, List
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class PollyService:
    def __init__(self):
        self.region = os.environ.get("AWS_REGION", "us-east-1")
        self.available = False
        self._client = None
        try:
            self._client = boto3.client(
                "polly",
                aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
                region_name=self.region,
            )
            self._client.describe_voices()
            self.available = True
        except Exception as e:
            logger.warning(f"Polly init failed: {e}")

    def get_status(self) -> Dict[str, Any]:
        if not self.available:
            return {"available": False}
        return {"available": True, "region": self.region, "service": "Amazon Polly"}

    def list_voices(self, language_code: str = None, engine: str = None) -> List[Dict[str, Any]]:
        kwargs = {}
        if language_code:
            kwargs["LanguageCode"] = language_code
        if engine:
            kwargs["Engine"] = engine
        resp = self._client.describe_voices(**kwargs)
        return [
            {
                "id": v.get("Id", ""),
                "name": v.get("Name", ""),
                "gender": v.get("Gender", ""),
                "language_code": v.get("LanguageCode", ""),
                "language_name": v.get("LanguageName", ""),
                "supported_engines": v.get("SupportedEngines", []),
            }
            for v in resp.get("Voices", [])
        ]

    def synthesize_speech(self, text: str, voice_id: str = "Joanna", output_format: str = "mp3", engine: str = "neural") -> Dict[str, Any]:
        resp = self._client.synthesize_speech(
            Text=text,
            VoiceId=voice_id,
            OutputFormat=output_format,
            Engine=engine,
        )
        return {
            "content_type": resp.get("ContentType", ""),
            "request_characters": resp.get("RequestCharacters", 0),
            "audio_available": resp.get("AudioStream") is not None,
        }

    def list_lexicons(self) -> List[Dict[str, Any]]:
        resp = self._client.list_lexicons()
        return [
            {
                "name": lex.get("Name", ""),
                "language_code": lex.get("Attributes", {}).get("LanguageCode", ""),
                "lexicon_count": lex.get("Attributes", {}).get("LexiconArn", ""),
                "size": lex.get("Attributes", {}).get("Size", 0),
                "alphabet": lex.get("Attributes", {}).get("Alphabet", ""),
            }
            for lex in resp.get("Lexicons", [])
        ]

    def list_speech_synthesis_tasks(self) -> List[Dict[str, Any]]:
        resp = self._client.list_speech_synthesis_tasks(MaxResults=20)
        return [
            {
                "task_id": t.get("TaskId", ""),
                "status": t.get("TaskStatus", ""),
                "output_format": t.get("OutputFormat", ""),
                "voice_id": t.get("VoiceId", ""),
                "engine": t.get("Engine", ""),
                "created_at": t.get("CreationTime", "").isoformat() if t.get("CreationTime") else "",
            }
            for t in resp.get("SynthesisTasks", [])
        ]
