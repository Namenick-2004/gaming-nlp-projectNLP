"""
FastAPI application entrypoint.

Run with:
    uvicorn app.main:app --reload --port 8000

Models (or the mock service) are loaded ONCE here at startup via
get_model_service(), not per-request, per the performance spec.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from googleapiclient.errors import HttpError
from app.config import settings
from app.db.database import Base, engine
from app.routers import videos, analysis, trends

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="YouTube Gaming Trend & Sentiment Analysis API",
    description="NLP backend for analyzing gaming video comments (Thai + English).",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HttpError)
async def youtube_api_error_handler(request: Request, exc: HttpError):
    """Expose a safe, actionable YouTube API error to local clients."""
    content = exc.content.decode("utf-8", errors="replace") if isinstance(exc.content, bytes) else str(exc.content)
    return JSONResponse(
        status_code=502,
        content={
            "detail": "YouTube API request failed",
            "youtube_status": getattr(exc.resp, "status", None),
            "youtube_error": content,
        },
    )


@app.exception_handler(OSError)
async def network_error_handler(request: Request, exc: OSError):
    """Return a useful response when local security software blocks YouTube."""
    return JSONResponse(
        status_code=503,
        content={
            "detail": "Cannot connect to the YouTube Data API. Check the internet connection, firewall, proxy, or antivirus settings.",
        },
    )

app.include_router(videos.router)
app.include_router(analysis.router)
app.include_router(trends.router)


@app.on_event("startup")
def preload_models():
    """Warms up the model singleton at boot instead of on first
    request, so the first user doesn't eat the ~seconds-long model
    load time."""
    from app.services.model_service import get_model_service
    get_model_service()


@app.get("/")
def health_check():
    return {
        "status": "ok",
        "mode": settings.APP_MODE,
        "youtube_source": "mock" if settings.APP_MODE == "mock" else "youtube_api",
        "nlp_source": "mock" if settings.APP_MODE in {"mock", "youtube_mock_nlp"} else "models",
    }
