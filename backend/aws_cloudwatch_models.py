"""
AWS CloudWatch Monitoring - Pydantic Models
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class AlarmState(str, Enum):
    OK = "OK"
    ALARM = "ALARM"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


class RuleState(str, Enum):
    ENABLED = "ENABLED"
    DISABLED = "DISABLED"


class SNSTopicInfo(BaseModel):
    topic_arn: str
    display_name: str = ""
    subscription_count: int = 0
    region: str = "us-east-1"


class CloudWatchAlarm(BaseModel):
    alarm_name: str
    alarm_description: str = ""
    metric_name: str = ""
    namespace: str = ""
    state_value: AlarmState = AlarmState.OK
    state_reason: str = ""
    threshold: float = 0
    comparison_operator: str = ""
    evaluation_periods: int = 1
    period: int = 300
    statistic: str = ""
    dimensions: List[Dict[str, str]] = []
    actions_enabled: bool = True
    alarm_actions: List[str] = []
    updated_at: Optional[str] = None


class EventBridgeRule(BaseModel):
    name: str
    description: str = ""
    state: RuleState = RuleState.ENABLED
    event_pattern: Optional[str] = None
    schedule_expression: Optional[str] = None
    managed_by: str = ""
    event_bus_name: str = "default"
    targets_count: int = 0


class CloudWatchMetricPoint(BaseModel):
    timestamp: str
    value: float
    unit: str = ""


class CloudWatchDashboardStats(BaseModel):
    total_alarms: int = 0
    ok_alarms: int = 0
    alarm_state: int = 0
    insufficient_data: int = 0
    total_sns_topics: int = 0
    total_eventbridge_rules: int = 0
    enabled_rules: int = 0
    alarms: List[CloudWatchAlarm] = []
    sns_topics: List[SNSTopicInfo] = []
    eventbridge_rules: List[EventBridgeRule] = []
    account_id: str = ""
    region: str = "us-east-1"
    last_synced: str = ""


class CloudWatchHealthResponse(BaseModel):
    status: str = "healthy"
    service: str = "AWS CloudWatch Monitoring"
    aws_connected: bool = False
    account_id: str = ""
    region: str = "us-east-1"
    alarms_count: int = 0
    sns_topics_count: int = 0
    eventbridge_rules_count: int = 0


class SNSPublishRequest(BaseModel):
    topic_arn: str
    subject: str = ""
    message: str


class SNSPublishResponse(BaseModel):
    message_id: str = ""
    success: bool = False
    error: str = ""
