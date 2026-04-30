from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


class ChatSource(BaseModel):
    title: str | None = None
    url: str | None = None
    type: str = "web"
    score: float | None = None


class ChatResponse(BaseModel):
    answer: str
    intent: str
    confidence: float | None = None
    mode: str
    matched_question: str | None = None
    sources: list[ChatSource] = Field(default_factory=list)
    session_id: str | None = None
    