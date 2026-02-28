"""
LLM Service - Native Google Gemini integration
Drop-in replacement for emergentintegrations.llm.chat
All LLM calls route through Google Gemini API
"""

import google.generativeai as genai
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class UserMessage:
    text: Optional[str] = None


@dataclass
class ImageContent:
    url: Optional[str] = None
    base64_data: Optional[str] = None
    mime_type: str = "image/png"


@dataclass
class FileContentWithMimeType:
    data: bytes = b""
    mime_type: str = "application/octet-stream"


class LlmChat:
    def __init__(self, api_key: str, session_id: str, system_message: str = ""):
        self.api_key = api_key
        self.session_id = session_id
        self.system_message = system_message
        self.model_name = "gemini-2.5-flash"

    def with_model(self, provider: str, model_name: str) -> "LlmChat":
        model_map = {
            "gpt-5": "gemini-2.5-pro",
            "gpt-5.2": "gemini-2.5-pro",
            "gpt-4o": "gemini-2.5-flash",
            "gpt-4o-mini": "gemini-2.5-flash",
            "claude-sonnet-4-5-20250929": "gemini-2.5-pro",
            "claude-3-7-sonnet-20250219": "gemini-2.5-pro",
        }
        if provider == "gemini":
            self.model_name = model_name
        else:
            self.model_name = model_map.get(model_name, "gemini-2.5-flash")
        return self

    async def send_message(self, user_message: UserMessage) -> str:
        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=self.system_message if self.system_message else None,
        )
        response = model.generate_content(user_message.text)
        return response.text
