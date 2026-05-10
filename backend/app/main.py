from fastapi import FastAPI

app = FastAPI(
    title="KTU CENG Chatbot Backend",
    description="Base backend service for the KTU CENG chatbot project.",
    version="0.1.0",
)


@app.get("/")
def read_root():
    return {"message": "KTU CENG chatbot backend is running"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
