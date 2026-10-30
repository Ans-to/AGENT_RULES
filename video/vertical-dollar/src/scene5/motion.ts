import {gsap} from 'gsap';
import {GlobalSettings} from '../GlobalSettings';
export const SCENE5_START=38, SCENE5_END=48, ZOOM_END=48.3, IMPACT=42.5;
const clamp=(n:number)=>Math.max(0,Math.min(1,n));
const attackEase=gsap.parseEase('power2.in'),dropEase=gsap.parseEase('power4.in'),easeOut=gsap.parseEase('power2.out'),zoomEase=gsap.parseEase('power4.in');

/** Stateless integer hash, so frame jitter is stable in editor and export. */
function hash(n:number):number {let x=(n^0x9e3779b9)>>>0;x=Math.imul(x^(x>>>16),0x7feb352d);x=Math.imul(x^(x>>>15),0x846ca68b);return ((x^(x>>>16))>>>0)/4294967295;}
export function sampleScene5(time:number){
  const attack=attackEase(clamp((time-38)/(IMPACT-38)));
  const drop=time<42?0:dropEase(clamp((time-42)/.5));
  const shatter=easeOut(clamp((time-IMPACT)/.25));
  const burst=Math.max(0,time-IMPACT);
  const impactShake=time>=IMPACT && time<IMPACT+.38?8*Math.cos(2*Math.PI*15*burst)*Math.exp(-8*burst):0;
  const frame=Math.floor(time*GlobalSettings.canvas.fps+1e-6);
  const glitch=time>=45 && time<45.3;
  const jitterX=glitch?Math.round((hash(frame*2)-.5)*10):0;
  const jitterY=glitch?Math.round((hash(frame*2+1)-.5)*10):0;
  return {active:time>=38 && time<48,fade:clamp((time-38)/.55),attack,drop,shatter,burst,impactShake,glitch,jitterX,jitterY,textVisible:time>=45};
}
export function sampleScene5Transition(time:number){
  const active=time>=SCENE5_END && time<ZOOM_END;
  const progress=clamp((time-SCENE5_END)/(ZOOM_END-SCENE5_END));
  return {active,zoom:1+4*zoomEase(progress),flash:active && Math.floor((time-SCENE5_END)*GlobalSettings.canvas.fps+1e-7)===0};
}
