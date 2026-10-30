import {gsap} from 'gsap';
export const SCENE6_START=48, SCENE6_END=60, REVEAL_START=48.3;
const clamp=(v:number)=>Math.max(0,Math.min(1,v));
const crownEase=gsap.parseEase('back.out(1.7)'),textEase=gsap.parseEase('power2.out');
export function sampleScene6(time:number){
  const active=time>=SCENE6_START&&time<SCENE6_END;
  // The outgoing Scene 5 flash/zoom occupies [48,48.3); reveal follows its black reset.
  const reveal=clamp((time-REVEAL_START)/.55);
  const crownScale=time<REVEAL_START?0:crownEase(clamp((time-REVEAL_START)/1));
  const crownRotation=Math.PI*2*Math.max(0,time-48)/12;
  const contentOpacity=1-clamp((time-57)/.35);
  const words=[0,.2,.4].map(offset=>textEase(clamp((time-53-offset)/.6)));
  const cta=time>=57;
  const dotScale=cta?1+.3*(.5-.5*Math.cos(2*Math.PI*(time-57))):1;
  const ctaOpacity=clamp((time-57)/.35);
  const followOpacity=clamp(time-57);
  return {active,reveal,crownScale,crownRotation,contentOpacity,words,cta,dotScale,ctaOpacity,followOpacity};
}
