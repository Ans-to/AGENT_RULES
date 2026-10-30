import {describe,it,expect} from 'vitest';
import {sampleScene6} from '../src/scene6/motion';
import {AudioManager} from '../src/audio/AudioManager';
describe('Scene 6 outro',()=>{
  it('is strictly active from 48 to 60 and starts black',()=>{
    expect(sampleScene6(47.999).active).toBe(false);expect(sampleScene6(48).active).toBe(true);
    expect(sampleScene6(48).reveal).toBe(0);expect(sampleScene6(48.3).reveal).toBe(0);
    expect(sampleScene6(59.999).active).toBe(true);expect(sampleScene6(60).active).toBe(false);
  });
  it('reveals the crown and turns once in twelve seconds',()=>{
    expect(sampleScene6(48.3).crownScale).toBe(0);expect(sampleScene6(49.3).crownScale).toBeCloseTo(1);
    expect(sampleScene6(48).crownRotation).toBe(0);expect(sampleScene6(60).crownRotation).toBeCloseTo(Math.PI*2);
  });
  it('staggers the three words beginning at 53',()=>{
    expect(sampleScene6(53).words).toEqual([0,0,0]);
    const p=sampleScene6(53.3).words;expect(p[0]).toBeGreaterThan(p[1]);expect(p[1]).toBeGreaterThan(0);expect(p[2]).toBe(0);
    expect(sampleScene6(54.1).words.every(x=>x===1)).toBe(true);
  });
  it('fades the crown and pulses the CTA from 57',()=>{
    expect(sampleScene6(56.999).cta).toBe(false);expect(sampleScene6(57).cta).toBe(true);
    expect(sampleScene6(57).dotScale).toBeCloseTo(1);expect(sampleScene6(57.5).dotScale).toBeCloseTo(1.3);expect(sampleScene6(58).dotScale).toBeCloseTo(1);
    expect(sampleScene6(57.35).contentOpacity).toBeCloseTo(0);expect(sampleScene6(57).followOpacity).toBe(0);expect(sampleScene6(58).followOpacity).toBe(1);
  });
  it('provides a 58–60s exponential low-pass and linear volume envelope',()=>{
    const audio=new AudioManager('/track');expect(audio.outroAt(57)).toEqual({gain:1,cutoffHz:20000});
    expect(audio.outroAt(59).gain).toBeCloseTo(.5);expect(audio.outroAt(59).cutoffHz).toBeCloseTo(2000);
    expect(audio.outroAt(60).gain).toBe(0);expect(audio.outroAt(60).cutoffHz).toBeCloseTo(200);
  });
  it('returns identical state after arbitrary seeks',()=>{const p=sampleScene6(53.7);sampleScene6(59);sampleScene6(48);expect(sampleScene6(53.7)).toEqual(p);});
});
