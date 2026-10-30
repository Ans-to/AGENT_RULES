# Reproduction notes

HyperFrames project files use bundled GSAP and Three.js 0.180.0 (Three.js MIT license in `assets/THREE-LICENSE.txt`; GSAP distribution banner records its license). Original geometry, soundtrack and effects are procedural. Standard system Arial and Georgia fallbacks are used; rendering can differ across machines. Adam narration was synthesized with Kokoro ONNX (not Chatterbox); the approved narration is included. `DIRECTOR_CUES.md` is the cue list and `MOTION_SCRIPT.md` the original provisional visual brief.

Requirements: Node.js 22+, HyperFrames CLI 0.8.216, Chromium with WebGL (SwiftShader works), FFmpeg/ffprobe, Python 3 with numpy and soundfile to regenerate audio. Serve the project over HTTP rather than opening index.html as a file, so module imports work. From repository root, regenerate HTML with `python video/dollar-film/scripts/build.py`. The bundled `assets/master.wav` is the delivery-ready audio input. To regenerate the original pre-master: `python video/dollar-film/scripts/sound.py`, then run FFmpeg loudness normalization on `assets/mix-pre.wav` (the original target was −16 LUFS, −1.5 dBTP, LRA 9) and add 2 dB; exact platform normalization may differ. Avoid overwriting the included master if an identical mix is required.

Render from the repository root, adapting executable paths to your system:

```
hyperframes check video/dollar-film
hyperframes render video/dollar-film --output video/dollar-film/why-the-dollar.mp4 --fps 30 --quality high --workers 1 --no-browser-gpu
```

In this environment the rendering used a locally installed Chromium and FFmpeg with `HYPERFRAMES_BROWSER_PATH` and `LD_LIBRARY_PATH` set. SwiftShader at one worker took about 3.4 minutes. The delivered MP4 was remuxed after rendering with +2 dB on its AAC audio for the YouTube loudness check; `assets/master.wav` was raised by the same amount for future renders. Encoding can make the resulting loudness differ slightly. Third-party dependencies and models must be installed separately if rebuilding on a new machine.
