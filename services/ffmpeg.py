from pathlib import Path
import subprocess

def run_ffmpeg(args: list, description: str = "FFmpeg operation"):
    cmd = ["ffmpeg", "-y"] + args
    print(f"[INFO] {description}...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg failed: {result.stderr}")

def extract_audio(video_path: Path, audio_path: Path):
    run_ffmpeg([
        "-i", str(video_path),
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        str(audio_path)
    ], "Extracting audio")

def create_softsub_mkv(video_path: Path, subtitle_path: Path, output_path: Path):
    run_ffmpeg([
        "-i", str(video_path),
        "-i", str(subtitle_path),
        "-c", "copy",
        "-c:s", "srt",
        "-metadata:s:s:0", "language=chi",
        str(output_path)
    ], "Creating soft-sub MKV")

def create_softsub_mp4(video_path: Path, subtitle_path: Path, output_path: Path):
    run_ffmpeg([
        "-i", str(video_path),
        "-i", str(subtitle_path),
        "-c:v", "copy",
        "-c:a", "copy",
        "-c:s", "mov_text",
        "-metadata:s:s:0", "language=chi",
        str(output_path)
    ], "Creating soft-sub MP4")

def create_hardsub_mp4(video_path: Path, subtitle_path: Path, output_path: Path):
    subtitle_filter = f"subtitles={str(subtitle_path).replace('\\', '/').replace(':', '\\\\:')}"
    run_ffmpeg([
        "-i", str(video_path),
        "-vf", subtitle_filter,
        "-c:a", "copy",
        str(output_path)
    ], "Creating hard-sub MP4 (this may take a while)")
