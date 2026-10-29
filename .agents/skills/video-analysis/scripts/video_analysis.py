from __future__ import annotations

import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".webm", ".m4v", ".avi"}
SUBTITLE_EXTENSIONS = {".srt", ".vtt", ".ass", ".ssa"}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create evidence-first video analysis artifacts from a local file or supported URL."
    )
    parser.add_argument("--input", required=True, help="Local video path or supported video URL.")
    parser.add_argument("--out", default="artifacts", help="Output root directory.")
    parser.add_argument("--sample-count", type=int, default=12, help="Representative frame count.")
    parser.add_argument("--ocr", choices=["off", "auto", "tesseract"], default="off")
    parser.add_argument("--asr", choices=["off", "faster-whisper"], default="off")
    parser.add_argument("--asr-model", default="small", help="faster-whisper model name.")
    parser.add_argument("--extract-audio", action="store_true", help="Extract mono 16 kHz WAV audio.")
    parser.add_argument("--keep-source-name", action="store_true", help="Keep source filename when copying local video.")
    args = parser.parse_args()

    run_dir = prepare_run_dir(Path(args.out), args.input)
    manifest: dict[str, Any] = {
        "tool": "video-analysis-skill",
        "version": "0.1.0",
        "started_at": now_iso(),
        "input": args.input,
        "run_dir": str(run_dir),
        "artifacts": {},
        "warnings": [],
    }

    try:
        ffmpeg = require_tool("ffmpeg")
        ffprobe = require_tool("ffprobe")
        video_path, source_kind, source_metadata = materialize_source(args.input, run_dir, args.keep_source_name)
        manifest["source_kind"] = source_kind
        manifest["source_video"] = str(video_path)
        manifest["source_metadata"] = source_metadata

        probe = run_ffprobe(ffprobe, video_path)
        manifest["artifacts"]["ffprobe_json"] = write_json(run_dir / "ffprobe.json", probe)

        media_summary = summarize_probe(probe)
        manifest["media_summary"] = media_summary
        manifest["artifacts"]["quality_gates"] = write_json(
            run_dir / "quality-gates.json",
            build_quality_gates(source_metadata, media_summary),
        )

        frames_dir = run_dir / "frames"
        frames_dir.mkdir(parents=True, exist_ok=True)
        sample_plan = build_sample_plan(float(media_summary.get("duration_seconds") or 0), args.sample_count)
        frame_paths = extract_frames(ffmpeg, video_path, sample_plan, frames_dir)
        manifest["sample_plan"] = sample_plan
        manifest["artifacts"]["frames"] = [str(path) for path in frame_paths]

        contact_sheet = build_contact_sheet(frame_paths, sample_plan, run_dir / "contact-sheet.jpg")
        if contact_sheet:
            manifest["artifacts"]["contact_sheet"] = str(contact_sheet)
        else:
            manifest["warnings"].append("Pillow is not available; contact sheet was not generated.")

        subtitles = collect_subtitles(video_path, run_dir)
        if subtitles:
            manifest["artifacts"]["subtitles"] = [str(path) for path in subtitles]

        if args.ocr != "off":
            ocr_result = run_ocr(args.ocr, frame_paths, sample_plan, run_dir / "ocr")
            manifest["artifacts"]["ocr"] = ocr_result
            if ocr_result.get("status") != "ok":
                manifest["warnings"].append(f"OCR status: {ocr_result.get('status')}")

        audio_path = None
        if args.extract_audio or args.asr != "off":
            if media_summary.get("audio_present"):
                audio_path = run_dir / "audio.wav"
                extract_audio(ffmpeg, video_path, audio_path)
                manifest["artifacts"]["audio"] = str(audio_path)
            else:
                manifest["warnings"].append("No audio stream detected; audio extraction skipped.")

        if args.asr != "off":
            if audio_path:
                asr_result = run_asr(args.asr, args.asr_model, audio_path, run_dir / "transcript")
                manifest["artifacts"]["asr"] = asr_result
                if asr_result.get("status") != "ok":
                    manifest["warnings"].append(f"ASR status: {asr_result.get('status')}")
            else:
                manifest["warnings"].append("ASR requested but no audio artifact exists.")

        manifest["artifacts"]["analysis_brief"] = write_text(
            run_dir / "analysis-brief.md",
            build_analysis_brief(manifest),
        )
        manifest["finished_at"] = now_iso()
        manifest["status"] = "passed"
        write_json(run_dir / "manifest.json", manifest)
        print(json.dumps({"status": "passed", "run_dir": str(run_dir)}, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        manifest["finished_at"] = now_iso()
        manifest["status"] = "failed"
        manifest["error"] = {"type": type(exc).__name__, "message": str(exc)}
        write_json(run_dir / "manifest.json", manifest)
        print(json.dumps({"status": "failed", "run_dir": str(run_dir), "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def is_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"}


def slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9._-]+", "-", value.strip()).strip("-")
    return value[:80] or "video"


def prepare_run_dir(out_root: Path, source: str) -> Path:
    name = slugify(Path(urlparse(source).path).stem if is_url(source) else Path(source).stem)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = out_root.expanduser().resolve() / f"{name}-{stamp}"
    run_dir.mkdir(parents=True, exist_ok=False)
    return run_dir


def run_command(command: list[str], cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=check,
    )


def require_tool(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise RuntimeError(f"{name} is required but was not found on PATH.")
    return path


def optional_tool(name: str) -> str | None:
    return shutil.which(name)


def materialize_source(source: str, run_dir: Path, keep_source_name: bool) -> tuple[Path, str, dict[str, Any]]:
    source_dir = run_dir / "source"
    source_dir.mkdir(parents=True, exist_ok=True)

    if is_url(source):
        yt_dlp = optional_tool("yt-dlp")
        if not yt_dlp:
            raise RuntimeError("URL input requires yt-dlp. Install it or provide a local video file.")
        output_template = str(source_dir / "source.%(ext)s")
        command = [
            yt_dlp,
            "--no-playlist",
            "--write-info-json",
            "--write-subs",
            "--write-auto-subs",
            "--sub-langs",
            "all",
            "--convert-subs",
            "srt",
            "-o",
            output_template,
            source,
        ]
        run_command(command)
        video_candidates = sorted(path for path in source_dir.iterdir() if path.suffix.lower() in VIDEO_EXTENSIONS)
        if not video_candidates:
            raise RuntimeError("yt-dlp completed but no supported video file was found.")
        metadata = {"url": source, "download_method": "yt-dlp"}
        info_path = source_dir / "source.info.json"
        if info_path.exists():
            metadata["info_json"] = str(info_path)
            try:
                metadata["source_title"] = json.loads(info_path.read_text(encoding="utf-8")).get("title")
            except Exception:
                pass
        return video_candidates[0], "url", metadata

    original = Path(source).expanduser().resolve()
    if not original.exists():
        raise FileNotFoundError(f"Input video does not exist: {original}")
    if original.suffix.lower() not in VIDEO_EXTENSIONS:
        raise RuntimeError(f"Unsupported video extension: {original.suffix}")
    target_name = original.name if keep_source_name else f"source{original.suffix.lower()}"
    target = source_dir / target_name
    shutil.copy2(original, target)
    for subtitle in sorted(original.parent.iterdir()):
        if subtitle.stem == original.stem and subtitle.suffix.lower() in SUBTITLE_EXTENSIONS:
            shutil.copy2(subtitle, source_dir / subtitle.name)
    return target, "local-file", {"original_name": original.name, "copied_to": str(target)}


def run_ffprobe(ffprobe: str, video_path: Path) -> dict[str, Any]:
    result = run_command([
        ffprobe,
        "-v",
        "error",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        str(video_path),
    ])
    return json.loads(result.stdout)


def summarize_probe(probe: dict[str, Any]) -> dict[str, Any]:
    streams = probe.get("streams") or []
    video_stream = next((stream for stream in streams if stream.get("codec_type") == "video"), {})
    audio_stream = next((stream for stream in streams if stream.get("codec_type") == "audio"), {})
    duration = parse_float((probe.get("format") or {}).get("duration")) or parse_float(video_stream.get("duration"))
    return {
        "duration_seconds": duration,
        "video_present": bool(video_stream),
        "audio_present": bool(audio_stream),
        "width": parse_int(video_stream.get("width")),
        "height": parse_int(video_stream.get("height")),
        "video_codec": video_stream.get("codec_name"),
        "audio_codec": audio_stream.get("codec_name"),
        "format_name": (probe.get("format") or {}).get("format_name"),
        "size_bytes": parse_int((probe.get("format") or {}).get("size")),
    }


def parse_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def build_quality_gates(source_metadata: dict[str, Any], summary: dict[str, Any]) -> dict[str, Any]:
    duration = summary.get("duration_seconds")
    return {
        "has_video_stream": bool(summary.get("video_present")),
        "has_audio_stream": bool(summary.get("audio_present")),
        "duration_seconds": duration,
        "duration_known": duration is not None and float(duration) > 0,
        "source_metadata_available": bool(source_metadata),
        "evidence_rule": "Do not claim exact dialogue without subtitles or ASR transcript.",
    }


def build_sample_plan(duration: float, sample_count: int) -> list[dict[str, Any]]:
    count = max(1, min(sample_count, 60))
    if duration <= 0:
        return [{"index": 1, "seconds": 0.0, "label": "00:00:00.000"}]
    if count == 1:
        seconds = min(duration / 2, max(duration - 0.1, 0))
        return [{"index": 1, "seconds": round(seconds, 3), "label": format_timestamp(seconds)}]
    step = duration / (count + 1)
    points = [min(max(step * (idx + 1), 0), max(duration - 0.1, 0)) for idx in range(count)]
    return [
        {"index": idx + 1, "seconds": round(seconds, 3), "label": format_timestamp(seconds)}
        for idx, seconds in enumerate(points)
    ]


def format_timestamp(seconds: float) -> str:
    total_ms = int(round(seconds * 1000))
    ms = total_ms % 1000
    total_seconds = total_ms // 1000
    s = total_seconds % 60
    total_minutes = total_seconds // 60
    m = total_minutes % 60
    h = total_minutes // 60
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"


def extract_frames(ffmpeg: str, video_path: Path, sample_plan: list[dict[str, Any]], frames_dir: Path) -> list[Path]:
    frame_paths: list[Path] = []
    for row in sample_plan:
        index = int(row["index"])
        seconds = float(row["seconds"])
        frame_path = frames_dir / f"frame-{index:02d}-{format_timestamp(seconds).replace(':', '-').replace('.', '_')}.jpg"
        run_command([
            ffmpeg,
            "-y",
            "-ss",
            f"{seconds:.3f}",
            "-i",
            str(video_path),
            "-frames:v",
            "1",
            "-q:v",
            "2",
            str(frame_path),
        ])
        frame_paths.append(frame_path)
    return frame_paths


def build_contact_sheet(frame_paths: list[Path], sample_plan: list[dict[str, Any]], out_path: Path) -> Path | None:
    try:
        from PIL import Image, ImageDraw, ImageFont
    except Exception:
        return None
    if not frame_paths:
        return None
    thumbs = []
    thumb_w, thumb_h = 320, 180
    label_h = 28
    for index, frame_path in enumerate(frame_paths):
        image = Image.open(frame_path).convert("RGB")
        image.thumbnail((thumb_w, thumb_h))
        canvas = Image.new("RGB", (thumb_w, thumb_h + label_h), "white")
        x = (thumb_w - image.width) // 2
        y = (thumb_h - image.height) // 2
        canvas.paste(image, (x, y))
        draw = ImageDraw.Draw(canvas)
        label = sample_plan[index].get("label", "")
        try:
            font = ImageFont.load_default()
        except Exception:
            font = None
        draw.rectangle((0, thumb_h, thumb_w, thumb_h + label_h), fill=(20, 24, 32))
        draw.text((8, thumb_h + 7), f"{index + 1:02d}  {label}", fill=(245, 245, 245), font=font)
        thumbs.append(canvas)
    cols = min(4, len(thumbs))
    rows = int(math.ceil(len(thumbs) / cols))
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), (14, 16, 22))
    for idx, thumb in enumerate(thumbs):
        x = (idx % cols) * thumb_w
        y = (idx // cols) * (thumb_h + label_h)
        sheet.paste(thumb, (x, y))
    sheet.save(out_path, quality=90)
    return out_path


def collect_subtitles(video_path: Path, run_dir: Path) -> list[Path]:
    subtitle_dir = run_dir / "subtitles"
    subtitle_dir.mkdir(parents=True, exist_ok=True)
    results: list[Path] = []
    source_dir = video_path.parent
    for subtitle in sorted(source_dir.iterdir()):
        if subtitle.suffix.lower() in SUBTITLE_EXTENSIONS:
            target = subtitle_dir / subtitle.name
            if subtitle.resolve() != target.resolve():
                shutil.copy2(subtitle, target)
            results.append(target)
    if not results:
        subtitle_dir.rmdir()
    return results


def run_ocr(mode: str, frame_paths: list[Path], sample_plan: list[dict[str, Any]], out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        import pytesseract
    except Exception:
        return {
            "status": "missing-python-package",
            "package": "pytesseract",
            "repair_hint": "Run python scripts/doctor.py --profile ocr --repair-plan.",
        }
    if mode in {"auto", "tesseract"} and not optional_tool("tesseract"):
        return {
            "status": "missing-system-tool",
            "tool": "tesseract",
            "repair_hint": "Run python scripts/doctor.py --profile ocr --repair-plan.",
        }
    rows = []
    for frame_path, sample in zip(frame_paths, sample_plan):
        try:
            text = pytesseract.image_to_string(str(frame_path)).strip()
        except Exception as exc:
            rows.append({"frame": str(frame_path), "timestamp": sample["label"], "error": str(exc)})
            continue
        rows.append({"frame": str(frame_path), "timestamp": sample["label"], "text": text})
    json_path = out_dir / "ocr-results.json"
    md_path = out_dir / "ocr-results.md"
    write_json(json_path, {"status": "ok", "rows": rows})
    lines = ["# OCR Results", ""]
    for row in rows:
        lines.append(f"## {row.get('timestamp')}")
        lines.append("")
        lines.append(row.get("text") or "(no text detected)")
        lines.append("")
    write_text(md_path, "\n".join(lines))
    return {"status": "ok", "json": str(json_path), "markdown": str(md_path)}


def extract_audio(ffmpeg: str, video_path: Path, out_path: Path) -> None:
    run_command([
        ffmpeg,
        "-y",
        "-i",
        str(video_path),
        "-vn",
        "-ac",
        "1",
        "-ar",
        "16000",
        str(out_path),
    ])


def run_asr(engine: str, model_name: str, audio_path: Path, out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    if engine != "faster-whisper":
        return {"status": "unsupported-engine", "engine": engine}
    try:
        from faster_whisper import WhisperModel
    except Exception:
        return {
            "status": "missing-python-package",
            "package": "faster-whisper",
            "repair_hint": "Run python scripts/doctor.py --profile asr --repair-plan.",
        }
    try:
        model = WhisperModel(model_name, device="auto", compute_type="int8")
        segments, info = model.transcribe(str(audio_path))
    except Exception as exc:
        return {
            "status": "asr-error",
            "engine": engine,
            "model": model_name,
            "detail": str(exc),
            "repair_hint": f"Run python scripts/doctor.py --profile asr --repair-plan --require-asr-model --asr-model {model_name}.",
        }
    rows = []
    text_parts = []
    for idx, segment in enumerate(segments):
        row = {
            "index": idx,
            "start": float(segment.start),
            "end": float(segment.end),
            "text": segment.text.strip(),
        }
        rows.append(row)
        text_parts.append(row["text"])
    json_path = out_dir / "transcript.json"
    text_path = out_dir / "transcript.txt"
    srt_path = out_dir / "transcript.srt"
    write_json(json_path, {"status": "ok", "language": getattr(info, "language", None), "segments": rows})
    write_text(text_path, "\n".join(text_parts).strip() + "\n")
    write_text(srt_path, to_srt(rows))
    return {"status": "ok", "engine": engine, "model": model_name, "json": str(json_path), "text": str(text_path), "srt": str(srt_path)}


def to_srt(rows: list[dict[str, Any]]) -> str:
    lines = []
    for idx, row in enumerate(rows, 1):
        lines.append(str(idx))
        lines.append(f"{srt_time(row['start'])} --> {srt_time(row['end'])}")
        lines.append(row["text"])
        lines.append("")
    return "\n".join(lines)


def srt_time(seconds: float) -> str:
    text = format_timestamp(seconds).replace(".", ",")
    return text


def build_analysis_brief(manifest: dict[str, Any]) -> str:
    summary = manifest.get("media_summary") or {}
    artifacts = manifest.get("artifacts") or {}
    lines = [
        "# Video Analysis Brief",
        "",
        "## Source",
        "",
        f"- Input: `{manifest.get('input')}`",
        f"- Source kind: `{manifest.get('source_kind')}`",
        f"- Duration: `{summary.get('duration_seconds')}` seconds",
        f"- Resolution: `{summary.get('width')}x{summary.get('height')}`",
        f"- Video codec: `{summary.get('video_codec')}`",
        f"- Audio present: `{summary.get('audio_present')}`",
        "",
        "## Evidence Artifacts",
        "",
    ]
    for key, value in artifacts.items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend([
        "",
        "## Evidence Rules",
        "",
        "- Metadata supports file, stream, duration, and codec claims.",
        "- Sampled frames and the contact sheet support visible-scene claims only for sampled timestamps.",
        "- OCR is weaker than subtitles or ASR and may contain recognition errors.",
        "- Spoken wording requires subtitle or ASR evidence.",
        "- If a claim is not supported by an artifact, label it as unsupported.",
        "",
        "## Initial Conclusion",
        "",
        "A reusable artifact set exists. Review `contact-sheet.jpg`, `frames/`, subtitles or ASR outputs, and `quality-gates.json` before making content claims.",
        "",
    ])
    warnings = manifest.get("warnings") or []
    if warnings:
        lines.extend(["## Warnings", ""])
        lines.extend(f"- {warning}" for warning in warnings)
        lines.append("")
    return "\n".join(lines)


def write_json(path: Path, data: Any) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(path)


def write_text(path: Path, text: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
