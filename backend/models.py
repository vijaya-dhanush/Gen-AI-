from datetime import datetime
from pydantic import BaseModel, Field


class MessageCreateRequest(BaseModel):
    content: str = Field(min_length=1)


class Message(BaseModel):
    role: str
    content: str | None = None
    stage1: list[dict] | None = None
    stage2: list[dict] | None = None
    stage3: str | None = None
    created_at: datetime


class Conversation(BaseModel):
    id: str
    created_at: datetime
    messages: list[Message]


class ConversationSummary(BaseModel):
    id: str
    created_at: datetime
    message_count: int
