"""Original procedural music, cloth swishes, and impact sounds tied to the fight frames."""
import math,random,struct,wave,sys
sr=48000;random.seed(118);tau=math.tau;hits=[104/24,160/24,228/24,278/24];swings=[3.6,6.1,8.8,11.2]
with wave.open(sys.argv[1],'wb') as w:
 w.setparams((2,2,sr,0,'NONE','not compressed'));buf=bytearray()
 for i in range(15*sr):
  t=i/sr;fade=min(1,t/.7,max(0,(15-t)/1.2));bass=(math.sin(tau*55*t)*.03+math.sin(tau*82.4*t)*.015)*(0.75+0.25*math.sin(tau*.13*t))
  pulse=0
  for n in range(30):
   dt=t-n*.5
   if 0<=dt<.18:pulse+=.035*math.exp(-18*dt)*math.sin(tau*(90*dt-60*dt*dt))
  hit=0
  for st in hits:
   dt=t-st
   if 0<=dt<.55:
    hit+=.24*math.exp(-12*dt)*math.sin(tau*(75*dt-50*dt*dt));hit+=(random.random()*2-1)*.09*math.exp(-35*dt)
  wind=0
  for st in swings:
   dt=t-st
   if 0<=dt<.38:wind+=(random.random()*2-1)*.038*math.sin(math.pi*dt/.38)**2
  v=max(-.9,min(.9,(bass+pulse+hit+wind)*fade));u=max(-.9,min(.9,(bass+pulse+hit*.94-wind*.8)*fade));buf.extend(struct.pack('<hh',int(v*32767),int(u*32767)))
  if len(buf)>192000:w.writeframesraw(buf);buf.clear()
 if buf:w.writeframesraw(buf)
