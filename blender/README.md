# Dot-writing opening scene (Blender)

This branch contains a procedural, code-generated opening animation inspired by the supplied reference: a bright point traces hand-drawn, single-line letterforms, with restrained cyan glow, a dark technical grid, and a clean title resolve. It uses no stock footage or paid assets.

## Render it in GitHub Actions

1. Open the repository's **Actions** tab.
2. Select **Render dot-writing Blender opener**.
3. Choose **Run workflow** on branch `work`.
4. Enter the exact phrase you want the dot to write (the current default is `IDEAS CHANGE EVERYTHING`).
5. Download the `dot-writes-opening` artifact after the workflow finishes.

The workflow installs Blender and FFmpeg on a GitHub-hosted Ubuntu runner, renders an MP4, checks that the output exists and is about eight seconds long, and uploads the result as a 14-day artifact.

## Render locally

With Blender installed:

```bash
OPENING_TEXT="YOUR WORDS HERE" blender -b --python blender/dot_writes_opening.py -- --output output/dot_writes_opening.mp4
```

The vector alphabet supports A–Z, digits, spaces, and basic punctuation. Unsupported symbols are skipped. The animation is designed as a reusable opening template; set `OPENING_TEXT` to the actual narration phrase so the lettering matches what is spoken.

## Honest fidelity note

This is a procedural recreation of the described *visual idea*, not a frame-perfect match. The source clip's exact phrase, camera timing, and original audio have not been extracted or synchronized by this workflow. The generated MP4 is silent; add/synchronize the source narration in a subsequent edit once its audio timing is available.
