"""Original procedural stereo underscore for LUMEN; no external samples."""
import math,random,struct,wave,sys
rate=48000;length=15;random.seed(56)
# Four voiced chords, each with its own harmonic movement.
chords=[(110,130.813,164.814,220),(87.307,110,130.813,174.614),(97.999,123.471,146.832,195.998),(82.407,103.826,123.471,164.814)]
def envelope(t,a=.8,r=1.8):return min(1,max(0,t)/a,max(0,(15-t))/r)
# musical arpeggio intervals aligned to 24 fps frame markers
notes=[]
for step in range(36):
 t=.5+step*.375
 if t>14:break
 chord=chords[int(t/3.0)%4];notes.append((t,chord[(step*3+step//4)%4]*2))
with wave.open(sys.argv[1] if len(sys.argv)>1 else 'score.wav','wb') as w:
 w.setparams((2,2,rate,0,'NONE','not compressed'));buf=bytearray()
 for i in range(length*rate):
  t=i/rate;ch=chords[int(t/3)%4];env=envelope(t)
  pad=sum(math.sin(math.tau*f*t+.14*math.sin(math.tau*.13*t))*.012+math.sin(math.tau*f*2*t)*.003 for f in ch)
  bass=math.sin(math.tau*ch[0]*.5*t)*.035
  arp=0.
  for st,f in notes:
   dt=t-st
   if 0<=dt<1.5:
    e=(1-math.exp(-35*dt))*math.exp(-3.3*dt);arp+=.052*e*(math.sin(math.tau*f*dt)+.22*math.sin(math.tau*f*2*dt)+.1*math.sin(math.tau*f*3*dt))
  # Soft low impacts at reveal/transition moments, generated without borrowed samples.
  hit=0
  for onset in (.7,4.0,8.0,11.0):
   dt=t-onset
   if 0<=dt<.8:hit+=.10*math.exp(-7*dt)*math.sin(math.tau*(62*dt-20*dt*dt))
  shimmer=.004*(random.random()*2-1)*max(0,1-abs(t-10.6)/.9)
  left=max(-.9,min(.9,(pad+bass+arp+hit+shimmer)*env));right=max(-.9,min(.9,(pad*.96+bass+arp*.88+hit-shimmer)*env))
  buf.extend(struct.pack('<hh',int(left*32767),int(right*32767)))
  if len(buf)>=192000:w.writeframesraw(buf);buf.clear()
 if buf:w.writeframesraw(buf)
