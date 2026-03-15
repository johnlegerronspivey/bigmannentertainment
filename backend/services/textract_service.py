"""AWS Textract Service - Extract text from images and documents."""
import os
import logging
import boto3
from typing import Dict, Any, List
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class TextractService:
    def __init__(self):
        self.region = os.environ.get("AWS_REGION", "us-east-1")
        self.available = False
        self._client = None
        try:
            self._client = boto3.client(
                "textract",
                aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
                region_name=self.region,
            )
            # Simple availability check
            self.available = True
        except Exception as e:
            logger.warning(f"Textract init failed: {e}")

    def get_status(self) -> Dict[str, Any]:
        if not self.available:
            return {"available": False}
        return {"available": True, "region": self.region, "service": "Amazon Textract"}

    def analyze_s3_document(self, bucket: str, key: str, feature_types: List[str] = None) -> Dict[str, Any]:
        if feature_types is None:
            feature_types = ["TABLES", "FORMS"]
        resp = self._client.analyze_document(
            Document={"S3Object": {"Bucket": bucket, "Name": key}},
            FeatureTypes=feature_types,
        )
        blocks = resp.get("Blocks", [])
        pages = [b for b in blocks if b.get("BlockType") == "PAGE"]
        lines = [b for b in blocks if b.get("BlockType") == "LINE"]
        tables = [b for b in blocks if b.get("BlockType") == "TABLE"]
        forms = [b for b in blocks if b.get("BlockType") == "KEY_VALUE_SET"]
        return {
            "total_blocks": len(blocks),
            "pages": len(pages),
            "lines": len(lines),
            "tables": len(tables),
            "forms": len(forms),
            "extracted_text": "\n".join(l.get("Text", "") for l in lines),
        }

    def detect_s3_text(self, bucket: str, key: str) -> Dict[str, Any]:
        resp = self._client.detect_document_text(
            Document={"S3Object": {"Bucket": bucket, "Name": key}},
        )
        blocks = resp.get("Blocks", [])
        lines = [b for b in blocks if b.get("BlockType") == "LINE"]
        words = [b for b in blocks if b.get("BlockType") == "WORD"]
        return {
            "total_blocks": len(blocks),
            "lines": len(lines),
            "words": len(words),
            "extracted_text": "\n".join(l.get("Text", "") for l in lines),
            "confidence": round(
                sum(l.get("Confidence", 0) for l in lines) / max(len(lines), 1), 2
            ),
        }

    def start_document_analysis(self, bucket: str, key: str, feature_types: List[str] = None) -> Dict[str, Any]:
        if feature_types is None:
            feature_types = ["TABLES", "FORMS"]
        resp = self._client.start_document_analysis(
            DocumentLocation={"S3Object": {"Bucket": bucket, "Name": key}},
            FeatureTypes=feature_types,
        )
        return {"job_id": resp.get("JobId", "")}

    def get_document_analysis(self, job_id: str) -> Dict[str, Any]:
        resp = self._client.get_document_analysis(JobId=job_id)
        status = resp.get("JobStatus", "")
        blocks = resp.get("Blocks", [])
        lines = [b for b in blocks if b.get("BlockType") == "LINE"]
        return {
            "job_status": status,
            "total_blocks": len(blocks),
            "lines": len(lines),
            "extracted_text": "\n".join(l.get("Text", "") for l in lines) if status == "SUCCEEDED" else "",
        }

    def list_adapters(self) -> List[Dict[str, Any]]:
        try:
            resp = self._client.list_adapters(MaxResults=20)
            return [
                {
                    "adapter_id": a.get("AdapterId", ""),
                    "adapter_name": a.get("AdapterName", ""),
                    "feature_types": a.get("FeatureTypes", []),
                    "created_at": a.get("CreationTime", "").isoformat() if a.get("CreationTime") else "",
                }
                for a in resp.get("Adapters", [])
            ]
        except ClientError:
            return []
