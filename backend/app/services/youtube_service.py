"""
Real integration with YouTube Data API v3.
The user never types a URL: this service auto-discovers gaming
videos via search + the "Gaming" video category, then the frontend
lets them click "Analyze" on whichever card they want.
"""
import json
import ssl

import requests

from app.config import settings
from app.services.cache import cache_get, cache_set

GAMING_CATEGORY_ID = "20"  # YouTube's fixed category id for "Gaming"


class YouTubeService:
    def __init__(self):
        # Imported lazily so APP_MODE=mock never requires
        # google-api-python-client to even be installed.
        from googleapiclient.discovery import build

        if not settings.YOUTUBE_API_KEY:
            raise RuntimeError(
                "YOUTUBE_API_KEY is empty. Set it in .env, or set APP_MODE=mock "
                "to develop the UI without a real API key."
            )
        self.client = build("youtube", "v3", developerKey=settings.YOUTUBE_API_KEY)

    def _videos_by_chart(self, chart: str, region_code: str = "TH", max_results: int = 20) -> list[dict]:
        cache_key = f"chart:{chart}:{region_code}:{max_results}"
        cached = cache_get(cache_key)
        if cached:
            return cached

        resp = self._execute(
            self.client.videos().list(
            part="snippet,statistics",
            chart=chart,                     # "mostPopular"
            videoCategoryId=GAMING_CATEGORY_ID,
            regionCode=region_code,
            maxResults=max_results,
            )
        )

        videos = [_map_video(item) for item in resp.get("items", [])]
        return cache_set(cache_key, videos)

    def trending(self, max_results: int = 20) -> list[dict]:
        return self._videos_by_chart("mostPopular", max_results=max_results)

    def search_gaming(self, query: str, order: str = "date", max_results: int = 20) -> list[dict]:
        """order: 'date' -> latest, 'viewCount' -> most viewed,
        'relevance' + we sort client-side by commentCount -> most commented."""
        cache_key = f"search:{query}:{order}:{max_results}"
        cached = cache_get(cache_key)
        if cached:
            return cached

        search_resp = self._execute(self.client.search().list(
            part="id",
            q=query,
            type="video",
            videoCategoryId=GAMING_CATEGORY_ID,
            order=order,
            maxResults=max_results,
        ))
        ids = [item["id"]["videoId"] for item in search_resp.get("items", [])]
        if not ids:
            return []

        videos_resp = self._execute(self.client.videos().list(
            part="snippet,statistics", id=",".join(ids)
        ))
        videos = [_map_video(item) for item in videos_resp.get("items", [])]
        return cache_set(cache_key, videos)

    def most_commented(self, query: str = "gaming", max_results: int = 20) -> list[dict]:
        videos = self.search_gaming(query, order="relevance", max_results=max_results)
        return sorted(videos, key=lambda v: v["comment_count"], reverse=True)

    def get_video(self, video_id: str) -> dict | None:
        resp = self._execute(
            self.client.videos().list(part="snippet,statistics", id=video_id)
        )
        items = resp.get("items", [])
        return _map_video(items[0]) if items else None

    def video_categories(self) -> list[dict]:
        cached = cache_get("video-categories:TH")
        if cached:
            return cached
        response = self._execute(self.client.videoCategories().list(
            part="snippet",
            regionCode="TH",
        ))
        categories = [
            {"id": item["id"], "title": item["snippet"]["title"]}
            for item in response.get("items", [])
            if item["snippet"].get("assignable", True)
        ]
        return cache_set("video-categories:TH", categories)

    def get_comments(self, video_id: str, max_comments: int = 500) -> list[str]:
        from googleapiclient.errors import HttpError

        cache_key = f"comments:{video_id}:{max_comments}"
        cached = cache_get(cache_key)
        if cached:
            return cached

        comments, page_token = [], None
        while len(comments) < max_comments:
            try:
                resp = self._execute(self.client.commentThreads().list(
                    part="snippet",
                    videoId=video_id,
                    maxResults=min(100, max_comments - len(comments)),
                    pageToken=page_token,
                    textFormat="plainText",
                ))
            except (ssl.SSLError, OSError):
                return cache_set(
                    cache_key,
                    self._get_comments_via_requests(video_id, max_comments),
                )
            except HttpError as exc:
                content = exc.content.decode("utf-8", errors="replace") if isinstance(exc.content, bytes) else str(exc.content)
                try:
                    error_payload = json.loads(content)
                except json.JSONDecodeError:
                    error_payload = {}
                reasons = {
                    error.get("reason")
                    for error in error_payload.get("error", {}).get("errors", [])
                }
                comments_unavailable = (
                    "commentsDisabled" in reasons
                    or "comments are disabled" in content.lower()
                )
                if comments_unavailable:
                    return cache_set(cache_key, [])
                raise
            for item in resp.get("items", []):
                text = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
                comments.append(text)
            page_token = resp.get("nextPageToken")
            if not page_token:
                break
        return cache_set(cache_key, comments)

    def _get_comments_via_requests(self, video_id: str, max_comments: int) -> list[str]:
        """Use requests only when httplib2 cannot negotiate TLS on this host."""
        comments, page_token = [], None
        endpoint = "https://www.googleapis.com/youtube/v3/commentThreads"

        while len(comments) < max_comments:
            params = {
                "part": "snippet",
                "videoId": video_id,
                "maxResults": min(100, max_comments - len(comments)),
                "textFormat": "plainText",
                "key": settings.YOUTUBE_API_KEY,
            }
            if page_token:
                params["pageToken"] = page_token

            response = requests.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            payload = response.json()
            comments.extend(
                item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
                for item in payload.get("items", [])
            )
            page_token = payload.get("nextPageToken")
            if not page_token:
                break

        return comments

    @staticmethod
    def _execute(request) -> dict:
        """Run a Google API request, falling back when httplib2 TLS fails."""
        try:
            return request.execute()
        except (ssl.SSLError, OSError):
            response = requests.get(request.uri, timeout=30)
            response.raise_for_status()
            return response.json()


def _map_video(item: dict) -> dict:
    snippet, stats = item["snippet"], item.get("statistics", {})
    return {
        "video_id": item["id"] if isinstance(item["id"], str) else item["id"].get("videoId"),
        "title": snippet["title"],
        "channel": snippet["channelTitle"],
        "thumbnail": snippet["thumbnails"]["medium"]["url"],
        "views": int(stats.get("viewCount", 0)),
        "likes": int(stats.get("likeCount", 0)),
        "comment_count": int(stats.get("commentCount", 0)),
        "published_at": snippet["publishedAt"],
        "game_category": snippet.get("categoryId"),
        "category_id": snippet.get("categoryId"),
    }


from functools import lru_cache
from app.config import settings


@lru_cache(maxsize=1)
def get_youtube_service():
    """Return the configured YouTube provider as a singleton."""
    if settings.APP_MODE == "mock":
        from app.services.mock_service import MockYouTubeService
        return MockYouTubeService()
    return YouTubeService()
