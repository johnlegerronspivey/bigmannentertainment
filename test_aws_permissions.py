#!/usr/bin/env python3
"""
Test AWS permissions without requiring full access
"""

import boto3
from botocore.exceptions import ClientError

# AWS Configuration
AWS_ACCESS_KEY_ID = "AKIAUSISWEIVP3L6DC5K"
AWS_SECRET_ACCESS_KEY = "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"
AWS_REGION = "us-east-1"
S3_BUCKET_NAME = "bigmann-entertainment-media"
SES_EMAIL = "no-reply@bigmannentertainment.com"

def test_s3_operations():
    """Test specific S3 operations"""
    print("🪣 Testing S3 operations...")
    
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
        
        # Test if bucket exists
        try:
            s3_client.head_bucket(Bucket=S3_BUCKET_NAME)
            print(f"✅ Bucket '{S3_BUCKET_NAME}' exists and is accessible")
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                print(f"📋 Bucket '{S3_BUCKET_NAME}' does not exist")
                
                # Try to create the bucket
                try:
                    if AWS_REGION == 'us-east-1':
                        s3_client.create_bucket(Bucket=S3_BUCKET_NAME)
                    else:
                        location = {'LocationConstraint': AWS_REGION}
                        s3_client.create_bucket(
                            Bucket=S3_BUCKET_NAME,
                            CreateBucketConfiguration=location
                        )
                    print(f"✅ Bucket '{S3_BUCKET_NAME}' created successfully")
                    return True
                except ClientError as create_error:
                    print(f"❌ Cannot create bucket: {create_error.response['Error']['Code']} - {create_error.response['Error']['Message']}")
                    return False
            else:
                print(f"❌ Error accessing bucket: {error_code} - {e.response['Error']['Message']}")
                return False
                
    except Exception as e:
        print(f"❌ S3 client error: {str(e)}")
        return False

def test_ses_operations():
    """Test specific SES operations"""
    print("📧 Testing SES operations...")
    
    try:
        ses_client = boto3.client(
            'ses',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
        
        # Test send quota (basic SES permission check)
        try:
            quota = ses_client.get_send_quota()
            print(f"✅ SES accessible - Max send: {quota['Max24HourSend']}, Sent: {quota['SentLast24Hours']}")
            
            # Check if email is verified
            identities = ses_client.list_verified_email_addresses()
            verified_emails = identities.get('VerifiedEmailAddresses', [])
            
            if SES_EMAIL in verified_emails:
                print(f"✅ Email '{SES_EMAIL}' is already verified")
            else:
                print(f"📋 Email '{SES_EMAIL}' is not verified")
                
                # Try to verify the email
                try:
                    ses_client.verify_email_identity(EmailAddress=SES_EMAIL)
                    print(f"✅ Verification email sent to '{SES_EMAIL}'")
                except ClientError as verify_error:
                    print(f"❌ Cannot verify email: {verify_error.response['Error']['Code']} - {verify_error.response['Error']['Message']}")
            
            return True
            
        except ClientError as e:
            print(f"❌ SES error: {e.response['Error']['Code']} - {e.response['Error']['Message']}")
            return False
            
    except Exception as e:
        print(f"❌ SES client error: {str(e)}")
        return False

def main():
    """Test AWS permissions and setup"""
    print("🧪 Testing AWS Permissions and Infrastructure")
    print("=" * 50)
    
    s3_ok = test_s3_operations()
    print()
    ses_ok = test_ses_operations()
    print()
    
    print("=" * 50)
    print("📊 Results:")
    print(f"  S3: {'✅ Working' if s3_ok else '❌ Issues'}")
    print(f"  SES: {'✅ Working' if ses_ok else '❌ Issues'}")
    
    if s3_ok and ses_ok:
        print("\n🎉 AWS infrastructure is ready!")
    else:
        print("\n⚠️ Some AWS services have issues")

if __name__ == "__main__":
    main()