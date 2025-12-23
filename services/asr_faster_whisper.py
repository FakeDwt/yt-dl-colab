from pathlib import Path
import json
from faster_whisper import WhisperModel

def transcribe_audio(
    audio_path: Path,
    output_srt: Path,
    output_json: Path,
    model_size: str = "medium",
    language: str = None,
    device: str = "auto"
):
    if device == "auto":
        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"
    
    compute_type = "float16" if device == "cuda" else "int8"
    
    print(f"[INFO] Loading faster-whisper model: {model_size} on {device} ({compute_type})")
    model = WhisperModel(model_size, device=device, compute_type=compute_type)
    
    print(f"[INFO] Transcribing audio: {audio_path}")
    segments, info = model.transcribe(
        str(audio_path),
        language=language,
        beam_size=5,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=500)
    )
    
    print(f"[INFO] Detected language: {info.language} (probability: {info.language_probability:.2f})")
    
    segments_list = []
    srt_lines = []
    
    for i, segment in enumerate(segments, start=1):
        segments_list.append({
            "id": i,
            "start": segment.start,
            "end": segment.end,
            "text": segment.text.strip()
        })
        
        srt_lines.append(f"{i}")
        srt_lines.append(format_timestamp(segment.start) + " --> " + format_timestamp(segment.end))
        srt_lines.append(segment.text.strip())
        srt_lines.append("")
    
    with open(output_srt, "w", encoding="utf-8") as f:
        f.write("\n".join(srt_lines))
    
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump({
            "language": info.language,
            "language_probability": info.language_probability,
            "segments": segments_list
        }, f, ensure_ascii=False, indent=2)
    
    print(f"[INFO] Transcription complete: {len(segments_list)} segments")

def format_timestamp(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
