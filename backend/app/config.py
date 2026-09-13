"""
Central application configuration.
Loaded once from environment variables / .env file.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # "mock" -> MockYouTubeService + MockModelService (no internet / GPU needed)
    # "youtube_mock_nlp" -> real YouTube API + MockModelService (API key only)
    # "live" -> RealYouTubeService + real HuggingFace models
    APP_MODE: str = "mock"

    YOUTUBE_API_KEY: str = ""

    DATABASE_URL: str = "sqlite:///./gaming_nlp.db"

    SENTIMENT_MODEL_PATH: str = "models/sentiment/wangchanberta_sentiment"
    EMOTION_MODEL_PATH: str = "models/emotion/wangchanberta_emotion"
    CATEGORY_MODEL_PATH: str = "models/category/wangchanberta_category"
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    SUMMARIZATION_MODEL_NAME: str = "google/mt5-small"

    DEVICE: str = "cpu"
    MAX_COMMENTS_PER_ANALYSIS: int = 100
    CACHE_TTL_SECONDS: int = 1800


settings = Settings()
