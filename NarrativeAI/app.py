import os
import uvicorn
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from generation_engine import generate_narrative_response

# إعداد المسارات
BASE_DIR = Path(__file__).resolve().parent
MEDIA_DIR = BASE_DIR / "media_files"
VIDEO_PATH = MEDIA_DIR / "the_last_kingdom_s01e01.mp4"

app = FastAPI(title="AI Narrative Continuity Companion")

# إعداد القوالب
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    """عرض الواجهة الرئيسية."""
    return templates.TemplateResponse(request, "index.html", {})

@app.get("/video")
def video_endpoint(request: Request):
    """
    مسار مخصص لبث الفيديو بطريقة آمنة تمنع استنزاف موارد النظام (File Descriptors).
    """
    if not VIDEO_PATH.exists():
        return {"error": "Video file not found"}

    file_size = VIDEO_PATH.stat().st_size
    
    def iter_file():
        with open(VIDEO_PATH, "rb") as f:
            while chunk := f.read(1024 * 1024):  # قراءة 1 ميجابايت في كل مرة
                yield chunk

    return StreamingResponse(
        iter_file(),
        media_type="video/mp4",
        headers={
            "Content-Length": str(file_size),
            "Accept-Ranges": "bytes",
        }
    )

@app.get("/api/ask")
async def ask_question(q: str, timestamp: float):
    """API للتعامل مع استفسارات المستخدم."""
    try:
        answer, context = generate_narrative_response(q, timestamp)
        return {"answer": answer, "context": context}
    except Exception as e:
        return {"answer": f"Error processing query: {str(e)}", "context": "Error during database query."}

if __name__ == "__main__":
    print("=========================================================")
    print("Server starting on http://127.0.0.1:8005")
    print("=========================================================")
    uvicorn.run("main:app", host="127.0.0.1", port=8005, reload=True)