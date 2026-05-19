from typing import Any, Literal

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1, max_length=2000)
    mode: Literal["text", "voice"] = "text"


class ChatResponse(BaseModel):
    reply: str
    used_tool: bool = False
    tool_name: str | None = None
    mode: Literal["text", "voice"] = "text"
    audio_url: str | None = None
    tts_failed: bool = False
    meta: dict[str, Any] = Field(default_factory=dict)
