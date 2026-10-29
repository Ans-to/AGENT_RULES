# Workflow

Video Analysis Skill is built around a deterministic artifact pipeline.

## Components

| Component | Role |
| --- | --- |
| ffmpeg | Frame extraction, audio extraction, media processing |
| ffprobe | Stream metadata and duration checks |
| yt-dlp | Optional URL materialization and subtitle harvesting |
| Pillow | Contact sheet generation |
| Tesseract + pytesseract | Optional OCR for sampled frames |
| faster-whisper | Optional local ASR for speech transcription |
| Docker | Reproducible runtime for base video analysis, OCR, and optional ASR |
| doctor.py | Guided dependency, tool, Docker, and model-cache diagnostics |

## Artifact Flow

1. Source is copied or downloaded into a run folder.
2. ffprobe writes technical metadata.
3. The sampler extracts representative frames across the duration.
4. Pillow builds a contact sheet from sampled frames.
5. Existing subtitles are copied into the artifact set when available.
6. OCR can be run over sampled frames when on-screen text matters.
7. Audio can be extracted and passed to faster-whisper when speech matters.
8. A manifest and analysis brief summarize what evidence exists.

## Setup Profiles

Use `scripts/doctor.py` before the first run, when moving between machines, or when enabling OCR/ASR.

| Profile | Purpose |
| --- | --- |
| `base` | Core local video analysis with metadata, frames, and contact sheet |
| `ocr` | Adds Tesseract-based OCR for visible text |
| `asr` | Adds faster-whisper and local model-cache checks |
| `full` | Checks URL materialization, OCR, ASR, Docker, and model-cache readiness |

The doctor reports missing required and recommended components. With `--repair-plan`, it returns platform-specific repair commands instead of assuming a package manager.

## Why Deterministic Artifacts First

Video questions are easy to over-answer from thumbnails, captions, or partial browser previews. This workflow creates stable artifacts that can be inspected, cited, rerun, and compared.

## Optional OCR

OCR is useful for slides, dashboards, captions, UI recordings, title cards, and visible labels. It is not reliable enough to replace direct visual inspection or subtitles.

## Optional ASR

ASR is useful when no subtitles exist and the task depends on speech. Keep ASR output separate from visible-frame evidence. Treat ASR as transcript evidence, not proof of visual events.

Before an ASR-heavy task, run:

```bash
python scripts/doctor.py --profile asr --repair-plan --require-asr-model --asr-model small
```

To preload the selected model:

```bash
python scripts/doctor.py --profile asr --download-asr-model small --asr-model small
```

## Good Fits

- summarizing a local recording
- checking what appears in a short clip
- extracting representative frames from a product demo
- reviewing a screen recording for visible errors
- confirming whether a clip contains readable text
- creating a reusable artifact set before content analysis

## Poor Fits

- bypassing access controls or paywalls
- reconstructing missing parts of a video
- claiming exact dialogue without transcript evidence
- proving identity or sensitive claims from low-quality clips
- making legal, medical, financial, or safety-critical conclusions without specialist review
