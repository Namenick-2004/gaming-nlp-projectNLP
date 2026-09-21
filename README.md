# Sports Comment Analysis with Gemini

เว็บวิเคราะห์ความคิดเห็นวิดีโอกีฬาบน YouTube ด้วย React + FastAPI + Gemini API

## เริ่มใช้งาน

1. ตั้งค่า `backend/.env` ตาม `backend/.env.example`:

```dotenv
YOUTUBE_API_KEY=your_youtube_key
GEMINI_API_KEY=your_gemini_key
GEMINI_MODEL=gemini-3.5-flash-lite
APP_MODE=live
DATABASE_URL=sqlite:///./sports_gemini.db
MAX_COMMENTS_PER_ANALYSIS=100
GEMINI_TIMEOUT_SECONDS=90
CACHE_TTL_SECONDS=1800
```

สร้างคีย์ Gemini ได้ที่ https://aistudio.google.com/apikey
เก็บคีย์เฉพาะ backend/.env (ถูก ignore โดย Git) และรีสตาร์ต backend หลังแก้ไข
ห้ามใส่คีย์ใน React หรือ environment ที่ขึ้นต้นด้วย VITE_

2. รัน backend (PowerShell):

```powershell
cd backend
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

3. รัน frontend อีก terminal:

```powershell
cd frontend
npm install
npm run dev
```

เปิด http://localhost:5173

## การวิเคราะห์

- YouTube API ค้นหาวิดีโอหมวด Sports (17) และดึงความคิดเห็น
- Backend ส่งข้อความตัวอย่างสูงสุด 100 ความคิดเห็น ความยาวสูงสุด 2,000 ตัวอักษรต่อความคิดเห็น ไปยัง Gemini
- Gemini ระบุ sentiment, emotion, หัวข้อกีฬา, คำสำคัญ และสรุปภาษาไทย
- Backend ตรวจรูปแบบ JSON และตรวจว่ามีผลสำหรับทุกความคิดเห็น ก่อนคำนวณเปอร์เซ็นต์และบันทึกผล
- จำนวนคำสำคัญนับจากความคิดเห็นจริง ไม่สร้างเปอร์เซ็นต์การเติบโตเมื่อไม่มีข้อมูลเปรียบเทียบ
- ผลใหม่เก็บใน sports_gemini.db เพื่อไม่ปะปนกับผลจากระบบเดิม
- ไม่โหลดหรือรันโมเดลในเครื่อง ไม่ต้องใช้ GPU, PyTorch หรือ Transformers
- APP_MODE=mock ใช้เฉพาะวิดีโอตัวอย่าง การวิเคราะห์ยังใช้ Gemini และต้องมีคีย์
- หากไม่มีคีย์ เว็บยังดูรายการวิดีโอได้ แต่การวิเคราะห์จะแจ้งวิธีตั้งค่า
- กรณีโควตาหมด คีย์ใช้ไม่ได้ เครือข่ายขัดข้อง หรือผลไม่ครบ จะแจ้งข้อผิดพลาดและไม่บันทึกผลปลอม

GEMINI_MODEL เปลี่ยนได้ตามโมเดลที่คีย์รองรับ โดยต้องรองรับ structured JSON output
เอกสารอ้างอิง: https://ai.google.dev/gemini-api/docs/generate-content/structured-output

## API

- GET / : สถานะระบบและสถานะการตั้งค่า Gemini (ไม่ส่งคีย์)
- GET /api/videos/trending, /latest, /most-viewed, /most-commented
- GET /api/videos/{video_id}, /api/videos/{video_id}/comments
- GET /api/sports-trends
- POST /api/analysis/{video_id}/run
- GET /api/analysis/{video_id}/sentiment, /emotion, /topics, /keywords, /summary, /trends

## ทดสอบ

```powershell
cd backend
.\venv\Scripts\python.exe -m pip install pytest
$env:APP_MODE='mock'
$env:DATABASE_URL='sqlite:///./gemini_test.db'
.\venv\Scripts\python.exe -m pytest -q
```

Tests จำลองคำตอบ Gemini จึงไม่ใช้คีย์หรือโควตาจริง ครอบคลุมการส่งคำขอ การคำนวณผล
รูปแบบคำตอบ คีย์ที่หายไป ข้อผิดพลาด API และเส้นทางบันทึกผล
