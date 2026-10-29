"""Generate narration from locally installed Kokoro assets. Run from repository root."""
import json, os, time
import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

segments = [
"Why does the world rely on the US dollar? The answer isn't one law. It's a system built over decades.",
"In nineteen forty four, delegates at Bretton Woods designed a new monetary order. Many currencies were tied to the dollar, and foreign central banks could exchange dollars for American gold.",
"In nineteen seventy one, the United States closed that gold window. The link broke, but the dollar's central role survived.",
"Why? America's huge economy and deep Treasury market offer investors a place to hold and trade dollar assets.",
"Businesses invoice global trade in dollars. Banks lend in dollars. Central banks keep dollar reserves.",
"Each use reinforces the others: the more people accept dollars, the more useful dollars become.",
"That network is powerful, but not permanent. Other currencies compete, and confidence can change.",
"The dollar leads not because it's the world's only currency, but because history, markets, and habit keep connecting the world to it."
]
base='.cache/tools/node_modules/kokoro-local-runtime/voices/am_michael.bin'
v=np.fromfile(base, dtype=np.float32).reshape(-1,1,256)
np.savez('.cache/model/michael.npz',am_michael=v)
model=Kokoro('.cache/model/model_quantized.onnx','.cache/model/michael.npz')
os.makedirs('video/assets/audio',exist_ok=True)
cues=[]; cursor=0.55
for i,text in enumerate(segments):
    a,sr=model.create(text,voice='am_michael',speed=1.06,lang='en-us')
    path=f'video/assets/audio/voice-{i+1}.wav'; sf.write(path,a,sr)
    dur=len(a)/sr
    cues.append({'index':i+1,'start':round(cursor,3),'duration':round(dur,3),'text':text,'file':f'assets/audio/voice-{i+1}.wav'})
    print(i+1,round(cursor,2),round(dur,2), flush=True)
    cursor+=dur+0.35
open('video/assets/cues.json','w').write(json.dumps(cues,indent=2)+'\n')
print('end',cursor)
