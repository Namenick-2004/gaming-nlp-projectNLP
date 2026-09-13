"""
Loads every NLP model ONCE at backend startup and exposes a single
`get_model_service()` singleton. Routers never import transformers
directly — they always go through this file, which also means
swapping a model (e.g. a new WangchanBERTa checkpoint) only requires
changing the path in `.env`, not touching any router code.

In APP_MODE=mock this module is bypassed entirely in favour of
mock_service.py, so the frontend/backend contract can be developed
and demoed without a GPU, without model weights, and without
internet access.
"""
from functools import lru_cache
from app.config import settings


class ModelService:
    """Wraps all five model families behind one object."""

    def __init__(self):
        # Imports are local so `APP_MODE=mock` never requires torch /
        # transformers / a GPU to even be installed.
        from app.services.nlp.sentiment import SentimentModel
        from app.services.nlp.emotion import EmotionModel
        from app.services.nlp.category import CategoryModel
        from app.services.nlp.embedding import EmbeddingService
        from app.services.nlp.summarization import SummarizationModel
        from app.services.nlp.keyword_extraction import KeywordExtractor

        device = settings.DEVICE

        self.sentiment = SentimentModel(settings.SENTIMENT_MODEL_PATH, device)
        self.emotion = EmotionModel(settings.EMOTION_MODEL_PATH, device)
        self.category = CategoryModel(settings.CATEGORY_MODEL_PATH, device)
        self.embedding = EmbeddingService(settings.EMBEDDING_MODEL_NAME, device)
        self.summarizer = SummarizationModel(settings.SUMMARIZATION_MODEL_NAME, device)
        self.keyword_extractor = KeywordExtractor(self.embedding.model)

    # ---- high level pipeline ----

    def analyze_comments(self, comments: list[str]) -> dict:
        """Runs every model over one batch of comments and returns
        aggregated, dashboard-ready percentages — never random values."""
        n = len(comments)
        if n == 0:
            return _empty_analysis()

        sentiments = self.sentiment.predict_batch(comments)
        emotions = self.emotion.predict_batch(comments)
        categories = self.category.predict_batch(comments)

        sentiment_dist = _aggregate_labels([s["label"] for s in sentiments],
                                            ["positive", "neutral", "negative"])
        emotion_dist = _aggregate_scores(emotions,
                                          ["joy", "anger", "sadness", "surprise", "fear", "neutral"])
        category_dist = _aggregate_multilabel(categories)
        keywords = self.keyword_extractor.extract(comments, top_n=10)
        summary = self.summarizer.summarize_comments(comments)

        return {
            "sentiment": {**sentiment_dist, "sample_size": n},
            "emotion": {**emotion_dist, "sample_size": n},
            "categories": {"categories": category_dist, "sample_size": n},
            "keywords": keywords,
            "summary": {"summary": summary, "based_on_comments": n},
        }


def _aggregate_labels(labels: list[str], all_labels: list[str]) -> dict:
    n = len(labels) or 1
    return {lab: round(labels.count(lab) / n * 100, 1) for lab in all_labels}


def _aggregate_scores(dist_list: list[dict], all_labels: list[str]) -> dict:
    n = len(dist_list) or 1
    return {lab: round(sum(d[lab] for d in dist_list) / n * 100, 1) for lab in all_labels}


def _aggregate_multilabel(label_lists: list[list[str]]) -> list[dict]:
    n = len(label_lists) or 1
    counts: dict[str, int] = {}
    for labels in label_lists:
        for lab in labels:
            counts[lab] = counts.get(lab, 0) + 1
    ranked = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
    return [{"category": lab, "percentage": round(c / n * 100, 1)} for lab, c in ranked]


def _empty_analysis() -> dict:
    zero = {"positive": 0, "neutral": 0, "negative": 0, "sample_size": 0}
    return {
        "sentiment": zero,
        "emotion": {"joy": 0, "anger": 0, "sadness": 0, "surprise": 0, "fear": 0, "neutral": 0, "sample_size": 0},
        "categories": {"categories": [], "sample_size": 0},
        "keywords": [],
        "summary": {"summary": "ไม่มีความคิดเห็นให้วิเคราะห์", "based_on_comments": 0},
    }


@lru_cache(maxsize=1)
def get_model_service() -> "ModelService | object":
    """Singleton accessor. Returns the mock service transparently
    when a mock NLP mode is selected so routers don't need branching
    logic."""
    if settings.APP_MODE in {"mock", "youtube_mock_nlp"}:
        from app.services.mock_service import MockModelService
        return MockModelService()
    return ModelService()
