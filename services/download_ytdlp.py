from pathlib import Path
import yt_dlp

def download_video(url: str, output_path: Path, cookies_path: str = None):
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': str(output_path.with_suffix('')),
        'merge_output_format': 'mp4',
        'quiet': False,
        'no_warnings': False,
    }
    
    if cookies_path:
        ydl_opts['cookiefile'] = cookies_path
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    if not output_path.exists():
        possible_path = output_path.with_suffix('.mp4')
        if possible_path.exists():
            return
        raise FileNotFoundError(f"Download completed but output not found at {output_path}")
