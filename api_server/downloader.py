import yt_dlp
import asyncio
import os
import uuid
import imageio_ffmpeg
import shutil

# الحصول على مسار ملف ffmpeg المدمج مع المكتبة
FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()

def _extract_info(url: str):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
        'extractor_args': {
            'youtube': [
                'player_client=android,ios',
                'player_skip=webpage'
            ]
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
            'Accept-Language': 'en-US,en;q=0.9',
        }
    }
    
    base_dirs = [os.getcwd(), os.path.dirname(__file__), os.path.dirname(os.path.dirname(__file__))]
    cookie_files = ["cookies.txt", "youtube.com_cookies.txt", "cookies.netscape.txt"]
    
    cookie_found = False
    for base_dir in base_dirs:
        for cookie_file in cookie_files:
            full_path = os.path.join(base_dir, cookie_file)
            if os.path.exists(full_path):
                tmp_cookie_path = os.path.join('/tmp', f"tmp_{cookie_file}")
                try:
                    shutil.copy2(full_path, tmp_cookie_path)
                    ydl_opts['cookiefile'] = tmp_cookie_path
                except Exception:
                    ydl_opts['cookiefile'] = full_path
                cookie_found = True
                break
        if cookie_found:
            break
            
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)

async def get_video_info(url: str):
    return await asyncio.to_thread(_extract_info, url)

def _download(url: str, format_id: str, is_audio: bool = False, start_time: str = None, end_time: str = None):
    # استخدام مجلد /tmp لأنه المجلد الوحيد القابل للكتابة في Vercel Serverless
    download_dir = "/tmp/downloads"
    os.makedirs(download_dir, exist_ok=True)
    filename = f"{download_dir}/{uuid.uuid4()}"

    actual_format = format_id
    if format_id == "best_quality":
        actual_format = "bestvideo[format_id!*=watermark]+bestaudio/best[format_id!*=watermark]/best"
    elif format_id != "best":
        actual_format = f"{format_id}+bestaudio/best"

    ydl_opts = {
        'format': actual_format if not is_audio else 'bestaudio/best',
        'outtmpl': f'{filename}.%(ext)s',
        'quiet': True,
        'noplaylist': True,
        'no_warnings': True,
        'merge_output_format': 'mp4',
        'ffmpeg_location': FFMPEG_PATH, # تحديد مسار ffmpeg صراحة
        'extractor_args': {
            'youtube': [
                'player_client=android,ios',
                'player_skip=webpage'
            ]
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
            'Accept-Language': 'en-US,en;q=0.9',
        }
    }

    base_dirs = [os.getcwd(), os.path.dirname(__file__), os.path.dirname(os.path.dirname(__file__))]
    cookie_files = ["cookies.txt", "youtube.com_cookies.txt", "cookies.netscape.txt"]
    
    cookie_found = False
    for base_dir in base_dirs:
        for cookie_file in cookie_files:
            full_path = os.path.join(base_dir, cookie_file)
            if os.path.exists(full_path):
                tmp_cookie_path = os.path.join('/tmp', f"tmp_{cookie_file}")
                try:
                    shutil.copy2(full_path, tmp_cookie_path)
                    ydl_opts['cookiefile'] = tmp_cookie_path
                except Exception:
                    ydl_opts['cookiefile'] = full_path
                cookie_found = True
                break
        if cookie_found:
            break

    if start_time and end_time:
        ydl_opts['external_downloader'] = FFMPEG_PATH # استخدام ffmpeg المدمج للقص
        ydl_opts['external_downloader_args'] = {'ffmpeg_i': ['-ss', start_time, '-to', end_time]}

    if is_audio:
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        ext = 'mp3' if is_audio else info.get('ext', 'mp4')
        return f"{filename}.{ext}"

async def download_media(url: str, format_id: str, is_audio: bool = False, start_time: str = None, end_time: str = None):
    return await asyncio.to_thread(_download, url, format_id, is_audio, start_time, end_time)
