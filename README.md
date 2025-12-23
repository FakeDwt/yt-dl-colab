# YouTube Video Translation Pipeline (v1)

自动化视频翻译流水线：下载 YouTube 视频 → ASR 转录 → 翻译成中文 → 输出多版本字幕视频。

## 功能特性

- **输入源**：YouTube URL 或本地视频文件
- **ASR**：faster-whisper（支持 GPU 加速）
- **翻译**：OpenAI 兼容接口（支持 GPT-4/Claude/自建网关等）
- **输出**：硬字幕 MP4（烧录字幕，通用兼容）
- **断点续跑**：所有中间产物落盘，支持失败后继续
- **Google Colab 友好**：设计用于 Colab + Google Drive

## 快速开始（Google Colab）

### 1. 挂载 Google Drive
```python
from google.colab import drive
drive.mount('/content/drive')
```

### 2. 安装依赖
```bash
!apt-get update && apt-get install -y ffmpeg
!pip install -r requirements.txt
```

### 3. 运行流水线
```bash
!python app.py \
  --url "https://www.youtube.com/watch?v=VIDEO_ID" \
  --run_root "/content/drive/MyDrive/youtube视频/runs" \
  --openai_api_key "YOUR_API_KEY"
```

## 命令行参数

### 输入源（二选一）
- `--url`：YouTube 视频链接
- `--input_video`：本地视频文件路径

### 目录配置
- `--run_root`：运行根目录（默认：`/content/drive/MyDrive/youtube视频/runs`）
- `--run_dir`：指定完整运行目录（覆盖自动创建）

### ASR 配置
- `--asr_model`：模型大小（默认：`medium`）
  - 可选：`tiny`, `base`, `small`, `medium`, `large-v2`, `large-v3`
- `--asr_language`：源语言（默认：`auto`）
- `--asr_device`：设备（默认：`auto`，自动检测 GPU）

### 翻译配置
- `--openai_api_key`：API 密钥（或设置 `OPENAI_API_KEY` 环境变量）
- `--openai_base_url`：API 基础 URL（或设置 `OPENAI_BASE_URL` 环境变量）
- `--openai_model`：模型名称（默认：`gpt-4o-mini`）

### 其他配置
- `--cookies`：cookies.txt 文件路径（用于受限视频）
- `--outputs`：输出格式（默认：`hardsub_mp4`，一般不需要修改）

### 控制选项
- `--force`：强制重跑所有步骤
- `--force_steps`：强制重跑指定步骤（逗号分隔）

## 输出文件结构

```
runs/
└── 2025-12-24_033000_VIDEO_ID/
    ├── input.mp4              # 输入视频
    ├── audio.wav              # 提取的音频
    ├── subtitle.src.srt       # 源语言字幕
    ├── subtitle.zh.srt        # 中文字幕
    ├── transcript.json        # ASR 详细结果
    └── video_zh_hardsub.mp4   # 硬字幕 MP4（最终输出）
```

## 断点续跑

流水线会自动检测已存在的输出文件并跳过对应步骤。如需重跑某步骤：

```bash
# 重跑翻译步骤
!python app.py --url "..." --force_steps "translate"

# 重跑所有步骤
!python app.py --url "..." --force
```

## 环境变量配置

可以在 Colab 中设置环境变量避免每次传参：

```python
import os
os.environ['OPENAI_API_KEY'] = 'your-key-here'
os.environ['OPENAI_BASE_URL'] = 'https://api.openai.com/v1'
```

## 注意事项

1. **GPU 加速**：Colab 免费版提供 T4 GPU，ASR 会自动使用
2. **存储空间**：确保 Google Drive 有足够空间（视频 + 中间产物）
3. **API 成本**：翻译会调用 OpenAI API，注意配额和成本
4. **受限视频**：需要 cookies.txt（从浏览器导出）

## v2 计划（未实现）

- 中文配音（TTS）
- 背景音乐保留（源分离）
- 严格时间对齐
- 多语言翻译
- 批量处理
