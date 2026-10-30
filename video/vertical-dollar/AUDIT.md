# Video audit — 2026-10-30

## Verified

- `npm run test`: 35 tests passed; `npm run build`: passed (Vite reports a large bundle warning).
- The full Motion Canvas export completed: 3,600 PNG frames numbered 000000–003599, no missing or extra frames. The batched exporter completed after an earlier Chromium disconnect at frame 128.
- FFmpeg decoded the complete MP4 without reported errors: 60.00 seconds, 3,600 video frames, 1080 × 1920, 60 fps, H.264/yuv420p with AAC 44.1 kHz mono audio.
- A 24-frame contact sheet covering all six scenes was visually inspected. Frame 1680 is the white 28s flash; frame 2280 is the black 38s handoff; frame 2880 is the green 48s flash. This is a spot check, not a frame-by-frame creative review.
- The actual browser audio-processing path was tested with an 8 kHz tone: RMS was approximately 0.518 at 57s, 0.0103 at 59s, and zero near 60s. This confirms attenuation and fade; it is not a listening review.
- Encoded audio `volumedetect`: mean -20.6 dBFS, peak -3.9 dBFS. These numbers alone do not establish subjective audibility or mix quality.
- MP4 SHA-256: `a5bd7fe105475ab323538044b680d4928b8014be2caac1fb81cc74dc9634d00e`.

## Limitations and findings

- The included soundtrack is the synthetic timing placeholder, **not finished synthwave/phonk music**, and this video has **no narration**. The user has been informed. No listening audit was performed; no claim of final creative approval is made.
- Scene 5's flash and zoom tail visually overlay Scene 6's black backing until 48.3s; the black reset is visible after the tail. A simultaneously visible pure-black frame and neon-green flash at 48.0s are incompatible.
- `npm audit` reported 16 development/dependency advisories (4 moderate, 10 high, 2 critical); `npm audit --omit=dev` reported zero production dependency advisories. Review dev tooling before exposing the development server to untrusted networks.
