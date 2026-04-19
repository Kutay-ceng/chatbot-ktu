from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None

class ChatResponse(BaseModel):
    answer: str
    intent: str
    confidence: float | None = None
    source: str
    matched_question: str | None = None