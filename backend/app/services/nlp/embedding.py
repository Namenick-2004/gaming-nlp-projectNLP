"""
Sentence embeddings for:
  - similarity search between comments
  - clustering comments into emergent (unlabeled) topics
Uses a multilingual Sentence-BERT model so Thai / English / mixed
comments all land in the same vector space.
"""
import numpy as np
from sentence_transformers import SentenceTransformer

try:
    import hdbscan
except ImportError:  # optional dependency
    hdbscan = None
from sklearn.cluster import KMeans


class EmbeddingService:
    def __init__(self, model_name: str, device: str = "cpu"):
        self.model = SentenceTransformer(model_name, device=device)

    def embed(self, texts: list[str]) -> np.ndarray:
        return self.model.encode(texts, show_progress_bar=False, normalize_embeddings=True)

    def cluster_topics(self, texts: list[str], method: str = "hdbscan", n_clusters: int = 8):
        """Groups comments into emergent topics that were not part of
        the fixed category taxonomy. Falls back to KMeans if HDBSCAN
        isn't installed."""
        vectors = self.embed(texts)
        if method == "hdbscan" and hdbscan is not None:
            clusterer = hdbscan.HDBSCAN(min_cluster_size=5, metric="euclidean")
            labels = clusterer.fit_predict(vectors)
        else:
            k = min(n_clusters, max(1, len(texts) // 5) or 1)
            labels = KMeans(n_clusters=k, n_init="auto", random_state=42).fit_predict(vectors)

        clusters: dict[int, list[str]] = {}
        for text, label in zip(texts, labels):
            clusters.setdefault(int(label), []).append(text)
        return clusters
