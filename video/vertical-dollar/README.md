# Vertical dollar film — Scenes 1–6

Motion Canvas 3.17, TypeScript, React Three Fiber/Three.js and GSAP; 1080 × 1920, **60 fps**, 60 seconds. `src/main.tsx` is the absolute-time master timeline. Scene 1 and the shared Scene 2/3 bridge use R3F WebGL canvases; later scenes use procedural Three.js canvases composited by Motion Canvas.

- **Scene 1 [0,8):** 3D dollar, particle shatter, kinetic title, O-zoom and chromatic drop. Its outgoing effect overlaps Scene 2 until 8.1s.
- **Scene 2 [8,18):** procedural balance, barrel and dollar bill; typewriter, particles, icosahedral wireframe globe and camera orbit.
- **Scene 3 [18,28):** reuses the same globe and camera; USA-to-Europe/Asia/Middle East routes, continuing orbit, and `88% OF ALL FX TRADES`. The separate [28,28.2) tail flashes white and whips the camera 90°; Scene 4 starts under that tail from the exact whip endpoint.
- **Scene 4 [28,38):** procedural vault, gold bars and green shield; impact at 28.6s, bars and bond text at 32s, shield and safe-haven text at 35s. Fades to black on [37.8,38).
- **Scene 5 [38,48):** pink-tinted challenger blocks and coin attack; extruded green dollar impact and seeded particle burst at 42.5s, and glitch text at 45s. Its separate [48,48.3) tail supplies the one-frame green flash and outgoing zoom/multisample blur.
- **Scene 6 [48,60):** pure-black backing, procedural green 3D crown and sequential text; CTA with pulsing green dot and `Follow for more.` from 57s. Because the requested Scene 5 flash must be visible at 48, it sits above Scene 6's black backing; the zoom tail remains visible until 48.3, when the screen resets to black and the crown fades in. Both a visible green flash and a visible black frame cannot occupy the same frame.

Three.js `LineBasicMaterial` has no dash-size/gap/offset properties. Scene 3 uses `LineDashedMaterial` for dash and gap, a shader uniform for dash offset, geometry draw ranges for reveal, and translucent additive tubes for glow. No second globe is created.

## Audio

`AudioManager` schedules the 8, 28 and 48-second cues and renders the preview track through Web Audio offline: the unfiltered audio switches to a low-pass at 58s, sweeping from 20 kHz to 200 Hz while gain fades linearly to zero by 60s. Motion Canvas plays the processed WAV blob; there is no second player and scrubbing is deterministic. The source remains `src/audio/placeholder.wav`, an original synthetic **placeholder, not a finished synthwave/phonk score**. To preview a supplied licensed track, put it under `src/audio/` and change the import in `src/audio/index.ts`. The FFmpeg command below applies the sweep and fade to `audio.mp3` for the final mux. Audio has not been independently listened to here.

## Editor and render

```sh
npm ci
npm run test
npm run build
npm run dev
```

Open the Motion Canvas editor at the displayed URL. Preview and render are both set to 60 fps; the project has 3,600 output frames numbered `000000.png` through `003599.png`. The 28s and 48s flashes are one 60-fps frame each.

To render the full image sequence from the terminal, install Chrome or Chromium and run from this directory:

```sh
npm run render
```

The command runs the Motion Canvas image-sequence exporter in headless Chrome in bounded batches, restarting Chromium between batches to limit memory use, and writes `output/project/%06d.png`. It refuses to overwrite existing numbered PNGs. If Chrome is not in your PATH, set `CHROME_PATH` to its executable; `CHROME_NO_SANDBOX=1` is only for environments that require disabling Chrome's sandbox. Output files are ignored by Git and can be large. A full render attempt was interrupted when Chromium disconnected after 128 frames. The revised batched runner was smoke-tested from a late-scene seek; a complete 3,600-frame render has not yet been verified.

With the final `audio.mp3` in this directory, use FFmpeg 7 or newer (with libx264 and AAC) to stitch the sequence into a 60-second video, including the audio sweep and fade:

```sh
ffmpeg -framerate 60 -start_number 0 -i output/project/%06d.png -i audio.mp3 \
  -af "apad=whole_dur=60,asendcmd=c='58-60 [expr] lowpass frequency 20000*exp(-4.605170186*TI)',lowpass=f=20000:enable='gte(t,58)',afade=t=out:st=58:d=2" \
  -frames:v 3600 -t 60 -c:v libx264 -pix_fmt yuv420p -r 60 \
  -c:a aac -b:a 192k -movflags +faststart final.mp4
```

FFmpeg's low-pass frequency is updated per audio block, so it approximates the smoother Web Audio preview sweep. If the source audio is shorter than 60 seconds, `apad` supplies silence; it does not extend music. The command assumes the supplied audio starts at project time zero.

Automated tests cover cues, scene timing, camera continuity, animation poses, flashes, seek determinism and the outro envelope. Editor seeks for representative frames including the crown and CTA were visually inspected, and the actual Web Audio sweep was verified with a test tone. A short 60-fps image-sequence render and FFmpeg stitching smoke test passed. No full video render, audio playback or listening audit has been performed.
