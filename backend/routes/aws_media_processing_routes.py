"""AWS Media Processing routes - MediaConvert transcoding + Transcribe captions."""
import os
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from config.database import db
from auth.service import get_current_user
from models.core import User
from datetime import datetime, timezone

router = APIRouter(prefix="/aws-media", tags=["AWS Media Processing"])
logger = logging.getLogger(__name__)

# Lazy-init services to avoid import-time crashes
_mc_svc = None
_tr_svc = None


def _mediaconvert():
    global _mc_svc
    if _mc_svc is None:
        from services.mediaconvert_service import MediaConvertService
        _mc_svc = MediaConvertService()
    return _mc_svc


def _transcribe():
    global _tr_svc
    if _tr_svc is None:
        from services.transcribe_service import TranscribeService
        _tr_svc = TranscribeService()
    return _tr_svc


# ── Pydantic models ──────────────────────────────────────────────
class MediaConvertJobRequest(BaseModel):
    s3_input_key: str
    preset: str


class TranscribeJobRequest(BaseModel):
    s3_input_key: str
    language_code: str = "en-US"
    enable_subtitles: bool = True
    subtitle_formats: list = ["vtt", "srt"]
    identify_language: bool = False


# ── Status ────────────────────────────────────────────────────────
@router.get("/status")
async def media_processing_status(current_user: User = Depends(get_current_user)):
    """Overall status of MediaConvert + Transcribe."""
    mc = _mediaconvert()
    tr = _transcribe()

    mc_status = mc.get_endpoint_info() if mc.available else {"available": False}
    tr_status = tr.get_status()

    # Pull stats from MongoDB
    mc_jobs = await db.mediaconvert_jobs.count_documents({"user_id": current_user.id})
    tr_jobs = await db.transcribe_jobs.count_documents({"user_id": current_user.id})

    return {
        "mediaconvert": {**mc_status, "total_jobs": mc_jobs},
        "transcribe": {**tr_status, "total_jobs": tr_jobs},
    }


# ══════════════════════════════════════════════════════════════════
#  MEDIACONVERT
# ══════════════════════════════════════════════════════════════════
@router.get("/mediaconvert/presets")
async def list_presets(current_user: User = Depends(get_current_user)):
    """List available transcoding presets."""
    return {"presets": _mediaconvert().get_presets()}


@router.post("/mediaconvert/jobs")
async def submit_mediaconvert_job(
    body: MediaConvertJobRequest,
    current_user: User = Depends(get_current_user),
):
    """Submit a MediaConvert transcoding job."""
    mc = _mediaconvert()
    if not mc.available:
        raise HTTPException(503, "MediaConvert not available")
    try:
        result = mc.submit_job(body.s3_input_key, body.preset, current_user.id)
        # Save to Mongo for history
        doc = {
            **result,
            "user_id": current_user.id,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        await db.mediaconvert_jobs.insert_one(doc)
        doc.pop("_id", None)
        return result
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        logger.error(f"MediaConvert job submit error: {e}")
        raise HTTPException(500, f"Failed to submit job: {str(e)}")


@router.get("/mediaconvert/jobs")
async def list_mediaconvert_jobs(
    status: Optional[str] = Query(None, description="SUBMITTED | PROGRESSING | COMPLETE | ERROR | CANCELED"),
    current_user: User = Depends(get_current_user),
):
    """List MediaConvert jobs from AWS."""
    mc = _mediaconvert()
    if not mc.available:
        raise HTTPException(503, "MediaConvert not available")
    try:
        # Try AWS list, filter by user
        all_jobs = mc.list_jobs(status=status or "SUBMITTED", max_results=50)
        user_jobs = [j for j in all_jobs if j.get("user_metadata", {}).get("user_id") == current_user.id]
        return {"jobs": user_jobs, "total": len(user_jobs)}
    except Exception as e:
        logger.error(f"List MC jobs error: {e}")
        # Fall back to Mongo records
        query = {"user_id": current_user.id}
        if status:
            query["status"] = status
        docs = await db.mediaconvert_jobs.find(query, {"_id": 0}).sort("created_at", -1).to_list(50)
        return {"jobs": docs, "total": len(docs), "source": "cache"}


@router.get("/mediaconvert/jobs/{job_id}")
async def get_mediaconvert_job(job_id: str, current_user: User = Depends(get_current_user)):
    """Get status of a specific MediaConvert job."""
    mc = _mediaconvert()
    if not mc.available:
        raise HTTPException(503, "MediaConvert not available")
    try:
        result = mc.get_job(job_id)
        # Update Mongo cache
        await db.mediaconvert_jobs.update_one(
            {"job_id": job_id},
            {"$set": {"status": result["status"], "progress": result.get("progress", 0)}},
        )
        return result
    except Exception as e:
        raise HTTPException(404, f"Job not found: {str(e)}")


# ══════════════════════════════════════════════════════════════════
#  TRANSCRIBE
# ══════════════════════════════════════════════════════════════════
@router.get("/transcribe/languages")
async def list_languages(current_user: User = Depends(get_current_user)):
    """List supported transcription languages."""
    return {"languages": _transcribe().get_languages()}


@router.post("/transcribe/jobs")
async def submit_transcribe_job(
    body: TranscribeJobRequest,
    current_user: User = Depends(get_current_user),
):
    """Start a transcription / subtitle generation job."""
    tr = _transcribe()
    if not tr.available:
        raise HTTPException(503, "Transcribe service not available")
    try:
        result = tr.start_transcription(
            s3_input_key=body.s3_input_key,
            user_id=current_user.id,
            language_code=body.language_code,
            enable_subtitles=body.enable_subtitles,
            subtitle_formats=body.subtitle_formats,
            identify_language=body.identify_language,
        )
        doc = {**result, "user_id": current_user.id}
        await db.transcribe_jobs.insert_one(doc)
        doc.pop("_id", None)
        return result
    except Exception as e:
        logger.error(f"Transcribe job submit error: {e}")
        raise HTTPException(500, f"Failed to start transcription: {str(e)}")


@router.get("/transcribe/jobs")
async def list_transcribe_jobs(
    status: Optional[str] = Query(None, description="IN_PROGRESS | COMPLETED | FAILED"),
    current_user: User = Depends(get_current_user),
):
    """List transcription jobs."""
    tr = _transcribe()
    if not tr.available:
        raise HTTPException(503, "Transcribe service not available")
    try:
        all_jobs = tr.list_jobs(status=status, max_results=50)
        return {"jobs": all_jobs, "total": len(all_jobs)}
    except Exception as e:
        logger.error(f"List transcribe jobs error: {e}")
        docs = await db.transcribe_jobs.find({"user_id": current_user.id}, {"_id": 0}).sort("created_at", -1).to_list(50)
        return {"jobs": docs, "total": len(docs), "source": "cache"}


@router.get("/transcribe/jobs/{job_name}")
async def get_transcribe_job(job_name: str, current_user: User = Depends(get_current_user)):
    """Get transcription result including text and subtitle files."""
    tr = _transcribe()
    if not tr.available:
        raise HTTPException(503, "Transcribe service not available")
    try:
        result = tr.get_job(job_name)
        # Update Mongo cache
        await db.transcribe_jobs.update_one(
            {"job_name": job_name},
            {"$set": {"status": result["status"]}},
        )
        return result
    except Exception as e:
        raise HTTPException(404, f"Transcription job not found: {str(e)}")


@router.delete("/transcribe/jobs/{job_name}")
async def delete_transcribe_job(job_name: str, current_user: User = Depends(get_current_user)):
    """Delete a transcription job."""
    tr = _transcribe()
    if not tr.available:
        raise HTTPException(503, "Transcribe service not available")
    success = tr.delete_job(job_name)
    if success:
        await db.transcribe_jobs.delete_one({"job_name": job_name})
        return {"deleted": True}
    raise HTTPException(500, "Failed to delete job")
