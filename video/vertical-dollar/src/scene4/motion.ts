import {gsap} from 'gsap';
export const SCENE4_START=28, SCENE4_END=38, FADE_START=37.8;
export const DOOR_IMPACT=28.6;
export const GOLD_COUNT=6;
const clamp=(v:number)=>Math.max(0,Math.min(1,v));
const power=gsap.parseEase('power4.in');
const back=gsap.parseEase('back.out(1.5)');
const pushEase=gsap.parseEase('power1.inOut');

/** Unit-mass spring with stiffness 100, damping 10, initial velocity zero. */
export function spring(t:number):number {
  if(t<=0)return 0;
  const omega=Math.sqrt(75);
  return 1-Math.exp(-5*t)*(Math.cos(omega*t)+5/omega*Math.sin(omega*t));
}
export function sampleScene4(time:number) {
  const doorProgress=power(clamp((time-28)/(DOOR_IMPACT-28)));
  const elapsed=time-DOOR_IMPACT;
  const shake=elapsed>=0 && elapsed<.4 ? 10*Math.cos(2*Math.PI*15*elapsed)*Math.exp(-7*elapsed) : 0;
  const gold=Array.from({length:GOLD_COUNT},(_,i)=>back(clamp((time-32-i*.1)/.6)));
  const push=pushEase(clamp((time-32)/1.2));
  const textCount=Math.min('US TREASURY BONDS'.length,Math.max(0,Math.floor((time-32)*13)));
  // Clamp the physical spring's overshoot to the requested 1.1 maximum.
  const shieldScale=Math.max(0,Math.min(1.1,spring(time-35)));
  const safeOpacity=clamp((time-35)/.7);
  const doorOpacity=1-pushEase(clamp((time-31.8)/.8));
  return {active:time>=SCENE4_START&&time<SCENE4_END,doorAngle:-Math.PI/2*(1-doorProgress),shake,gold,push,textCount,shieldScale,safeOpacity,doorOpacity};
}

/** Fade Scene 4 to black before the exact 38-second handoff. */
export function sampleScene4Transition(time:number) {
  return {active:time>=FADE_START && time<SCENE4_END,black:clamp((time-FADE_START)/(SCENE4_END-FADE_START))};
}
