"""
ORM tables. Kept intentionally small: the app is analysis-first, so
we mainly cache videos/comments and store analysis snapshots so the
dashboard doesn't have to hit the YouTube API or re-run inference
every time a page loads.
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, JSON
from datetime import datetime
from app.db.database import Base


class Video(Base):
    __tablename__ = "videos"

    video_id = Column(String, primary_key=True, index=True)
    title = Column(String)
    channel = Column(String)
    thumbnail = Column(String)
    views = Column(Integer)
    likes = Column(Integer)
    comment_count = Column(Integer)
    published_at = Column(String)
    game_category = Column(String, nullable=True)
    fetched_at = Column(DateTime, default=datetime.utcnow)


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    video_id = Column(String, index=True)
    text = Column(Text)
    author = Column(String, nullable=True)
    like_count = Column(Integer, default=0)
    published_at = Column(String, nullable=True)
    fetched_at = Column(DateTime, default=datetime.utcnow)


class AnalysisSnapshot(Base):
    """
    One row per (video, analysis run). Storing the raw JSON output of
    the NLP pipeline lets the dashboard re-render instantly and lets
    /api/analysis/{id}/trends compare "before vs after patch".
    """
    __tablename__ = "analysis_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    video_id = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    sentiment_json = Column(JSON)
    emotion_json = Column(JSON)
    category_json = Column(JSON)
    keywords_json = Column(JSON)
    summary_text = Column(Text, nullable=True)
    sample_size = Column(Integer, default=0)
