"""AWS Comprehend & Personalize routes - AI-powered content analytics."""
import logging
from typing import List
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from config.database import db
from auth.service import get_current_user
from models.core import User
from datetime import datetime, timezone

router = APIRouter(prefix="/aws-ai", tags=["AWS AI Analytics"])
logger = logging.getLogger(__name__)

_comprehend_svc = None
_personalize_svc = None


def _comprehend():
    global _comprehend_svc
    if _comprehend_svc is None:
        from services.comprehend_service import ComprehendService
        _comprehend_svc = ComprehendService()
    return _comprehend_svc


def _personalize():
    global _personalize_svc
    if _personalize_svc is None:
        from services.personalize_service import PersonalizeService
        _personalize_svc = PersonalizeService()
    return _personalize_svc


# ── Pydantic models ──────────────────────────────────────────────
class AnalyzeTextRequest(BaseModel):
    text: str
    language: str = "en"


class BatchSentimentRequest(BaseModel):
    texts: List[str]
    language: str = "en"


class GetRecommendationsRequest(BaseModel):
    campaign_arn: str
    user_id: str
    num_results: int = 10


# ══════════════════════════════════════════════════════════════════
#  STATUS
# ══════════════════════════════════════════════════════════════════
@router.get("/status")
async def ai_status(current_user: User = Depends(get_current_user)):
    """Overall status of Comprehend + Personalize."""
    c = _comprehend()
    p = _personalize()
    return {
        "comprehend": c.get_status(),
        "personalize": p.get_status(),
    }


# ══════════════════════════════════════════════════════════════════
#  COMPREHEND - Sentiment Analysis
# ══════════════════════════════════════════════════════════════════
@router.post("/comprehend/sentiment")
async def detect_sentiment(
    body: AnalyzeTextRequest,
    current_user: User = Depends(get_current_user),
):
    """Detect sentiment of text."""
    c = _comprehend()
    if not c.available:
        raise HTTPException(503, "Comprehend not available")
    try:
        result = c.detect_sentiment(body.text, body.language)
        doc = {
            "user_id": current_user.id,
            "type": "sentiment",
            "input_text": body.text[:200],
            "result": result,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        await db.comprehend_analyses.insert_one(doc)
        return result
    except Exception as e:
        logger.error(f"Sentiment detection error: {e}")
        raise HTTPException(500, f"Sentiment detection failed: {str(e)}")


@router.post("/comprehend/entities")
async def detect_entities(
    body: AnalyzeTextRequest,
    current_user: User = Depends(get_current_user),
):
    """Detect named entities in text."""
    c = _comprehend()
    if not c.available:
        raise HTTPException(503, "Comprehend not available")
    try:
        entities = c.detect_entities(body.text, body.language)
        return {"entities": entities, "total": len(entities)}
    except Exception as e:
        logger.error(f"Entity detection error: {e}")
        raise HTTPException(500, f"Entity detection failed: {str(e)}")


@router.post("/comprehend/key-phrases")
async def detect_key_phrases(
    body: AnalyzeTextRequest,
    current_user: User = Depends(get_current_user),
):
    """Extract key phrases from text."""
    c = _comprehend()
    if not c.available:
        raise HTTPException(503, "Comprehend not available")
    try:
        phrases = c.detect_key_phrases(body.text, body.language)
        return {"key_phrases": phrases, "total": len(phrases)}
    except Exception as e:
        logger.error(f"Key phrase detection error: {e}")
        raise HTTPException(500, f"Key phrase detection failed: {str(e)}")


@router.post("/comprehend/language")
async def detect_language(
    body: AnalyzeTextRequest,
    current_user: User = Depends(get_current_user),
):
    """Detect dominant language of text."""
    c = _comprehend()
    if not c.available:
        raise HTTPException(503, "Comprehend not available")
    try:
        languages = c.detect_language(body.text)
        return {"languages": languages, "total": len(languages)}
    except Exception as e:
        logger.error(f"Language detection error: {e}")
        raise HTTPException(500, f"Language detection failed: {str(e)}")


@router.post("/comprehend/pii")
async def detect_pii(
    body: AnalyzeTextRequest,
    current_user: User = Depends(get_current_user),
):
    """Detect PII entities in text."""
    c = _comprehend()
    if not c.available:
        raise HTTPException(503, "Comprehend not available")
    try:
        pii = c.detect_pii(body.text, body.language)
        return {"pii_entities": pii, "total": len(pii)}
    except Exception as e:
        logger.error(f"PII detection error: {e}")
        raise HTTPException(500, f"PII detection failed: {str(e)}")


@router.post("/comprehend/syntax")
async def detect_syntax(
    body: AnalyzeTextRequest,
    current_user: User = Depends(get_current_user),
):
    """Analyze syntax and part-of-speech tags."""
    c = _comprehend()
    if not c.available:
        raise HTTPException(503, "Comprehend not available")
    try:
        tokens = c.detect_syntax(body.text, body.language)
        return {"tokens": tokens, "total": len(tokens)}
    except Exception as e:
        logger.error(f"Syntax detection error: {e}")
        raise HTTPException(500, f"Syntax detection failed: {str(e)}")


@router.post("/comprehend/batch-sentiment")
async def batch_sentiment(
    body: BatchSentimentRequest,
    current_user: User = Depends(get_current_user),
):
    """Batch sentiment analysis on multiple texts (max 25)."""
    c = _comprehend()
    if not c.available:
        raise HTTPException(503, "Comprehend not available")
    if len(body.texts) > 25:
        raise HTTPException(400, "Maximum 25 texts per batch")
    try:
        results = c.batch_detect_sentiment(body.texts, body.language)
        return {"results": results, "total": len(results)}
    except Exception as e:
        logger.error(f"Batch sentiment error: {e}")
        raise HTTPException(500, f"Batch sentiment failed: {str(e)}")


@router.get("/comprehend/endpoints")
async def list_endpoints(current_user: User = Depends(get_current_user)):
    """List Comprehend custom endpoints."""
    c = _comprehend()
    if not c.available:
        raise HTTPException(503, "Comprehend not available")
    try:
        endpoints = c.list_endpoints()
        return {"endpoints": endpoints, "total": len(endpoints)}
    except Exception as e:
        logger.error(f"List endpoints error: {e}")
        raise HTTPException(500, f"Failed to list endpoints: {str(e)}")


@router.get("/comprehend/history")
async def analysis_history(
    limit: int = Query(20, le=100),
    current_user: User = Depends(get_current_user),
):
    """Get recent analysis history."""
    docs = await db.comprehend_analyses.find(
        {"user_id": current_user.id}, {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    return {"history": docs, "total": len(docs)}


# ══════════════════════════════════════════════════════════════════
#  PERSONALIZE - Recommendations
# ══════════════════════════════════════════════════════════════════
@router.get("/personalize/dataset-groups")
async def list_dataset_groups(current_user: User = Depends(get_current_user)):
    """List Personalize dataset groups."""
    p = _personalize()
    if not p.available:
        raise HTTPException(503, "Personalize not available")
    try:
        groups = p.list_dataset_groups()
        return {"dataset_groups": groups, "total": len(groups)}
    except Exception as e:
        logger.error(f"List dataset groups error: {e}")
        raise HTTPException(500, f"Failed to list dataset groups: {str(e)}")


@router.get("/personalize/campaigns")
async def list_campaigns(current_user: User = Depends(get_current_user)):
    """List Personalize campaigns."""
    p = _personalize()
    if not p.available:
        raise HTTPException(503, "Personalize not available")
    try:
        campaigns = p.list_campaigns()
        return {"campaigns": campaigns, "total": len(campaigns)}
    except Exception as e:
        logger.error(f"List campaigns error: {e}")
        raise HTTPException(500, f"Failed to list campaigns: {str(e)}")


@router.get("/personalize/solutions")
async def list_solutions(current_user: User = Depends(get_current_user)):
    """List Personalize solutions."""
    p = _personalize()
    if not p.available:
        raise HTTPException(503, "Personalize not available")
    try:
        solutions = p.list_solutions()
        return {"solutions": solutions, "total": len(solutions)}
    except Exception as e:
        logger.error(f"List solutions error: {e}")
        raise HTTPException(500, f"Failed to list solutions: {str(e)}")


@router.get("/personalize/recipes")
async def list_recipes(current_user: User = Depends(get_current_user)):
    """List available Personalize recipes."""
    p = _personalize()
    if not p.available:
        raise HTTPException(503, "Personalize not available")
    try:
        recipes = p.list_recipes()
        return {"recipes": recipes, "total": len(recipes)}
    except Exception as e:
        logger.error(f"List recipes error: {e}")
        raise HTTPException(500, f"Failed to list recipes: {str(e)}")


@router.post("/personalize/recommendations")
async def get_recommendations(
    body: GetRecommendationsRequest,
    current_user: User = Depends(get_current_user),
):
    """Get personalized recommendations from a campaign."""
    p = _personalize()
    if not p.available:
        raise HTTPException(503, "Personalize not available")
    try:
        recs = p.get_recommendations(body.campaign_arn, body.user_id, body.num_results)
        return {"recommendations": recs, "total": len(recs)}
    except Exception as e:
        logger.error(f"Get recommendations error: {e}")
        raise HTTPException(500, f"Failed to get recommendations: {str(e)}")


@router.get("/personalize/datasets")
async def list_datasets(
    dataset_group_arn: str = Query(None),
    current_user: User = Depends(get_current_user),
):
    """List Personalize datasets."""
    p = _personalize()
    if not p.available:
        raise HTTPException(503, "Personalize not available")
    try:
        datasets = p.list_datasets(dataset_group_arn)
        return {"datasets": datasets, "total": len(datasets)}
    except Exception as e:
        logger.error(f"List datasets error: {e}")
        raise HTTPException(500, f"Failed to list datasets: {str(e)}")


@router.get("/personalize/event-trackers")
async def list_event_trackers(
    dataset_group_arn: str = Query(None),
    current_user: User = Depends(get_current_user),
):
    """List Personalize event trackers."""
    p = _personalize()
    if not p.available:
        raise HTTPException(503, "Personalize not available")
    try:
        trackers = p.list_event_trackers(dataset_group_arn)
        return {"event_trackers": trackers, "total": len(trackers)}
    except Exception as e:
        logger.error(f"List event trackers error: {e}")
        raise HTTPException(500, f"Failed to list event trackers: {str(e)}")
