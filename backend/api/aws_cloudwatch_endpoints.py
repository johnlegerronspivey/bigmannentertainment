"""
AWS CloudWatch Monitoring - API Endpoints
Real-time monitoring of CloudWatch Alarms, SNS Topics, and EventBridge Rules
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List

from aws_cloudwatch_models import (
    CloudWatchDashboardStats, CloudWatchHealthResponse,
    CloudWatchAlarm, SNSTopicInfo, EventBridgeRule,
    SNSPublishRequest, SNSPublishResponse
)
from aws_cloudwatch_service import get_cloudwatch_service, CloudWatchMonitoringService

router = APIRouter(prefix="/cloudwatch", tags=["AWS CloudWatch Monitoring"])


def get_service() -> CloudWatchMonitoringService:
    service = get_cloudwatch_service()
    if service is None:
        raise HTTPException(status_code=503, detail="CloudWatch monitoring service not initialized")
    return service


@router.get("/health", response_model=CloudWatchHealthResponse)
async def health_check(service: CloudWatchMonitoringService = Depends(get_service)):
    return service.check_health()


@router.get("/dashboard", response_model=CloudWatchDashboardStats)
async def get_dashboard(service: CloudWatchMonitoringService = Depends(get_service)):
    return service.get_dashboard()


@router.get("/alarms", response_model=List[CloudWatchAlarm])
async def get_alarms(service: CloudWatchMonitoringService = Depends(get_service)):
    return service.get_alarms()


@router.get("/sns-topics", response_model=List[SNSTopicInfo])
async def get_sns_topics(service: CloudWatchMonitoringService = Depends(get_service)):
    return service.get_sns_topics()


@router.get("/eventbridge-rules", response_model=List[EventBridgeRule])
async def get_eventbridge_rules(service: CloudWatchMonitoringService = Depends(get_service)):
    return service.get_eventbridge_rules()


@router.post("/sns/publish", response_model=SNSPublishResponse)
async def publish_sns_message(
    request: SNSPublishRequest,
    service: CloudWatchMonitoringService = Depends(get_service)
):
    result = service.publish_sns_message(request.topic_arn, request.subject, request.message)
    if not result.success:
        raise HTTPException(status_code=500, detail=result.error)
    return result
