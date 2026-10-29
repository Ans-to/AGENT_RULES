# Final video audit

**File:** `dollar-world-currency.mp4`
**Verdict:** technical gates pass, with limitations below.
**Format:** 66.367 seconds, 1920×1080, 30 fps, H.264 video, 48 kHz stereo AAC; 9,906,957 bytes. The entire final file decoded without errors.

## Actual rendered-video inspection

The installed Video Analysis skill inspected the actual MP4. It returned `passed` and extracted ffprobe metadata, quality gates, a 16-frame timestamped contact sheet and individual frames under `audit/final-evidence/`. Visual review of the contact sheet confirms the eight intended story sections are represented, including the 1944 gold arrangement, the 1971 break, Treasury securities, trade/banks/reserves, network effects, competing currencies and the concluding explanation. Sampled frames do not prove what happens between samples; the auditor did not use OCR or speech recognition. Narration-to-scene timing is based on the generated audio cue metadata, not independently force-aligned speech.

## Repair and final checks

The first actual render failed the YouTube loudness gate at **−21.5 LUFS** (7.5 dB below target); its other measured checks passed. The original word-per-minute figure counted source notes as narration, so it is not a valid speech-pace result. The initial audit JSON is `audit/rendercheck-initial.json`.

**Repair 1 of at most 3:** normalized the rendered mix to the YouTube loudness target with FFmpeg loudnorm, authored the normalized audio as the composition's master while retaining the original cue positions, added explanatory scene animations, rechecked the composition and re-rendered the full MP4. `audio/master.wav` is the source mix used in the final render. No further repair attempts were needed.

Final command (with local FFmpeg/ffprobe on PATH):

```sh
rendercheck check video/dollar-world-currency.mp4 --script video/NARRATION.txt \
  --preset youtube --expect-seconds 66.3667 --expect-width 1920 \
  --expect-height 1080 --expect-fps 30 --json
```

Result `audit/rendercheck-final.json`: 11 passes, zero failures, zero skips. 139.2 WPM (based on supplied script and total runtime, **not** ASR), −14.7 LUFS, −1.4 dBTP, zero clipped samples, 0.0 s detected silence, 0.0 s black, 0.0 s frozen, streams aligned. Duration, resolution and frame rate pass. `audit/ffprobe-final.json` records stream metadata. These objective tests do not establish intelligibility or factual accuracy.

HyperFrames final source check (`audit/repaired-check.json`) passed with zero runtime, layout, contrast, motion or audio errors. It reported nine structural warnings because this small project keeps eight scenes in a single root file rather than separate sub-compositions; it also reported a small-type warning affecting decorative labels. Main headlines and explanation lines are larger; not every incidental label is guaranteed readable on a small phone. Check findings are not a substitute for viewing all 1,991 frames.

## Limitations

- Chatterbox model weights were unavailable, so the selected open-source Kokoro `am_michael` voice was used. The user selected it after hearing a generated sample; this is not a claim that an independent expert rated naturalness or intelligibility.
- There was no available local ASR model or OCR binary. Exact narration and on-screen words have not been independently machine-transcribed; the generated text, cue timings, audio tracks and sampled visual frames provide partial evidence only.
- The editorial vector design is original code-generated art, with no Blender or stock photographs. A synthesized background bed was made with code.
- Research sources are listed in `SCRIPT.md`. The video says the dollar is the leading global currency, not the only one, and limits historical gold convertibility to foreign central banks.
