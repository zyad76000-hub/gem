from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from routes import router
import os

app = FastAPI(
    title="Video Downloader Pro API",
    description="واجهة برمجة تطبيقات احترافية لتحميل الفيديوهات لتطبيقات الهواتف.",
    version="1.0.0"
)

# السماح لتطبيقات الهاتف (CORS) بالاتصال بالسيرفر
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")

@app.get("/", response_class=HTMLResponse)
async def root():
    html_path = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>مرحباً بك! يرجى إنشاء ملف index.html</h1>"

