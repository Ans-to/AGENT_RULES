import json,html
from pathlib import Path
root=Path('video/dollar-film'); timings=json.loads(Path('video/narration/timings.json').read_text())['segments']
phrases=[
 [('WHY DOES THE',0,.27),('WORLD RELY ON',.27,.53),('THE DOLLAR?',.53,.76),('A GLOBAL SYSTEM',.76,1)],
 [('BRETTON WOODS',0,.27),('1944',.27,.40),('CURRENCIES → DOLLAR',.40,.69),('CENTRAL BANKS ↔ GOLD',.69,1)],
 [('1971',0,.24),('GOLD WINDOW',.24,.47),('CLOSED',.47,.67),('THE ROLE SURVIVED',.67,1)],
 [('A LARGE ECONOMY',0,.28),('DEEP MARKETS',.28,.57),('HOLD + TRADE',.57,.79),('DOLLAR ASSETS',.79,1)],
 [('TRADE',0,.33),('BANKS LEND',.33,.64),('CENTRAL BANK RESERVES',.64,1)],
 [('EACH USE',0,.25),('REINFORCES',.25,.49),('MORE PEOPLE',.49,.74),('MORE USEFUL',.74,1)],
 [('NOT PERMANENT',0,.34),('OTHER CURRENCIES',.34,.67),('CONFIDENCE CAN CHANGE',.67,1)],
 [('NOT THE ONLY CURRENCY',0,.31),('HISTORY',.31,.53),('MARKETS',.53,.70),('HABIT',.70,.84),('A CONNECTED WORLD',.84,1)]
]
ends=[6.556,16.568,23.337,30.875,37.281,43.283,49.305,58.4]
body=[]; tl=[]; labels=['THE QUESTION','THE ORIGIN','THE BREAK','THE MARKET','GLOBAL USE','THE NETWORK','THE LIMIT','THE ANSWER']
for i,(segment, seq) in enumerate(zip(timings,phrases)):
 start=segment['start_seconds']; duration=segment['duration_seconds'];
 for j,(text,a,b) in enumerate(seq):
  begin=round(start+a*duration,3); stop=round(start+b*duration,3)
  if i==7 and j==len(seq)-1: stop=58.0
  d=round(stop-begin,3); id=f'p{i+1}_{j+1}'
  # Letters remain a live, seekable part of the timeline, not baked title cards.
  letters=''.join('<span class="word">'+''.join(f'<span class="glyph">{html.escape(ch)}</span>' for ch in word)+'</span>' for word in text.split(' '))
  size=92 if len(text)>22 else 112 if len(text)>15 else 140
  body.append(f'<div id="{id}" class="clip phrase theme{i%2}" data-start="{begin}" data-duration="{d}" data-track-index="1" style="font-size:{size}px"><div class="glyphs">{letters}</div></div>')
  if d>=.4:
   tl.append(f'tl.fromTo("#{id} .glyph:not(.space)",{{opacity:0,y:65,scaleY:.55,scaleX:1.25,rotation:-4}},{{opacity:1,y:0,scaleY:1,scaleX:1,rotation:0,duration:.37,stagger:{{each:.015,from:"start"}},ease:"back.out(1.5)"}},{begin});')
   tl.append(f'tl.to("#{id} .glyphs",{{opacity:0,x:35,filter:"blur(6px)",duration:.15,ease:"power2.in"}},{max(begin+.32,stop-.18):.3f});')
 start=segment['start_seconds']; stop=ends[i]
 body.append(f'<div id="tag{i+1}" class="clip section-label" data-start="{start}" data-duration="{stop-start:.3f}" data-track-index="2"><span>{i+1:02d}</span> / {labels[i]}</div>')
 if i>0:
  t=start-.16
  body.append(f'<div id="wipe{i}" class="clip wipe" data-start="{t:.3f}" data-duration=".46" data-track-index="3"><div class="wipe-inner"></div></div>')
  tl.append(f'tl.fromTo("#wipe{i} .wipe-inner",{{xPercent:-110}},{{xPercent:110,duration:.46,ease:"power2.inOut"}},{t:.3f});')
content='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=1920,height=1080"><link rel="stylesheet" href="style.css"><script src="assets/gsap.min.js"></script><script type="module" src="assets/scene3d.js"></script></head><body><div id="root" data-composition-id="main" data-start="0" data-duration="58.4" data-width="1920" data-height="1080">
<canvas id="world" width="960" height="540"></canvas><div class="shade"></div><div class="edge"></div><div class="eyebrow">THE WORLD'S RESERVE CURRENCY</div><div class="footer">HISTORY <span>×</span> MARKETS <span>×</span> NETWORKS</div>
BODY
<audio id="master" class="clip" data-start="0" data-duration="58.4" data-track-index="4" src="assets/master.wav"></audio></div>
<script>window.__timelines=window.__timelines||{};const tl=gsap.timeline({paused:true});TL
window.__timelines.main=tl;</script></body></html>'''.replace('BODY','\n'.join(body)).replace('TL','\n'.join(tl))
(root/'index.html').write_text(content)
