import {describe, expect, it} from 'vitest';
import {OIL_TEXT, sampleScene2} from '../src/scene2/motion';

describe('Scene 2 absolute-time choreography', () => {
  it('exists only on the half-open 8.0–18.0 second interval', () => {
    expect(sampleScene2(7.999).active).toBe(false);
    expect(sampleScene2(8).active).toBe(true);
    expect(sampleScene2(17.999).active).toBe(true);
    expect(sampleScene2(18).active).toBe(false);
  });
  it('starts the barrel drop at 8 and tilts the balance after impact', () => {
    expect(sampleScene2(8).fall).toBe(0);
    expect(sampleScene2(8).tilt).toBe(0);
    expect(sampleScene2(8.6).tilt).toBeGreaterThan(0);
    expect(sampleScene2(9.2).fall).toBeCloseTo(1);
    expect(sampleScene2(9.2).tilt).toBeCloseTo(.3);
  });
  it('types the correct code line at 12 and stops blinking at completion', () => {
    expect(sampleScene2(11.999).textOpacity).toBe(0);
    expect(sampleScene2(12).textCount).toBe(0);
    expect(sampleScene2(12).cursorVisible).toBe(true);
    expect(sampleScene2(12.5).cursorVisible).toBe(false);
    expect(sampleScene2(13.5).textCount).toBe(OIL_TEXT.length);
    expect(sampleScene2(13.5).typing).toBe(false);
    expect(sampleScene2(13.5).cursorVisible).toBe(true);
    expect(sampleScene2(13.9).cursorVisible).toBe(true);
  });
  it('forms particles and completes a 45-degree camera orbit', () => {
    expect(sampleScene2(15).explosion).toBe(0);
    expect(sampleScene2(15.5).explosion).toBeGreaterThan(0);
    expect(sampleScene2(17.9).formation).toBe(1);
    expect(sampleScene2(17.9).orbit).toBeCloseTo(Math.PI / 4);
  });
  it('returns identical poses when time is sampled out of order', () => {
    const before=sampleScene2(16.2);sampleScene2(9);sampleScene2(17.8);
    expect(sampleScene2(16.2)).toEqual(before);
  });
});
