"""Original synthesized score and transitions; no third-party audio."""
import math,random,struct,wave,sys
rate=48000;random.seed(92);tau=math.tau;length=15
chords=[(73.416,110.,146.832,174.614),(65.406,98.,130.813,164.814),(55.,82.407,110.,164.814),(73.416,110.,146.832,220.)]
notes=[(.6,293.665),(1.5,329.628),(2.35,349.228),(3.6,329.628),(4.55,293.665),(5.15,261.626),(6.65,220),(7.9,246.942),(9.1,261.626),(10.9,293.665),(11.55,329.628),(12.3,349.228),(13.3,440.)]
with wave.open(sys.argv[1],'wb') as w:
 w.setparams((2,2,rate,0,'NONE','not compressed'));buf=bytearray()
 for i in range(rate*length):
  t=i/rate;ch=chords[min(3,int(t/3.75))];fade=min(1,t/1.2,max(0,(15-t)/2.2));swell=.65+.35*min(1,t/11)
  pad=sum((math.sin(tau*f*t+.3*math.sin(t*.21))+ .17*math.sin(tau*f*2*t))*.014 for f in ch)*swell
  low=.04*math.sin(tau*ch[0]*.5*t);piano=0
  for start,f in notes:
   dt=t-start
   if 0<=dt<2:
    a=(1-math.exp(-35*dt))*math.exp(-2.4*dt);piano+=.065*a*(math.sin(tau*f*dt)+.25*math.sin(tau*f*2*dt)+.10*math.sin(tau*f*3*dt))
  impact=0
  for st in (0.5,3.32,6.87,11.2):
   dt=t-st
   if 0<=dt<1.1:impact+=.11*math.exp(-6*dt)*math.sin(tau*(52*dt-12*dt*dt))
  rush=0
  for st in (3.32,6.87,11.2):
   q=1-abs(t-st)/.6
   if q>0:rush+=(random.random()*2-1)*.012*q*q
  v=(pad+low+piano+impact+rush)*fade;left=max(-.9,min(.9,v));right=max(-.9,min(.9,(pad*.95+low+piano*.9+impact-rush)*fade));buf.extend(struct.pack('<hh',int(left*32767),int(right*32767)))
  if len(buf)>192000:w.writeframesraw(buf);buf.clear()
 if buf:w.writeframesraw(buf)
