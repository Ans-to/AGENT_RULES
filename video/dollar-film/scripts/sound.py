import json, math
from pathlib import Path
import numpy as np
import soundfile as sf
root=Path('video/dollar-film'); sr=48000; dur=58.4
v, rate=sf.read(root/'assets/narration.wav',dtype='float32'); assert rate==sr
if v.ndim>1: v=v.mean(axis=1)
n=int(dur*sr); t=np.arange(n,dtype=np.float32)/sr
# Original subtle harmonics, slow chord motion, and an unobtrusive periodic pulse.
progression=[(55,69.296,82.407),(51.913,65.406,77.782),(48.999,61.735,73.416),(55,69.296,82.407)]
phase=(t%8)/8; chordindex=(t//8).astype(int)%4
bed=np.zeros(n,dtype=np.float32)
for idx,notes in enumerate(progression):
 mask=(chordindex==idx).astype(np.float32)
 for f in notes:
  bed += mask*np.sin(2*np.pi*f*t + 0.18*np.sin(t*.23))*0.008
pulse=(np.sin(2*np.pi*55*t)*np.exp(-((t%0.75)*8))) *0.014
fade=np.minimum(1,np.minimum(t/1.2,(dur-t)/2.0)).clip(0,1)
bed=(bed+pulse)*fade
mix=np.zeros(n,dtype=np.float32); mix[:len(v)]=v*0.78; mix+=bed
rng=np.random.default_rng(38)
cuetimes=[(0.3,'sweep'),(1.25,'metal'),(3.0,'tick'),(4.6,'tick'),(6.32,'sweep'),(6.75,'metal'),(8.4,'tick'),(9.25,'tick'),(10.05,'tick'),(13.4,'tone'),(16.3,'sweep'),(16.8,'crack'),(17.35,'impact'),(19.6,'impact'),(20.85,'tone'),(23.08,'sweep'),(24.15,'sweep'),(25.3,'tick'),(26.15,'tick'),(26.9,'tick'),(28.2,'tick'),(28.7,'tick'),(30.6,'sweep'),(31.25,'impact'),(33.55,'tick'),(35.55,'impact'),(37.0,'sweep'),(38.2,'tone'),(38.75,'tone'),(39.3,'tone'),(40.1,'tick'),(41.1,'tick'),(43.05,'sweep'),(43.65,'tone'),(44.15,'tone'),(44.65,'tone'),(46.8,'impact'),(49.05,'sweep'),(49.65,'tone'),(52.2,'tick'),(53.4,'tick'),(54.45,'tone')]
for time,kind in cuetimes:
 length={'tick':.08,'metal':.8,'impact':.8,'tone':.5,'sweep':.6,'crack':.35}[kind]
 x=np.arange(int(sr*length),dtype=np.float32)/sr
 if kind=='tick': wave=np.sin(2*np.pi*1250*x)*np.exp(-x*55)*.045
 elif kind=='metal': wave=(np.sin(2*np.pi*740*x)+.5*np.sin(2*np.pi*1135*x))*np.exp(-x*7)*.025
 elif kind=='tone': wave=(np.sin(2*np.pi*440*x)+.45*np.sin(2*np.pi*660*x))*np.exp(-x*5)*.018
 elif kind=='impact': wave=np.sin(2*np.pi*(85-30*x)*x)*np.exp(-x*6)*.032
 elif kind=='crack': wave=rng.normal(0,1,len(x)).astype(np.float32)*np.exp(-x*25)*.024
 else: wave=rng.normal(0,1,len(x)).astype(np.float32)*(np.sin(np.pi*x/length)**2)*.008
 start=int(time*sr); mix[start:start+len(wave)]+=wave[:n-start]
sf.write(root/'assets'/'mix-pre.wav',mix,sr,subtype='PCM_16')
(root/'assets'/'sound-cues.json').write_text(json.dumps(cuetimes,indent=2))
