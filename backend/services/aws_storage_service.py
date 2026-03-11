"""
AWS S3 Storage Service for Agency Assets
Handles image/video uploads, thumbnails, and metadata
"""

import os
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import uuid
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone, timedelta
import mimetypes
import logging
from PIL import Image
import io
import json

logger = logging.getLogger(__name__)

class AWSStorageService:
    """AWS S3 service for agency asset management"""
    
    def __init__(self):
        self.aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.region_name = os.getenv('AWS_REGION', 'us-east-1')
        self.bucket_name = os.getenv('S3_BUCKET_NAME', 'bme-agency-assets')
        
        # Initialize S3 client
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=self.aws_access_key,
                aws_secret_access_key=self.aws_secret_key,
                region_name=self.region_name
            )
            
            # Verify bucket exists or create it
            self._ensure_bucket_exists()
            
        except (ClientError, NoCredentialsError) as e:
            logger.error(f"Error initializing AWS S3 client: {str(e)}")
            self.s3_client = None
    
    def _ensure_bucket_exists(self):
        """Ensure the S3 bucket exists"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                # Bucket doesn't exist, create it
                try:
                    if self.region_name == 'us-east-1':
                        self.s3_client.create_bucket(Bucket=self.bucket_name)
                    else:
                        self.s3_client.create_bucket(
                            Bucket=self.bucket_name,
                            CreateBucketConfiguration={'LocationConstraint': self.region_name}
                        )
                    
                    # Set bucket policy for public read access to preview images
                    bucket_policy = {
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Sid": "PublicReadGetObject",
                                "Effect": "Allow",
                                "Principal": "*",
                                "Action": "s3:GetObject",
                                "Resource": f"arn:aws:s3:::{self.bucket_name}/previews/*"
                            }
                        ]
                    }
                    
                    self.s3_client.put_bucket_policy(
                        Bucket=self.bucket_name,
                        Policy=json.dumps(bucket_policy)
                    )
                    
                    logger.info(f"Created S3 bucket: {self.bucket_name}")
                except ClientError as create_error:
                    logger.error(f"Error creating bucket: {str(create_error)}")
    
    async def upload_agency_asset(self, file_data: bytes, filename: str, agency_id: str, 
                                 asset_type: str = "image", metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Upload agency asset (image/video) to S3"""
        try:
            if not self.s3_client:
                return {'status': 'error', 'error': 'S3 client not initialized'}
            
            # Generate unique filename
            file_extension = os.path.splitext(filename)[1].lower()
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            # Determine MIME type
            mime_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
            
            # Create folder structure: assets/{agency_id}/{asset_type}/{year}/{month}/
            now = datetime.now(timezone.utc)
            folder_path = f"assets/{agency_id}/{asset_type}/{now.year}/{now.month:02d}"
            full_key = f"{folder_path}/{unique_filename}"
            
            # Upload original file
            s3_metadata = {
                'agency-id': agency_id,
                'asset-type': asset_type,
                'upload-date': now.isoformat(),
                'original-filename': filename
            }
            
            if metadata:
                for key, value in metadata.items():
                    s3_metadata[f'custom-{key}'] = str(value)
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=full_key,
                Body=file_data,
                ContentType=mime_type,
                Metadata=s3_metadata,
                ServerSideEncryption='AES256'
            )
            
            # Generate URL
            s3_url = f"https://{self.bucket_name}.s3.{self.region_name}.amazonaws.com/{full_key}"
            
            # Generate thumbnails and previews for images
            thumbnail_url = None
            preview_url = None
            
            if asset_type == "image" and mime_type.startswith('image/'):
                thumbnail_url = await self._generate_thumbnail(file_data, full_key, agency_id)
                preview_url = await self._generate_watermarked_preview(file_data, full_key, agency_id)
            
            # Get file info
            file_size = len(file_data)
            dimensions = {}
            
            if asset_type == "image":
                try:
                    with Image.open(io.BytesIO(file_data)) as img:
                        dimensions = {'width': img.width, 'height': img.height}
                except Exception as e:
                    logger.warning(f"Could not get image dimensions: {str(e)}")
            
            return {
                'status': 'success',
                's3_url': s3_url,
                'thumbnail_url': thumbnail_url,
                'preview_url': preview_url,
                'filename': unique_filename,
                'original_filename': filename,
                'file_size': file_size,
                'mime_type': mime_type,
                'dimensions': dimensions,
                'folder_path': folder_path,
                'upload_date': now.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error uploading asset to S3: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    async def _generate_thumbnail(self, image_data: bytes, original_key: str, agency_id: str) -> Optional[str]:
        """Generate thumbnail image"""
        try:
            with Image.open(io.BytesIO(image_data)) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Create thumbnail (300x300 max)
                img.thumbnail((300, 300), Image.Resampling.LANCZOS)
                
                # Save to bytes
                thumbnail_buffer = io.BytesIO()
                img.save(thumbnail_buffer, format='JPEG', quality=85, optimize=True)
                thumbnail_data = thumbnail_buffer.getvalue()
                
                # Upload thumbnail
                thumbnail_key = original_key.replace('assets/', 'thumbnails/')
                thumbnail_key = os.path.splitext(thumbnail_key)[0] + '_thumb.jpg'
                
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=thumbnail_key,
                    Body=thumbnail_data,
                    ContentType='image/jpeg',
                    Metadata={'agency-id': agency_id, 'asset-type': 'thumbnail'},
                    ServerSideEncryption='AES256'
                )
                
                return f"https://{self.bucket_name}.s3.{self.region_name}.amazonaws.com/{thumbnail_key}"
                
        except Exception as e:
            logger.error(f"Error generating thumbnail: {str(e)}")
            return None
    
    async def _generate_watermarked_preview(self, image_data: bytes, original_key: str, agency_id: str) -> Optional[str]:
        """Generate watermarked preview image"""
        try:
            with Image.open(io.BytesIO(image_data)) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Resize for preview (max 800px on longest side)
                max_size = 800
                if max(img.size) > max_size:
                    ratio = max_size / max(img.size)
                    new_size = tuple(int(dim * ratio) for dim in img.size)
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                
                # Add watermark
                watermark_text = "BIG MANN ENTERTAINMENT - PREVIEW"
                from PIL import ImageDraw, ImageFont
                
                draw = ImageDraw.Draw(img)
                
                # Try to use a font, fall back to default if not available
                try:
                    font_size = max(20, min(img.size) // 20)
                    font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", font_size)
                except:
                    font = ImageFont.load_default()
                
                # Get text size
                bbox = draw.textbbox((0, 0), watermark_text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                # Position watermark (center-bottom)
                x = (img.width - text_width) // 2
                y = img.height - text_height - 20
                
                # Add semi-transparent background
                overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
                overlay_draw = ImageDraw.Draw(overlay)
                overlay_draw.rectangle([x-10, y-5, x+text_width+10, y+text_height+5], fill=(0, 0, 0, 128))
                
                # Composite overlay
                img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
                
                # Add text
                draw = ImageDraw.Draw(img)
                draw.text((x, y), watermark_text, fill=(255, 255, 255), font=font)
                
                # Save to bytes
                preview_buffer = io.BytesIO()
                img.save(preview_buffer, format='JPEG', quality=80, optimize=True)
                preview_data = preview_buffer.getvalue()
                
                # Upload preview
                preview_key = original_key.replace('assets/', 'previews/')
                preview_key = os.path.splitext(preview_key)[0] + '_preview.jpg'
                
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=preview_key,
                    Body=preview_data,
                    ContentType='image/jpeg',
                    Metadata={'agency-id': agency_id, 'asset-type': 'preview'},
                    ACL='public-read',  # Make previews publicly accessible
                    ServerSideEncryption='AES256'
                )
                
                return f"https://{self.bucket_name}.s3.{self.region_name}.amazonaws.com/{preview_key}"
                
        except Exception as e:
            logger.error(f"Error generating watermarked preview: {str(e)}")
            return None
    
    async def upload_document(self, file_data: bytes, filename: str, agency_id: str, 
                            document_type: str = "kyc", entity_id: str = None) -> Dict[str, Any]:
        """Upload KYC or legal documents"""
        try:
            if not self.s3_client:
                return {'status': 'error', 'error': 'S3 client not initialized'}
            
            # Generate unique filename
            file_extension = os.path.splitext(filename)[1].lower()
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            # Create folder structure: documents/{agency_id}/{document_type}/
            folder_path = f"documents/{agency_id}/{document_type}"
            if entity_id:
                folder_path += f"/{entity_id}"
            
            full_key = f"{folder_path}/{unique_filename}"
            
            # Determine MIME type
            mime_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
            
            # Upload with encryption
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=full_key,
                Body=file_data,
                ContentType=mime_type,
                Metadata={
                    'agency-id': agency_id,
                    'document-type': document_type,
                    'entity-id': entity_id or '',
                    'upload-date': datetime.now(timezone.utc).isoformat(),
                    'original-filename': filename
                },
                ServerSideEncryption='AES256'
            )
            
            # Generate presigned URL for secure access
            presigned_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': full_key},
                ExpiresIn=3600  # 1 hour
            )
            
            return {
                'status': 'success',
                's3_url': f"https://{self.bucket_name}.s3.{self.region_name}.amazonaws.com/{full_key}",
                'presigned_url': presigned_url,
                'filename': unique_filename,
                'original_filename': filename,
                'file_size': len(file_data),
                'mime_type': mime_type,
                'document_type': document_type,
                'folder_path': folder_path
            }
            
        except Exception as e:
            logger.error(f"Error uploading document to S3: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    async def generate_presigned_upload_url(self, agency_id: str, asset_type: str = "image", 
                                          expires_in: int = 3600) -> Dict[str, Any]:
        """Generate presigned URL for direct uploads"""
        try:
            if not self.s3_client:
                return {'status': 'error', 'error': 'S3 client not initialized'}
            
            # Generate unique key
            unique_filename = f"{uuid.uuid4()}"
            now = datetime.now(timezone.utc)
            folder_path = f"assets/{agency_id}/{asset_type}/{now.year}/{now.month:02d}"
            key = f"{folder_path}/{unique_filename}"
            
            # Generate presigned POST
            presigned_post = self.s3_client.generate_presigned_post(
                Bucket=self.bucket_name,
                Key=key,
                Fields={
                    'Content-Type': 'image/jpeg',
                    'x-amz-server-side-encryption': 'AES256',
                    'x-amz-meta-agency-id': agency_id,
                    'x-amz-meta-asset-type': asset_type
                },
                Conditions=[
                    ['content-length-range', 1024, 50 * 1024 * 1024],  # 1KB to 50MB
                    {'Content-Type': 'image/jpeg'},
                    {'x-amz-server-side-encryption': 'AES256'}
                ],
                ExpiresIn=expires_in
            )
            
            return {
                'status': 'success',
                'presigned_post': presigned_post,
                'upload_url': presigned_post['url'],
                'fields': presigned_post['fields'],
                'key': key,
                'expires_in': expires_in
            }
            
        except Exception as e:
            logger.error(f"Error generating presigned upload URL: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    async def delete_asset(self, s3_url: str) -> Dict[str, Any]:
        """Delete asset from S3"""
        try:
            if not self.s3_client:
                return {'status': 'error', 'error': 'S3 client not initialized'}
            
            # Extract key from URL
            key = s3_url.split(f"{self.bucket_name}.s3.{self.region_name}.amazonaws.com/")[1]
            
            # Delete main file
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
            
            # Delete related files (thumbnail, preview)
            thumbnail_key = key.replace('assets/', 'thumbnails/').rsplit('.', 1)[0] + '_thumb.jpg'
            preview_key = key.replace('assets/', 'previews/').rsplit('.', 1)[0] + '_preview.jpg'
            
            for related_key in [thumbnail_key, preview_key]:
                try:
                    self.s3_client.delete_object(Bucket=self.bucket_name, Key=related_key)
                except:
                    pass  # Related files might not exist
            
            return {'status': 'success', 'deleted_key': key}
            
        except Exception as e:
            logger.error(f"Error deleting asset from S3: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    async def get_asset_metadata(self, s3_url: str) -> Dict[str, Any]:
        """Get asset metadata from S3"""
        try:
            if not self.s3_client:
                return {'status': 'error', 'error': 'S3 client not initialized'}
            
            # Extract key from URL
            key = s3_url.split(f"{self.bucket_name}.s3.{self.region_name}.amazonaws.com/")[1]
            
            # Get object metadata
            response = self.s3_client.head_object(Bucket=self.bucket_name, Key=key)
            
            return {
                'status': 'success',
                'metadata': response.get('Metadata', {}),
                'content_type': response.get('ContentType'),
                'content_length': response.get('ContentLength'),
                'last_modified': response.get('LastModified').isoformat() if response.get('LastModified') else None,
                'etag': response.get('ETag', '').strip('"')
            }
            
        except Exception as e:
            logger.error(f"Error getting asset metadata: {str(e)}")
            return {'status': 'error', 'error': str(e)}

# Global service instance
storage_service = AWSStorageService()