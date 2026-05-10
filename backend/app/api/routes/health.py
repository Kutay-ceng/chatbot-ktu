from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/")
def read_root():
    return {"message": "KTU CENG chatbot backend is running"}


@router.get("/health")
def health_check():
    return {"status": "ok"}
