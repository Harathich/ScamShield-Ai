from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.connection import Base, engine
from app.routes.analyze import router as analyze_router
from app.routes.analyze_domain import router as analyze_domain_router
from app.routes.language import router as language_router
from app.routes.identity import router as identity_router
from app.routes.analyze_recruitment import router as analyze_recruitment_router
from app.routes.ocr import router as ocr_router
from app.routes.orchestrator import router as orchestrator_router
from app.routes.auth import router as auth_router, user_router
from app.routes.history import router as history_router

# Initialize database tables
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"[Warning] Error creating database tables on startup: {e}")

app = FastAPI(
    title="ScamShield AI Backend",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(history_router)
app.include_router(analyze_router)
app.include_router(analyze_domain_router)
app.include_router(language_router)
app.include_router(identity_router)
app.include_router(analyze_recruitment_router)
app.include_router(ocr_router)
app.include_router(orchestrator_router)


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