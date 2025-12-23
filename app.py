#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path
from pipeline.runner import PipelineRunner
from pipeline.paths import create_run_directory

def main():
    parser = argparse.ArgumentParser(description="YouTube Video Translation Pipeline (v1)")
    
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--url", help="YouTube URL to download")
    input_group.add_argument("--input_video", help="Path to existing video file")
    
    parser.add_argument("--run_root", default="/content/drive/MyDrive/youtube视频/runs",
                        help="Root directory for runs (default: %(default)s)")
    parser.add_argument("--run_dir", help="Specific run directory (overrides auto-creation)")
    parser.add_argument("--cookies", help="Path to cookies.txt file for yt-dlp")
    
    parser.add_argument("--asr_model", default="medium", 
                        choices=["tiny", "base", "small", "medium", "large-v2", "large-v3"],
                        help="Faster-whisper model size (default: %(default)s)")
    parser.add_argument("--asr_language", default="auto", 
                        help="Source language for ASR (default: auto-detect)")
    parser.add_argument("--asr_device", default="auto",
                        choices=["auto", "cuda", "cpu"],
                        help="Device for ASR (default: auto)")
    
    parser.add_argument("--translate_provider", default="openai_compatible",
                        help="Translation provider (default: %(default)s)")
    parser.add_argument("--openai_api_key", help="OpenAI API key (or set OPENAI_API_KEY env)")
    parser.add_argument("--openai_base_url", help="OpenAI base URL (or set OPENAI_BASE_URL env)")
    parser.add_argument("--openai_model", default="gpt-4o-mini",
                        help="OpenAI model name (default: %(default)s)")
    
    parser.add_argument("--outputs", default="hardsub_mp4",
                        help="Comma-separated output formats (default: %(default)s)")
    parser.add_argument("--force", action="store_true",
                        help="Force re-run all steps (overwrite existing outputs)")
    parser.add_argument("--force_steps", help="Force re-run specific steps (comma-separated)")
    
    args = parser.parse_args()
    
    if args.run_dir:
        run_dir = Path(args.run_dir)
    else:
        run_dir = create_run_directory(args.run_root, args.url or args.input_video)
    
    run_dir.mkdir(parents=True, exist_ok=True)
    print(f"[INFO] Run directory: {run_dir}")
    
    config = {
        "url": args.url,
        "input_video": args.input_video,
        "cookies": args.cookies,
        "asr_model": args.asr_model,
        "asr_language": args.asr_language,
        "asr_device": args.asr_device,
        "translate_provider": args.translate_provider,
        "openai_api_key": args.openai_api_key,
        "openai_base_url": args.openai_base_url,
        "openai_model": args.openai_model,
        "outputs": [x.strip() for x in args.outputs.split(",")],
        "force": args.force,
        "force_steps": [x.strip() for x in args.force_steps.split(",")] if args.force_steps else []
    }
    
    runner = PipelineRunner(run_dir, config)
    
    try:
        runner.run()
        print("\n[SUCCESS] Pipeline completed!")
        print(f"[INFO] All outputs are in: {run_dir}")
    except Exception as e:
        print(f"\n[ERROR] Pipeline failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
