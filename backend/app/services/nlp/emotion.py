"""
Emotion classifier: WangchanBERTa fine-tuned for 6-class emotion
(joy, anger, sadness, surprise, fear, neutral).
"""
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from app.services.nlp.preprocessing import preprocess_for_sentiment_or_emotion

LABELS = ["joy", "anger", "sadness", "surprise", "fear", "neutral"]


class EmotionModel:
    def __init__(self, model_path: str, device: str = "cpu"):
        self.device = device
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
        self.model.to(device)
        self.model.eval()

    @torch.no_grad()
    def predict_batch(self, texts: list[str]) -> list[dict]:
        """Returns the full probability distribution per comment so the
        caller can aggregate a dashboard-level percentage breakdown."""
        results = []
        for start in range(0, len(texts), 32):
            clean = [preprocess_for_sentiment_or_emotion(t) for t in texts[start:start + 32]]
            inputs = self.tokenizer(clean, return_tensors="pt", truncation=True,
                                     max_length=256, padding=True).to(self.device)
            probs = torch.softmax(self.model(**inputs).logits, dim=-1).tolist()
            results.extend(dict(zip(LABELS, p)) for p in probs)
        return results
