"""
Preprocessing pipeline for raw YouTube comments, following the spec:

    YouTube Comments
        -> Language Detection
        -> Text Cleaning
        -> Emoji Handling
        -> Thai Tokenization
        -> Normalization
        -> Transformer Tokenizer   (done inside each model class, not here)
        -> Model Inference

IMPORTANT: emoji are NOT stripped before emotion analysis. Emoji such
as 😂 😡 😭 ❤️ carry real emotional signal, so we only strip emoji
right before running category classification / keyword extraction,
where they add noise instead of signal.
"""
import re
import emoji
from pythainlp.tokenize import word_tokenize
from pythainlp.util import normalize as thai_normalize

URL_RE = re.compile(r"https?://\S+")
MENTION_RE = re.compile(r"@\w+")
REPEAT_CHAR_RE = re.compile(r"(.)\1{3,}")  # "555555" / "มากกกกก" -> collapse

# Common gaming / internet slang normalization map.
# Extend this table as new slang is discovered in real comment data.
SLANG_MAP = {
    "op": "overpowered",
    "gg": "good game",
    "af": "very",
    "broken": "overpowered",
    "555": "haha",
}


def detect_language(text: str) -> str:
    """Very lightweight heuristic: Thai if it contains Thai script,
    otherwise English/mixed. A real deployment can swap this for
    `langdetect` or `fasttext` without changing the pipeline shape."""
    return "th" if re.search(r"[\u0E00-\u0E7F]", text) else "en"


def clean_text(text: str) -> str:
    text = URL_RE.sub(" ", text)
    text = MENTION_RE.sub(" ", text)
    text = REPEAT_CHAR_RE.sub(r"\1\1\1", text)  # cap long repeats, keep signal
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_slang(text: str) -> str:
    tokens = text.split()
    normalized = [SLANG_MAP.get(tok.lower(), tok) for tok in tokens]
    return " ".join(normalized)


def tokenize_thai(text: str) -> list[str]:
    return word_tokenize(text, engine="newmm")


def preprocess_for_sentiment_or_emotion(raw_text: str) -> str:
    """Keeps emoji intact — emotion/sentiment models need them."""
    text = clean_text(raw_text)
    text = thai_normalize(text)
    text = normalize_slang(text)
    return text


def preprocess_for_category_or_keywords(raw_text: str) -> str:
    """Strips emoji — they add noise to topic/keyword signals."""
    text = clean_text(raw_text)
    text = emoji.replace_emoji(text, replace="")
    text = thai_normalize(text)
    text = normalize_slang(text)
    return text


def clean_generated_text(text: str) -> str:
    """Clean generated model output before returning to the UI.

    This strips Hugging Face special-token markers like <extra_id_0>, removes
    repeated nonsense text patterns, and normalizes spaces so Thai summaries
    read naturally instead of showing broken token artifacts.
    """
    text = text or ""
    text = re.sub(r"<extra_id_\d+>", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"<\s*/?s>", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"(\S)\1{3,}", r"\1\1\1", text)
    text = re.sub(r"(\W)\1{3,}", r"\1\1", text)
    text = text.replace("ค่ะค่ะ", "ค่ะ").replace("ๆๆ", "ๆ")
    text = re.sub(r"\s+([.,!?;:])", r"\1", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text if text else "ยังไม่มีข้อมูลสรุปที่เพียงพอ" 
