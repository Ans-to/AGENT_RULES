from __future__ import annotations

import argparse
import importlib.util
import json
import platform
import shutil
import sys
from pathlib import Path
from typing import Any


MIN_PYTHON = (3, 10)


def main() -> int:
    args = parse_args()
    actions: list[dict[str, Any]] = []

    if args.download_asr_model:
        actions.append(download_asr_model(args.download_asr_model))

    checks = build_checks(args)
    missing = [row for row in checks if not row["ok"]]
    required_ok = all(row["ok"] for row in checks if row["level"] == "required")
    recommended_ok = all(row["ok"] for row in checks if row["level"] == "recommended")
    actions_ok = all(row["ok"] for row in actions)

    if not required_ok:
        status = "missing-required"
    elif not actions_ok:
        status = "action-failed"
    elif not recommended_ok:
        status = "ready-with-recommended-gaps"
    else:
        status = "ready"

    result = {
        "status": status,
        "profile": args.profile,
        "platform": platform_summary(),
        "checks": checks,
        "missing": missing,
        "actions": actions,
        "summary": summarize(checks, actions),
    }
    if args.repair_plan:
        result["repair_plan"] = build_repair_plan(missing, args)

    if args.format == "markdown":
        print(to_markdown(result))
    else:
        print(json.dumps(result, indent=2))

    return 0 if status in {"ready", "ready-with-recommended-gaps"} else 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check Video Analysis Skill dependencies and repair options.")
    parser.add_argument(
        "--profile",
        choices=["base", "ocr", "asr", "full"],
        default="base",
        help="Capability profile to check. base checks core video analysis; full checks URL, OCR, ASR, and Docker readiness.",
    )
    parser.add_argument("--repair-plan", action="store_true", help="Include system-specific repair options for missing checks.")
    parser.add_argument("--format", choices=["json", "markdown"], default="json", help="Output format.")
    parser.add_argument("--asr-model", default="small", help="faster-whisper model name to check for ASR profiles.")
    parser.add_argument(
        "--require-asr-model",
        action="store_true",
        help="Treat the local ASR model cache as required instead of recommended.",
    )
    parser.add_argument(
        "--download-asr-model",
        metavar="MODEL",
        help="Pre-download and initialize a faster-whisper model, for example: small.",
    )
    parser.add_argument("--check-docker", action="store_true", help="Check whether Docker is available.")
    return parser.parse_args()


def build_checks(args: argparse.Namespace) -> list[dict[str, Any]]:
    checks = [
        check_python(),
        check_tool("ffmpeg", "FFmpeg", "required", "system-tool"),
        check_tool("ffprobe", "FFprobe", "required", "system-tool"),
        check_import("PIL", "Pillow", "required"),
    ]

    if args.profile in {"base", "full"}:
        checks.append(check_import("yt_dlp", "yt-dlp", "recommended" if args.profile == "base" else "required"))

    if args.profile in {"ocr", "full"}:
        checks.extend([
            check_tool("tesseract", "Tesseract OCR", "required", "system-tool"),
            check_import("pytesseract", "pytesseract", "required"),
        ])

    if args.profile in {"asr", "full"}:
        checks.append(check_import("faster_whisper", "faster-whisper", "required"))
        checks.append(check_asr_model(args.asr_model, "required" if args.require_asr_model else "recommended"))

    if args.check_docker or args.profile == "full":
        checks.append(check_tool("docker", "Docker", "recommended", "system-tool"))

    return checks


def check_python() -> dict[str, Any]:
    return {
        "id": "python",
        "name": "Python",
        "category": "runtime",
        "level": "required",
        "ok": sys.version_info >= MIN_PYTHON,
        "detail": sys.version.split()[0],
    }


def check_tool(tool: str, name: str, level: str, category: str) -> dict[str, Any]:
    path = shutil.which(tool)
    return {
        "id": tool,
        "name": name,
        "category": category,
        "level": level,
        "ok": bool(path),
        "detail": path or "not found",
    }


def check_import(module: str, package: str, level: str) -> dict[str, Any]:
    found = importlib.util.find_spec(module) is not None
    return {
        "id": package,
        "name": package,
        "category": "python-package",
        "level": level,
        "ok": found,
        "detail": "installed" if found else "not installed",
    }


def check_asr_model(model: str, level: str) -> dict[str, Any]:
    if importlib.util.find_spec("faster_whisper") is None:
        return {
            "id": "asr-model",
            "name": f"faster-whisper model: {model}",
            "category": "model-cache",
            "level": level,
            "ok": False,
            "detail": "blocked because faster-whisper is not installed",
        }

    paths = possible_model_cache_paths(model)
    existing = [path for path in paths if path.exists()]
    return {
        "id": "asr-model",
        "name": f"faster-whisper model: {model}",
        "category": "model-cache",
        "level": level,
        "ok": bool(existing),
        "detail": str(existing[0]) if existing else "not found in local Hugging Face cache",
        "expected_cache_paths": [str(path) for path in paths],
    }


def possible_model_cache_paths(model: str) -> list[Path]:
    repo = model if "/" in model else f"Systran/faster-whisper-{model}"
    cache_name = "models--" + repo.replace("/", "--")
    roots: list[Path] = []
    for env_name in ("HF_HOME", "HUGGINGFACE_HUB_CACHE"):
        value = platform_env(env_name)
        if value:
            root = Path(value)
            roots.append(root if root.name == "hub" else root / "hub")
    home = Path.home()
    roots.append(home / ".cache" / "huggingface" / "hub")
    roots.append(home / ".cache" / "huggingface")
    unique_roots = list(dict.fromkeys(roots))
    return [root / cache_name for root in unique_roots]


def platform_env(name: str) -> str | None:
    import os

    value = os.environ.get(name)
    return value or None


def download_asr_model(model: str) -> dict[str, Any]:
    try:
        from faster_whisper import WhisperModel
    except Exception as exc:
        return {
            "id": "download-asr-model",
            "name": f"Download ASR model: {model}",
            "ok": False,
            "detail": f"faster-whisper is not installed: {exc}",
        }

    try:
        WhisperModel(model, device="cpu", compute_type="int8")
    except Exception as exc:
        return {
            "id": "download-asr-model",
            "name": f"Download ASR model: {model}",
            "ok": False,
            "detail": str(exc),
        }
    return {
        "id": "download-asr-model",
        "name": f"Download ASR model: {model}",
        "ok": True,
        "detail": "model initialized successfully",
    }


def build_repair_plan(missing: list[dict[str, Any]], args: argparse.Namespace) -> list[dict[str, Any]]:
    return [repair_step(row, args) for row in missing]


def repair_step(check: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    check_id = check["id"]
    options = repair_options(check_id, args.asr_model)
    return {
        "id": check_id,
        "name": check["name"],
        "level": check["level"],
        "current": check["detail"],
        "options": options,
    }


def repair_options(check_id: str, asr_model: str) -> list[dict[str, str]]:
    system = platform.system().lower()

    if check_id == "python":
        return by_platform(system, {
            "windows": [
                cmd("winget", "winget install Python.Python.3.12"),
                cmd("official", "Install Python 3.10+ from https://www.python.org/downloads/"),
            ],
            "darwin": [cmd("brew", "brew install python")],
            "linux": [cmd("apt", "sudo apt-get update && sudo apt-get install -y python3 python3-pip")],
        })
    if check_id in {"ffmpeg", "ffprobe"}:
        return by_platform(system, {
            "windows": [
                cmd("winget", "winget install Gyan.FFmpeg"),
                cmd("chocolatey", "choco install ffmpeg"),
                cmd("scoop", "scoop install ffmpeg"),
            ],
            "darwin": [cmd("brew", "brew install ffmpeg")],
            "linux": [cmd("apt", "sudo apt-get update && sudo apt-get install -y ffmpeg")],
        })
    if check_id == "yt-dlp":
        return [cmd("pip", "python -m pip install -U yt-dlp"), cmd("requirements", "python -m pip install -r requirements.txt")]
    if check_id == "Pillow":
        return [cmd("requirements", "python -m pip install -r requirements.txt")]
    if check_id == "tesseract":
        return by_platform(system, {
            "windows": [
                cmd("winget", "winget install UB-Mannheim.TesseractOCR"),
                cmd("chocolatey", "choco install tesseract"),
            ],
            "darwin": [cmd("brew", "brew install tesseract")],
            "linux": [cmd("apt", "sudo apt-get update && sudo apt-get install -y tesseract-ocr tesseract-ocr-eng")],
        })
    if check_id == "pytesseract":
        return [cmd("requirements", "python -m pip install -r requirements.txt")]
    if check_id == "faster-whisper":
        return [cmd("requirements", "python -m pip install -r requirements-asr.txt")]
    if check_id == "asr-model":
        return [
            cmd("doctor", f"python scripts/doctor.py --profile asr --download-asr-model {asr_model} --asr-model {asr_model}"),
            cmd("docker", f"docker build --target asr --build-arg PRELOAD_ASR_MODEL={asr_model} -t video-analysis-skill:asr-{asr_model} ."),
        ]
    if check_id == "docker":
        return by_platform(system, {
            "windows": [cmd("official", "Install Docker Desktop from https://www.docker.com/products/docker-desktop/")],
            "darwin": [cmd("official", "Install Docker Desktop from https://www.docker.com/products/docker-desktop/")],
            "linux": [cmd("official", "Install Docker Engine from https://docs.docker.com/engine/install/")],
        })
    return [cmd("manual", "Review the check detail and install the missing component.")]


def by_platform(system: str, values: dict[str, list[dict[str, str]]]) -> list[dict[str, str]]:
    if system.startswith("win"):
        return values.get("windows", [])
    if system == "darwin":
        return values.get("darwin", [])
    return values.get("linux", [])


def cmd(manager: str, command: str) -> dict[str, str]:
    return {"method": manager, "command": command}


def platform_summary() -> dict[str, str]:
    return {
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "python": sys.version.split()[0],
    }


def summarize(checks: list[dict[str, Any]], actions: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "total_checks": len(checks),
        "missing_required": sum(1 for row in checks if row["level"] == "required" and not row["ok"]),
        "missing_recommended": sum(1 for row in checks if row["level"] == "recommended" and not row["ok"]),
        "actions": len(actions),
        "failed_actions": sum(1 for row in actions if not row["ok"]),
    }


def to_markdown(result: dict[str, Any]) -> str:
    lines = [
        f"# Video Analysis Skill Doctor",
        "",
        f"- Status: `{result['status']}`",
        f"- Profile: `{result['profile']}`",
        f"- Platform: {result['platform']['system']} {result['platform']['release']} ({result['platform']['machine']})",
        "",
        "## Checks",
        "",
        "| Component | Level | Status | Detail |",
        "| --- | --- | --- | --- |",
    ]
    for row in result["checks"]:
        status = "ok" if row["ok"] else "missing"
        lines.append(f"| {row['name']} | {row['level']} | {status} | {row['detail']} |")

    if result.get("actions"):
        lines.extend(["", "## Actions", ""])
        for action in result["actions"]:
            status = "ok" if action["ok"] else "failed"
            lines.append(f"- {action['name']}: {status} - {action['detail']}")

    if result.get("repair_plan"):
        lines.extend(["", "## Repair Plan", ""])
        for step in result["repair_plan"]:
            lines.append(f"### {step['name']}")
            lines.append(f"- Level: `{step['level']}`")
            lines.append(f"- Current: {step['current']}")
            for option in step["options"]:
                lines.append(f"- `{option['method']}`: `{option['command']}`")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
