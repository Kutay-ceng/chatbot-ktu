from fastapi import FastAPI

from backend.app.api.routes.chat import router as chat_router
from backend.app.api.routes.health import router as health_router

app = FastAPI(
    title="KTU CENG Chatbot Backend",
    description="Base backend service for the KTU CENG chatbot project.",
    version="0.1.0",
)
app.include_router(health_router)
app.include_router(chat_router)
