# Install And Repair

`scripts/doctor.py` is the setup and recovery entrypoint for Video Analysis Skill. It checks the active machine, reports what is missing, and returns repair options without silently changing the system.

## Profiles

| Profile | Use When | Required Checks | Recommended Checks |
| --- | --- | --- | --- |
| `base` | Metadata, frame extraction, contact sheets | Python, ffmpeg, ffprobe, Pillow | yt-dlp |
| `ocr` | On-screen text matters | Base stack, Tesseract, pytesseract | none |
| `asr` | Spoken content matters | Base stack, faster-whisper | selected ASR model cache |
| `full` | Preparing a complete install | URL support, OCR, ASR | Docker, selected ASR model cache |

## Repair Plan

Run:

```bash
python scripts/doctor.py --profile full --repair-plan --format markdown
```

The repair plan includes platform-aware options for:

- Python 3.10+
- ffmpeg and ffprobe
- yt-dlp
- Tesseract OCR
- Python packages from `requirements.txt` and `requirements-asr.txt`
- Docker
- local faster-whisper model cache

The script does not install system software by itself. An agent should present the plan, ask for approval, then run only the selected commands.

## Local ASR Model

For speech-heavy tasks, preload a model:

```bash
python -m pip install -r requirements-asr.txt
python scripts/doctor.py --profile asr --download-asr-model small --asr-model small
```

To require that the model already exists locally:

```bash
python scripts/doctor.py --profile asr --repair-plan --require-asr-model --asr-model small
```

## Docker Profiles

Base image:

```bash
docker build --target final -t video-analysis-skill:base .
```

ASR image:

```bash
docker build --target asr -t video-analysis-skill:asr .
```

ASR image with a preloaded model:

```bash
docker build --target asr --build-arg PRELOAD_ASR_MODEL=small -t video-analysis-skill:asr-small .
```

Use Docker when system tools are unavailable, difficult to install, or need to be reproduced across machines.
