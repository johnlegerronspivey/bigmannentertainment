import os
import asyncio
from llm_service import LlmChat, UserMessage, ImageContent, FileContentWithMimeType
from dotenv import load_dotenv

load_dotenv()

class ModerationService:
    def __init__(self):
        # Changed to use GOOGLE_API_KEY as requested by user
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            print("⚠️ GOOGLE_API_KEY not found in environment variables")
        
    async def moderate_text(self, text: str) -> dict:
        if not self.api_key:
            return {"error": "API key not configured", "safe": False}
            
        chat = LlmChat(
            api_key=self.api_key,
            session_id=f"mod-text-{hash(text)}",
            system_message="You are a content moderation AI. Analyze the text for hate speech, violence, self-harm, sexual content, and harassment. Return a JSON response with keys: 'safe' (boolean), 'categories' (list of strings), 'reason' (string), and 'confidence' (float 0-1). Ensure valid JSON."
        ).with_model("gemini", "gemini-2.5-flash")
        
        try:
            user_msg = UserMessage(text=f"Analyze this text for moderation: {text}")
            response = await chat.send_message(user_msg)
            return {"result": response, "status": "processed"}
        except Exception as e:
            print(f"Moderation error: {e}")
            return {"error": str(e), "safe": False}

    async def moderate_image(self, image_path: str = None, mime_type: str = "image/jpeg", image_base64: str = None) -> dict:
        if not self.api_key:
            return {"error": "API key not configured", "safe": False}
            
        chat = LlmChat(
            api_key=self.api_key,
            session_id="mod-image",
            system_message="You are a content moderation AI. Analyze the image for nudity, violence, self-harm, and hate symbols. Return a JSON response with keys: 'safe' (boolean), 'categories' (list of strings), 'reason' (string). Ensure valid JSON."
        ).with_model("gemini", "gemini-2.5-flash")
        
        try:
            content = []
            if image_path:
                content.append(FileContentWithMimeType(file_path=image_path, mime_type=mime_type))
            elif image_base64:
                content.append(ImageContent(image_base64=image_base64))
            
            user_msg = UserMessage(
                text="Analyze this image for moderation.",
                file_contents=content
            )
            response = await chat.send_message(user_msg)
            return {"result": response, "status": "processed"}
        except Exception as e:
            print(f"Moderation error: {e}")
            return {"error": str(e), "safe": False}

moderation_service = ModerationService()
