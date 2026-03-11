"""
AWS CloudWatch Monitoring - Service Layer
Real-time monitoring of CloudWatch Alarms, SNS Topics, and EventBridge Rules
"""

import os
import boto3
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import load_dotenv
import logging

from aws_cloudwatch_models import (
    CloudWatchAlarm, AlarmState, SNSTopicInfo,
    EventBridgeRule, RuleState, CloudWatchDashboardStats,
    CloudWatchHealthResponse, SNSPublishResponse
)

load_dotenv()
logger = logging.getLogger(__name__)

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

_cloudwatch_service = None


class CloudWatchMonitoringService:
    """Service for real-time AWS CloudWatch, SNS, and EventBridge monitoring"""

    def __init__(self):
        self.cw_client = None
        self.sns_client = None
        self.events_client = None
        self.sts_client = None
        self.aws_connected = False
        self._init_clients()

    def _init_clients(self):
        try:
            kwargs = {"region_name": AWS_REGION}
            if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
                kwargs["aws_access_key_id"] = AWS_ACCESS_KEY_ID
                kwargs["aws_secret_access_key"] = AWS_SECRET_ACCESS_KEY

            self.cw_client = boto3.client("cloudwatch", **kwargs)
            self.sns_client = boto3.client("sns", **kwargs)
            self.events_client = boto3.client("events", **kwargs)
            self.sts_client = boto3.client("sts", **kwargs)

            self.sts_client.get_caller_identity()
            self.aws_connected = True
            logger.info("CloudWatch monitoring: AWS clients connected")
        except Exception as e:
            logger.warning(f"CloudWatch monitoring: AWS connection failed: {e}")
            self.aws_connected = False

    def _account_id(self) -> str:
        try:
            return self.sts_client.get_caller_identity()["Account"]
        except Exception:
            return "314108682794"

    # ==================== CloudWatch Alarms ====================

    def get_alarms(self) -> List[CloudWatchAlarm]:
        if not self.aws_connected:
            return []
        try:
            resp = self.cw_client.describe_alarms(MaxRecords=100)
            alarms = []
            for a in resp.get("MetricAlarms", []):
                alarms.append(CloudWatchAlarm(
                    alarm_name=a["AlarmName"],
                    alarm_description=a.get("AlarmDescription", ""),
                    metric_name=a.get("MetricName", ""),
                    namespace=a.get("Namespace", ""),
                    state_value=AlarmState(a.get("StateValue", "OK")),
                    state_reason=a.get("StateReason", ""),
                    threshold=a.get("Threshold", 0),
                    comparison_operator=a.get("ComparisonOperator", ""),
                    evaluation_periods=a.get("EvaluationPeriods", 1),
                    period=a.get("Period", 300),
                    statistic=a.get("Statistic", ""),
                    dimensions=[
                        {"name": d["Name"], "value": d["Value"]}
                        for d in a.get("Dimensions", [])
                    ],
                    actions_enabled=a.get("ActionsEnabled", True),
                    alarm_actions=a.get("AlarmActions", []),
                    updated_at=a.get("StateUpdatedTimestamp", datetime.now(timezone.utc)).isoformat() if a.get("StateUpdatedTimestamp") else None
                ))
            return alarms
        except Exception as e:
            logger.error(f"Error fetching CloudWatch alarms: {e}")
            return []

    # ==================== SNS Topics ====================

    def get_sns_topics(self) -> List[SNSTopicInfo]:
        if not self.aws_connected:
            return []
        try:
            resp = self.sns_client.list_topics()
            topics = []
            for t in resp.get("Topics", []):
                arn = t["TopicArn"]
                try:
                    attrs = self.sns_client.get_topic_attributes(TopicArn=arn)["Attributes"]
                    display_name = attrs.get("DisplayName", "")
                    sub_count = int(attrs.get("SubscriptionsConfirmed", 0))
                except Exception:
                    display_name = ""
                    sub_count = 0

                topics.append(SNSTopicInfo(
                    topic_arn=arn,
                    display_name=display_name or arn.split(":")[-1],
                    subscription_count=sub_count,
                    region=AWS_REGION
                ))
            return topics
        except Exception as e:
            logger.error(f"Error fetching SNS topics: {e}")
            return []

    def publish_sns_message(self, topic_arn: str, subject: str, message: str) -> SNSPublishResponse:
        if not self.aws_connected:
            return SNSPublishResponse(success=False, error="AWS not connected")
        try:
            kwargs = {"TopicArn": topic_arn, "Message": message}
            if subject and not topic_arn.endswith(".fifo"):
                kwargs["Subject"] = subject
            resp = self.sns_client.publish(**kwargs)
            return SNSPublishResponse(
                message_id=resp.get("MessageId", ""),
                success=True
            )
        except Exception as e:
            return SNSPublishResponse(success=False, error=str(e))

    # ==================== EventBridge Rules ====================

    def get_eventbridge_rules(self) -> List[EventBridgeRule]:
        if not self.aws_connected:
            return []
        try:
            resp = self.events_client.list_rules()
            rules = []
            for r in resp.get("Rules", []):
                # Count targets
                targets_count = 0
                try:
                    targets = self.events_client.list_targets_by_rule(Rule=r["Name"])
                    targets_count = len(targets.get("Targets", []))
                except Exception:
                    pass

                rules.append(EventBridgeRule(
                    name=r["Name"],
                    description=r.get("Description", ""),
                    state=RuleState(r.get("State", "ENABLED")),
                    event_pattern=r.get("EventPattern"),
                    schedule_expression=r.get("ScheduleExpression"),
                    managed_by=r.get("ManagedBy", ""),
                    event_bus_name=r.get("EventBusName", "default"),
                    targets_count=targets_count
                ))
            return rules
        except Exception as e:
            logger.error(f"Error fetching EventBridge rules: {e}")
            return []

    # ==================== Dashboard ====================

    def get_dashboard(self) -> CloudWatchDashboardStats:
        alarms = self.get_alarms()
        topics = self.get_sns_topics()
        rules = self.get_eventbridge_rules()

        ok_count = sum(1 for a in alarms if a.state_value == AlarmState.OK)
        alarm_count = sum(1 for a in alarms if a.state_value == AlarmState.ALARM)
        insuf_count = sum(1 for a in alarms if a.state_value == AlarmState.INSUFFICIENT_DATA)
        enabled_rules = sum(1 for r in rules if r.state == RuleState.ENABLED)

        return CloudWatchDashboardStats(
            total_alarms=len(alarms),
            ok_alarms=ok_count,
            alarm_state=alarm_count,
            insufficient_data=insuf_count,
            total_sns_topics=len(topics),
            total_eventbridge_rules=len(rules),
            enabled_rules=enabled_rules,
            alarms=alarms,
            sns_topics=topics,
            eventbridge_rules=rules,
            account_id=self._account_id(),
            region=AWS_REGION,
            last_synced=datetime.now(timezone.utc).isoformat()
        )

    def check_health(self) -> CloudWatchHealthResponse:
        alarms = self.get_alarms() if self.aws_connected else []
        topics = self.get_sns_topics() if self.aws_connected else []
        rules = self.get_eventbridge_rules() if self.aws_connected else []

        return CloudWatchHealthResponse(
            status="healthy" if self.aws_connected else "degraded",
            aws_connected=self.aws_connected,
            account_id=self._account_id() if self.aws_connected else "",
            region=AWS_REGION,
            alarms_count=len(alarms),
            sns_topics_count=len(topics),
            eventbridge_rules_count=len(rules)
        )


def initialize_cloudwatch_service() -> Optional[CloudWatchMonitoringService]:
    global _cloudwatch_service
    try:
        _cloudwatch_service = CloudWatchMonitoringService()
        return _cloudwatch_service
    except Exception as e:
        logger.error(f"Failed to initialize CloudWatch monitoring: {e}")
        return None


def get_cloudwatch_service() -> Optional[CloudWatchMonitoringService]:
    return _cloudwatch_service
