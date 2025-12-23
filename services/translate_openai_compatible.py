from pathlib import Path
import os
from openai import OpenAI
from services.subtitle import parse_srt, write_srt

def translate_subtitle(
    input_srt: Path,
    output_srt: Path,
    api_key: str = None,
    base_url: str = None,
    model: str = "gpt-4o-mini"
):
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    base_url = base_url or os.getenv("OPENAI_BASE_URL")
    
    if not api_key:
        raise ValueError("OpenAI API key not provided (use --openai_api_key or OPENAI_API_KEY env)")
    
    client_kwargs = {"api_key": api_key}
    if base_url:
        client_kwargs["base_url"] = base_url
    
    client = OpenAI(**client_kwargs)
    
    print(f"[INFO] Translating subtitle using model: {model}")
    subtitles = parse_srt(input_srt)
    
    if not subtitles:
        raise ValueError(f"No valid subtitles found in {input_srt}")
    
    batch_size = 20
    translated_subtitles = []
    
    for i in range(0, len(subtitles), batch_size):
        batch = subtitles[i:i+batch_size]
        print(f"[INFO] Translating batch {i//batch_size + 1}/{(len(subtitles)-1)//batch_size + 1}")
        
        texts = [sub["text"] for sub in batch]
        prompt = build_translation_prompt(texts)
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a professional subtitle translator. Translate the following subtitles to Chinese. Keep the same number of lines and preserve timing. Only output the translated text, one per line, without numbering."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        translated_texts = response.choices[0].message.content.strip().split('\n')
        translated_texts = [t.strip() for t in translated_texts if t.strip()]
        
        if len(translated_texts) != len(batch):
            print(f"[WARN] Translation count mismatch: expected {len(batch)}, got {len(translated_texts)}")
            translated_texts = translated_texts[:len(batch)] + [""] * (len(batch) - len(translated_texts))
        
        for j, sub in enumerate(batch):
            translated_subtitles.append({
                "index": sub["index"],
                "timestamp": sub["timestamp"],
                "text": translated_texts[j] if j < len(translated_texts) else sub["text"]
            })
    
    write_srt(translated_subtitles, output_srt)
    print(f"[INFO] Translation complete: {len(translated_subtitles)} subtitles")

def build_translation_prompt(texts: list) -> str:
    return "\n".join(f"{i+1}. {text}" for i, text in enumerate(texts))
