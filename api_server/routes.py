from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from fastapi.responses import FileResponse
from schemas import URLRequest
from downloader import get_video_info, download_media
import os

router = APIRouter()

def cleanup_file(filepath: str):
    """حذف الملف من السيرفر بعد إرساله للمستخدم لتوفير المساحة"""
    if os.path.exists(filepath):
        os.remove(filepath)

@router.post("/info")
async def get_info(req: URLRequest):
    try:
        info = await get_video_info(req.url)
        if not info:
            raise HTTPException(status_code=400, detail="Could not fetch video info")
        
        # تنسيق الجودات بشكل احترافي لتطبيق الهاتف
        formats = []
        for f in info.get('formats', []):
            if f.get('vcodec') != 'none':
                formats.append({
                    "format_id": f.get('format_id'),
                    "resolution": f.get('resolution') or f"{f.get('height', 0)}p",
                    "ext": f.get('ext'),
                    "filesize": f.get('filesize') or f.get('filesize_approx') or 0,
                    "tbr": f.get('tbr') or 0
                })
        
        # ترتيب الجودات من الأفضل للأقل
        formats = sorted(formats, key=lambda x: x['tbr'], reverse=True)
        
        return {
            "title": info.get('title'),
            "duration": info.get('duration_string'),
            "thumbnail": info.get('thumbnail'),
            "formats": formats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download")
async def download_video(
    background_tasks: BackgroundTasks,
    url: str = Query(..., description="رابط الفيديو"),
    format_id: str = Query("best_quality", description="معرف الجودة"),
    is_audio: bool = Query(False, description="تحميل كصوت فقط"),
    start_time: str = Query(None, description="وقت البداية"),
    end_time: str = Query(None, description="وقت النهاية")
):
    try:
        filepath = await download_media(
            url=url,
            format_id=format_id,
            is_audio=is_audio,
            start_time=start_time,
            end_time=end_time
        )
        
        # إرسال الملف كـ Stream لتطبيق الهاتف، ثم حذفه فوراً من السيرفر!
        background_tasks.add_task(cleanup_file, filepath)
        return FileResponse(
            path=filepath, 
            filename=f"video_{format_id}.{filepath.split('.')[-1]}",
            media_type='application/octet-stream'
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
