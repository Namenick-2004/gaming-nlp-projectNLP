"""
Comment-category classifier: multi-label WangchanBERTa over 12 gaming
topics (Gameplay, Character, Weapon, Map, Graphics, Update, Bug,
Ranking, Skin, Price, Performance, Other).

Multi-label -> sigmoid per class + a threshold, NOT softmax, because
one comment can legitimately belong to several categories at once
("ตัวละครใหม่เล่นสนุกมาก แต่สกิลแรงเกินไป" -> Character + Gameplay).
"""
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from app.services.nlp.preprocessing import preprocess_for_category_or_keywords

LABELS = [
    "gameplay", "character", "weapon", "map", "graphics", "update",
    "bug", "ranking", "skin", "price", "performance", "other",
]

THRESHOLD = 0.5


class CategoryModel:
    def __init__(self, model_path: str, device: str = "cpu"):
        self.device = device
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_path, problem_type="multi_label_classification"
        )
        self.model.to(device)
        self.model.eval()

    @torch.no_grad()
    def predict_batch(self, texts: list[str]) -> list[list[str]]:
        results = []
        for start in range(0, len(texts), 32):
            clean = [preprocess_for_category_or_keywords(t) for t in texts[start:start + 32]]
            inputs = self.tokenizer(clean, return_tensors="pt", truncation=True,
                                     max_length=256, padding=True).to(self.device)
            probs = torch.sigmoid(self.model(**inputs).logits).tolist()
            for p in probs:
                labels = [LABELS[i] for i, score in enumerate(p) if score >= THRESHOLD]
                results.append(labels or ["other"])
        return results
