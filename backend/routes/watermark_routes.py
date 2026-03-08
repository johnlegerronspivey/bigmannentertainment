"""
Content Watermarking - Apply text/image watermarks to media assets
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
from config.database import db
from auth.service import get_current_user
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import math

router = APIRouter(prefix="/watermark", tags=["Content Watermarking"])


class WatermarkSettings(BaseModel):
    text: Optional[str] = None
    position: str = "center"  # center, top-left, top-right, bottom-left, bottom-right, tiled
    opacity: float = 0.3
    font_size: int = 36
    color: str = "#FFFFFF"
    rotation: int = -30
    enabled: bool = True


def serialize_settings(doc):
    if not doc:
        return None
    doc["id"] = str(doc.pop("_id"))
    for k in ["created_at", "updated_at"]:
        if k in doc and isinstance(doc[k], datetime):
            doc[k] = doc[k].isoformat()
    return doc


def hex_to_rgba(hex_color: str, opacity: float):
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return (r, g, b, int(opacity * 255))


def apply_watermark(image: Image.Image, settings: dict) -> Image.Image:
    """Apply watermark to a PIL Image"""
    text = settings.get("text", "WATERMARK")
    position = settings.get("position", "center")
    opacity = settings.get("opacity", 0.3)
    font_size = settings.get("font_size", 36)
    color = settings.get("color", "#FFFFFF")
    rotation = settings.get("rotation", -30)

    if image.mode != "RGBA":
        image = image.convert("RGBA")

    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except (OSError, IOError):
        font = ImageFont.load_default()

    rgba = hex_to_rgba(color, opacity)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    iw, ih = image.size

    if position == "tiled":
        # Create tiled watermark
        step_x = tw + 100
        step_y = th + 80
        txt_img = Image.new("RGBA", (tw + 20, th + 20), (0, 0, 0, 0))
        txt_draw = ImageDraw.Draw(txt_img)
        txt_draw.text((10, 10), text, font=font, fill=rgba)
        txt_img = txt_img.rotate(rotation, expand=True, resample=Image.BICUBIC)

        for x in range(-txt_img.width, iw + txt_img.width, step_x):
            for y in range(-txt_img.height, ih + txt_img.height, step_y):
                overlay.paste(txt_img, (x, y), txt_img)
    else:
        positions = {
            "center": ((iw - tw) // 2, (ih - th) // 2),
            "top-left": (20, 20),
            "top-right": (iw - tw - 20, 20),
            "bottom-left": (20, ih - th - 20),
            "bottom-right": (iw - tw - 20, ih - th - 20),
        }
        pos = positions.get(position, positions["center"])

        txt_img = Image.new("RGBA", (tw + 20, th + 20), (0, 0, 0, 0))
        txt_draw = ImageDraw.Draw(txt_img)
        txt_draw.text((10, 10), text, font=font, fill=rgba)
        if rotation != 0:
            txt_img = txt_img.rotate(rotation, expand=True, resample=Image.BICUBIC)
        overlay.paste(txt_img, pos, txt_img)

    return Image.alpha_composite(image, overlay)


@router.get("/settings")
async def get_watermark_settings(current_user=Depends(get_current_user)):
    user_id = current_user.get("id") if isinstance(current_user, dict) else current_user.id
    settings = await db.watermark_settings.find_one({"user_id": user_id})
    if not settings:
        return {
            "text": "BIG MANN ENTERTAINMENT",
            "position": "center",
            "opacity": 0.3,
            "font_size": 36,
            "color": "#FFFFFF",
            "rotation": -30,
            "enabled": True,
        }
    return serialize_settings(settings)


@router.put("/settings")
async def update_watermark_settings(data: WatermarkSettings, current_user=Depends(get_current_user)):
    user_id = current_user.get("id") if isinstance(current_user, dict) else current_user.id
    update_data = data.dict()
    update_data["user_id"] = user_id
    update_data["updated_at"] = datetime.now(timezone.utc)

    await db.watermark_settings.update_one(
        {"user_id": user_id},
        {"$set": update_data, "$setOnInsert": {"created_at": datetime.now(timezone.utc)}},
        upsert=True,
    )
    return {"status": "success", "settings": update_data}


@router.post("/preview")
async def preview_watermark(
    file: UploadFile = File(...),
    text: str = Form("BIG MANN ENTERTAINMENT"),
    position: str = Form("center"),
    opacity: float = Form(0.3),
    font_size: int = Form(36),
    color: str = Form("#FFFFFF"),
    rotation: int = Form(-30),
    current_user=Depends(get_current_user),
):
    """Upload an image and return a watermarked preview"""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are supported")

    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 10MB)")

    image = Image.open(io.BytesIO(contents))
    settings = {
        "text": text,
        "position": position,
        "opacity": opacity,
        "font_size": font_size,
        "color": color,
        "rotation": rotation,
    }
    watermarked = apply_watermark(image, settings)

    buf = io.BytesIO()
    watermarked.save(buf, format="PNG")
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/png")


@router.post("/apply")
async def apply_watermark_to_asset(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
):
    """Apply saved watermark settings to an uploaded image, return base64"""
    user_id = current_user.get("id") if isinstance(current_user, dict) else current_user.id

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are supported")

    contents = await file.read()
    image = Image.open(io.BytesIO(contents))

    settings_doc = await db.watermark_settings.find_one({"user_id": user_id})
    settings = {
        "text": settings_doc.get("text", "BIG MANN ENTERTAINMENT") if settings_doc else "BIG MANN ENTERTAINMENT",
        "position": settings_doc.get("position", "center") if settings_doc else "center",
        "opacity": settings_doc.get("opacity", 0.3) if settings_doc else 0.3,
        "font_size": settings_doc.get("font_size", 36) if settings_doc else 36,
        "color": settings_doc.get("color", "#FFFFFF") if settings_doc else "#FFFFFF",
        "rotation": settings_doc.get("rotation", -30) if settings_doc else -30,
    }

    watermarked = apply_watermark(image, settings)

    buf = io.BytesIO()
    watermarked.save(buf, format="PNG")
    buf.seek(0)
    b64 = base64.b64encode(buf.getvalue()).decode()

    return {
        "status": "success",
        "filename": file.filename,
        "watermarked_image": f"data:image/png;base64,{b64}",
        "settings_applied": settings,
    }
