from pydantic import BaseModel
from typing import List, Optional

class URLRequest(BaseModel):
    url: str

class DownloadRequest(BaseModel):
    url: str
    format_id: str = "best_quality"
    is_audio: bool = False
    start_time: Optional[str] = None
    end_time: Optional[str] = None
