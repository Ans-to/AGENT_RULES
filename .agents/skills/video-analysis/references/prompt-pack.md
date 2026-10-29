# Prompt Pack

## Install Video Analysis Skill

```text
Install Video Analysis Skill from this public repository:
https://github.com/BYDFi2025/video-analysis-skill

If you can persist skills in this environment:
1. Clone or download the repository.
2. Install it as a skill named video-analysis in the appropriate skill directory for this agent.
3. Include SKILL.md, references, scripts, agents, requirements, Dockerfile, and README.
4. Do not copy .git, artifacts, caches, generated outputs, virtual environments, or temporary files.
5. From the repository root, run python scripts/doctor.py --profile full --repair-plan.
6. If dependencies, tools, Docker, OCR, ASR, or local transcription models are missing, show me the repair options first and ask before changing the system.

If you cannot persist skills:
1. Load SKILL.md and the relevant references for this chat only.
2. Tell me clearly that this is a session-only setup.

Return:
- install mode: persistent or session-only
- installed path, if available
- doctor status
- missing dependencies
- recommended repair plan
- one safe test command or test task I can run next
```

## Analyze A Local Clip

```text
Use Video Analysis Skill to analyze this local video file. Create metadata, representative frames, a contact sheet, quality gates, and an evidence brief before summarizing it.
```

## Analyze A Video URL

```text
Use Video Analysis Skill to analyze this video URL. Materialize the source with supported tools, collect metadata, frames, subtitles if available, and summarize only from artifacts.
```

## Spoken Content

```text
Use Video Analysis Skill to determine what is said in this video. Use subtitles if available. If no subtitles exist, use local ASR when available. Do not claim exact wording without transcript evidence.
```

## Prepare Local ASR

```text
Use Video Analysis Skill to prepare local speech transcription. Run the ASR doctor profile, show missing dependencies and model-cache status, then ask before installing packages or downloading the selected transcription model.
```

## On-Screen Text

```text
Use Video Analysis Skill with OCR enabled to inspect visible on-screen text. Treat OCR as approximate and cite the frame timestamps where text appears.
```

## Evidence Report

```text
Use Video Analysis Skill to produce an evidence-backed report with artifact paths, evidence class, key findings, and unsupported points.
```
