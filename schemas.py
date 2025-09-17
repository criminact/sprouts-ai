from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str = Field(..., description="Role of the message: user|system|assistant")
    content: str = Field(..., description="Message content")


class AskRequest(BaseModel):
    messages: List[ChatMessage]
    model: Optional[str] = Field(
        default="openai/gpt-oss-20b",
        description="Model identifier to use.",
    )
    extra_params: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional additional params forwarded to the Groq API call.",
    )


class ModerationResult(BaseModel):
    action: str
    category: str
    severity: float
    reasons: List[str] = []


class AskResponse(BaseModel):
    type: str
    message: str
    suggested_next: Optional[str] = None
    safety: Dict[str, Any] = {}


