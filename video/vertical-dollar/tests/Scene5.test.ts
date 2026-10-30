import {describe,it,expect} from 'vitest';
import {IMPACT,sampleScene5,sampleScene5Transition} from '../src/scene5/motion';
import {sampleScene4Transition} from '../src/scene4/motion';

describe('Scene 5 and finale',()=>{
  it('occupies only [38,48), starting fully black after Scene 4',()=>{
    expect(sampleScene5(37.999).active).toBe(false);expect(sampleScene5(38).active).toBe(true);
    expect(sampleScene5(38).fade).toBe(0);expect(sampleScene4Transition(38).black).toBe(1);
    expect(sampleScene5(38.55).fade).toBeCloseTo(1);
    expect(sampleScene5(47.999).active).toBe(true);expect(sampleScene5(48).active).toBe(false);
  });
  it('accelerates all challengers from the edges to the center together',()=>{
    expect(sampleScene5(38).attack).toBe(0);
    expect(sampleScene5(40.25).attack).toBeCloseTo(.125);
    expect(sampleScene5(IMPACT).attack).toBe(1);
    expect(sampleScene5(42).attack).toBeGreaterThan(sampleScene5(40).attack);
  });
  it('drops the dollar at 42 and shatters on impact at 42.5',()=>{
    expect(sampleScene5(41.999).drop).toBe(0);expect(sampleScene5(42).drop).toBe(0);
    expect(sampleScene5(42.25).drop).toBeCloseTo(1/32);
    expect(sampleScene5(IMPACT).drop).toBe(1);expect(sampleScene5(42.499).shatter).toBe(0);
    expect(sampleScene5(IMPACT).impactShake).toBe(8);
    expect(sampleScene5(42.75).shatter).toBe(1);expect(sampleScene5(42.75).burst).toBeCloseTo(.25);
  });
  it('glitches for exactly 0.3 seconds, then retains the text',()=>{
    expect(sampleScene5(44.999).textVisible).toBe(false);
    expect(sampleScene5(45).glitch).toBe(true);expect(sampleScene5(45.299).glitch).toBe(true);
    const p=sampleScene5(45.3);expect(p.glitch).toBe(false);expect(p.textVisible).toBe(true);expect(p.jitterX).toBe(0);expect(p.jitterY).toBe(0);
    for(let i=0;i<9;i++){const f=sampleScene5(45+i/30);expect(Math.abs(f.jitterX)).toBeLessThanOrEqual(5);expect(Math.abs(f.jitterY)).toBeLessThanOrEqual(5);}
  });
  it('flashes green for one frame and scales forward in a separate tail',()=>{
    expect(sampleScene5Transition(47.999).active).toBe(false);
    expect(sampleScene5Transition(48).flash).toBe(true);expect(sampleScene5Transition(48).zoom).toBe(1);
    expect(sampleScene5Transition(48+1/60).flash).toBe(false);
    expect(sampleScene5Transition(48.15).zoom).toBeCloseTo(1.125);
    expect(sampleScene5Transition(48.29999).zoom).toBeCloseTo(5,2);
    expect(sampleScene5Transition(48.3).active).toBe(false);
  });
  it('remains deterministic when seeking out of order',()=>{
    const a=sampleScene5(45.1);sampleScene5(38);sampleScene5(48);expect(sampleScene5(45.1)).toEqual(a);
  });
});
