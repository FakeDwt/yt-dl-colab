from pathlib import Path
from datetime import datetime
import re

def create_run_directory(run_root: str, source: str) -> Path:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    
    if source.startswith("http"):
        video_id = extract_video_id(source)
        name = f"{timestamp}_{video_id}"
    else:
        video_name = Path(source).stem
        safe_name = re.sub(r'[^\w\-]', '_', video_name)[:50]
        name = f"{timestamp}_{safe_name}"
    
    return Path(run_root) / name

def extract_video_id(url: str) -> str:
    patterns = [
        r'(?:v=|/)([0-9A-Za-z_-]{11}).*',
        r'youtu\.be/([0-9A-Za-z_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return "video"

class RunPaths:
    def __init__(self, run_dir: Path):
        self.run_dir = run_dir
        
        self.input_video = run_dir / "input.mp4"
        self.audio = run_dir / "audio.wav"
        self.subtitle_src = run_dir / "subtitle.src.srt"
        self.subtitle_zh = run_dir / "subtitle.zh.srt"
        self.transcript_json = run_dir / "transcript.json"
        
        self.video_zh_softsub_mkv = run_dir / "video_zh_softsub.mkv"
        self.video_zh_softsub_mp4 = run_dir / "video_zh_softsub.mp4"
        self.video_zh_hardsub_mp4 = run_dir / "video_zh_hardsub.mp4"
        
        self.log_file = run_dir / "pipeline.log"
