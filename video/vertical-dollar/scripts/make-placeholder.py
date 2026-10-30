"""Produce a clearly temporary 120 BPM cue track, not a licensed music bed."""
import math, struct, wave
from pathlib import Path
sr=44100; duration=60
out=Path('src/audio/placeholder.wav')
with wave.open(str(out),'wb') as wav:
    wav.setnchannels(1);wav.setsampwidth(2);wav.setframerate(sr)
    chunk=bytearray()
    for n in range(sr*duration):
        t=n/sr; beat=t%0.5; hat=(t+.25)%0.5
        kick=math.sin(2*math.pi*(45*beat+35*(1-math.exp(-beat*24))/24))*math.exp(-beat*16)*.37
        bass=(math.sin(2*math.pi*55*t)+.3*math.sin(2*math.pi*110*t))*0.09
        tick=math.sin(2*math.pi*5100*hat)*math.exp(-hat*65)*.025
        elapsed=min((t-x for x in (8,28,48) if 0 <= t-x < .7),default=None)
        boom=math.sin(2*math.pi*42*elapsed)*math.exp(-elapsed*5)*.24 if elapsed is not None else 0
        tail=min(1,(duration-t)/2)
        sample=max(-.96,min(.96,(kick+bass+tick+boom)*max(0,tail)))
        chunk+=struct.pack('<h',round(sample*32767))
        if len(chunk)>=65536:
            wav.writeframesraw(chunk);chunk.clear()
    wav.writeframesraw(chunk)
print(out)
