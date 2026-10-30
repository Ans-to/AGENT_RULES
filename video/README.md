# Why Is the US Dollar the World's Currency?

- `dollar-world-currency.mp4` — finished 1080p video, 66.37 seconds.
- `SCRIPT.md` and `NARRATION.txt` — narrative script, sources and exact TTS input.
- `SPEC.md` — director's visual and continuity plan.
- `AUDIT.md` — final technical results, repair history and limitations.
- `INSTALLATION.md` — setup commands, dependencies, licenses, verification and blockers.
- `index.html`, `style.css`, `assets/` and `scripts/` — HyperFrames project and original motion-graphics source.
- `audit/` — machine-readable results, evidence frames and contact sheets.

The movie is built from eight scene-level narration cues in `assets/cues.json`; the final audio is `assets/audio/master.wav`. Rendering requires HyperFrames 0.8.216, FFmpeg/ffprobe and Chrome; setup and environment details are in `INSTALLATION.md`. The model/runtime caches are intentionally not versioned. `scripts/build.py` regenerates the HTML and music bed using the already present final master. Generating new speech requires the local Kokoro weights as documented and should be followed by an audio mix/normalization and re-render; simply changing narration text will not update the existing master.
