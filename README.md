# Dollar Empire — Remotion project

A 60-second cinematic motion-graphics adaptation of **“Dollar Empire: The History and Power of the US Currency.”** The landscape and vertical compositions use the same scene architecture and frame-based synchronization map.

## Compositions

- `BrettonWoods-Landscape` — 1920×1080, 30 fps, 1,800 frames
- `BrettonWoods-Vertical` — 1080×1920, 30 fps, 1,800 frames

## Run

```bash
npm install
npm run dev
```

Use the Remotion Studio composition selector to switch formats. Render either format with:

```bash
npm run render:landscape
npm run render:vertical
```

Renders are written to `deliverables/`.

## Synchronization gate

Before rendering or handing off a build, run:

```bash
npm run verify:sync
```

This checks the fixed duration and frame rate, contiguous voiceover cue ranges, dual composition registration and dimensions, required visual standards, and local asset references. The selected narration is embedded as four timed audio clips, and a quiet, custom-generated ambient score fills the 60-second picture. Voiceover text and frame ranges are maintained in `src/sync.ts`; `scripts/generate-ambient.py` regenerates the ambient WAV.
