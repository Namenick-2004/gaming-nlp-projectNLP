"""
Sentiment classifier: fine-tuned WangchanBERTa (3-class).
Loaded once (see model_service.py) and reused for every request.
"""
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from app.services.nlp.preprocessing import preprocess_for_sentiment_or_emotion
from pythainlp.tokenize import word_tokenize

# Pongsathorn/wangchanberta-base-sentiment documents this exact ordering:
# class 0 = pos, class 1 = neu, class 2 = neg.
PONGSATHORN_SENTIMENT_MODEL = "Pongsathorn/wangchanberta-base-sentiment"
PONGSATHORN_LABELS = ["positive", "neutral", "negative"]


class SentimentModel:
    def __init__(self, model_path: str, device: str = "cpu"):
        self.device = device
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
        self.model.to(device)
        self.model.eval()
        if model_path.rstrip("/") == PONGSATHORN_SENTIMENT_MODEL:
            self.labels = PONGSATHORN_LABELS
        else:
            # The project's locally trained checkpoints use this ordering.
            self.labels = ["negative", "neutral", "positive"]

    @staticmethod
    def _prepare_text(text: str) -> str:
        clean = preprocess_for_sentiment_or_emotion(text)
        # This checkpoint was trained with Thai word segmentation. Joining the
        # tokens with spaces mirrors the model author's documented inference.
        return " ".join(word_tokenize(clean, engine="longest"))

    @torch.no_grad()
    def predict(self, text: str) -> dict:
        clean = self._prepare_text(text)
        inputs = self.tokenizer(clean, return_tensors="pt", truncation=True, max_length=256).to(self.device)
        logits = self.model(**inputs).logits
        probs = torch.softmax(logits, dim=-1).squeeze().tolist()
        top_idx = int(torch.tensor(probs).argmax())
        return {"label": self.labels[top_idx], "confidence": round(float(probs[top_idx]), 4)}

    @torch.no_grad()
    def predict_batch(self, texts: list[str]) -> list[dict]:
        results = []
        for start in range(0, len(texts), 32):
            clean = [self._prepare_text(t) for t in texts[start:start + 32]]
            inputs = self.tokenizer(clean, return_tensors="pt", truncation=True,
                                     max_length=256, padding=True).to(self.device)
            probs = torch.softmax(self.model(**inputs).logits, dim=-1).tolist()
            for p in probs:
                idx = p.index(max(p))
                results.append({"label": self.labels[idx], "confidence": round(p[idx], 4)})
        return results
