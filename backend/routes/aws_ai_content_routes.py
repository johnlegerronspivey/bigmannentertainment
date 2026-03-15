"""AWS AI Content routes - Translate, Polly, Textract, SageMaker."""
import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from auth.service import get_current_user
from models.core import User

router = APIRouter(prefix="/aws-ai-content", tags=["AWS AI Content"])
logger = logging.getLogger(__name__)

_translate_svc = None
_polly_svc = None
_textract_svc = None
_sagemaker_svc = None


def _translate():
    global _translate_svc
    if _translate_svc is None:
        from services.translate_service import TranslateService
        _translate_svc = TranslateService()
    return _translate_svc


def _polly():
    global _polly_svc
    if _polly_svc is None:
        from services.polly_service import PollyService
        _polly_svc = PollyService()
    return _polly_svc


def _textract():
    global _textract_svc
    if _textract_svc is None:
        from services.textract_service import TextractService
        _textract_svc = TextractService()
    return _textract_svc


def _sagemaker():
    global _sagemaker_svc
    if _sagemaker_svc is None:
        from services.sagemaker_service import SageMakerService
        _sagemaker_svc = SageMakerService()
    return _sagemaker_svc


# ── Pydantic models ──────────────────────────────────────────────
class TranslateTextRequest(BaseModel):
    text: str
    source_language: str = "auto"
    target_language: str = "es"


class SynthesizeSpeechRequest(BaseModel):
    text: str
    voice_id: str = "Joanna"
    output_format: str = "mp3"
    engine: str = "neural"


class AnalyzeDocumentRequest(BaseModel):
    bucket: str
    key: str
    feature_types: Optional[List[str]] = None


# ══════════════════════════════════════════════════════════════════
#  STATUS
# ══════════════════════════════════════════════════════════════════
@router.get("/status")
async def ai_content_status(current_user: User = Depends(get_current_user)):
    return {
        "translate": _translate().get_status(),
        "polly": _polly().get_status(),
        "textract": _textract().get_status(),
        "sagemaker": _sagemaker().get_status(),
    }


# ══════════════════════════════════════════════════════════════════
#  TRANSLATE
# ══════════════════════════════════════════════════════════════════
@router.post("/translate/text")
async def translate_text(body: TranslateTextRequest, current_user: User = Depends(get_current_user)):
    svc = _translate()
    if not svc.available:
        raise HTTPException(503, "Translate not available")
    try:
        return svc.translate_text(body.text, body.source_language, body.target_language)
    except Exception as e:
        logger.error(f"Translate error: {e}")
        raise HTTPException(500, f"Translation failed: {str(e)}")


@router.get("/translate/languages")
async def list_languages(current_user: User = Depends(get_current_user)):
    svc = _translate()
    if not svc.available:
        raise HTTPException(503, "Translate not available")
    try:
        langs = svc.list_languages()
        return {"languages": langs, "total": len(langs)}
    except Exception as e:
        logger.error(f"List languages error: {e}")
        raise HTTPException(500, f"Failed to list languages: {str(e)}")


@router.get("/translate/terminologies")
async def list_terminologies(current_user: User = Depends(get_current_user)):
    svc = _translate()
    if not svc.available:
        raise HTTPException(503, "Translate not available")
    try:
        terms = svc.list_terminologies()
        return {"terminologies": terms, "total": len(terms)}
    except Exception as e:
        logger.error(f"List terminologies error: {e}")
        raise HTTPException(500, f"Failed to list terminologies: {str(e)}")


@router.get("/translate/parallel-data")
async def list_parallel_data(current_user: User = Depends(get_current_user)):
    svc = _translate()
    if not svc.available:
        raise HTTPException(503, "Translate not available")
    try:
        data = svc.list_parallel_data()
        return {"parallel_data": data, "total": len(data)}
    except Exception as e:
        logger.error(f"List parallel data error: {e}")
        raise HTTPException(500, f"Failed to list parallel data: {str(e)}")


# ══════════════════════════════════════════════════════════════════
#  POLLY
# ══════════════════════════════════════════════════════════════════
@router.get("/polly/voices")
async def list_voices(
    language_code: str = Query(None),
    engine: str = Query(None),
    current_user: User = Depends(get_current_user),
):
    svc = _polly()
    if not svc.available:
        raise HTTPException(503, "Polly not available")
    try:
        voices = svc.list_voices(language_code, engine)
        return {"voices": voices, "total": len(voices)}
    except Exception as e:
        logger.error(f"List voices error: {e}")
        raise HTTPException(500, f"Failed to list voices: {str(e)}")


@router.post("/polly/synthesize")
async def synthesize_speech(body: SynthesizeSpeechRequest, current_user: User = Depends(get_current_user)):
    svc = _polly()
    if not svc.available:
        raise HTTPException(503, "Polly not available")
    try:
        return svc.synthesize_speech(body.text, body.voice_id, body.output_format, body.engine)
    except Exception as e:
        logger.error(f"Synthesize error: {e}")
        raise HTTPException(500, f"Speech synthesis failed: {str(e)}")


@router.get("/polly/lexicons")
async def list_lexicons(current_user: User = Depends(get_current_user)):
    svc = _polly()
    if not svc.available:
        raise HTTPException(503, "Polly not available")
    try:
        lexicons = svc.list_lexicons()
        return {"lexicons": lexicons, "total": len(lexicons)}
    except Exception as e:
        logger.error(f"List lexicons error: {e}")
        raise HTTPException(500, f"Failed to list lexicons: {str(e)}")


@router.get("/polly/tasks")
async def list_speech_tasks(current_user: User = Depends(get_current_user)):
    svc = _polly()
    if not svc.available:
        raise HTTPException(503, "Polly not available")
    try:
        tasks = svc.list_speech_synthesis_tasks()
        return {"tasks": tasks, "total": len(tasks)}
    except Exception as e:
        logger.error(f"List tasks error: {e}")
        raise HTTPException(500, f"Failed to list tasks: {str(e)}")


# ══════════════════════════════════════════════════════════════════
#  TEXTRACT
# ══════════════════════════════════════════════════════════════════
@router.post("/textract/analyze")
async def analyze_document(body: AnalyzeDocumentRequest, current_user: User = Depends(get_current_user)):
    svc = _textract()
    if not svc.available:
        raise HTTPException(503, "Textract not available")
    try:
        return svc.analyze_s3_document(body.bucket, body.key, body.feature_types)
    except Exception as e:
        logger.error(f"Analyze document error: {e}")
        raise HTTPException(500, f"Document analysis failed: {str(e)}")


@router.post("/textract/detect-text")
async def detect_text(body: AnalyzeDocumentRequest, current_user: User = Depends(get_current_user)):
    svc = _textract()
    if not svc.available:
        raise HTTPException(503, "Textract not available")
    try:
        return svc.detect_s3_text(body.bucket, body.key)
    except Exception as e:
        logger.error(f"Detect text error: {e}")
        raise HTTPException(500, f"Text detection failed: {str(e)}")


@router.post("/textract/start-analysis")
async def start_analysis(body: AnalyzeDocumentRequest, current_user: User = Depends(get_current_user)):
    svc = _textract()
    if not svc.available:
        raise HTTPException(503, "Textract not available")
    try:
        return svc.start_document_analysis(body.bucket, body.key, body.feature_types)
    except Exception as e:
        logger.error(f"Start analysis error: {e}")
        raise HTTPException(500, f"Failed to start analysis: {str(e)}")


@router.get("/textract/analysis/{job_id}")
async def get_analysis_result(job_id: str, current_user: User = Depends(get_current_user)):
    svc = _textract()
    if not svc.available:
        raise HTTPException(503, "Textract not available")
    try:
        return svc.get_document_analysis(job_id)
    except Exception as e:
        logger.error(f"Get analysis error: {e}")
        raise HTTPException(500, f"Failed to get analysis: {str(e)}")


@router.get("/textract/adapters")
async def list_adapters(current_user: User = Depends(get_current_user)):
    svc = _textract()
    if not svc.available:
        raise HTTPException(503, "Textract not available")
    try:
        adapters = svc.list_adapters()
        return {"adapters": adapters, "total": len(adapters)}
    except Exception as e:
        logger.error(f"List adapters error: {e}")
        raise HTTPException(500, f"Failed to list adapters: {str(e)}")


# ══════════════════════════════════════════════════════════════════
#  SAGEMAKER
# ══════════════════════════════════════════════════════════════════
@router.get("/sagemaker/notebooks")
async def list_notebooks(current_user: User = Depends(get_current_user)):
    svc = _sagemaker()
    if not svc.available:
        raise HTTPException(503, "SageMaker not available")
    try:
        nbs = svc.list_notebook_instances()
        return {"notebooks": nbs, "total": len(nbs)}
    except Exception as e:
        logger.error(f"List notebooks error: {e}")
        raise HTTPException(500, f"Failed to list notebooks: {str(e)}")


@router.get("/sagemaker/training-jobs")
async def list_training_jobs(current_user: User = Depends(get_current_user)):
    svc = _sagemaker()
    if not svc.available:
        raise HTTPException(503, "SageMaker not available")
    try:
        jobs = svc.list_training_jobs()
        return {"training_jobs": jobs, "total": len(jobs)}
    except Exception as e:
        logger.error(f"List training jobs error: {e}")
        raise HTTPException(500, f"Failed to list training jobs: {str(e)}")


@router.get("/sagemaker/models")
async def list_models(current_user: User = Depends(get_current_user)):
    svc = _sagemaker()
    if not svc.available:
        raise HTTPException(503, "SageMaker not available")
    try:
        models = svc.list_models()
        return {"models": models, "total": len(models)}
    except Exception as e:
        logger.error(f"List models error: {e}")
        raise HTTPException(500, f"Failed to list models: {str(e)}")


@router.get("/sagemaker/endpoints")
async def list_endpoints(current_user: User = Depends(get_current_user)):
    svc = _sagemaker()
    if not svc.available:
        raise HTTPException(503, "SageMaker not available")
    try:
        endpoints = svc.list_endpoints()
        return {"endpoints": endpoints, "total": len(endpoints)}
    except Exception as e:
        logger.error(f"List endpoints error: {e}")
        raise HTTPException(500, f"Failed to list endpoints: {str(e)}")


@router.get("/sagemaker/processing-jobs")
async def list_processing_jobs(current_user: User = Depends(get_current_user)):
    svc = _sagemaker()
    if not svc.available:
        raise HTTPException(503, "SageMaker not available")
    try:
        jobs = svc.list_processing_jobs()
        return {"processing_jobs": jobs, "total": len(jobs)}
    except Exception as e:
        logger.error(f"List processing jobs error: {e}")
        raise HTTPException(500, f"Failed to list processing jobs: {str(e)}")


@router.get("/sagemaker/feature-groups")
async def list_feature_groups(current_user: User = Depends(get_current_user)):
    svc = _sagemaker()
    if not svc.available:
        raise HTTPException(503, "SageMaker not available")
    try:
        groups = svc.list_feature_groups()
        return {"feature_groups": groups, "total": len(groups)}
    except Exception as e:
        logger.error(f"List feature groups error: {e}")
        raise HTTPException(500, f"Failed to list feature groups: {str(e)}")
