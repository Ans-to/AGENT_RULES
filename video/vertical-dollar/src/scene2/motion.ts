import {gsap} from 'gsap';

export const SCENE2_START = 8;
export const SCENE2_END = 18;
export const OIL_TEXT = '> OIL = DOLLARS';
const clamp = (v: number) => Math.max(0, Math.min(1, v));
const bounce = gsap.parseEase('bounce.out');
const tiltEase = gsap.parseEase('power3.out');
const formationEase = gsap.parseEase('power4.out');
const orbitEase = gsap.parseEase('power2.inOut');

/** Pure absolute-time pose: safe to render out of order or seek backwards. */
export function sampleScene2(time: number) {
  const active = time >= SCENE2_START && time < SCENE2_END;
  const fall = bounce(clamp((time - 8) / 1.2));
  const tilt = .30 * tiltEase(clamp((time - 8.45) / .65));
  const textCount = Math.min(OIL_TEXT.length, Math.max(0, Math.floor((time - 12) * 14)));
  const typing = time >= 12 && textCount < OIL_TEXT.length;
  const cursorVisible = time >= 12 && (typing ? Math.floor((time - 12) * 2) % 2 === 0 : true);
  const textOpacity = time < 12 ? 0 : 1 - clamp((time - 15) / .3);
  const explosion = formationEase(clamp((time - 15) / .75));
  const formation = formationEase(clamp((time - 15.55) / 1.85));
  const globeVisibility = clamp((time - 15.35) / 1.25);
  const orbit = (Math.PI / 4) * orbitEase(clamp((time - 15) / 2.8));
  const balanceScale = 1 - clamp((time - 15.05) / .8);
  return {active, fall, tilt, textCount, typing, cursorVisible, textOpacity, explosion, formation, globeVisibility, orbit, balanceScale};
}
