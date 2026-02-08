from datetime import datetime, timezone
from typing import Literal, Optional

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: str
    name: Optional[str] = None


class AgentStreamRequest(BaseModel):
    session_id: Optional[str] = Field(default=None, description="Existing session id")
    messages: list[ChatMessage] = Field(default_factory=list)


class AgentStreamEvent(BaseModel):
    type: Literal["session", "token", "final", "error"]
    session_id: Optional[str] = None
    content: Optional[str] = None
    llm_calls: Optional[int] = None
    created_at: Optional[str] = None


class SessionState(BaseModel):
    session_id: str
    messages: list[ChatMessage] = Field(default_factory=list)
    llm_calls: int = 0
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
