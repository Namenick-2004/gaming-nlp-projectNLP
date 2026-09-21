"""
Pydantic response/request models shared across routers.
Keeping them here means the frontend and backend response
shapes always match one source of truth.
"""
from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel


# ---------- YouTube video ----------

class VideoCard(BaseModel):
    video_id: str
    title: str
    channel: str
    thumbnail: str
    views: int
    likes: int
    comment_count: int
    published_at: str
    sport_category: Optional[str] = None
    category_id: Optional[str] = None


class VideoList(BaseModel):
    items: List[VideoCard]


# ---------- Sentiment ----------

class SentimentDistribution(BaseModel):
    positive: float
    neutral: float
    negative: float
    sample_size: int


# ---------- Emotion ----------

class EmotionDistribution(BaseModel):
    joy: float
    anger: float
    sadness: float
    surprise: float
    fear: float
    neutral: float
    sample_size: int


# ---------- Category ----------

class CategoryScore(BaseModel):
    category: str
    percentage: float


class CategoryDistribution(BaseModel):
    categories: List[CategoryScore]
    sample_size: int


# ---------- Keywords ----------

class Keyword(BaseModel):
    keyword: str
    count: int
    importance: float
    trend_percent: Optional[float] = None


# ---------- Trending ----------

class TrendingTopic(BaseModel):
    topic: str
    mentions: int
    growth_percent: float


# ---------- Sentiment trend over time ----------

class SentimentTrendPoint(BaseModel):
    date: str
    positive: float
    neutral: float
    negative: float


# ---------- Summary ----------

class SummaryResult(BaseModel):
    summary: str
    based_on_comments: int
