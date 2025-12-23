from pathlib import Path
import json
import re

def parse_srt(srt_path: Path) -> list:
    with open(srt_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    blocks = re.split(r'\n\s*\n', content.strip())
    subtitles = []
    
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) >= 3:
            try:
                index = int(lines[0])
                timestamp = lines[1]
                text = '\n'.join(lines[2:])
                subtitles.append({
                    "index": index,
                    "timestamp": timestamp,
                    "text": text
                })
            except (ValueError, IndexError):
                continue
    
    return subtitles

def write_srt(subtitles: list, output_path: Path):
    lines = []
    for sub in subtitles:
        lines.append(str(sub["index"]))
        lines.append(sub["timestamp"])
        lines.append(sub["text"])
        lines.append("")
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def validate_subtitle(srt_path: Path) -> bool:
    try:
        subtitles = parse_srt(srt_path)
        return len(subtitles) > 0
    except Exception:
        return False

def count_speech_segments(json_path: Path) -> tuple:
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        segments = data.get("segments", [])
        total_chars = sum(len(seg.get("text", "")) for seg in segments)
        return len(segments), total_chars
    except Exception:
        return 0, 0
