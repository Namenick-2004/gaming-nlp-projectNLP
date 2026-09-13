"""
Keyword extraction using KeyBERT + a multilingual sentence embedding
model (NOT plain word counting). We also track how often each phrase
recurs across the comment set to compute a "Trend %" figure.
"""
from collections import Counter
from keybert import KeyBERT
from app.services.nlp.preprocessing import preprocess_for_category_or_keywords


class KeywordExtractor:
    def __init__(self, sentence_transformer_model):
        # Reuse the already-loaded SentenceTransformer for embeddings
        # so we don't load a second copy of the model into memory.
        self.kw_model = KeyBERT(model=sentence_transformer_model)

    def extract(self, comments: list[str], top_n: int = 10,
                previous_period_keywords: dict[str, int] | None = None) -> list[dict]:
        cleaned = [preprocess_for_category_or_keywords(c) for c in comments]
        joined = " ".join(cleaned)

        # KeyBERT gives us (phrase, relevance_score) pairs
        candidates = self.kw_model.extract_keywords(
            joined,
            keyphrase_ngram_range=(1, 2),
            stop_words=None,   # pythainlp/thai stopwords handled upstream
            top_n=top_n * 2,
            use_mmr=True,
            diversity=0.5,
        )

        # Count literal occurrences across comments for frequency / trend
        counts = Counter()
        for phrase, _ in candidates:
            counts[phrase] = sum(phrase in c for c in cleaned)

        results = []
        prev = previous_period_keywords or {}
        for phrase, score in candidates[:top_n]:
            count = counts[phrase]
            prev_count = prev.get(phrase, 0)
            trend = ((count - prev_count) / prev_count * 100) if prev_count else 100.0
            results.append({
                "keyword": phrase,
                "count": count,
                "importance": round(float(score), 4),
                "trend_percent": round(trend, 1),
            })
        return sorted(results, key=lambda x: x["importance"], reverse=True)
