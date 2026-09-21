"""Sample sports videos for offline UI development; no mock analysis."""
from datetime import datetime, timedelta

SAMPLE_COMMENTS = [
    "นักเตะยิงประตูสวยมาก ชอบทีมนี้", "โค้ชวางแผนดี ทีมเล่นสนุก",
    "กรรมการตัดสินแย่มาก ไม่ยุติธรรม", "ตั๋วราคาแพงไป แต่สนามสวย",
    "ทีมชาติอันดับดีขึ้น แฟนบอลดีใจ", "การแข่งขันวันนี้สนุกมาก",
    "นักกีฬาบาดเจ็บ เสียดายมาก", "กองหลังเล่นห่วย เสียประตูง่าย",
    "วอลเลย์บอลนัดนี้ฟอร์มดี ชนะสวยงาม", "อยากให้ถ่ายทอดสดชัดกว่านี้",
]


class MockYouTubeService:
    """Deterministic fake video/comment catalog for UI development."""

    _SPORTS = ["ฟุตบอล", "วอลเลย์บอล", "บาสเกตบอล", "แบดมินตัน", "มวย", "เทนนิส"]
    _CATEGORIES = [{"id": "17", "title": "Sports"}]

    def _fake_video(self, i: int) -> dict:
        sport = self._SPORTS[i % len(self._SPORTS)]
        return {
            "video_id": f"mock_{i:03d}",
            "title": f"[{sport}] คลิปไฮไลท์สุดมันส์ ep.{i}",
            "channel": f"SportsChannelTH{i % 5}",
            "thumbnail": "https://via.placeholder.com/320x180.png?text=" + sport.replace(" ", "+"),
            "views": 10000 + i * 3771,
            "likes": 500 + i * 97,
            "comment_count": 80 + i * 13,
            "published_at": (datetime.utcnow() - timedelta(days=i)).isoformat() + "Z",
            "sport_category": sport,
            "category_id": "17",
        }

    def trending(self, max_results: int = 20) -> list[dict]:
        return [self._fake_video(i) for i in range(max_results)]

    def search_sports(self, query: str, order: str = "date", max_results: int = 20) -> list[dict]:
        query = query.strip().lower()
        videos = [self._fake_video(i) for i in range(max_results * 2)]
        if query and query != "sports":
            videos = [video for video in videos if query in video["title"].lower() or query in video["sport_category"].lower()]
        return videos[:max_results]

    def most_commented(self, query: str = "sports", max_results: int = 20) -> list[dict]:
        vids = self.search_sports(query, order="relevance", max_results=max_results)
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
