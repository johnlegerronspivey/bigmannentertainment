"""AWS S3 service for media file storage."""
import os
import logging
from datetime import datetime
from typing import List, Optional
import boto3
from fastapi import HTTPException, UploadFile
from botocore.exceptions import ClientError

class S3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.bucket_name = os.getenv('S3_BUCKET_NAME')
        self.logger = logging.getLogger(__name__)
        
    def generate_object_key(self, user_id: str, file_type: str, filename: str) -> str:
        """Generate organized object key for S3 storage"""
        timestamp = datetime.now().strftime('%Y/%m/%d')
        file_extension = filename.split('.')[-1] if '.' in filename else ''
        clean_filename = f"{datetime.now().isoformat()}_{filename}"
        return f"{file_type}/{user_id}/{timestamp}/{clean_filename}"
        
    async def upload_file(self, file: UploadFile, user_id: str, file_type: str) -> dict:
        """Upload file to S3 with proper error handling and metadata"""
        try:
            # Validate file type and size
            self._validate_file(file, file_type)
            
            # Generate object key
            object_key = self.generate_object_key(user_id, file_type, file.filename)
            
            # Prepare metadata
            metadata = {
                'user_id': user_id,
                'file_type': file_type,
                'original_filename': file.filename,
                'upload_timestamp': datetime.now().isoformat(),
                'content_type': file.content_type or 'application/octet-stream'
            }
            
            # Upload file to S3
            self.s3_client.upload_fileobj(
                file.file,
                self.bucket_name,
                object_key,
                ExtraArgs={
                    'Metadata': metadata,
                    'ContentType': file.content_type or 'application/octet-stream',
                    'ServerSideEncryption': 'AES256'
                }
            )
            
            # Generate file URL
            file_url = f"https://{self.bucket_name}.s3.{os.getenv('AWS_REGION', 'us-east-1')}.amazonaws.com/{object_key}"
            
            return {
                'object_key': object_key,
                'file_url': file_url,
                'bucket': self.bucket_name,
                'size': file.size,
                'content_type': file.content_type,
                'metadata': metadata
            }
            
        except ClientError as e:
            self.logger.error(f"S3 upload error: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"File upload failed: {str(e)}"
            )
        except Exception as e:
            self.logger.error(f"Unexpected upload error: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Upload failed: {str(e)}"
            )
    
    def _validate_file(self, file: UploadFile, file_type: str):
        """Validate file type and size constraints"""
        # Define allowed file types for media platform
        allowed_types = {
            'audio': ['audio/mpeg', 'audio/wav', 'audio/ogg', 'audio/m4a', 'audio/mp3'],
            'video': ['video/mp4', 'video/quicktime', 'video/avi', 'video/webm'],
            'image': ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/jpg']
        }
        
        # Define size limits (in bytes)
        size_limits = {
            'audio': 50 * 1024 * 1024,  # 50MB
            'video': 500 * 1024 * 1024,  # 500MB
            'image': 10 * 1024 * 1024   # 10MB
        }
        
        if file_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type: {file_type}"
            )
        
        if file.content_type and file.content_type not in allowed_types[file_type]:
            raise HTTPException(
                status_code=415,
                detail=f"Unsupported file format: {file.content_type}"
            )
        
        if file.size and file.size > size_limits[file_type]:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {size_limits[file_type] / (1024*1024):.1f}MB"
            )

    def generate_presigned_url(self, object_key: str, expiration: int = 3600) -> str:
        """Generate presigned URL for secure file access"""
        try:
            response = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': object_key},
                ExpiresIn=expiration
            )
            return response
        except ClientError as e:
            self.logger.error(f"Error generating presigned URL: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to generate access URL"
            )

    def delete_file(self, object_key: str) -> bool:
        """Delete file from S3"""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=object_key)
            return True
        except ClientError as e:
            self.logger.error(f"Error deleting file: {e}")
            return False

    def list_user_files(self, user_id: str, file_type: Optional[str] = None) -> List[dict]:
        """List files for a specific user"""
        try:
            prefix = f"{file_type}/{user_id}/" if file_type else f"audio/{user_id}/,video/{user_id}/,image/{user_id}/"
            
            files = []
            
            # If specific file type, search that prefix
            if file_type:
                prefixes = [f"{file_type}/{user_id}/"]
            else:
                prefixes = [f"audio/{user_id}/", f"video/{user_id}/", f"image/{user_id}/"]
            
            for prefix in prefixes:
                try:
                    response = self.s3_client.list_objects_v2(
                        Bucket=self.bucket_name,
                        Prefix=prefix
                    )
                    
                    for obj in response.get('Contents', []):
                        # Get object metadata
                        try:
                            metadata_response = self.s3_client.head_object(
                                Bucket=self.bucket_name,
                                Key=obj['Key']
                            )
                            
                            files.append({
                                'object_key': obj['Key'],
                                'size': obj['Size'],
                                'last_modified': obj['LastModified'].isoformat(),
                                'metadata': metadata_response.get('Metadata', {}),
                                'content_type': metadata_response.get('ContentType', '')
                            })
                        except Exception as e:
                            self.logger.warning(f"Could not get metadata for {obj['Key']}: {e}")
                except Exception as e:
                    self.logger.warning(f"Could not list objects with prefix {prefix}: {e}")
            
            return files
            
        except ClientError as e:
            self.logger.error(f"Error listing files: {e}")
            return []


