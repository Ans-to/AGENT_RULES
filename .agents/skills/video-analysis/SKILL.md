---
name: video-analysis
description: Use when a user asks an AI agent to analyze a local video, supported video URL, screen recording, social clip, subtitles, visible frames, on-screen text, or spoken content with evidence-backed artifacts before making claims.
---

# Video Analysis

Use this skill when a task depends on what is actually visible or spoken in a video.

## Core Rule

Materialize artifacts before answering. Do not rely on one browser preview, post caption, thumbnail, or memory of a video.

## Standard Workflow

1. **Lock the source**
   - Confirm the exact local file, URL, clip, or timestamp.
   - Ask for the exact source if the target video is ambiguous.

2. **Create artifacts**
   - Run `python scripts/doctor.py --profile base --repair-plan` if the environment is unknown.
   - Use `--profile ocr`, `--profile asr`, or `--profile full` when OCR, local transcription, URL materialization, or Docker readiness matters.
   - If `doctor.py` reports missing required or recommended components, present the repair plan and ask before changing the system.
   - Run `python scripts/video_analysis.py --input <file-or-url> --out artifacts`.
   - Enable `--ocr auto` only when on-screen text matters.
   - Enable `--extract-audio --asr faster-whisper` only when spoken content matters and `doctor.py --profile asr` is ready or the user accepts the ASR repair plan.

3. **Read the evidence**
   - Start with `manifest.json`.
   - Read `analysis-brief.md`.
   - Inspect `quality-gates.json`.
   - Inspect `contact-sheet.jpg` and `frames/`.
   - Use subtitles or ASR transcript for speech.
   - Use OCR only as weaker on-screen-text evidence.

4. **Answer with evidence class**
   - State whether the answer is based on metadata, frames, subtitles, ASR, OCR, or context.
   - Mark unsupported claims as unsupported.

## Acceptance Rule

Do not call the task complete until:

- a concrete artifact folder exists
- visible claims are backed by frames or the contact sheet
- spoken claims are backed by subtitles or ASR
- technical claims are backed by ffprobe metadata
- limitations are stated clearly

## Output Style

Keep the final answer concise:

- What was analyzed
- Evidence used
- Key findings
- Artifacts
- Unverified or unsupported points

Read `references/evidence-grading.md` for the evidence hierarchy, `references/workflow.md` for the full pipeline model, and `references/install-and-repair.md` for setup profiles and repair behavior.
