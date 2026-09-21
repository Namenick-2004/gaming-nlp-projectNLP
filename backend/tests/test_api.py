import os
os.environ.setdefault("APP_MODE", "mock")

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
    assert resp.json()["nlp_source"] == "gemini"
    assert "GEMINI_API_KEY" not in resp.json()


def test_missing_key_returns_actionable_error(monkeypatch):
    from app.config import settings
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "")
    response = client.post("/api/analysis/mock_001/run")
    assert response.status_code == 503
    assert "GEMINI_API_KEY" in response.json()["detail"]


def test_list_videos():
    resp = client.get("/api/videos/trending?max_results=5")
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert len(items) == 5
    assert "video_id" in items[0]
    assert all(item["category_id"] == "17" for item in items)
    assert all(item["sport_category"] for item in items)


def test_sports_trends():
    response = client.get("/api/sports-trends")
    assert response.status_code == 200
    assert response.json()["trending_sports"]


def test_youtube_discovery_uses_sports_category():
    from unittest.mock import MagicMock, patch
    from app.services.youtube_service import YouTubeService
    service = YouTubeService.__new__(YouTubeService)
    service.client = MagicMock()
    service.client.videos.return_value.list.return_value.execute.return_value = {"items": []}
    service.client.search.return_value.list.return_value.execute.return_value = {"items": []}
    with patch("app.services.youtube_service.cache_get", return_value=None):
        service.trending()
        service.search_sports("football")
    assert service.client.videos.return_value.list.call_args.kwargs["videoCategoryId"] == "17"
    assert service.client.search.return_value.list.call_args.kwargs["videoCategoryId"] == "17"


def test_non_sports_chart_falls_back_to_sports_search():
    from unittest.mock import MagicMock, patch
    from app.services.youtube_service import YouTubeService
    service = YouTubeService.__new__(YouTubeService)
    service.client = MagicMock()
    service.client.videos.return_value.list.return_value.execute.return_value = {
        "items": [{"snippet": {"categoryId": "20"}}]
    }
    service.search_sports = MagicMock(return_value=[{"category_id": "17"}])
    with patch("app.services.youtube_service.cache_get", return_value=None):
        assert service.trending(4) == [{"category_id": "17"}]
    service.search_sports.assert_called_once_with("กีฬา", order="relevance", max_results=4)


def test_video_comments():
    resp = client.get("/api/videos/mock_001/comments")
    assert resp.status_code == 200
    assert len(resp.json()["comments"]) > 0


def test_full_analysis_pipeline(monkeypatch):
    from app.config import settings
    from app.services.gemini_service import GeminiService
    from tests.test_gemini import response_for
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "test-key")
    monkeypatch.setattr("app.services.gemini_service.httpx.post", lambda *args, **kwargs: response_for(kwargs["json"]))
    resp = client.post("/api/analysis/mock_001/run")
    assert resp.status_code == 200
    body = resp.json()
    assert "sentiment" in body and "emotion" in body and "categories" in body
    assert "summary" in body

    sentiment = body["sentiment"]
    total = sentiment["positive"] + sentiment["neutral"] + sentiment["negative"]
    assert 99 <= total <= 101  # percentages should sum to ~100
