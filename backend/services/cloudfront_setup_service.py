"""
CloudFront Distribution Setup Service
Programmatically creates and manages CloudFront distributions using AWS credentials.
"""
import os
import uuid
import logging
from typing import Dict, Any, Optional
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class CloudFrontSetupService:
    """Creates and manages CloudFront distributions for the S3 media bucket."""

    def __init__(self):
        self.client = boto3.client(
            "cloudfront",
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
            region_name=os.environ.get("AWS_REGION", "us-east-1"),
        )
        self.s3_bucket = os.environ.get("S3_BUCKET_NAME", "bigmann-entertainment-media")
        self.region = os.environ.get("AWS_REGION", "us-east-1")

    def get_existing_distribution(self) -> Optional[Dict[str, Any]]:
        """Check if a distribution already exists for the S3 bucket."""
        try:
            paginator = self.client.get_paginator("list_distributions")
            for page in paginator.paginate():
                dist_list = page.get("DistributionList", {})
                for dist in dist_list.get("Items", []):
                    origins = dist.get("Origins", {}).get("Items", [])
                    for origin in origins:
                        domain = origin.get("DomainName", "")
                        if self.s3_bucket in domain:
                            return {
                                "distribution_id": dist["Id"],
                                "domain_name": dist["DomainName"],
                                "status": dist["Status"],
                                "enabled": dist.get("Enabled", False),
                                "origin_domain": domain,
                            }
            return None
        except ClientError as e:
            logger.error(f"Error listing CloudFront distributions: {e}")
            return None

    def create_distribution(self, comment: str = "Big Mann Entertainment Media CDN") -> Dict[str, Any]:
        """Create a new CloudFront distribution for the S3 media bucket."""
        existing = self.get_existing_distribution()
        if existing:
            logger.info(f"Distribution already exists: {existing['distribution_id']}")
            return {
                "success": True,
                "created": False,
                "message": "Distribution already exists for this S3 bucket",
                **existing,
            }

        origin_domain = f"{self.s3_bucket}.s3.{self.region}.amazonaws.com"
        caller_ref = f"bme-{uuid.uuid4().hex[:12]}"

        try:
            oai_resp = self.client.create_cloud_front_origin_access_identity(
                CloudFrontOriginAccessIdentityConfig={
                    "CallerReference": caller_ref,
                    "Comment": f"OAI for {self.s3_bucket}",
                }
            )
            oai_id = oai_resp["CloudFrontOriginAccessIdentity"]["Id"]

            dist_config = {
                "CallerReference": caller_ref,
                "Comment": comment,
                "Enabled": True,
                "Origins": {
                    "Quantity": 1,
                    "Items": [
                        {
                            "Id": f"S3-{self.s3_bucket}",
                            "DomainName": origin_domain,
                            "S3OriginConfig": {
                                "OriginAccessIdentity": f"origin-access-identity/cloudfront/{oai_id}"
                            },
                        }
                    ],
                },
                "DefaultCacheBehavior": {
                    "TargetOriginId": f"S3-{self.s3_bucket}",
                    "ViewerProtocolPolicy": "redirect-to-https",
                    "AllowedMethods": {
                        "Quantity": 2,
                        "Items": ["GET", "HEAD"],
                        "CachedMethods": {"Quantity": 2, "Items": ["GET", "HEAD"]},
                    },
                    "ForwardedValues": {
                        "QueryString": False,
                        "Cookies": {"Forward": "none"},
                    },
                    "MinTTL": 0,
                    "DefaultTTL": 86400,
                    "MaxTTL": 31536000,
                    "Compress": True,
                },
                "ViewerCertificate": {"CloudFrontDefaultCertificate": True},
                "PriceClass": "PriceClass_100",
                "DefaultRootObject": "",
            }

            resp = self.client.create_distribution(DistributionConfig=dist_config)
            dist = resp["Distribution"]
            distribution_id = dist["Id"]
            domain_name = dist["DomainName"]

            logger.info(f"Created CloudFront distribution {distribution_id} -> {domain_name}")

            return {
                "success": True,
                "created": True,
                "distribution_id": distribution_id,
                "domain_name": domain_name,
                "status": dist["Status"],
                "origin_domain": origin_domain,
                "oai_id": oai_id,
                "message": f"Distribution created. Domain: {domain_name}",
            }

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            logger.error(f"CloudFront create failed [{error_code}]: {error_msg}")
            return {
                "success": False,
                "created": False,
                "error": error_code,
                "message": error_msg,
            }

    def get_distribution_status(self, distribution_id: str) -> Dict[str, Any]:
        """Get the current status of a distribution."""
        try:
            resp = self.client.get_distribution(Id=distribution_id)
            dist = resp["Distribution"]
            return {
                "distribution_id": distribution_id,
                "domain_name": dist["DomainName"],
                "status": dist["Status"],
                "enabled": dist["DistributionConfig"]["Enabled"],
                "last_modified": str(dist.get("LastModifiedTime", "")),
            }
        except ClientError as e:
            return {"error": str(e)}

    def update_env_distribution_id(self, distribution_id: str, domain_name: str) -> bool:
        """Update the .env file with the new distribution ID and domain."""
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        try:
            with open(env_path, "r") as f:
                lines = f.readlines()

            updated_dist = False
            updated_domain = False
            new_lines = []
            for line in lines:
                if line.startswith("CLOUDFRONT_DISTRIBUTION_ID="):
                    new_lines.append(f'CLOUDFRONT_DISTRIBUTION_ID="{distribution_id}"\n')
                    updated_dist = True
                elif line.startswith("CLOUDFRONT_DOMAIN="):
                    new_lines.append(f'CLOUDFRONT_DOMAIN="{domain_name}"\n')
                    updated_domain = True
                else:
                    new_lines.append(line)

            if not updated_dist:
                new_lines.append(f'CLOUDFRONT_DISTRIBUTION_ID="{distribution_id}"\n')
            if not updated_domain:
                new_lines.append(f'CLOUDFRONT_DOMAIN="{domain_name}"\n')

            with open(env_path, "w") as f:
                f.writelines(new_lines)

            os.environ["CLOUDFRONT_DISTRIBUTION_ID"] = distribution_id
            os.environ["CLOUDFRONT_DOMAIN"] = domain_name
            logger.info(f"Updated .env with CLOUDFRONT_DISTRIBUTION_ID={distribution_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update .env: {e}")
            return False
