"""
Video discovery endpoints. The user never provides a URL — the
dashboard calls these on load to auto-populate video cards.
"""
from fastapi import APIRouter, Query
from app.services.youtube_service import get_youtube_service
from app.models.schemas import VideoList

router = APIRouter(prefix="/api/videos", tags=["videos"])


@router.get("", response_model=VideoList)
def list_videos(query: str = Query(""), max_results: int = Query(20, le=50)):
    yt = get_youtube_service()
    videos = yt.search_sports(query, order="relevance", max_results=max_results) if query.strip() else yt.trending(max_results=max_results)
    return {"items": videos}


@router.get("/trending", response_model=VideoList)
def trending_videos(query: str = Query(""), max_results: int = Query(20, le=50)):
    yt = get_youtube_service()
    videos = yt.search_sports(query, order="relevance", max_results=max_results) if query.strip() else yt.trending(max_results=max_results)
    return {"items": videos}


@router.get("/latest", response_model=VideoList)
def latest_videos(query: str = Query("sports"), max_results: int = Query(20, le=50)):
    yt = get_youtube_service()
    return {"items": yt.search_sports(query.strip() or "sports", order="date", max_results=max_results)}


@router.get("/most-viewed", response_model=VideoList)
def most_viewed_videos(query: str = Query("sports"), max_results: int = Query(20, le=50)):
    yt = get_youtube_service()
    return {"items": yt.search_sports(query.strip() or "sports", order="viewCount", max_results=max_results)}


@router.get("/most-commented", response_model=VideoList)
def most_commented_videos(query: str = Query("sports"), max_results: int = Query(20, le=50)):
    yt = get_youtube_service()
    return {"items": yt.most_commented(query.strip() or "sports", max_results=max_results)}


@router.get("/categories")
def video_categories():
    return {"items": get_youtube_service().video_categories()}


@router.get("/{video_id}")
def get_video(video_id: str):
    yt = get_youtube_service()
    video = yt.get_video(video_id)
    if not video:
        return {"error": "video not found"}
    return video


@router.get("/{video_id}/comments")
def get_video_comments(video_id: str, max_comments: int = Query(200, le=500)):
    yt = get_youtube_service()
    return {"video_id": video_id, "comments": yt.get_comments(video_id, max_comments=max_comments)}
