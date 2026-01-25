"""
AWS Enterprise Mapping API Endpoints
Provides REST API for AWS infrastructure discovery, mapping, and management
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from datetime import datetime, timezone

from aws_enterprise_mapping_models import (
    AWSServiceType, ResourceStatus, AWSResource,
    EC2Instance, S3Bucket, RDSInstance, LambdaFunction,
    CloudFrontDistribution, IAMRole, CostBreakdown,
    InfrastructureMap, EnterpriseMetrics, ResourceAction,
    ResourceAlert
)
import aws_enterprise_mapping_service

router = APIRouter(prefix="/api/aws-enterprise", tags=["AWS Enterprise Mapping"])


@router.get("/health", response_model=dict)
async def health_check():
    """Check AWS Enterprise Mapping service health"""
    service = aws_enterprise_mapping_service.enterprise_mapping_service
    
    if not service:
        return {
            "status": "unavailable",
            "message": "AWS Enterprise Mapping service not initialized"
        }
    
    try:
        account_id = await service.get_account_id()
        return {
            "status": "healthy",
            "account_id": account_id,
            "region": service.default_region,
            "message": "AWS Enterprise Mapping service operational"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


# =========================
# Resource Discovery
# =========================

@router.get("/resources/ec2", response_model=List[EC2Instance])
async def list_ec2_instances(
    region: Optional[str] = Query(None, description="AWS region")
):
    """List all EC2 instances"""
    try:
        service = aws_enterprise_mapping_service.enterprise_mapping_service
        if not service:
            raise HTTPException(status_code=503, detail="Service not available")
        
        instances = await service.discover_ec2_instances(region)
        return instances
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing EC2 instances: {str(e)}")


@router.get("/resources/s3", response_model=List[S3Bucket])
async def list_s3_buckets():
    """List all S3 buckets"""
    try:
        service = aws_enterprise_mapping_service.enterprise_mapping_service
        if not service:
            raise HTTPException(status_code=503, detail="Service not available")
        
        buckets = await service.discover_s3_buckets()
        return buckets
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing S3 buckets: {str(e)}")


@router.get("/resources/rds", response_model=List[RDSInstance])
async def list_rds_instances(
    region: Optional[str] = Query(None, description="AWS region")
):
    """List all RDS instances"""
    try:
        service = aws_enterprise_mapping_service.enterprise_mapping_service
        if not service:
            raise HTTPException(status_code=503, detail="Service not available")
        
        instances = await service.discover_rds_instances(region)
        return instances
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing RDS instances: {str(e)}")


@router.get("/resources/lambda", response_model=List[LambdaFunction])
async def list_lambda_functions(
    region: Optional[str] = Query(None, description="AWS region")
):
    """List all Lambda functions"""
    try:
        service = aws_enterprise_mapping_service.enterprise_mapping_service
        if not service:
            raise HTTPException(status_code=503, detail="Service not available")
        
        functions = await service.discover_lambda_functions(region)
        return functions
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing Lambda functions: {str(e)}")


@router.get("/resources/cloudfront", response_model=List[CloudFrontDistribution])
async def list_cloudfront_distributions():
    """List all CloudFront distributions"""
    try:
        service = aws_enterprise_mapping_service.enterprise_mapping_service
        if not service:
            raise HTTPException(status_code=503, detail="Service not available")
        
        distributions = await service.discover_cloudfront_distributions()
        return distributions
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing CloudFront distributions: {str(e)}")


@router.get("/resources/iam-roles", response_model=List[IAMRole])
async def list_iam_roles():
    """List all IAM roles"""
    try:
        service = aws_enterprise_mapping_service.enterprise_mapping_service
        if not service:
            raise HTTPException(status_code=503, detail="Service not available")
        
        roles = await service.discover_iam_roles()
        return roles
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing IAM roles: {str(e)}")


# =========================
# Infrastructure Mapping
# =========================

@router.get("/infrastructure-map", response_model=InfrastructureMap)
async def get_infrastructure_map():
    """Generate complete infrastructure map"""
    try:
        service = aws_enterprise_mapping_service.enterprise_mapping_service
        if not service:
            raise HTTPException(status_code=503, detail="Service not available")
        
        infra_map = await service.generate_infrastructure_map()
        return infra_map
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating infrastructure map: {str(e)}")


# =========================
# Cost Management
# =========================

@router.get("/costs", response_model=CostBreakdown)
async def get_cost_breakdown(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """Get cost breakdown for specified period"""
    try:
        service = aws_enterprise_mapping_service.enterprise_mapping_service
        if not service:
            raise HTTPException(status_code=503, detail="Service not available")
        
        cost_breakdown = await service.get_cost_breakdown(start_date, end_date)
        return cost_breakdown
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting cost breakdown: {str(e)}")


# =========================
# Enterprise Metrics
# =========================

@router.get("/metrics", response_model=EnterpriseMetrics)
async def get_enterprise_metrics():
    """Get enterprise-wide metrics"""
    try:
        service = aws_enterprise_mapping_service.enterprise_mapping_service
        if not service:
            raise HTTPException(status_code=503, detail="Service not available")
        
        metrics = await service.get_enterprise_metrics()
        return metrics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting enterprise metrics: {str(e)}")


# =========================
# Resource Actions
# =========================

@router.post("/resources/actions", response_model=ResourceAction)
async def execute_resource_action(action: ResourceAction):
    """Execute an action on a resource (start, stop, etc.)"""
    try:
        service = aws_enterprise_mapping_service.enterprise_mapping_service
        if not service:
            raise HTTPException(status_code=503, detail="Service not available")
        
        result = await service.execute_resource_action(action)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing action: {str(e)}")


# =========================
# Alerts
# =========================

@router.get("/alerts", response_model=List[ResourceAlert])
async def list_alerts(
    severity: Optional[str] = Query(None, description="Filter by severity"),
    acknowledged: Optional[bool] = Query(None, description="Filter by acknowledged status")
):
    """List resource alerts"""
    try:
        service = aws_enterprise_mapping_service.enterprise_mapping_service
        if not service:
            raise HTTPException(status_code=503, detail="Service not available")
        
        alerts = await service.get_resource_alerts(severity, acknowledged)
        return alerts
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing alerts: {str(e)}")


@router.post("/alerts", response_model=ResourceAlert)
async def create_alert(alert: ResourceAlert):
    """Create a new resource alert"""
    try:
        service = aws_enterprise_mapping_service.enterprise_mapping_service
        if not service:
            raise HTTPException(status_code=503, detail="Service not available")
        
        result = await service.create_alert(alert)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating alert: {str(e)}")


@router.post("/alerts/{alert_id}/acknowledge", response_model=dict)
async def acknowledge_alert(
    alert_id: str,
    user_id: str = Query(..., description="User acknowledging the alert")
):
    """Acknowledge a resource alert"""
    try:
        service = aws_enterprise_mapping_service.enterprise_mapping_service
        if not service:
            raise HTTPException(status_code=503, detail="Service not available")
        
        success = await service.acknowledge_alert(alert_id, user_id)
        
        if success:
            return {"message": "Alert acknowledged successfully"}
        else:
            raise HTTPException(status_code=404, detail="Alert not found")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error acknowledging alert: {str(e)}")


# =========================
# Service Types Reference
# =========================

@router.get("/service-types", response_model=dict)
async def get_service_types():
    """Get all AWS service types and their descriptions"""
    return {
        "service_types": {
            "compute": {
                "name": "Compute",
                "description": "EC2, Lambda, ECS, EKS",
                "icon": "cpu"
            },
            "storage": {
                "name": "Storage",
                "description": "S3, EBS, EFS, Glacier",
                "icon": "database"
            },
            "database": {
                "name": "Database",
                "description": "RDS, DynamoDB, ElastiCache",
                "icon": "database"
            },
            "networking": {
                "name": "Networking",
                "description": "VPC, CloudFront, Route53, API Gateway",
                "icon": "network"
            },
            "security": {
                "name": "Security",
                "description": "IAM, KMS, WAF, Shield",
                "icon": "shield"
            },
            "analytics": {
                "name": "Analytics",
                "description": "Athena, Redshift, QuickSight",
                "icon": "chart"
            },
            "ai_ml": {
                "name": "AI/ML",
                "description": "SageMaker, Rekognition, Comprehend",
                "icon": "brain"
            },
            "management": {
                "name": "Management",
                "description": "CloudWatch, CloudTrail, Config",
                "icon": "settings"
            },
            "application": {
                "name": "Application",
                "description": "SNS, SQS, Step Functions",
                "icon": "app"
            },
            "media": {
                "name": "Media",
                "description": "MediaConvert, MediaLive, Elemental",
                "icon": "video"
            }
        }
    }


@router.get("/regions", response_model=dict)
async def get_available_regions():
    """Get available AWS regions"""
    return {
        "regions": [
            {"code": "us-east-1", "name": "US East (N. Virginia)", "status": "active"},
            {"code": "us-east-2", "name": "US East (Ohio)", "status": "active"},
            {"code": "us-west-1", "name": "US West (N. California)", "status": "active"},
            {"code": "us-west-2", "name": "US West (Oregon)", "status": "active"},
            {"code": "eu-west-1", "name": "Europe (Ireland)", "status": "active"},
            {"code": "eu-west-2", "name": "Europe (London)", "status": "active"},
            {"code": "eu-central-1", "name": "Europe (Frankfurt)", "status": "active"},
            {"code": "ap-northeast-1", "name": "Asia Pacific (Tokyo)", "status": "active"},
            {"code": "ap-southeast-1", "name": "Asia Pacific (Singapore)", "status": "active"},
            {"code": "ap-southeast-2", "name": "Asia Pacific (Sydney)", "status": "active"},
            {"code": "sa-east-1", "name": "South America (São Paulo)", "status": "active"}
        ],
        "default_region": "us-east-1"
    }
