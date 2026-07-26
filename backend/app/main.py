from fastapi import FastAPI

from app.routes.analyze import router as analyze_router
from app.routes.language import router as language_router
from app.routes.reputation import router as reputation_router

app = FastAPI(
    title="ScamShield AI Backend",
    version="1.0.0"
)

app.include_router(analyze_router)
app.include_router(language_router)
app.include_router(reputation_router)


@app.get("/")
def root():
    return {
        "message": "ScamShield AI Backend Running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }