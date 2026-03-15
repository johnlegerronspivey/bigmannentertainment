"""AWS Messaging routes - Kinesis, SNS, SQS, EventBridge."""
import logging
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from auth.service import get_current_user
from models.core import User

router = APIRouter(prefix="/aws-messaging", tags=["AWS Messaging & Events"])
logger = logging.getLogger(__name__)

_kinesis_svc = None
_sns_svc = None
_sqs_svc = None
_eventbridge_svc = None


def _kinesis():
    global _kinesis_svc
    if _kinesis_svc is None:
        from services.kinesis_service import KinesisService
        _kinesis_svc = KinesisService()
    return _kinesis_svc


def _sns():
    global _sns_svc
    if _sns_svc is None:
        from services.sns_service import SNSService
        _sns_svc = SNSService()
    return _sns_svc


def _sqs():
    global _sqs_svc
    if _sqs_svc is None:
        from services.sqs_service import SQSService
        _sqs_svc = SQSService()
    return _sqs_svc


def _eventbridge():
    global _eventbridge_svc
    if _eventbridge_svc is None:
        from services.eventbridge_service import EventBridgeService
        _eventbridge_svc = EventBridgeService()
    return _eventbridge_svc


# ── Pydantic models ──────────────────────────────────────────────
class PublishSNSRequest(BaseModel):
    topic_arn: str
    message: str
    subject: str = None


class SendSQSRequest(BaseModel):
    queue_url: str
    message_body: str
    delay_seconds: int = 0


# ══════════════════════════════════════════════════════════════════
#  STATUS
# ══════════════════════════════════════════════════════════════════
@router.get("/status")
async def messaging_status(current_user: User = Depends(get_current_user)):
    return {
        "kinesis": _kinesis().get_status(),
        "sns": _sns().get_status(),
        "sqs": _sqs().get_status(),
        "eventbridge": _eventbridge().get_status(),
    }


# ══════════════════════════════════════════════════════════════════
#  KINESIS
# ══════════════════════════════════════════════════════════════════
@router.get("/kinesis/streams")
async def list_kinesis_streams(current_user: User = Depends(get_current_user)):
    svc = _kinesis()
    if not svc.available:
        raise HTTPException(503, "Kinesis not available")
    try:
        streams = svc.list_streams()
        return {"streams": streams, "total": len(streams)}
    except Exception as e:
        logger.error(f"List streams error: {e}")
        raise HTTPException(500, f"Failed to list streams: {str(e)}")


@router.get("/kinesis/firehose")
async def list_firehose_streams(current_user: User = Depends(get_current_user)):
    svc = _kinesis()
    if not svc.available:
        raise HTTPException(503, "Kinesis not available")
    try:
        streams = svc.list_firehose_streams()
        return {"firehose_streams": streams, "total": len(streams)}
    except Exception as e:
        logger.error(f"List firehose error: {e}")
        raise HTTPException(500, f"Failed to list firehose streams: {str(e)}")


@router.get("/kinesis/streams/{stream_name}")
async def describe_stream(stream_name: str, current_user: User = Depends(get_current_user)):
    svc = _kinesis()
    if not svc.available:
        raise HTTPException(503, "Kinesis not available")
    try:
        return svc.describe_stream(stream_name)
    except Exception as e:
        logger.error(f"Describe stream error: {e}")
        raise HTTPException(500, f"Failed to describe stream: {str(e)}")


@router.get("/kinesis/streams/{stream_name}/metrics")
async def stream_metrics(stream_name: str, current_user: User = Depends(get_current_user)):
    svc = _kinesis()
    if not svc.available:
        raise HTTPException(503, "Kinesis not available")
    try:
        return svc.get_stream_metrics(stream_name)
    except Exception as e:
        logger.error(f"Stream metrics error: {e}")
        raise HTTPException(500, f"Failed to get metrics: {str(e)}")


# ══════════════════════════════════════════════════════════════════
#  SNS
# ══════════════════════════════════════════════════════════════════
@router.get("/sns/topics")
async def list_topics(current_user: User = Depends(get_current_user)):
    svc = _sns()
    if not svc.available:
        raise HTTPException(503, "SNS not available")
    try:
        topics = svc.list_topics()
        return {"topics": topics, "total": len(topics)}
    except Exception as e:
        logger.error(f"List topics error: {e}")
        raise HTTPException(500, f"Failed to list topics: {str(e)}")


@router.get("/sns/subscriptions")
async def list_subscriptions(
    topic_arn: str = Query(None),
    current_user: User = Depends(get_current_user),
):
    svc = _sns()
    if not svc.available:
        raise HTTPException(503, "SNS not available")
    try:
        subs = svc.list_subscriptions(topic_arn)
        return {"subscriptions": subs, "total": len(subs)}
    except Exception as e:
        logger.error(f"List subscriptions error: {e}")
        raise HTTPException(500, f"Failed to list subscriptions: {str(e)}")


@router.get("/sns/platform-applications")
async def list_platform_apps(current_user: User = Depends(get_current_user)):
    svc = _sns()
    if not svc.available:
        raise HTTPException(503, "SNS not available")
    try:
        apps = svc.list_platform_applications()
        return {"platform_applications": apps, "total": len(apps)}
    except Exception as e:
        logger.error(f"List platform apps error: {e}")
        raise HTTPException(500, f"Failed to list platform apps: {str(e)}")


@router.post("/sns/publish")
async def publish_message(body: PublishSNSRequest, current_user: User = Depends(get_current_user)):
    svc = _sns()
    if not svc.available:
        raise HTTPException(503, "SNS not available")
    try:
        return svc.publish_message(body.topic_arn, body.message, body.subject)
    except Exception as e:
        logger.error(f"Publish error: {e}")
        raise HTTPException(500, f"Failed to publish: {str(e)}")


# ══════════════════════════════════════════════════════════════════
#  SQS
# ══════════════════════════════════════════════════════════════════
@router.get("/sqs/queues")
async def list_queues(current_user: User = Depends(get_current_user)):
    svc = _sqs()
    if not svc.available:
        raise HTTPException(503, "SQS not available")
    try:
        queues = svc.list_queues()
        return {"queues": queues, "total": len(queues)}
    except Exception as e:
        logger.error(f"List queues error: {e}")
        raise HTTPException(500, f"Failed to list queues: {str(e)}")


@router.get("/sqs/queue-details")
async def get_queue_details(queue_url: str = Query(...), current_user: User = Depends(get_current_user)):
    svc = _sqs()
    if not svc.available:
        raise HTTPException(503, "SQS not available")
    try:
        return svc.get_queue_attributes(queue_url)
    except Exception as e:
        logger.error(f"Queue details error: {e}")
        raise HTTPException(500, f"Failed to get queue details: {str(e)}")


@router.post("/sqs/send")
async def send_message(body: SendSQSRequest, current_user: User = Depends(get_current_user)):
    svc = _sqs()
    if not svc.available:
        raise HTTPException(503, "SQS not available")
    try:
        return svc.send_message(body.queue_url, body.message_body, body.delay_seconds)
    except Exception as e:
        logger.error(f"Send message error: {e}")
        raise HTTPException(500, f"Failed to send message: {str(e)}")


@router.post("/sqs/purge")
async def purge_queue(queue_url: str = Query(...), current_user: User = Depends(get_current_user)):
    svc = _sqs()
    if not svc.available:
        raise HTTPException(503, "SQS not available")
    try:
        return svc.purge_queue(queue_url)
    except Exception as e:
        logger.error(f"Purge queue error: {e}")
        raise HTTPException(500, f"Failed to purge queue: {str(e)}")


# ══════════════════════════════════════════════════════════════════
#  EVENTBRIDGE
# ══════════════════════════════════════════════════════════════════
@router.get("/eventbridge/buses")
async def list_event_buses(current_user: User = Depends(get_current_user)):
    svc = _eventbridge()
    if not svc.available:
        raise HTTPException(503, "EventBridge not available")
    try:
        buses = svc.list_event_buses()
        return {"event_buses": buses, "total": len(buses)}
    except Exception as e:
        logger.error(f"List buses error: {e}")
        raise HTTPException(500, f"Failed to list buses: {str(e)}")


@router.get("/eventbridge/rules")
async def list_rules(
    event_bus_name: str = Query("default"),
    current_user: User = Depends(get_current_user),
):
    svc = _eventbridge()
    if not svc.available:
        raise HTTPException(503, "EventBridge not available")
    try:
        rules = svc.list_rules(event_bus_name)
        return {"rules": rules, "total": len(rules)}
    except Exception as e:
        logger.error(f"List rules error: {e}")
        raise HTTPException(500, f"Failed to list rules: {str(e)}")


@router.get("/eventbridge/rules/{rule_name}/targets")
async def list_targets(
    rule_name: str,
    event_bus_name: str = Query("default"),
    current_user: User = Depends(get_current_user),
):
    svc = _eventbridge()
    if not svc.available:
        raise HTTPException(503, "EventBridge not available")
    try:
        targets = svc.list_targets(rule_name, event_bus_name)
        return {"targets": targets, "total": len(targets)}
    except Exception as e:
        logger.error(f"List targets error: {e}")
        raise HTTPException(500, f"Failed to list targets: {str(e)}")


@router.get("/eventbridge/archives")
async def list_archives(current_user: User = Depends(get_current_user)):
    svc = _eventbridge()
    if not svc.available:
        raise HTTPException(503, "EventBridge not available")
    try:
        archives = svc.list_archives()
        return {"archives": archives, "total": len(archives)}
    except Exception as e:
        logger.error(f"List archives error: {e}")
        raise HTTPException(500, f"Failed to list archives: {str(e)}")


@router.get("/eventbridge/connections")
async def list_connections(current_user: User = Depends(get_current_user)):
    svc = _eventbridge()
    if not svc.available:
        raise HTTPException(503, "EventBridge not available")
    try:
        connections = svc.list_connections()
        return {"connections": connections, "total": len(connections)}
    except Exception as e:
        logger.error(f"List connections error: {e}")
        raise HTTPException(500, f"Failed to list connections: {str(e)}")


@router.get("/eventbridge/api-destinations")
async def list_api_destinations(current_user: User = Depends(get_current_user)):
    svc = _eventbridge()
    if not svc.available:
        raise HTTPException(503, "EventBridge not available")
    try:
        dests = svc.list_api_destinations()
        return {"api_destinations": dests, "total": len(dests)}
    except Exception as e:
        logger.error(f"List API destinations error: {e}")
        raise HTTPException(500, f"Failed to list API destinations: {str(e)}")
