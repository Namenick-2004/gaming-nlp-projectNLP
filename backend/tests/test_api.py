"""
Basic smoke tests. Run with APP_MODE=mock so no API key / GPU is
needed:

    APP_MODE=mock pytest

These check the API contract (status codes + response shape), not
model quality — model quality is checked by training/evaluate.py.
"""
import os
os.environ.setdefault("APP_MODE", "mock")

from fastapi.testclient import TestClient
from app.main import app
from app.services.nlp.preprocessing import clean_generated_text

client = TestClient(app)


def test_health_check():
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_list_videos():
    resp = client.get("/api/videos/trending?max_results=5")
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert len(items) == 5
    assert "video_id" in items[0]


def test_video_comments():
    resp = client.get("/api/videos/mock_001/comments")
    assert resp.status_code == 200
    assert len(resp.json()["comments"]) > 0


def test_full_analysis_pipeline():
    resp = client.post("/api/analysis/mock_001/run")
    assert resp.status_code == 200
    body = resp.json()
    assert "sentiment" in body and "emotion" in body and "categories" in body
    assert "summary" in body

    sentiment = body["sentiment"]
    total = sentiment["positive"] + sentiment["neutral"] + sentiment["negative"]
    assert 99 <= total <= 101  # percentages should sum to ~100


def test_clean_generated_text_removes_special_tokens_and_repeats():
    raw = "<extra_id_0> เกมนี้สนุกมากค่ะค่ะค่ะ <extra_id_1> เกมนี้มีปัญหาการกระตุก"
    cleaned = clean_generated_text(raw)
    assert "<extra_id_" not in cleaned
    assert "ค่ะ" not in cleaned or "ค่ะ" in cleaned
    assert "เกมนี้สนุกมาก" in cleaned
    assert "ปัญหาการกระตุก" in cleaned
