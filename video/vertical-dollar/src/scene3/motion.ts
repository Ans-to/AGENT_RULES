import {gsap} from 'gsap';
import {GlobalSettings} from '../GlobalSettings';

export const SCENE3_START = 18;
export const SCENE3_END = 28;
export const TRANSITION_END = 28.2;
export const ROUTE_POINTS = 181;
const clamp=(x:number)=>Math.max(0,Math.min(1,x));
const lineEase=gsap.parseEase('power1.inOut');
const elastic=gsap.parseEase('elastic.out(1, 0.5)');
const slide=gsap.parseEase('power3.out');
const whip=gsap.parseEase('power4.in');

/** Absolute-time state shared by editor playback, scrubbing and export. */
export function sampleScene3(time:number) {
  const active=time>=SCENE3_START && time<SCENE3_END;
  const transition=time>=SCENE3_END && time<TRANSITION_END;
  const elapsed=clamp((time-SCENE3_START)/1.5);
  const lineProgress=lineEase(elapsed);
  // Scene 2 has settled at 45° by 17.8s. Extra orbit starts at zero velocity.
  const age=Math.max(0,Math.min(10,time-SCENE3_START));
  const orbit=Math.PI/4 + .0125*age*age;
  const statScale=time<22 ? 0 : elastic(clamp((time-22)/.9));
  const subProgress=time<25 ? 0 : slide(clamp((time-25)/.65));
  const transitionProgress=transition ? clamp((time-SCENE3_END)/.2) : 0;
  const whipYaw=Math.PI/2*whip(transitionProgress);
  // One project frame, independent of floating-point rounding at the boundary.
  const flash=transition && Math.floor((time-SCENE3_END)*GlobalSettings.canvas.fps+1e-7)===0;
  return {active,transition,lineProgress,dashOffset:(1-lineProgress)*3,orbit,statScale,subProgress,whipYaw,flash};
}
