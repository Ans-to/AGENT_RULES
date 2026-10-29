"""Build a restrained 60-second ambient score for Dollar Empire (stdlib only)."""
import math
import struct
import wave
from pathlib import Path

RATE = 48_000
SECONDS = 60
OUT = Path(__file__).resolve().parents[1] / "public" / "audio" / "ambient-bed.wav"
# Low, open chords with a shared top tone; deliberately no percussion or busy motifs.
CHORDS = [
    (0, 10, (36.71, 73.42, 110.00, 146.83, 164.81, 220.00)),  # Dm add 9
    (10, 25, (32.70, 65.41, 98.00, 130.81, 146.83, 196.00)),  # C add 9
    (25, 45, (49.00, 73.42, 98.00, 146.83, 196.00, 220.00)),  # G6/9
    (45, 60, (36.71, 73.42, 110.00, 146.83, 185.00, 220.00)), # D major color
]


def smoothstep(x: float) -> float:
    x = min(1.0, max(0.0, x))
    return x * x * (3.0 - 2.0 * x)


def chord_at(t: float):
    idx = next(i for i, (start, end, _) in enumerate(CHORDS) if start <= t < end)
    start, end, current = CHORDS[idx]
    blend = 0.0
    following = current
    # Crossfade harmonies gently over two seconds around each section change.
    if idx < len(CHORDS) - 1 and t > end - 2:
        blend = smoothstep((t - (end - 2)) / 2)
        following = CHORDS[idx + 1][2]
    return current, following, blend


OUT.parent.mkdir(parents=True, exist_ok=True)
with wave.open(str(OUT), "wb") as wav:
    wav.setnchannels(2)
    wav.setsampwidth(2)
    wav.setframerate(RATE)
    block = bytearray()
    for n in range(RATE * SECONDS):
        t = n / RATE
        chord_a, chord_b, blend = chord_at(t)
        fade_in = smoothstep(t / 2.2)
        fade_out = smoothstep((SECONDS - t) / 4.0)
        swell = 0.68 + 0.18 * math.sin(2 * math.pi * t / 18.0) + 0.10 * math.sin(2 * math.pi * t / 31.0 + 0.8)
        pulse = 0.92 + 0.08 * math.sin(2 * math.pi * t / 5.2)
        left = right = 0.0
        for i, (fa, fb) in enumerate(zip(chord_a, chord_b)):
            freq = fa + (fb - fa) * blend
            # Soft sine fundamentals, with sparse upper harmonics for cinematic air.
            phase = 2 * math.pi * freq * t
            weight = (0.36 if i < 2 else 0.21 if i < 4 else 0.12) / (1 + i * 0.22)
            tone = math.sin(phase) + 0.15 * math.sin(2 * phase + i * 0.2)
            pan = 0.72 + 0.22 * math.sin(i * 1.3)
            left += tone * weight * pan
            right += tone * weight * (1.0 - pan + 0.5)
        value_scale = 0.035 * swell * pulse * fade_in * fade_out
        left *= value_scale
        right *= value_scale
        block.extend(struct.pack("<hh", int(max(-1, min(1, left)) * 32767), int(max(-1, min(1, right)) * 32767)))
        if len(block) >= 192_000:
            wav.writeframesraw(block)
            block.clear()
    if block:
        wav.writeframesraw(block)
print(f"Wrote {OUT}")
