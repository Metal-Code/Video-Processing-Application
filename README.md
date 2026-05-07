# Video Processing Application

A browser-based video processing suite built with Streamlit. Upload a video and run it through a set of tools — compression, trimming, cropping, filtering, subtitle generation, AI summarisation, and natural language Q&A — entirely in the browser with no desktop software required.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Local Setup](#local-setup)
- [Configuration and Secrets](#configuration-and-secrets)
- [Deploying to Streamlit Cloud](#deploying-to-streamlit-cloud)
- [Tool Reference](#tool-reference)
- [How Compression Works](#how-compression-works)
- [How AI Features Work](#how-ai-features-work)
- [Known Limitations](#known-limitations)
- [Contributing](#contributing)

---

## Overview

This application lets you process video files directly in the browser through a Streamlit interface. All processing happens server-side — the user uploads a file, selects a tool from the sidebar, and the result is made available for download. No video data is stored permanently; all files are written to temporary paths and cleaned up automatically when a new file is uploaded.

AI-powered features (Video Overview and Ask Questions) use OpenRouter to route requests to a free large language model. Transcription is handled locally using OpenAI Whisper running on the server.

---

## Features

**Compress Video**
Reduces file size to approximately 50% of the original using H.264 video encoding and AAC audio at 96kbps. Bitrate is calculated dynamically based on the source file duration and size. The output is web-optimised using the `+faststart` flag so it can begin playing before fully downloading.

**Generate Subtitles**
Transcribes the audio track using Whisper and outputs the full transcript as a downloadable text file. Supports English, Hindi, Spanish, French, German, and Chinese. Language can be selected before transcription to improve accuracy.

**Video Overview**
Transcribes the video and sends the transcript to an LLM via OpenRouter for summarisation. Returns a concise prose summary of the video's content. Requires an OpenRouter API key.

**Frame-by-Frame Viewer**
Extracts and displays individual frames using OpenCV. A slider lets you scrub through the entire frame index of the video. Useful for inspecting specific moments, checking for artifacts, or grabbing reference stills.

**Trim Video**
Cuts the video to a specified start and end time using MoviePy. Both timestamps are selected via sliders. The trimmed output is re-encoded with libx264 and made available for download.

**Crop Video**
Displays the first frame of the video as a spatial reference. Accepts pixel coordinates (x1, y1, x2, y2) as inputs and applies the crop to every frame of the video. Validates that the crop region is geometrically valid before processing.

**Add Filter**
Applies one of four frame-level visual filters — Grayscale, Sepia, Invert, or Brighten — to the entire video using MoviePy's frame processing pipeline. Sepia uses a standard 3x3 colour matrix transformation. Brighten multiplies each channel by 1.2 and clamps to 0–255.

**Ask Questions About Video**
Transcribes the video and holds the transcript in session state. Accepts a free-text question and sends it along with the transcript to an LLM via OpenRouter. The transcript is cached per file so repeated questions do not re-run Whisper. Requires an OpenRouter API key.

---

## Tech Stack

| Layer | Technology |
|---|---|
| UI and server | Streamlit |
| Video processing | FFmpeg (CLI), MoviePy 1.0.3, OpenCV |
| Transcription | OpenAI Whisper (base model) |
| AI / LLM | OpenRouter (free tier) via OpenAI SDK |
| Image handling | Pillow, NumPy |
| Runtime | Python 3.10+ |

---

## Project Structure

```
Video-Processing-Application/
├── app.py                  Main Streamlit application
├── compressor.py           Video compression logic using FFmpeg
├── requirements.txt        Python dependencies
├── packages.txt            System-level packages (ffmpeg) for Streamlit Cloud
├── runtime.txt             Python version pin for Streamlit Cloud
└── .streamlit/
    └── secrets.toml        API keys — never committed to version control
```

---

## Local Setup

### Prerequisites

Python 3.10 or higher and FFmpeg must be installed on your system before running the application.

Install FFmpeg:

```bash
# macOS
brew install ffmpeg

# Ubuntu / Debian
sudo apt-get install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html and add to PATH
```

### Installation

Clone the repository:

```bash
git clone https://github.com/Metal-Code/Video-Processing-Application.git
cd Video-Processing-Application
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Whisper requires PyTorch. If it is not pulled in automatically:

```bash
pip install torch
```

### Running

```bash
streamlit run app.py
```

The application opens at `http://localhost:8501`.

---

## Configuration and Secrets

AI features require an OpenRouter API key. Create a free account at [openrouter.ai](https://openrouter.ai) and generate a key from the Keys section of the dashboard.

Create the secrets file at `.streamlit/secrets.toml`:

```toml
OPENROUTER_API_KEY = "sk-or-your-key-here"
```

This file is listed in `.gitignore` and must never be committed to version control. If you accidentally commit it, rotate the key immediately on the OpenRouter dashboard and follow the steps in the Git history rewrite section below.

### Removing a Secret from Git History

If a secret has been committed, remove it before pushing:

```bash
pip install git-filter-repo
git filter-repo --path .streamlit/secrets.toml --invert-paths --force
git remote add origin https://github.com/Metal-Code/Video-Processing-Application.git
git push origin main --force
```

---

## Deploying to Streamlit Cloud

1. Push your code to GitHub (ensure `secrets.toml` is not included).
2. Go to [share.streamlit.io](https://share.streamlit.io) and connect your repository.
3. Set the main file path to `app.py`.
4. Open **Settings → Secrets** in the Streamlit Cloud dashboard and paste:

```toml
OPENROUTER_API_KEY = "sk-or-your-key-here"
```

5. FFmpeg is declared as a system dependency in `packages.txt` and will be installed automatically by Streamlit Cloud on each deploy.

---

## Tool Reference

### Compress Video

The compression pipeline is handled entirely in `compressor.py`. It uses `ffprobe` to read the source duration, calculates a target video bitrate that brings the total file size to roughly 50% of the original (accounting for the fixed 96kbps audio track), and passes these parameters to `ffmpeg` with CRF 26 and the `fast` preset. The `-fs` hard size limit is intentionally not used, as it truncates the video at the byte limit rather than re-encoding more efficiently.

If `ffprobe` fails, the duration falls back to a size-based estimate. If `ffmpeg` fails mid-way, any partial output file is deleted before the exception is raised.

### Generate Subtitles

Whisper is loaded once per session using `@st.cache_resource` and reused across all tools. The `base` model is used as a balance between accuracy and inference speed. The language parameter is passed directly to Whisper's transcribe function — specifying it prevents the model from spending time on language detection and improves accuracy for non-English content.

### Video Overview and Ask Questions

Both tools transcribe the video first, then send the transcript to OpenRouter using the OpenAI-compatible SDK. The model is set to `openrouter/free`, which is OpenRouter's internal router that automatically selects from whichever free models are currently available. This avoids errors caused by specific free model IDs being deprecated or renamed.

The transcript is cached in `st.session_state` keyed to the uploaded filename. Switching to a new video clears the cache. Switching between tools also clears it to prevent stale transcripts from being used.

---

## How Compression Works

```
Input file
    |
    v
ffprobe reads duration
    |
    v
Calculate target bitrate:
  target_size = original_size * 0.5
  audio_size  = 96kbps * duration
  video_size  = target_size - audio_size
  video_kbps  = video_size * 8 / duration / 1024
  clamped to [500, 8000] kbps
    |
    v
ffmpeg encodes:
  codec: libx264
  crf: 26
  preset: fast
  audio: aac 96k
  flags: +faststart
    |
    v
Output file (~50% of original size)
```

---

## How AI Features Work

```
Uploaded video
    |
    v
Whisper (base) transcribes audio to text
    |
    v
Transcript stored in session_state
    |
    v
User action (Summarise / Ask question)
    |
    v
Prompt built: transcript + instruction or question
    |
    v
OpenRouter API (model: openrouter/free)
    |
    v
Response displayed in text area
```

---

## Known Limitations

- **Whisper inference time** scales with video length. Long videos (over 10 minutes) may take a significant amount of time to transcribe, particularly on CPU.
- **MoviePy 1.0.3 is pinned** because MoviePy 2.x removed the `moviepy.editor` module that this application depends on. Do not upgrade without refactoring the import and API usage.
- **Temporary files** are written to the system temp directory and cleaned up when a new file is uploaded, but not on application shutdown. On long-running deployments, disk usage should be monitored.
- **AI features depend on OpenRouter's free tier availability.** The `openrouter/free` router mitigates this, but responses may be slower or queued during high demand periods.
- **Crop and trim re-encode the full video.** For large files this is slow. A future optimisation would be to use FFmpeg's stream copy (`-c copy`) for trim when the timestamps align with keyframes.
- **No authentication.** This application is designed for single-user or internal use. Do not expose it publicly without adding access controls.

---

## Contributing

Pull requests are welcome. For significant changes, open an issue first to discuss what you want to change.

When contributing, ensure that no API keys, credentials, or secrets are included in any commit. Run the application locally and verify all eight tools work end-to-end before submitting a pull request.