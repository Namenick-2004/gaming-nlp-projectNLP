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
    game_category: Optional[str] = None
    category_id: Optional[str] = None


class VideoList(BaseModel):
    items: List[VideoCard]


# ---------- Sentiment ----------

class SentimentResult(BaseModel):
    label: str            # positive | neutral | negative
    confidence: float


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
    trend_percent: float


# ---------- Trending ----------

class TrendingTopic(BaseModel):
    topic: str
    mentions: int
    growth_percent: float


class TrendingGame(BaseModel):
    name: str
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


# ---------- Single comment analysis (internal use) ----------

class AnalyzedComment(BaseModel):
    text: str
    sentiment: SentimentResult
    emotion: dict
    categories: List[str]


# ---------- Model evaluation ----------

class ClassMetric(BaseModel):
    label: str
    precision: float
    recall: float
    f1: float
    support: int


class ModelEvaluationReport(BaseModel):
    model_name: str
    accuracy: float
    macro_f1: float
    micro_f1: Optional[float] = None
    per_class: List[ClassMetric]
    confusion_matrix: List[List[int]]
    labels: List[str]
