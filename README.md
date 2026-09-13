# ระบบวิเคราะห์ความคิดเห็นและกระแสของวิดีโอเกมบน YouTube ด้วย NLP
### YouTube Gaming Trend and Sentiment Analysis Using Thai Transformer Models

Full-stack project: React dashboard + FastAPI backend + fine-tuned
WangchanBERTa models for sentiment / emotion / topic classification
of Thai (and English/mixed) YouTube gaming comments. Users never
paste a URL — the dashboard auto-discovers gaming videos through the
YouTube Data API.

---

## 1. Project structure

```
project/
├── backend/
│   ├── app/
│   │   ├── main.py                # FastAPI entrypoint
│   │   ├── config.py               # env-based settings
│   │   ├── models/schemas.py       # Pydantic response models
│   │   ├── routers/                # videos.py, analysis.py, trends.py
│   │   ├── services/
│   │   │   ├── youtube_service.py  # REAL YouTube Data API v3 integration
│   │   │   ├── mock_service.py     # Mock video/comments + heuristic NLP (UI dev only)
│   │   │   ├── model_service.py    # loads real models ONCE, runs the pipeline
│   │   │   ├── cache.py
│   │   │   └── nlp/                # preprocessing, sentiment, emotion, category,
│   │   │                           # keyword_extraction, embedding, summarization, trending
│   │   └── db/                     # SQLAlchemy models + session
│   ├── training/                   # train_sentiment.py, train_emotion.py,
│   │                                # train_category.py, evaluate.py, dataset_sample.csv
│   └── tests/test_api.py
└── frontend/
    └── src/
        ├── api/client.js
        ├── pages/ (Dashboard, VideoAnalysis, ModelEvaluation)
        └── components/ (VideoCard, charts, keyword list, skeletons...)
```

**Execution modes**, controlled by `APP_MODE` in `.env`:

| Mode  | Video source | NLP source | Needs |
|-------|--------------|------------|-------|
| `mock` | `MockYouTubeService` — fixed sample videos/comments | `MockModelService` — keyword-heuristic (deterministic, NOT random) | nothing — good for building/demoing the UI |
| `youtube_mock_nlp` | `YouTubeService` — real YouTube Data API v3 | `MockModelService` — deterministic heuristic NLP | YouTube API key; useful before model checkpoints are trained |
| `live` | `YouTubeService` — real YouTube Data API v3 | `ModelService` — real fine-tuned WangchanBERTa/mT5/Sentence-BERT models | YouTube API key + trained model checkpoints |

The two are completely separate modules so it's always obvious which
one is running — there is no "fake number pretending to be a real
model output" anywhere in the `live` path.

---

## 2. Quick start (UI only, no API key / GPU needed)

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # leave APP_MODE=mock
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 — the dashboard, video analysis page, and
model evaluation page all work against mock data immediately.

To use real YouTube videos and comments before the trained NLP models are
available, set `APP_MODE=youtube_mock_nlp` and provide `YOUTUBE_API_KEY`.
The video data is real, while sentiment/emotion/topic results still use the
deterministic mock NLP service and must be labeled as provisional.

---

## 3. Running for real (`APP_MODE=live`)

### 3.1 Get a YouTube Data API key
1. Go to https://console.cloud.google.com/ → create/select a project.
2. Enable **YouTube Data API v3** (APIs & Services → Library).
3. Create an API key (APIs & Services → Credentials).
4. Put it in `backend/.env`:
   ```
   YOUTUBE_API_KEY=AIza...
   APP_MODE=live
   ```

### 3.2 Prepare the dataset
`backend/training/dataset_sample.csv` is a *tiny* example. For a real
model, collect a proper Thai gaming-comments dataset with columns:

```csv
text,sentiment,emotion,category
"เกมสนุกมาก",positive,joy,gameplay
"ตัวละครใหม่โกงเกินไป",negative,anger,character
```

- `sentiment`: `positive` | `neutral` | `negative`
- `emotion`: `joy` | `anger` | `sadness` | `surprise` | `fear` | `neutral`
- `category`: one or more of the 12 topic labels, semicolon-separated
  for multi-label rows (`character;gameplay`)

Include Thai, English, Thai-English mixed, slang, emoji, and
abbreviations so the model generalizes to real YouTube comments.

### 3.3 Fine-tune the models
```bash
cd backend/training
python train_sentiment.py --data your_dataset.csv --output ../models/sentiment/wangchanberta_sentiment
python train_emotion.py   --data your_dataset.csv --output ../models/emotion/wangchanberta_emotion
python train_category.py  --data your_dataset.csv --output ../models/category/wangchanberta_category
```
Each script performs an 80/10/10 train/validation/test split and
**never touches the test set during training**, per the project
requirement. The held-out test CSV is saved next to the script
(`*_test_holdout.csv`).

### 3.4 Evaluate
```bash
python evaluate.py --task sentiment --model ../models/sentiment/wangchanberta_sentiment --data sentiment_test_holdout.csv
python evaluate.py --task emotion   --model ../models/emotion/wangchanberta_emotion     --data emotion_test_holdout.csv
python evaluate.py --task category  --model ../models/category/wangchanberta_category   --data category_test_holdout.csv
```
Each run prints and saves a JSON report (accuracy, precision, recall,
F1, confusion matrix / per-class metrics for the multi-label
category model). Paste that JSON into the **Model Evaluation** page
in the frontend to render it as tables.

### 3.5 Point the backend at your model folders
`backend/.env`:
```
SENTIMENT_MODEL_PATH=models/sentiment/wangchanberta_sentiment
EMOTION_MODEL_PATH=models/emotion/wangchanberta_emotion
CATEGORY_MODEL_PATH=models/category/wangchanberta_category
DEVICE=cuda   # or cpu
```
Restart the backend — `get_model_service()` loads every model once
at startup (see `app/main.py`'s `preload_models`).

---

## 4. API endpoints

```
GET  /api/videos/trending
GET  /api/videos/latest
GET  /api/videos/most-viewed
GET  /api/videos/most-commented
GET  /api/videos/{video_id}
GET  /api/videos/{video_id}/comments

POST /api/analysis/{video_id}/run         # runs the full NLP pipeline
GET  /api/analysis/{video_id}/sentiment
GET  /api/analysis/{video_id}/emotion
GET  /api/analysis/{video_id}/topics
GET  /api/analysis/{video_id}/keywords
GET  /api/analysis/{video_id}/summary
GET  /api/analysis/{video_id}/trends      # sentiment over past analysis snapshots

GET  /api/gaming-trends                   # trending games / videos / overall sentiment+emotion
```

---

## 5. Design notes / how each spec requirement is met

- **No random demo values in production**: `ModelService.analyze_comments()`
  always aggregates real per-comment model outputs; `MockModelService`
  is a separate, clearly-named class using keyword heuristics (not
  `random.choice`) and is only ever used when `APP_MODE=mock`.
- **Emoji kept for emotion/sentiment, stripped for topics/keywords**:
  see `app/services/nlp/preprocessing.py`.
- **Multi-label topics**: `category.py` uses a sigmoid head + 0.5
  threshold (not softmax) so one comment can hit several categories.
- **Trending = rules, not an LLM**: `app/services/nlp/trending.py`
  compares mention counts between two time windows — no model calls.
- **Models loaded once**: `get_model_service()` / `get_youtube_service()`
  are `lru_cache`d singletons, warmed up in FastAPI's startup event.
- **Caching**: `app/services/cache.py` wraps YouTube API responses
  and fetched comments in a TTL cache to save quota and avoid
  redundant inference.

---

## 6. Testing

```bash
cd backend
APP_MODE=mock pytest
```

---

## 7. Known limitations / next steps for the student

- The bundled `dataset_sample.csv` has ~15 rows — purely to make the
  training scripts runnable end-to-end. Real model quality requires
  a real labeled dataset (hundreds to thousands of rows per class).
- `train_*.py` use `airesearch/wangchanberta-base-att-spm-uncased` as
  the base checkpoint — swap for any other Thai-capable encoder if
  preferred.
- Background-task queuing (Celery/RQ) is not wired up; `/run` executes
  synchronously. For very large comment volumes, move the pipeline
  call in `analysis.py` into a `BackgroundTasks`/task-queue job and
  poll a status endpoint instead.
- `MockYouTubeService`/`MockModelService` are for UI development only
  — do not present their output as real analysis results.
