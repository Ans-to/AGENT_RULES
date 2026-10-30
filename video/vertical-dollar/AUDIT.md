# Project audit — 2026-10-30

## Verified

- `npm run test`: 35 tests passed; `npm run build`: passed (Vite reports a large bundle warning).
- Motion Canvas is configured for 1080 × 1920, 60 fps and a 60-second timeline.
- Representative scene and transition frames have been inspected in the editor, including the outro crown and CTA. The one-frame flash and scene boundaries have automated checks. These spot checks are not a full visual audit.
- The actual browser audio-processing path was tested with an 8 kHz tone: RMS was approximately 0.518 at 57s, 0.0103 at 59s, and zero near 60s. This confirms strong high-frequency attenuation and fade; it is not a listening review.
- A three-frame 60-fps Motion Canvas image-sequence export and a short FFmpeg H.264/AAC stitching test succeeded. A three-frame late-timeline export from frame 1984 was also verified after fixing a frame-boundary rounding error.
- The included WAV is a synthesized timing placeholder, 60 seconds, 44.1 kHz mono. It is not the requested finished music or a narrated soundtrack. The unprocessed placeholder measured mean -20.6 dBFS and peak -3.9 dBFS; these numbers do not establish subjective audibility or mix quality.

## Limitations and findings

- A full 3,600-frame export initially failed after 128 frames because Chromium disconnected. The renderer was changed to restart Chromium between 64-frame batches to limit memory use, and its frame-range rounding was fixed. Full-run reliability and the completed video remain unverified.
- No complete MP4/video was exported, no whole-video audit or audio listening was completed, and no claim of final creative approval is made. The final licensed music and narration have not been integrated.
- `npm audit` reported 16 development/dependency advisories (4 moderate, 10 high, 2 critical); `npm audit --omit=dev` reported zero production dependency advisories. Review and update dev tooling before exposing the development server to untrusted networks.
- Scene 5's required green flash and zoom tail visually overlay Scene 6's black backing until 48.3s; the black reset is visible after the tail. A simultaneously visible pure-black frame and neon-green flash at 48.0s are incompatible.
