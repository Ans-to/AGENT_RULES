import json, math, wave, struct
from pathlib import Path
cues=json.loads(Path('video/assets/cues.json').read_text())
end=math.ceil((cues[-1]['start']+cues[-1]['duration']+1)*30)/30

graphics=[
'''<div class="hero-dollar">$</div><div class="orbit o1"></div><div class="orbit o2"></div><div class="node n1">¥</div><div class="node n2">€</div><div class="node n3">£</div><div class="node n4">₹</div>''',
'''<div class="anchor"><div class="ticket"><small>INTERNATIONAL<br>MONETARY ORDER</small><strong>1944</strong><b>BRETTON WOODS</b></div><div class="chain">→</div><div class="goldbar"><span>GOLD</span><small>$35 / OUNCE</small></div></div>''',
'''<div class="breakline"><div class="coin">$</div><div class="broken"><span></span><i>×</i><span></span></div><div class="goldbar broken-gold"><span>GOLD</span><small>CONVERTIBILITY</small></div></div>''',
'''<div class="treasury"><div class="bond b1"></div><div class="bond b2"></div><div class="bond b3"><small>UNITED STATES</small><b>TREASURY</b><span>SECURITY</span><strong>$</strong></div></div><div class="bars"><i></i><i></i><i></i><i></i><i></i><i></i></div>''',
'''<div class="network"><div class="centercoin">$</div><div class="link l1"></div><div class="link l2"></div><div class="link l3"></div><div class="netitem t1"><b>TRADE</b><small>INVOICING</small></div><div class="netitem t2"><b>BANKS</b><small>LENDING</small></div><div class="netitem t3"><b>RESERVES</b><small>CENTRAL BANKS</small></div></div>''',
'''<div class="ringnet"><div class="core">$</div><div class="circle c1"></div><div class="circle c2"></div><div class="dot d1"></div><div class="dot d2"></div><div class="dot d3"></div><div class="dot d4"></div><div class="dot d5"></div><div class="dot d6"></div><div class="cycle">MORE USERS<br><b>MORE USEFUL</b></div></div>''',
'''<div class="compete"><div class="curr usd">$<small>US DOLLAR</small></div><div class="curr eur">€<small>EURO</small></div><div class="curr yen">¥<small>YEN</small></div><div class="curr pound">£<small>POUND</small></div></div>''',
'''<div class="finalmark"><div class="final-ring"></div><div class="final-dollar">$</div><span class="final-node a"></span><span class="final-node b"></span><span class="final-node c"></span><span class="final-node d"></span></div>'''
]
shots=[
('THE GLOBAL<br><em>COMMON</em><br>DENOMINATOR','ONE CURRENCY. MANY CONNECTIONS.','The dollar is widely used — not the only currency.'),
('A NEW<br><em>MONETARY</em><br>ORDER','BRETTON WOODS  /  1944','Currencies tied to the dollar; the dollar linked to gold.'),
('THE GOLD<br><em>WINDOW</em><br>CLOSES','THE BREAK  /  1971','Foreign governments could no longer exchange dollars for gold.'),
('THE POWER<br>OF <em>DEEP</em><br>MARKETS','THE TREASURY MARKET','A large market makes dollar assets easier to buy and sell.'),
('DOLLARS<br>MOVE THE<br><em>WORLD</em>','THREE REINFORCING USES','Trade invoices, bank lending, and official reserves.'),
('A NETWORK<br>THAT <em>FEEDS</em><br>ITSELF','THE NETWORK EFFECT','More users make the currency more useful to others.'),
('LEADERSHIP<br>IS NOT<br><em>GUARANTEED</em>','A SYSTEM THAT CAN CHANGE','Other currencies compete; confidence matters.'),
('HISTORY.<br>MARKETS.<br><em>HABIT.</em>','THE ANSWER','The dollar leads because connections endure.')]
scene=[]; timeline=[]; audio=[]
for i,(cue,(title,kicker,foot),graphic) in enumerate(zip(cues,shots,graphics)):
 start=0 if i==0 else round(cue['start']-.18,3)
 stop=end if i==len(cues)-1 else round(cues[i+1]['start']-.18,3)
 dur=stop-start
 scene.append(f'''<section id="scene{i+1}" class="clip scene {'dark' if i in [0,2,5,7] else 'light'}" data-start="{start}" data-duration="{dur:.3f}" data-track-index="0">
 <div class="rule"></div><div class="serial">WORLD CURRENCY <span> / </span> {i+1:02d}</div><div class="copy"><div class="kicker">{kicker}</div><h1>{title}</h1><div class="underline"></div><p>{foot}</p></div><div class="art">{graphic}</div><div class="baseline">DOLLAR SYSTEM <span>•</span> A VISUAL EXPLAINER</div></section>''')
 audio.append(f'<audio id="voice{i+1}" class="clip" data-start="{cue["start"]}" data-duration="{cue["duration"]}" data-track-index="1" src="{cue["file"]}"></audio>')
 timeline += [f'tl.fromTo("#scene{i+1} .copy", {{opacity:0, x:-42}}, {{opacity:1, x:0, duration:.55, ease:"power3.out"}}, {start});',f'tl.fromTo("#scene{i+1} .art", {{opacity:0, scale:.90, x:55}}, {{opacity:1, scale:1, x:0, duration:.8, ease:"power3.out"}}, {start+.08:.3f});',f'tl.fromTo("#scene{i+1} .underline", {{scaleX:0}}, {{scaleX:1, duration:.65, ease:"power2.out"}}, {start+.35:.3f});',f'tl.to("#scene{i+1} .art", {{x:-18, duration:{max(dur-.9,.2):.3f}, ease:"none"}}, {start+.9:.3f});']
# Music, intentionally understated; original oscillator composition.
sr=24000
with wave.open('video/assets/audio/bed.wav','wb') as w:
 w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr)
 samples=[]
 notes=[110.0,130.81,164.81,146.83]
 for j in range(int(sr*end)):
  t=j/sr; fade=min(1,t/1.5,(end-t)/2); chord=notes[int(t/8)%len(notes)]
  v=(math.sin(2*math.pi*chord*t)+0.35*math.sin(2*math.pi*chord*1.5*t)+0.23*math.sin(2*math.pi*chord*2*t))*0.027*fade
  v+=math.sin(2*math.pi*55*t)*0.012*math.exp(-((t%1.0)*7))*fade
  samples.append(struct.pack('<h',int(max(-1,min(1,v))*32767)))
 w.writeframes(b''.join(samples))
timeline += [
 'tl.fromTo("#scene1 .hero-dollar", {scale:.65,rotation:-20}, {scale:1,rotation:0,duration:1.1,ease:"back.out(1.3)"}, .25);',
 'tl.to("#scene1 .o1", {rotation:22,duration:7.3,ease:"none"}, .1);',
 'tl.fromTo("#scene2 .goldbar", {x:100,opacity:0}, {x:0,opacity:1,duration:.8,ease:"power3.out"}, 8.8);',
 'tl.fromTo("#scene3 .broken i", {scale:0,opacity:0}, {scale:1,opacity:1,duration:.6,ease:"back.out(2)"}, 21.5);',
 'tl.fromTo("#scene4 .bond", {y:100,opacity:0}, {y:0,opacity:1,duration:.7,stagger:.14,ease:"power3.out"}, 30);',
 'tl.fromTo("#scene4 .bars i", {scaleY:.05}, {scaleY:1,transformOrigin:"bottom",duration:1,stagger:.10,ease:"power2.out"}, 31.1);',
 'tl.fromTo("#scene5 .netitem", {scale:.7,opacity:0}, {scale:1,opacity:1,duration:.5,stagger:1.45,ease:"back.out(1.4)"}, 38);',
 'tl.fromTo("#scene6 .dot", {scale:0}, {scale:1,duration:.3,stagger:.35,ease:"back.out(2)"}, 45.3);',
 'tl.fromTo("#scene7 .curr:not(.usd)", {y:75,opacity:0}, {y:0,opacity:1,duration:.6,stagger:.35,ease:"power2.out"}, 52);',
 'tl.fromTo("#scene8 .final-node", {scale:0}, {scale:1,duration:.5,stagger:.25,ease:"back.out(2)"}, 58.1);'
]
html='''<!doctype html><html lang="en"><head><meta charset="utf-8"><script src="assets/gsap.min.js"></script><link rel="stylesheet" href="style.css"></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="DURATION" data-width="1920" data-height="1080">SCENES
AUDIOS

</div><script>window.__timelines=window.__timelines||{};const tl=gsap.timeline({paused:true});TIMELINE
window.__timelines.main=tl;</script></body></html>'''.replace('DURATION',str(end)).replace('SCENES','\n'.join(scene)).replace('AUDIOS','<audio id="master" class="clip" data-start="0" data-duration="'+str(end)+'" data-track-index="1" src="assets/audio/master.wav"></audio>').replace('TIMELINE','\n'.join(timeline))
Path('video/index.html').write_text(html)
Path('video/hyperframes.json').write_text(json.dumps({'$schema':'https://hyperframes.heygen.com/schema/hyperframes.json','paths':{'assets':'assets','blocks':'compositions','components':'compositions/components'},'authoringSkill':'hyperframes'},indent=2))
print('Duration:',end)
