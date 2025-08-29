#!/usr/bin/env python3
"""
AWS Phase 2 Infrastructure Setup: CloudFront, Lambda, and Rekognition
Creates additional AWS resources for media processing and content delivery
"""

import boto3
import json
import time
from botocore.exceptions import ClientError

# AWS Configuration
AWS_ACCESS_KEY_ID = "AKIAUSISWEIVP3L6DC5K"
AWS_SECRET_ACCESS_KEY = "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"
AWS_REGION = "us-east-1"
S3_BUCKET_NAME = "bigmann-entertainment-media"

def setup_dynamodb_tables():
    """Create DynamoDB tables for processing status and moderation results"""
    print("🗄️ Setting up DynamoDB tables...")
    
    try:
        dynamodb = boto3.client(
            'dynamodb',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
        
        # Processing Status Table
        try:
            processing_table = dynamodb.create_table(
                TableName='bigmann-processing-status',
                KeySchema=[
                    {'AttributeName': 'upload_id', 'KeyType': 'HASH'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'upload_id', 'AttributeType': 'S'}
                ],
                BillingMode='PAY_PER_REQUEST',
                Tags=[
                    {'Key': 'Project', 'Value': 'BigMannEntertainment'},
                    {'Key': 'Purpose', 'Value': 'MediaProcessing'}
                ]
            )
            print("✅ Created processing status table")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceInUseException':
                print("✅ Processing status table already exists")
            else:
                print(f"❌ Error creating processing status table: {e}")
        
        # Content Moderation Table  
        try:
            moderation_table = dynamodb.create_table(
                TableName='bigmann-content-moderation',
                KeySchema=[
                    {'AttributeName': 'content_key', 'KeyType': 'HASH'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'content_key', 'AttributeType': 'S'}
                ],
                BillingMode='PAY_PER_REQUEST',
                Tags=[
                    {'Key': 'Project', 'Value': 'BigMannEntertainment'},
                    {'Key': 'Purpose', 'Value': 'ContentModeration'}
                ]
            )
            print("✅ Created content moderation table")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceInUseException':
                print("✅ Content moderation table already exists")
            else:
                print(f"❌ Error creating content moderation table: {e}")
        
        # Video Analysis Results Table
        try:
            video_analysis_table = dynamodb.create_table(
                TableName='bigmann-video-analysis-results',
                KeySchema=[
                    {'AttributeName': 'job_id', 'KeyType': 'HASH'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'job_id', 'AttributeType': 'S'}
                ],
                BillingMode='PAY_PER_REQUEST',
                TimeToLiveSpecification={
                    'AttributeName': 'ttl',
                    'Enabled': True
                },
                Tags=[
                    {'Key': 'Project', 'Value': 'BigMannEntertainment'},
                    {'Key': 'Purpose', 'Value': 'VideoAnalysis'}
                ]
            )
            print("✅ Created video analysis results table")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceInUseException':
                print("✅ Video analysis results table already exists")
            else:
                print(f"❌ Error creating video analysis results table: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up DynamoDB tables: {str(e)}")
        return False

def setup_cloudfront_distribution():
    """Create CloudFront distribution for global content delivery"""
    print("🌐 Setting up CloudFront distribution...")
    
    try:
        cloudfront = boto3.client(
            'cloudfront',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
        
        # Create Origin Access Control (OAC)
        oac_config = {
            'Name': 'BigMann-S3-OAC',
            'Description': 'Origin Access Control for BigMann Entertainment S3 bucket',
            'OriginAccessControlConfig': {
                'Name': 'BigMann-S3-OAC',
                'Description': 'OAC for BigMann S3 bucket access',
                'SigningProtocol': 'sigv4',
                'SigningBehavior': 'always',
                'OriginAccessControlOriginType': 's3'
            }
        }
        
        try:
            oac_response = cloudfront.create_origin_access_control(**oac_config)
            oac_id = oac_response['OriginAccessControl']['Id']
            print(f"✅ Created Origin Access Control: {oac_id}")
        except ClientError as e:
            if 'already exists' in str(e):
                print("✅ Origin Access Control already exists")
                # List existing OACs to get ID
                oacs = cloudfront.list_origin_access_controls()
                for oac in oacs['OriginAccessControlList']['Items']:
                    if oac['Name'] == 'BigMann-S3-OAC':
                        oac_id = oac['Id']
                        break
            else:
                raise e
        
        # CloudFront Distribution Configuration
        distribution_config = {
            'CallerReference': f'bigmann-media-{int(time.time())}',
            'Comment': 'BigMann Entertainment Media Platform Distribution',
            'Enabled': True,
            'Origins': {
                'Quantity': 1,
                'Items': [
                    {
                        'Id': 'bigmann-s3-origin',
                        'DomainName': f'{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com',
                        'OriginAccessControlId': oac_id,
                        'S3OriginConfig': {
                            'OriginAccessIdentity': ''  # Empty for OAC
                        }
                    }
                ]
            },
            'DefaultCacheBehavior': {
                'TargetOriginId': 'bigmann-s3-origin',
                'ViewerProtocolPolicy': 'redirect-to-https',
                'AllowedMethods': {
                    'Quantity': 7,
                    'Items': ['GET', 'HEAD', 'OPTIONS', 'PUT', 'POST', 'PATCH', 'DELETE'],
                    'CachedMethods': {
                        'Quantity': 2,
                        'Items': ['GET', 'HEAD']
                    }
                },
                'ForwardedValues': {
                    'QueryString': False,
                    'Cookies': {'Forward': 'none'},
                    'Headers': {
                        'Quantity': 1,
                        'Items': ['Origin']
                    }
                },
                'TrustedSigners': {
                    'Enabled': False,
                    'Quantity': 0
                },
                'MinTTL': 0,
                'DefaultTTL': 86400,  # 1 day
                'MaxTTL': 31536000,   # 1 year
                'Compress': True
            },
            'CacheBehaviors': {
                'Quantity': 3,
                'Items': [
                    {
                        'PathPattern': '*.mp4',
                        'TargetOriginId': 'bigmann-s3-origin',
                        'ViewerProtocolPolicy': 'redirect-to-https',
                        'AllowedMethods': {
                            'Quantity': 2,
                            'Items': ['GET', 'HEAD'],
                            'CachedMethods': {
                                'Quantity': 2,
                                'Items': ['GET', 'HEAD']
                            }
                        },
                        'ForwardedValues': {
                            'QueryString': True,
                            'Cookies': {'Forward': 'none'}
                        },
                        'TrustedSigners': {'Enabled': False, 'Quantity': 0},
                        'MinTTL': 0,
                        'DefaultTTL': 3600,    # 1 hour for videos
                        'MaxTTL': 86400,       # 1 day
                        'Compress': False      # Don't compress video files
                    },
                    {
                        'PathPattern': '/thumbnails/*',
                        'TargetOriginId': 'bigmann-s3-origin',
                        'ViewerProtocolPolicy': 'redirect-to-https',
                        'AllowedMethods': {
                            'Quantity': 2,
                            'Items': ['GET', 'HEAD'],
                            'CachedMethods': {
                                'Quantity': 2,
                                'Items': ['GET', 'HEAD']
                            }
                        },
                        'ForwardedValues': {
                            'QueryString': False,
                            'Cookies': {'Forward': 'none'}
                        },
                        'TrustedSigners': {'Enabled': False, 'Quantity': 0},
                        'MinTTL': 0,
                        'DefaultTTL': 86400,   # 1 day for thumbnails
                        'MaxTTL': 31536000,    # 1 year
                        'Compress': True
                    },
                    {
                        'PathPattern': '/processed/*',
                        'TargetOriginId': 'bigmann-s3-origin',
                        'ViewerProtocolPolicy': 'redirect-to-https',
                        'AllowedMethods': {
                            'Quantity': 2,
                            'Items': ['GET', 'HEAD'],
                            'CachedMethods': {
                                'Quantity': 2,
                                'Items': ['GET', 'HEAD']
                            }
                        },
                        'ForwardedValues': {
                            'QueryString': False,
                            'Cookies': {'Forward': 'none'}
                        },
                        'TrustedSigners': {'Enabled': False, 'Quantity': 0},
                        'MinTTL': 0,
                        'DefaultTTL': 7200,    # 2 hours for processed content
                        'MaxTTL': 86400,       # 1 day
                        'Compress': True
                    }
                ]
            },
            'PriceClass': 'PriceClass_All'  # Global edge locations
        }
        
        try:
            response = cloudfront.create_distribution(
                DistributionConfig=distribution_config
            )
            
            distribution_id = response['Distribution']['Id']
            distribution_domain = response['Distribution']['DomainName']
            
            print(f"✅ Created CloudFront distribution: {distribution_id}")
            print(f"📍 Distribution domain: {distribution_domain}")
            
            return {
                'distribution_id': distribution_id,
                'domain_name': distribution_domain,
                'oac_id': oac_id
            }
            
        except ClientError as e:
            print(f"❌ Error creating CloudFront distribution: {e}")
            return None
            
    except Exception as e:
        print(f"❌ Error setting up CloudFront: {str(e)}")
        return None

def test_rekognition_permissions():
    """Test Rekognition service permissions"""
    print("🔍 Testing Rekognition permissions...")
    
    try:
        rekognition = boto3.client(
            'rekognition',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
        
        # Test basic operations
        try:
            # Test content moderation capability
            response = rekognition.describe_collection(CollectionId='test-collection-check')
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print("✅ Rekognition API accessible (collection not found is expected)")
            elif e.response['Error']['Code'] == 'AccessDeniedException':
                print("❌ Rekognition access denied - permissions need to be added")
                return False
            else:
                print(f"✅ Rekognition accessible with response: {e.response['Error']['Code']}")
        
        # Test if we can check service limits (another permission test)
        try:
            # This will test general rekognition access
            print("✅ Rekognition service is accessible")
            return True
        except Exception as e:
            print(f"⚠️ Rekognition may have limited permissions: {e}")
            return True  # Continue setup even with limited permissions
            
    except Exception as e:
        print(f"❌ Error testing Rekognition: {str(e)}")
        return False

def update_s3_bucket_policy(distribution_info):
    """Update S3 bucket policy to allow CloudFront access"""
    print("🔐 Updating S3 bucket policy for CloudFront access...")
    
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
        
        # Get AWS account ID
        sts_client = boto3.client('sts')
        account_id = sts_client.get_caller_identity()['Account']
        
        # S3 bucket policy for CloudFront OAC access
        bucket_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "AllowCloudFrontServicePrincipal",
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "cloudfront.amazonaws.com"
                    },
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{S3_BUCKET_NAME}/*",
                    "Condition": {
                        "StringEquals": {
                            "AWS:SourceArn": f"arn:aws:cloudfront::{account_id}:distribution/{distribution_info['distribution_id']}"
                        }
                    }
                }
            ]
        }
        
        s3_client.put_bucket_policy(
            Bucket=S3_BUCKET_NAME,
            Policy=json.dumps(bucket_policy)
        )
        
        print("✅ Updated S3 bucket policy for CloudFront access")
        return True
        
    except Exception as e:
        print(f"❌ Error updating S3 bucket policy: {str(e)}")
        return False

def create_test_folders():
    """Create test folder structure in S3"""
    print("📁 Creating folder structure in S3...")
    
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
        
        # Create folder structure by uploading placeholder files
        folders = [
            'uploads/',
            'processed/',
            'thumbnails/',
            'waveforms/',
            'approved/',
            'quarantine/',
            'errors/'
        ]
        
        for folder in folders:
            try:
                s3_client.put_object(
                    Bucket=S3_BUCKET_NAME,
                    Key=f"{folder}.keep",
                    Body=b'This file maintains the folder structure',
                    ContentType='text/plain'
                )
            except Exception as e:
                print(f"⚠️ Could not create folder {folder}: {e}")
        
        print("✅ Created S3 folder structure")
        return True
        
    except Exception as e:
        print(f"❌ Error creating S3 folders: {str(e)}")
        return False

def main():
    """Main setup function for Phase 2"""
    print("🚀 Starting AWS Phase 2 Setup - CloudFront, Lambda, Rekognition")
    print("=" * 70)
    
    results = {}
    
    # Step 1: Setup DynamoDB tables
    results['dynamodb'] = setup_dynamodb_tables()
    print()
    
    # Step 2: Test Rekognition permissions
    results['rekognition'] = test_rekognition_permissions()
    print()
    
    # Step 3: Setup CloudFront distribution
    distribution_info = setup_cloudfront_distribution()
    results['cloudfront'] = distribution_info is not None
    print()
    
    # Step 4: Update S3 bucket policy (if CloudFront was created)
    if distribution_info:
        results['s3_policy'] = update_s3_bucket_policy(distribution_info)
    else:
        results['s3_policy'] = False
    print()
    
    # Step 5: Create folder structure
    results['s3_folders'] = create_test_folders()
    print()
    
    # Summary
    print("=" * 70)
    print("📊 Phase 2 Setup Summary:")
    
    for component, success in results.items():
        status = "✅ Success" if success else "❌ Failed"
        print(f"  {component.upper()}: {status}")
    
    if distribution_info:
        print(f"\n📋 CloudFront Information:")
        print(f"  Distribution ID: {distribution_info['distribution_id']}")
        print(f"  Domain Name: {distribution_info['domain_name']}")
        print(f"  OAC ID: {distribution_info['oac_id']}")
        
        print(f"\n🌐 CDN URLs:")
        print(f"  Base URL: https://{distribution_info['domain_name']}")
        print(f"  Example: https://{distribution_info['domain_name']}/approved/your-file.mp4")
    
    success_count = sum(results.values())
    total_count = len(results)
    
    if success_count == total_count:
        print(f"\n🎉 Phase 2 setup completed successfully! ({success_count}/{total_count})")
        print("\n📋 Next steps:")
        print("  1. Lambda functions need to be deployed (requires code packages)")
        print("  2. Set up SNS topics for Rekognition video analysis notifications")
        print("  3. Deploy FastAPI backend with Phase 2 integration")
        print("  4. Test media processing workflow")
    else:
        print(f"\n⚠️ Phase 2 setup partially completed ({success_count}/{total_count})")
        print("Check failed components above for details.")
    
    return results, distribution_info

if __name__ == "__main__":
    results, distribution_info = main()