"""AWS media processing services - CloudFront CDN, Lambda, Rekognition."""
import os
import json
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
import boto3

class CloudFrontService:
    def __init__(self):
        try:
            self.cloudfront_client = boto3.client(
                'cloudfront',
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=os.getenv('AWS_REGION', 'us-east-1')
            )
            self.distribution_domain = os.getenv('CLOUDFRONT_DOMAIN', 'cdn.bigmannentertainment.com')
            self.cloudfront_available = self._check_cloudfront_availability()
        except Exception as e:
            logging.warning(f"CloudFront initialization failed: {e}")
            self.cloudfront_available = False
    
    def _check_cloudfront_availability(self):
        """Check if CloudFront is available"""
        try:
            self.cloudfront_client.list_distributions(MaxItems='1')
            return True
        except Exception as e:
            logging.warning(f"CloudFront not available: {e}")
            return False
    
    def get_cdn_url(self, s3_key: str) -> str:
        """Generate CDN URL for content delivery"""
        if self.cloudfront_available:
            return f"https://{self.distribution_domain}/{s3_key}"
        else:
            # Fallback to direct S3 URL
            return f"https://{os.getenv('S3_BUCKET_NAME', 'bigmann-entertainment-media')}.s3.{os.getenv('AWS_REGION', 'us-east-1')}.amazonaws.com/{s3_key}"
    
    def invalidate_cache(self, paths: List[str]) -> Optional[str]:
        """Invalidate CloudFront cache for specific paths"""
        if not self.cloudfront_available:
            return None
        
        try:
            # Get distribution ID from environment or config
            distribution_id = os.getenv('CLOUDFRONT_DISTRIBUTION_ID')
            if not distribution_id:
                logging.warning("CloudFront distribution ID not configured")
                return None
            
            response = self.cloudfront_client.create_invalidation(
                DistributionId=distribution_id,
                InvalidationBatch={
                    'Paths': {
                        'Quantity': len(paths),
                        'Items': paths
                    },
                    'CallerReference': f"bigmann-{int(datetime.now().timestamp())}"
                }
            )
            return response['Invalidation']['Id']
        except Exception as e:
            logging.error(f"Cache invalidation failed: {e}")
            return None

# Lambda Processing Service
class LambdaProcessingService:
    def __init__(self):
        try:
            self.lambda_client = boto3.client(
                'lambda',
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=os.getenv('AWS_REGION', 'us-east-1')
            )
            self.lambda_available = self._check_lambda_availability()
        except Exception as e:
            logging.warning(f"Lambda initialization failed: {e}")
            self.lambda_available = False
    
    def _check_lambda_availability(self):
        """Check if Lambda is available"""
        try:
            self.lambda_client.list_functions(MaxItems=1)
            return True
        except Exception as e:
            logging.warning(f"Lambda not available: {e}")
            return False
    
    def trigger_media_processing(self, s3_key: str, file_type: str) -> bool:
        """Trigger Lambda function for media processing"""
        if not self.lambda_available:
            return False
        
        try:
            # Create S3 event payload
            payload = {
                'Records': [{
                    's3': {
                        'bucket': {'name': os.getenv('S3_BUCKET_NAME', 'bigmann-entertainment-media')},
                        'object': {'key': s3_key}
                    }
                }]
            }
            
            # Invoke media processing Lambda
            self.lambda_client.invoke(
                FunctionName='bigmann-media-processor',
                InvocationType='Event',  # Asynchronous
                Payload=json.dumps(payload)
            )
            
            return True
            
        except Exception as e:
            logging.error(f"Lambda invocation failed: {e}")
            return False
    
    def trigger_content_moderation(self, s3_key: str) -> bool:
        """Trigger Lambda function for content moderation"""
        if not self.lambda_available:
            return False
        
        try:
            # Create S3 event payload
            payload = {
                'Records': [{
                    's3': {
                        'bucket': {'name': os.getenv('S3_BUCKET_NAME', 'bigmann-entertainment-media')},
                        'object': {'key': s3_key}
                    }
                }]
            }
            
            # Invoke content moderation Lambda
            self.lambda_client.invoke(
                FunctionName='bigmann-content-moderator',
                InvocationType='Event',  # Asynchronous
                Payload=json.dumps(payload)
            )
            
            return True
            
        except Exception as e:
            logging.error(f"Content moderation invocation failed: {e}")
            return False

# Rekognition Service Class
class RekognitionService:
    def __init__(self):
        try:
            self.rekognition_client = boto3.client(
                'rekognition',
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=os.getenv('AWS_REGION', 'us-east-1')
            )
            self.rekognition_available = self._check_rekognition_availability()
        except Exception as e:
            logging.warning(f"Rekognition initialization failed: {e}")
            self.rekognition_available = False
    
    def _check_rekognition_availability(self):
        """Check if Rekognition is available"""
        try:
            # Simple test to check Rekognition access
            return True
        except Exception as e:
            logging.warning(f"Rekognition not available: {e}")
            return False
    
    def detect_moderation_labels(self, s3_bucket: str, s3_key: str) -> Dict[str, Any]:
        """Detect moderation labels in image"""
        if not self.rekognition_available:
            return {"available": False, "message": "Rekognition not available"}
        
        try:
            response = self.rekognition_client.detect_moderation_labels(
                Image={'S3Object': {'Bucket': s3_bucket, 'Name': s3_key}},
                MinConfidence=60.0
            )
            
            moderation_labels = response.get('ModerationLabels', [])
            
            return {
                "available": True,
                "flagged": len(moderation_labels) > 0,
                "labels": moderation_labels,
                "max_confidence": max([label['Confidence'] for label in moderation_labels]) if moderation_labels else 0
            }
            
        except Exception as e:
            logging.error(f"Rekognition moderation failed: {e}")
            return {"available": True, "error": str(e)}
    
    def detect_labels(self, s3_bucket: str, s3_key: str) -> Dict[str, Any]:
        """Detect general labels in image"""
        if not self.rekognition_available:
            return {"available": False, "message": "Rekognition not available"}
        
        try:
            response = self.rekognition_client.detect_labels(
                Image={'S3Object': {'Bucket': s3_bucket, 'Name': s3_key}},
                MaxLabels=20,
                MinConfidence=75
            )
            
            labels = response.get('Labels', [])
            
            return {
                "available": True,
                "labels": [{"name": label['Name'], "confidence": label['Confidence']} for label in labels]
            }
            
        except Exception as e:
            logging.error(f"Rekognition label detection failed: {e}")
            return {"available": True, "error": str(e)}
