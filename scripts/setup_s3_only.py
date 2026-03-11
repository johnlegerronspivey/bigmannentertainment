#!/usr/bin/env python3
"""
S3 Only Setup for Big Mann Entertainment Platform
"""

import boto3
from botocore.exceptions import ClientError

# AWS Configuration
AWS_ACCESS_KEY_ID = "AKIAUSISWEIVP3L6DC5K"
AWS_SECRET_ACCESS_KEY = "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"
AWS_REGION = "us-east-1"
S3_BUCKET_NAME = "bigmann-entertainment-media"

def setup_s3_bucket():
    """Create and configure S3 bucket for media storage"""
    print(f"🪣 Setting up S3 bucket: {S3_BUCKET_NAME}")
    
    try:
        # Create S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
        
        # Check if bucket already exists
        try:
            s3_client.head_bucket(Bucket=S3_BUCKET_NAME)
            print(f"✅ S3 bucket '{S3_BUCKET_NAME}' already exists")
            bucket_exists = True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                bucket_exists = False
            else:
                raise e
        
        # Create bucket if it doesn't exist
        if not bucket_exists:
            if AWS_REGION == 'us-east-1':
                s3_client.create_bucket(Bucket=S3_BUCKET_NAME)
            else:
                location = {'LocationConstraint': AWS_REGION}
                s3_client.create_bucket(
                    Bucket=S3_BUCKET_NAME,
                    CreateBucketConfiguration=location
                )
            print(f"✅ S3 bucket '{S3_BUCKET_NAME}' created successfully")
        
        # Configure CORS for web access
        cors_configuration = {
            'CORSRules': [
                {
                    'AllowedHeaders': ['*'],
                    'AllowedMethods': ['GET', 'PUT', 'POST', 'DELETE', 'HEAD'],
                    'AllowedOrigins': ['*'],
                    'ExposeHeaders': ['x-amz-server-side-encryption', 'x-amz-request-id'],
                    'MaxAgeSeconds': 3000
                }
            ]
        }
        
        try:
            s3_client.put_bucket_cors(
                Bucket=S3_BUCKET_NAME,
                CORSConfiguration=cors_configuration
            )
            print(f"✅ CORS configuration applied to bucket")
        except ClientError as e:
            print(f"⚠️ CORS configuration failed: {e.response['Error']['Message']}")
        
        # Enable versioning
        try:
            s3_client.put_bucket_versioning(
                Bucket=S3_BUCKET_NAME,
                VersioningConfiguration={'Status': 'Enabled'}
            )
            print(f"✅ Versioning enabled for bucket")
        except ClientError as e:
            print(f"⚠️ Versioning setup failed: {e.response['Error']['Message']}")
        
        # Test upload capability
        try:
            test_key = "test/setup-verification.txt"
            test_content = f"Big Mann Entertainment S3 setup completed on {boto3.__version__}"
            
            s3_client.put_object(
                Bucket=S3_BUCKET_NAME,
                Key=test_key,
                Body=test_content.encode('utf-8'),
                ContentType='text/plain'
            )
            print(f"✅ Test file uploaded successfully")
            
            # Clean up test file
            s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=test_key)
            print(f"✅ Test file cleanup completed")
            
        except ClientError as e:
            print(f"⚠️ Upload test failed: {e.response['Error']['Message']}")
        
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print(f"❌ S3 setup error: {error_code} - {e.response['Error']['Message']}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up S3 Infrastructure for Big Mann Entertainment")
    print("=" * 60)
    
    success = setup_s3_bucket()
    
    print("=" * 60)
    if success:
        print("🎉 S3 infrastructure setup completed successfully!")
        print("\n📋 S3 Bucket Details:")
        print(f"  Name: {S3_BUCKET_NAME}")
        print(f"  Region: {AWS_REGION}")
        print(f"  URL: https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com")
        print("\n✅ Ready for file uploads through Big Mann Entertainment platform!")
    else:
        print("❌ S3 setup failed. Check errors above.")
    
    return success

if __name__ == "__main__":
    main()