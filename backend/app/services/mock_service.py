"""
Mock services — used ONLY when APP_MODE=mock.

These exist purely so the React dashboard can be built and demoed
before a YouTube API key / fine-tuned models exist. They are kept in
a completely separate module from YouTubeService / ModelService
(the real, production code paths) as required by the spec, so there
is never any ambiguity about which one is running in production.

Note this is heuristic, NOT random: sentiment/emotion/category for
mock comments are derived from a small keyword lexicon so the demo
dashboard still reacts sensibly to different sample comments instead
of flickering with random noise on every refresh.
"""
import re
from datetime import datetime, timedelta

POS_WORDS = ["สนุก", "ดี", "เจ๋ง", "สวย", "ชอบ", "โคตร", "gg", "op ", "ปัง"]
NEG_WORDS = ["โกง", "แย่", "บั๊ก", "bug", "กระตุก", "broken", "lag", "ห่วย"]

CATEGORY_KEYWORDS = {
    "character": ["ตัวละคร", "character"],
    "weapon": ["อาวุธ", "ปืน", "weapon"],
    "map": ["แมพ", "map"],
    "graphics": ["กราฟิก", "graphic"],
    "update": ["แพทช์", "อัปเดต", "update", "patch"],
    "bug": ["บั๊ก", "bug"],
    "ranking": ["แรงค์", "rank"],
    "skin": ["สกิน", "skin"],
    "price": ["ราคา", "price"],
    "performance": ["กระตุก", "เฟรม", "fps", "lag"],
    "gameplay": ["เกมเพลย์", "เล่น", "gameplay"],
}

SAMPLE_COMMENTS = [
    "ตัวละครใหม่โกงมาก แต่กราฟิกสวยดี", "แพทช์นี้ทำเกมลื่นขึ้นเยอะ gg",
    "เกมกระตุกมากหลังอัปเดต บั๊กเพียบ", "สกินใหม่ราคาแพงไป แต่สวยมาก",
    "ระบบแรงค์ปีนยากมาก ตัวละคร op เกิน", "555555 เกมนี้สนุกโคตร",
    "map ใหม่ออกแบบดีนะ เล่นสนุก", "weapon balance ห่วยมาก broken af",
    "graphic สวยขึ้นเยอะเมื่อเทียบซีซั่นก่อน", "อยากให้แก้ bug เรื่อง lag ทีครับ",
]


def _classify_sentiment(text: str) -> dict:
    score = sum(w in text.lower() for w in POS_WORDS) - sum(w in text.lower() for w in NEG_WORDS)
    if score > 0:
        return {"label": "positive", "confidence": 0.80}
    if score < 0:
        return {"label": "negative", "confidence": 0.78}
    return {"label": "neutral", "confidence": 0.65}


def _classify_categories(text: str) -> list[str]:
    hits = [cat for cat, kws in CATEGORY_KEYWORDS.items() if any(k in text.lower() for k in kws)]
    return hits or ["other"]


def _classify_emotion(text: str) -> dict:
    sent = _classify_sentiment(text)["label"]
    base = {"joy": 0.1, "anger": 0.1, "sadness": 0.05, "surprise": 0.1, "fear": 0.05, "neutral": 0.6}
    if sent == "positive":
        base.update(joy=0.6, neutral=0.2)
    elif sent == "negative":
        base.update(anger=0.5, sadness=0.15, neutral=0.15)
    return base


class MockModelService:
    """Drop-in replacement for ModelService with the exact same
    `analyze_comments` contract, so routers never need to know
    whether they're talking to mock or production models."""

    def analyze_comments(self, comments: list[str]) -> dict:
        from app.services.model_service import _aggregate_labels, _aggregate_scores, _aggregate_multilabel, _empty_analysis

        if not comments:
            return _empty_analysis()

        sentiments = [_classify_sentiment(c) for c in comments]
        emotions = [_classify_emotion(c) for c in comments]
        categories = [_classify_categories(c) for c in comments]

        sentiment_dist = _aggregate_labels([s["label"] for s in sentiments], ["positive", "neutral", "negative"])
        emotion_dist = _aggregate_scores(emotions, ["joy", "anger", "sadness", "surprise", "fear", "neutral"])
        category_dist = _aggregate_multilabel(categories)

        keywords = [
            {"keyword": kw, "count": sum(kw in c.lower() for c in comments), "importance": 0.7, "trend_percent": 15.0}
            for kw in ["ตัวละครใหม่", "แพทช์ล่าสุด", "ระบบแรงค์", "สกิน", "บั๊ก"]
        ]

        top_pos = next((c for c in comments if _classify_sentiment(c)["label"] == "positive"), None)
        top_neg = next((c for c in comments if _classify_sentiment(c)["label"] == "negative"), None)
        summary_parts = []
        if top_pos:
            summary_parts.append("ผู้ชมส่วนใหญ่ชื่นชอบตัวละครใหม่และการปรับปรุงเกมเพลย์")
        if top_neg:
            summary_parts.append("มีข้อกังวลเกี่ยวกับความสมดุลของตัวละครและปัญหาบั๊กหลังอัปเดต")
        summary = " แต่".join(summary_parts) or "ยังไม่มีข้อมูลเพียงพอสำหรับสรุปผล"

        n = len(comments)
        return {
            "sentiment": {**sentiment_dist, "sample_size": n},
            "emotion": {**emotion_dist, "sample_size": n},
            "categories": {"categories": category_dist, "sample_size": n},
            "keywords": keywords,
            "summary": {"summary": summary, "based_on_comments": n},
        }


class MockYouTubeService:
    """Deterministic fake video/comment catalog for UI development."""

    _GAMES = ["Valorant", "GTA VI", "Minecraft", "PUBG", "ROV", "Free Fire"]
    _CATEGORIES = [{"id": "20", "title": "Gaming"}]

    def _fake_video(self, i: int) -> dict:
        game = self._GAMES[i % len(self._GAMES)]
        return {
            "video_id": f"mock_{i:03d}",
            "title": f"[{game}] คลิปไฮไลท์สุดมันส์ ep.{i}",
            "channel": f"GamerChannelTH{i % 5}",
            "thumbnail": "https://via.placeholder.com/320x180.png?text=" + game.replace(" ", "+"),
            "views": 10000 + i * 3771,
            "likes": 500 + i * 97,
            "comment_count": 80 + i * 13,
            "published_at": (datetime.utcnow() - timedelta(days=i)).isoformat() + "Z",
            "game_category": game,
            "category_id": "20",
        }

    def trending(self, max_results: int = 20) -> list[dict]:
        return [self._fake_video(i) for i in range(max_results)]

    def search_gaming(self, query: str, order: str = "date", max_results: int = 20) -> list[dict]:
        query = query.strip().lower()
        videos = [self._fake_video(i) for i in range(max_results * 2)]
        if query and query != "gaming":
            videos = [video for video in videos if query in video["title"].lower() or query in video["game_category"].lower()]
        return videos[:max_results]

    def most_commented(self, query: str = "gaming", max_results: int = 20) -> list[dict]:
        vids = [self._fake_video(i) for i in range(max_results)]
        return sorted(vids, key=lambda v: v["comment_count"], reverse=True)

    def video_categories(self) -> list[dict]:
        return self._CATEGORIES

    def get_video(self, video_id: str) -> dict | None:
        try:
            i = int(video_id.split("_")[-1])
        except ValueError:
            i = 0
        return self._fake_video(i)

    def get_comments(self, video_id: str, max_comments: int = 500) -> list[str]:
        reps = max(1, max_comments // len(SAMPLE_COMMENTS))
        return (SAMPLE_COMMENTS * reps)[:max_comments]
