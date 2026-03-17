import yt_dlp
import asyncio
import os
import uuid
import imageio_ffmpeg

# الحصول على مسار ملف ffmpeg المدمج مع المكتبة
FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()

def _extract_info(url: str):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
        'impersonate': 'chrome',
        'extractor_args': {
            'youtube': [
                'player_client=android,ios,tv,web',
                'player_skip=webpage'
            ]
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }
    }
    
    cookie_files = ["cookies.txt", "youtube.com_cookies.txt", "cookies.netscape.txt"]
    for cookie_file in cookie_files:
        if os.path.exists(cookie_file):
            ydl_opts['cookiefile'] = cookie_file
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
        'impersonate': 'chrome',
        'extractor_args': {
            'youtube': [
                'player_client=android,ios,tv,web',
                'player_skip=webpage'
            ]
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }
    }

    cookie_files = ["cookies.txt", "youtube.com_cookies.txt", "cookies.netscape.txt"]
    for cookie_file in cookie_files:
        if os.path.exists(cookie_file):
            ydl_opts['cookiefile'] = cookie_file
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
