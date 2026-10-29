from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str], cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)


def run_unchecked(command: list[str], cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def test_doctor_required_dependencies() -> None:
    result = run([sys.executable, "scripts/doctor.py"])
    data = json.loads(result.stdout)
    assert data["status"] in {"ready", "ready-with-recommended-gaps"}
    assert data["profile"] == "base"


def test_doctor_repair_plan_for_required_asr_model() -> None:
    result = run_unchecked([
        sys.executable,
        "scripts/doctor.py",
        "--profile",
        "asr",
        "--repair-plan",
        "--require-asr-model",
        "--asr-model",
        "unit-test-model-not-present",
    ])
    data = json.loads(result.stdout)
    assert data["profile"] == "asr"
    assert data["status"] in {"missing-required", "ready", "ready-with-recommended-gaps"}
    if data["status"] == "missing-required":
        missing_ids = {row["id"] for row in data["missing"]}
        assert "asr-model" in missing_ids or "faster-whisper" in missing_ids
        plan_ids = {row["id"] for row in data["repair_plan"]}
        assert "asr-model" in plan_ids or "faster-whisper" in plan_ids


def test_doctor_markdown_format() -> None:
    result = run([
        sys.executable,
        "scripts/doctor.py",
        "--profile",
        "base",
        "--repair-plan",
        "--format",
        "markdown",
    ])
    assert "# Video Analysis Skill Doctor" in result.stdout
    assert "| Component | Level | Status | Detail |" in result.stdout


def test_pipeline_generates_artifacts(tmp_path: Path) -> None:
    if not shutil.which("ffmpeg"):
        raise AssertionError("ffmpeg is required for this test")
    sample = tmp_path / "sample.mp4"
    run([
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        "testsrc=size=320x180:rate=10:duration=2",
        "-f",
        "lavfi",
        "-i",
        "sine=frequency=440:duration=2",
        "-shortest",
        "-pix_fmt",
        "yuv420p",
        str(sample),
    ])
    out_root = tmp_path / "runs"
    result = run([
        sys.executable,
        "scripts/video_analysis.py",
        "--input",
        str(sample),
        "--out",
        str(out_root),
        "--sample-count",
        "4",
    ])
    payload = json.loads(result.stdout)
    assert payload["status"] == "passed"
    run_dir = Path(payload["run_dir"])
    assert (run_dir / "manifest.json").exists()
    assert (run_dir / "analysis-brief.md").exists()
    assert (run_dir / "contact-sheet.jpg").exists()
    frames = sorted((run_dir / "frames").glob("*.jpg"))
    assert len(frames) == 4
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["media_summary"]["video_present"] is True
    assert manifest["media_summary"]["audio_present"] is True
