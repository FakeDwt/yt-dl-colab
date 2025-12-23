from pathlib import Path
from typing import Dict, Any
from .paths import RunPaths
from services.download_ytdlp import download_video
from services.ffmpeg import extract_audio, create_hardsub_mp4
from services.asr_faster_whisper import transcribe_audio
from services.translate_openai_compatible import translate_subtitle
from services.subtitle import validate_subtitle, count_speech_segments
import shutil

class PipelineRunner:
    def __init__(self, run_dir: Path, config: Dict[str, Any]):
        self.run_dir = run_dir
        self.config = config
        self.paths = RunPaths(run_dir)
        
    def should_run_step(self, step_name: str, output_path: Path) -> bool:
        if self.config["force"]:
            return True
        if step_name in self.config["force_steps"]:
            return True
        if not output_path.exists():
            return True
        print(f"[SKIP] {step_name}: output already exists at {output_path}")
        return False
    
    def run(self):
        print("\n=== Step 1: Get Video ===")
        if self.should_run_step("get_video", self.paths.input_video):
            if self.config["url"]:
                print(f"[INFO] Downloading from URL: {self.config['url']}")
                download_video(
                    url=self.config["url"],
                    output_path=self.paths.input_video,
                    cookies_path=self.config.get("cookies")
                )
            elif self.config["input_video"]:
                print(f"[INFO] Copying video from: {self.config['input_video']}")
                shutil.copy2(self.config["input_video"], self.paths.input_video)
            print(f"[DONE] Video ready at: {self.paths.input_video}")
        
        print("\n=== Step 2: Extract Audio ===")
        if self.should_run_step("extract_audio", self.paths.audio):
            extract_audio(self.paths.input_video, self.paths.audio)
            print(f"[DONE] Audio extracted to: {self.paths.audio}")
        
        print("\n=== Step 3: ASR (faster-whisper) ===")
        if self.should_run_step("asr", self.paths.subtitle_src):
            transcribe_audio(
                audio_path=self.paths.audio,
                output_srt=self.paths.subtitle_src,
                output_json=self.paths.transcript_json,
                model_size=self.config["asr_model"],
                language=self.config["asr_language"] if self.config["asr_language"] != "auto" else None,
                device=self.config["asr_device"]
            )
            print(f"[DONE] Transcription saved to: {self.paths.subtitle_src}")
        
        print("\n=== Step 4: Speech Detection ===")
        segment_count, total_chars = count_speech_segments(self.paths.transcript_json)
        print(f"[INFO] Detected {segment_count} speech segments, {total_chars} characters")
        if segment_count < 5 or total_chars < 50:
            print("[WARN] Very little speech detected, translation may not be meaningful")
        
        print("\n=== Step 5: Translate to Chinese ===")
        if self.should_run_step("translate", self.paths.subtitle_zh):
            translate_subtitle(
                input_srt=self.paths.subtitle_src,
                output_srt=self.paths.subtitle_zh,
                api_key=self.config.get("openai_api_key"),
                base_url=self.config.get("openai_base_url"),
                model=self.config["openai_model"]
            )
            print(f"[DONE] Translation saved to: {self.paths.subtitle_zh}")
        
        print("\n=== Step 6: Generate Hard-sub MP4 ===")
        if self.should_run_step("hardsub_mp4", self.paths.video_zh_hardsub_mp4):
            create_hardsub_mp4(
                video_path=self.paths.input_video,
                subtitle_path=self.paths.subtitle_zh,
                output_path=self.paths.video_zh_hardsub_mp4
            )
            print(f"[DONE] Hard-sub MP4: {self.paths.video_zh_hardsub_mp4}")
