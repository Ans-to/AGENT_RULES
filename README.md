# Dollar Empire — Remotion project

A Remotion project containing a 60-second cinematic motion-graphics adaptation of **“Dollar Empire: The History and Power of the US Currency”** and a separate 15-second **Katana / NOISE** kinetic-typography film. Both have paired landscape and vertical compositions.

## Compositions

- `BrettonWoods-Landscape` — 1920×1080, 30 fps, 1,800 frames
- `BrettonWoods-Vertical` — 1080×1920, 30 fps, 1,800 frames
- `Katana-Noise-Landscape` — 1920×1080, 30 fps, 450 frames
- `Katana-Noise-Vertical` — 1080×1920, 30 fps, 450 frames

## Run

```bash
npm install
npm run dev
```

Use the Remotion Studio composition selector to switch formats. Render either format with:

```bash
npm run render:landscape
npm run render:vertical
npm run render:noise:landscape
npm run render:noise:vertical
```

The Katana/NOISE cut is a separate 15-second kinetic-typography sequence: perspective grid drift, pulsing nodes, a light-sweep reveal, dimensional lettering, particles, and restrained HUD framing. Its landscape and vertical renders are also written to `deliverables/`.

## Synchronization gate

Before rendering or handing off a build, run:

```bash
npm run verify:sync
```

This checks the fixed duration and frame rate, contiguous voiceover cue ranges, dual composition registration and dimensions, required visual standards, and local asset references. The selected narration is embedded as four timed audio clips, and a quiet, custom-generated ambient score fills the 60-second picture. Voiceover text and frame ranges are maintained in `src/sync.ts`; `scripts/generate-ambient.py` regenerates the ambient WAV.
