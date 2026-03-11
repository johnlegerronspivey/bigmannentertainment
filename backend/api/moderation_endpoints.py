from fastapi import APIRouter, UploadFile, File, Body, HTTPException
from pydantic import BaseModel
from moderation_service import moderation_service
import shutil
import os
import uuid
from typing import Optional

router = APIRouter(prefix="/moderation", tags=["Content Moderation"])

class TextModerationRequest(BaseModel):
    text: str

@router.post("/text")
async def moderate_text(request: TextModerationRequest):
    result = await moderation_service.moderate_text(request.text)
    return result

@router.post("/image")
async def moderate_image(file: UploadFile = File(...)):
    # Save file temporarily
    temp_filename = f"temp_{uuid.uuid4()}_{file.filename}"
    temp_path = f"/tmp/{temp_filename}"
    
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        mime_type = file.content_type or "image/jpeg"
        
        result = await moderation_service.moderate_image(image_path=temp_path, mime_type=mime_type)
        return result
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
