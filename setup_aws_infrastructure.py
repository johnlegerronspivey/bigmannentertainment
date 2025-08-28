#!/usr/bin/env python3
"""
AWS Infrastructure Setup for Big Mann Entertainment Platform
Creates S3 bucket and verifies SES email address
"""

import boto3
import os
from botocore.exceptions import ClientError

# AWS Configuration
AWS_ACCESS_KEY_ID = "AKIAUSISWEIVP3L6DC5K"
AWS_SECRET_ACCESS_KEY = "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"
AWS_REGION = "us-east-1"
S3_BUCKET_NAME = "bigmann-entertainment-media"
SES_EMAIL = "no-reply@bigmannentertainment.com"

def setup_s3_bucket():
    """Create S3 bucket for media storage"""
    print(f"🪣 Setting up S3 bucket: {S3_BUCKET_NAME}")
    
    try:
        # Create S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
        
        # Create bucket (us-east-1 doesn't need CreateBucketConfiguration)
        if AWS_REGION == 'us-east-1':
            s3_client.create_bucket(Bucket=S3_BUCKET_NAME)
        else:
            location = {'LocationConstraint': AWS_REGION}
            s3_client.create_bucket(
                Bucket=S3_BUCKET_NAME,
                CreateBucketConfiguration=location
            )
        
        print(f"✅ S3 bucket '{S3_BUCKET_NAME}' created successfully")
        
        # Configure bucket for website hosting and CORS
        cors_configuration = {
            'CORSRules': [
                {
                    'AllowedHeaders': ['*'],
                    'AllowedMethods': ['GET', 'PUT', 'POST', 'DELETE', 'HEAD'],
                    'AllowedOrigins': ['*'],
                    'ExposeHeaders': ['x-amz-server-side-encryption'],
                    'MaxAgeSeconds': 3000
                }
            ]
        }
        
        s3_client.put_bucket_cors(
            Bucket=S3_BUCKET_NAME,
            CORSConfiguration=cors_configuration
        )
        print(f"✅ CORS configuration applied to bucket")
        
        # Enable versioning
        s3_client.put_bucket_versioning(
            Bucket=S3_BUCKET_NAME,
            VersioningConfiguration={'Status': 'Enabled'}
        )
        print(f"✅ Versioning enabled for bucket")
        
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        
        if error_code == 'BucketAlreadyOwnedByYou':
            print(f"✅ S3 bucket '{S3_BUCKET_NAME}' already exists and is owned by you")
            return True
        elif error_code == 'BucketAlreadyExists':
            print(f"❌ S3 bucket name '{S3_BUCKET_NAME}' is already taken by another AWS account")
            return False
        else:
            print(f"❌ Error creating S3 bucket: {error_code} - {e.response['Error']['Message']}")
            return False
    except Exception as e:
        print(f"❌ Unexpected error creating S3 bucket: {str(e)}")
        return False

def setup_ses_email():
    """Verify SES email address"""
    print(f"📧 Setting up SES email verification: {SES_EMAIL}")
    
    try:
        # Create SES client
        ses_client = boto3.client(
            'ses',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
        
        # Verify email address
        response = ses_client.verify_email_identity(EmailAddress=SES_EMAIL)
        print(f"✅ Verification email sent to {SES_EMAIL}")
        print(f"📬 Please check your email and click the verification link")
        
        # Check current verification status
        identities = ses_client.list_verified_email_addresses()
        verified_emails = identities.get('VerifiedEmailAddresses', [])
        
        if SES_EMAIL in verified_emails:
            print(f"✅ Email {SES_EMAIL} is already verified")
        else:
            print(f"⏳ Email {SES_EMAIL} verification is pending")
            
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print(f"❌ Error verifying SES email: {error_code} - {e.response['Error']['Message']}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error verifying SES email: {str(e)}")
        return False

def check_aws_permissions():
    """Check if AWS credentials have necessary permissions"""
    print("🔐 Checking AWS permissions...")
    
    try:
        # Test S3 permissions
        s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
        
        # List buckets to test S3 access
        buckets = s3_client.list_buckets()
        print(f"✅ S3 access confirmed - found {len(buckets['Buckets'])} buckets")
        
        # Test SES permissions
        ses_client = boto3.client(
            'ses',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
        
        # Get send quota to test SES access
        quota = ses_client.get_send_quota()
        print(f"✅ SES access confirmed - daily send limit: {quota['Max24HourSend']}")
        
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print(f"❌ AWS permission error: {error_code} - {e.response['Error']['Message']}")
        return False
    except Exception as e:
        print(f"❌ Error checking AWS permissions: {str(e)}")
        return False

def main():
    """Main setup function"""
    print("🚀 Starting AWS Infrastructure Setup for Big Mann Entertainment")
    print("=" * 60)
    
    # Check permissions first
    if not check_aws_permissions():
        print("❌ AWS permissions check failed. Cannot proceed with setup.")
        return False
    
    print()
    
    # Setup S3 bucket
    s3_success = setup_s3_bucket()
    print()
    
    # Setup SES email
    ses_success = setup_ses_email()
    print()
    
    # Summary
    print("=" * 60)
    print("📊 AWS Infrastructure Setup Summary:")
    print(f"  S3 Bucket: {'✅ Success' if s3_success else '❌ Failed'}")
    print(f"  SES Email: {'✅ Success' if ses_success else '❌ Failed'}")
    
    if s3_success and ses_success:
        print("\n🎉 AWS infrastructure setup completed successfully!")
        print("\n📋 Next steps:")
        print("  1. Check your email for SES verification link")
        print("  2. Click the verification link to activate SES")
        print("  3. Run backend tests to verify functionality")
        return True
    else:
        print("\n⚠️ Some components failed to setup. Check errors above.")
        return False

if __name__ == "__main__":
    main()