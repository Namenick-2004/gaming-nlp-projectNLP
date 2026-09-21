"""
Cross-video / sports-wide trend endpoints for the dashboard's
"Trending Sports" and "Trending Keywords" widgets.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import AnalysisSnapshot
from app.services.youtube_service import get_youtube_service

router = APIRouter(prefix="/api/sports-trends", tags=["trends"])


@router.get("")
def sports_trends(db: Session = Depends(get_db)):
    yt = get_youtube_service()
    current_videos = yt.trending(max_results=50)

    # YouTube does not expose the sport name as a separate field. Use the
    # real video title and view count instead of exposing category ids such
    # as "17" as if they were sport names.
    trending_sports = [
        {
            "name": video["title"],
            "views": video["views"],
            "video_id": video["video_id"],
        }
        for video in sorted(current_videos, key=lambda item: item["views"], reverse=True)[:10]
    ]

    overall_sentiment = _overall_sentiment(db)
    overall_emotion = _overall_emotion(db)

    return {
        "trending_sports": trending_sports,
        "trending_videos": current_videos[:20],
        "overall_sentiment": overall_sentiment,
        "overall_emotion": overall_emotion,
    }


def _overall_sentiment(db: Session) -> dict:
    snaps = db.query(AnalysisSnapshot).order_by(AnalysisSnapshot.created_at.desc()).limit(50).all()
    if not snaps:
        return {"positive": 0, "neutral": 0, "negative": 0}
    n = len(snaps)
    return {
        "positive": round(sum(s.sentiment_json.get("positive", 0) for s in snaps) / n, 1),
        "neutral": round(sum(s.sentiment_json.get("neutral", 0) for s in snaps) / n, 1),
        "negative": round(sum(s.sentiment_json.get("negative", 0) for s in snaps) / n, 1),
    }


def _overall_emotion(db: Session) -> dict:
    snaps = db.query(AnalysisSnapshot).order_by(AnalysisSnapshot.created_at.desc()).limit(50).all()
    labels = ["joy", "anger", "sadness", "surprise", "fear", "neutral"]
    if not snaps:
        return {lab: 0 for lab in labels}
    n = len(snaps)
    return {lab: round(sum(s.emotion_json.get(lab, 0) for s in snaps) / n, 1) for lab in labels}
