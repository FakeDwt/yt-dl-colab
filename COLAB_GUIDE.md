# Colab 运行完整指引

## 前置准备

1. **Google 账号**：确保有 Google Drive 访问权限
2. **OpenAI API Key**：准备好翻译用的 API 密钥
3. **代码上传**：将本地代码上传到 GitHub 或直接上传到 Google Drive

---

## 方案 A：从 GitHub 运行（推荐）

### 1. 上传代码到 GitHub
在本地项目目录执行：
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

### 2. 在 Colab 运行

打开 Google Colab：https://colab.research.google.com/

#### Cell 1：挂载 Drive
```python
from google.colab import drive
drive.mount('/content/drive')
```

#### Cell 2：克隆代码
```bash
!git clone YOUR_GITHUB_REPO_URL /content/yt-dl-colab
%cd /content/yt-dl-colab
```

#### Cell 3：安装依赖
```bash
!apt-get update && apt-get install -y ffmpeg
!pip install -q -r requirements.txt
```

#### Cell 4：配置 API（方式 1：环境变量）
```python
import os
os.environ['OPENAI_API_KEY'] = 'sk-your-key-here'
```

#### Cell 5：运行流水线
```bash
!python app.py \
  --url "https://www.youtube.com/watch?v=VIDEO_ID" \
  --run_root "/content/drive/MyDrive/youtube视频/runs"
```

---

## 方案 B：从 Google Drive 运行

### 1. 上传代码到 Drive
将整个 `yt-dl-colab` 文件夹上传到 Google Drive，例如：
```
/content/drive/MyDrive/projects/yt-dl-colab/
```

### 2. 在 Colab 运行

#### Cell 1：挂载 Drive
```python
from google.colab import drive
drive.mount('/content/drive')
```

#### Cell 2：切换到项目目录
```bash
%cd /content/drive/MyDrive/projects/yt-dl-colab
```

#### Cell 3：安装依赖
```bash
!apt-get update && apt-get install -y ffmpeg
!pip install -q -r requirements.txt
```

#### Cell 4：运行流水线
```bash
!python app.py \
  --url "https://www.youtube.com/watch?v=VIDEO_ID" \
  --run_root "/content/drive/MyDrive/youtube视频/runs" \
  --openai_api_key "sk-your-key-here"
```

---

## 常用命令示例

### 基本使用（YouTube URL）
```bash
!python app.py \
  --url "https://www.youtube.com/watch?v=dQw4w9WgXcQ" \
  --run_root "/content/drive/MyDrive/youtube视频/runs" \
  --openai_api_key "YOUR_KEY"
```

### 使用本地视频
```bash
!python app.py \
  --input_video "/content/drive/MyDrive/videos/my_video.mp4" \
  --run_root "/content/drive/MyDrive/youtube视频/runs" \
  --openai_api_key "YOUR_KEY"
```

### 使用 cookies（受限视频）
```bash
!python app.py \
  --url "https://www.youtube.com/watch?v=VIDEO_ID" \
  --cookies "/content/drive/MyDrive/youtube视频/cookies.txt" \
  --run_root "/content/drive/MyDrive/youtube视频/runs" \
  --openai_api_key "YOUR_KEY"
```

### 自定义 ASR 模型
```bash
!python app.py \
  --url "https://www.youtube.com/watch?v=VIDEO_ID" \
  --run_root "/content/drive/MyDrive/youtube视频/runs" \
  --asr_model "large-v3" \
  --openai_api_key "YOUR_KEY"
```

### 使用自定义 API 端点
```bash
!python app.py \
  --url "https://www.youtube.com/watch?v=VIDEO_ID" \
  --run_root "/content/drive/MyDrive/youtube视频/runs" \
  --openai_api_key "YOUR_KEY" \
  --openai_base_url "https://your-api-gateway.com/v1" \
  --openai_model "gpt-4"
```

### 断点续跑（重跑翻译）
```bash
!python app.py \
  --url "https://www.youtube.com/watch?v=VIDEO_ID" \
  --run_dir "/content/drive/MyDrive/youtube视频/runs/2025-12-24_033000_VIDEO_ID" \
  --force_steps "translate"
```

---

## 输出文件位置

运行完成后，所有文件在：
```
/content/drive/MyDrive/youtube视频/runs/<timestamp>_<video_id>/
├── input.mp4              # 输入视频
├── audio.wav              # 提取的音频
├── subtitle.src.srt       # 源语言字幕
├── subtitle.zh.srt        # 中文字幕
├── transcript.json        # ASR 详细结果
└── video_zh_hardsub.mp4   # 最终输出（硬字幕）
```

### 检查输出
```bash
!ls -lh /content/drive/MyDrive/youtube视频/runs/*/video_zh_hardsub.mp4
```

### 下载到本地
在 Colab 文件浏览器中右键点击文件 → Download

---

## 常见问题

### 1. GPU 加速
Colab 免费版提供 T4 GPU，ASR 会自动使用。查看 GPU 状态：
```python
!nvidia-smi
```

### 2. 运行时间限制
- 免费版：最长 12 小时
- 建议处理 < 30 分钟的视频

### 3. 存储空间
确保 Google Drive 有足够空间（视频大小 × 3 左右）

### 4. API 配额
翻译会调用 OpenAI API，注意：
- 每个字幕块都会调用 API
- 建议使用 `gpt-4o-mini`（成本低）
- 监控 API 使用量

### 5. 依赖安装失败
如果 `pip install` 报错，尝试：
```bash
!pip install --upgrade pip
!pip install -r requirements.txt --no-cache-dir
```

### 6. FFmpeg 错误
确保已安装 ffmpeg：
```bash
!apt-get update && apt-get install -y ffmpeg
!ffmpeg -version
```

---

## 调试技巧

### 查看详细日志
```bash
!python app.py --url "..." --run_root "..." 2>&1 | tee output.log
```

### 测试短视频
先用短视频（< 5 分钟）测试流程

### 分步运行
```bash
# 只下载
!python app.py --url "..." --run_root "..." --force_steps "get_video"

# 只 ASR
!python app.py --url "..." --run_root "..." --force_steps "asr"

# 只翻译
!python app.py --url "..." --run_root "..." --force_steps "translate"
```

---

## 更新代码

### 方案 A（GitHub）
```bash
%cd /content/yt-dl-colab
!git pull origin main
```

### 方案 B（Drive）
直接在本地修改后重新上传到 Drive，Colab 会自动同步
