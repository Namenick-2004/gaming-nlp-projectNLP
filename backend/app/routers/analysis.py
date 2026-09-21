"""
Per-video analysis endpoints. `analyze_video()` is the single place
that fetches comments -> runs the whole NLP pipeline -> stores a
snapshot -> returns dashboard-ready numbers. The individual
GET /api/analysis/{video_id}/<facet> endpoints re-use the same
snapshot so the frontend can fetch pieces independently without
re-running inference five times.
"""
from fastapi import APIRouter, Query, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.services.youtube_service import get_youtube_service
from app.services.gemini_service import get_gemini_service
from app.db.database import get_db
from app.db.models import AnalysisSnapshot
from app.config import settings

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


def _run_analysis(video_id: str, db: Session) -> dict:
    service = get_gemini_service()
    service.ensure_configured()
    yt = get_youtube_service()
    comments = yt.get_comments(video_id, max_comments=settings.MAX_COMMENTS_PER_ANALYSIS)

    result = service.analyze_comments(comments)

    snapshot = AnalysisSnapshot(
        video_id=video_id,
        sentiment_json=result["sentiment"],
        emotion_json=result["emotion"],
        category_json=result["categories"],
        keywords_json=result["keywords"],
        summary_text=result["summary"]["summary"],
        sample_size=result["summary"]["based_on_comments"],
    )
    db.add(snapshot)
    db.commit()
    return result


def _latest_snapshot(video_id: str, db: Session) -> AnalysisSnapshot | None:
    return (
        db.query(AnalysisSnapshot)
        .filter(AnalysisSnapshot.video_id == video_id)
        .order_by(AnalysisSnapshot.created_at.desc())
        .first()
    )


@router.post("/{video_id}/run")
def analyze_video(video_id: str, db: Session = Depends(get_db)):
    """Triggers the full pipeline for a video the user clicked
    'Analyze' on. Returns the complete result in one call; the
    per-facet GET endpoints below are for re-reading it later."""
    return _run_analysis(video_id, db)


@router.get("/{video_id}/sentiment")
def get_sentiment(video_id: str, db: Session = Depends(get_db)):
    snap = _latest_snapshot(video_id, db) or _ensure_analysis(video_id, db)
    return snap.sentiment_json if isinstance(snap, AnalysisSnapshot) else snap["sentiment"]


@router.get("/{video_id}/emotion")
def get_emotion(video_id: str, db: Session = Depends(get_db)):
    snap = _latest_snapshot(video_id, db) or _ensure_analysis(video_id, db)
    return snap.emotion_json if isinstance(snap, AnalysisSnapshot) else snap["emotion"]


@router.get("/{video_id}/topics")
def get_topics(video_id: str, db: Session = Depends(get_db)):
    snap = _latest_snapshot(video_id, db) or _ensure_analysis(video_id, db)
    return snap.category_json if isinstance(snap, AnalysisSnapshot) else snap["categories"]


@router.get("/{video_id}/keywords")
def get_keywords(video_id: str, db: Session = Depends(get_db)):
    snap = _latest_snapshot(video_id, db) or _ensure_analysis(video_id, db)
    return snap.keywords_json if isinstance(snap, AnalysisSnapshot) else snap["keywords"]


@router.get("/{video_id}/summary")
def get_summary(video_id: str, db: Session = Depends(get_db)):
    snap = _latest_snapshot(video_id, db) or _ensure_analysis(video_id, db)
    if isinstance(snap, AnalysisSnapshot):
        return {"summary": snap.summary_text, "based_on_comments": snap.sample_size}
    return snap["summary"]


@router.get("/{video_id}/trends")
def get_sentiment_trend(video_id: str, db: Session = Depends(get_db)):
    """Sentiment over each stored snapshot for this video, so the
    frontend can plot 'did sentiment improve after the last patch?'."""
    snapshots = (
        db.query(AnalysisSnapshot)
        .filter(AnalysisSnapshot.video_id == video_id)
        .order_by(AnalysisSnapshot.created_at.asc())
        .all()
    )
    return [
        {
            "date": s.created_at.isoformat(),
            "positive": s.sentiment_json.get("positive", 0),
            "neutral": s.sentiment_json.get("neutral", 0),
            "negative": s.sentiment_json.get("negative", 0),
        }
        for s in snapshots
    ]


def _ensure_analysis(video_id: str, db: Session):
    """Called when a facet is requested before /run has ever been
    triggered for this video — runs it once, on demand."""
    return _run_analysis(video_id, db)
