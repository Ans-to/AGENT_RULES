import {describe, expect, it, vi} from 'vitest';
import {AudioManager} from '../src/audio/AudioManager';

describe('AudioManager', () => {
  it('uses a 120 BPM timeline and schedules all three requested drops', () => {
    const audio = new AudioManager('/track.wav');
    expect(audio.bpm).toBe(120);
    expect(audio.drops.map(drop => drop.time)).toEqual([8, 28, 48]);
  });
  it('shows a 20px shift for the first 0.1 seconds including the exact drop frame', () => {
    const audio = new AudioManager('/track.wav');
    expect(audio.visualAt(7.999).chromaticShiftPx).toBe(0);
    expect(audio.visualAt(8).chromaticShiftPx).toBe(20);
    expect(audio.visualAt(8.099).chromaticShiftPx).toBe(20);
    expect(audio.visualAt(8.1).chromaticShiftPx).toBe(0);
    expect(audio.visualAt(28).drop?.time).toBe(28);
    expect(audio.visualAt(28).chromaticShiftPx).toBe(0);
  });
  it('notifies once on forward crossings, never on seeks or repeated frames', () => {
    const audio = new AudioManager('/track.wav');
    const callback=vi.fn();audio.subscribe(callback);
    audio.advance(7.99);audio.advance(8);audio.advance(8);audio.advance(8.05);
    expect(callback).toHaveBeenCalledTimes(1);
    audio.seek(7);audio.advance(8);expect(callback).toHaveBeenCalledTimes(2);
    audio.seek(30);audio.advance(29);expect(callback).toHaveBeenCalledTimes(2);
  });
  it('finds several cues when a frame jumps forward, but none in reverse', () => {
    const audio=new AudioManager('/track.wav');
    expect(audio.crossings(0,49).map(x=>x.time)).toEqual([8,28,48]);
    expect(audio.crossings(49,0)).toEqual([]);
  });
  it('loads the configured track and reports HTTP failures', async () => {
    const audio=new AudioManager('/track.wav');
    const fetchMock=vi.spyOn(globalThis,'fetch').mockResolvedValueOnce(new Response(new Uint8Array([1,2,3]))).mockResolvedValueOnce(new Response('',{status:404}));
    await expect(audio.load()).resolves.toBeUndefined();
    await expect(new AudioManager('/track.wav').load()).rejects.toThrow('Audio load failed (404)');
    expect(fetchMock).toHaveBeenCalledWith('/track.wav');fetchMock.mockRestore();
  });
});
