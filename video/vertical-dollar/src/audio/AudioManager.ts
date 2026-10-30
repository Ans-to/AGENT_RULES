import {GlobalSettings} from '../GlobalSettings';

export type BassDrop = Readonly<{type: 'bass-drop'; time: number; index: number}>;
export type VisualEffect = Readonly<{drop: BassDrop | null; chromaticShiftPx: number}>;
export type CueListener = (event: BassDrop) => void;

/**
 * Project-wide cue schedule. Motion Canvas owns playback of trackUrl, so preview
 * and export share a single audio track. This class does not play another copy.
 * Visual state is sampled from absolute project time, making seek/export safe.
 */
export class AudioManager {
  public readonly bpm = GlobalSettings.audio.bpm;
  public readonly trackUrl: string;
  public readonly drops: readonly BassDrop[];
  private listeners = new Set<CueListener>();
  private previousTime = 0;
  private loading?: Promise<void>;
  private bytes?: Promise<ArrayBuffer>;
  private processedUrl?: Promise<string>;

  constructor(trackUrl: string, drops: readonly number[] = GlobalSettings.audio.bassDropsSeconds) {
    this.trackUrl = trackUrl;
    this.drops = drops.map((time, index) => ({type: 'bass-drop', time, index}));
  }

  /** Load/probe the same URL used by the Motion Canvas project, without playing it. */
  async load(): Promise<void> {
    if (!this.loading) {
      this.loading = (async () => {
        await this.fetchTrack();
      })().catch(error => { this.loading = undefined; throw error; });
    }
    await this.loading;
  }

  private fetchTrack(): Promise<ArrayBuffer> {
    this.bytes ??= fetch(this.trackUrl).then(async response => {
      if (!response.ok) throw new Error(`Audio load failed (${response.status}): ${this.trackUrl}`);
      return response.arrayBuffer();
    }).catch(error => {this.bytes=undefined;throw error;});
    return this.bytes;
  }

  /** Absolute-time envelope used by the preview's real audio processing. */
  outroAt(time:number): {gain:number; cutoffHz:number} {
    const p=Math.max(0,Math.min(1,(time-58)/2));
    return {gain:1-p,cutoffHz:20000*Math.pow(.01,p)};
  }

  /**
   * Render the same track that Motion Canvas plays: a seek-safe offline
   * low-pass sweep and gain fade from 58s to 60s. No duplicate player.
   */
  createProcessedTrack(): Promise<string> {
    this.processedUrl ??= (async()=>{
      const raw=await this.fetchTrack();
      const decoder=new OfflineAudioContext(1,1,44100);
      const decoded=await decoder.decodeAudioData(raw.slice(0));
      const sampleRate=decoded.sampleRate,channels=Math.min(2,decoded.numberOfChannels);
      const offline=new OfflineAudioContext(channels,Math.ceil(60*sampleRate),sampleRate);
      const source=offline.createBufferSource();source.buffer=decoded;
      const dry=offline.createGain(),wet=offline.createGain(),filter=offline.createBiquadFilter();
      filter.type='lowpass';filter.Q.value=Math.SQRT1_2;
      filter.frequency.setValueAtTime(20000,0);filter.frequency.setValueAtTime(20000,58);
      filter.frequency.exponentialRampToValueAtTime(200,60);
      dry.gain.setValueAtTime(1,0);dry.gain.setValueAtTime(0,58);
      wet.gain.setValueAtTime(0,0);wet.gain.setValueAtTime(1,58);wet.gain.linearRampToValueAtTime(0,60);
      source.connect(dry).connect(offline.destination);source.connect(filter).connect(wet).connect(offline.destination);source.start(0);
      const buffer=await offline.startRendering();
      return URL.createObjectURL(new Blob([encodeWav(buffer)],{type:'audio/wav'}));
    })().catch(error=>{this.processedUrl=undefined;throw error;});
    return this.processedUrl;
  }

  subscribe(listener: CueListener): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  /** Pure crossing query: half-open (from, to]; reverse seeks emit nothing. */
  crossings(from: number, to: number): readonly BassDrop[] {
    return to > from ? this.drops.filter(drop => from < drop.time && drop.time <= to) : [];
  }

  /** Optional notifications during forward playback; call seek() on scrubbing. */
  advance(time: number): void {
    for (const event of this.crossings(this.previousTime, time)) {
      for (const listener of this.listeners) listener(event);
    }
    this.previousTime = time;
  }

  seek(time: number): void { this.previousTime = time; }

  /** Frame-addressable visual state, including the exact first drop frame. */
  visualAt(time: number): VisualEffect {
    const drop = this.drops.find(item => time >= item.time && time < item.time + 0.1) ?? null;
    return {drop, chromaticShiftPx: drop?.index === 0 ? 20 : 0};
  }
}

/** Encode interleaved 16-bit PCM for Motion Canvas's existing audio player. */
function encodeWav(buffer:AudioBuffer):ArrayBuffer {
  const channels=buffer.numberOfChannels,length=buffer.length,bytes=new ArrayBuffer(44+length*channels*2),v=new DataView(bytes);
  const write=(at:number,text:string)=>{for(let i=0;i<text.length;i++)v.setUint8(at+i,text.charCodeAt(i));};
  write(0,'RIFF');v.setUint32(4,36+length*channels*2,true);write(8,'WAVE');write(12,'fmt ');v.setUint32(16,16,true);v.setUint16(20,1,true);v.setUint16(22,channels,true);v.setUint32(24,buffer.sampleRate,true);v.setUint32(28,buffer.sampleRate*channels*2,true);v.setUint16(32,channels*2,true);v.setUint16(34,16,true);write(36,'data');v.setUint32(40,length*channels*2,true);
  const data=Array.from({length:channels},(_,i)=>buffer.getChannelData(i));let offset=44;
  for(let i=0;i<length;i++)for(let c=0;c<channels;c++){const s=Math.max(-1,Math.min(1,data[c][i]));v.setInt16(offset,s<0?s*32768:s*32767,true);offset+=2;}
  return bytes;
}
