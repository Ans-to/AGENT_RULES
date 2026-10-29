import { existsSync, readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { DURATION_IN_FRAMES, FPS, NOISE_DURATION_IN_FRAMES, sceneCues, voiceoverCues } from '../src/sync';

const errors: string[] = [];
const projectRoot = resolve(process.cwd());

function audioDurationSeconds(filePath: string): number | undefined {
  const bytes = readFileSync(filePath);
  if (bytes.subarray(0, 4).toString() === 'RIFF' && bytes.subarray(8, 12).toString() === 'WAVE') {
    const sampleRate = bytes.readUInt32LE(24);
    const channels = bytes.readUInt16LE(22);
    const bitsPerSample = bytes.readUInt16LE(34);
    const dataOffset = bytes.indexOf('data', 12, 'ascii');
    if (dataOffset < 0 || !sampleRate || !channels || !bitsPerSample) return undefined;
    const dataBytes = bytes.readUInt32LE(dataOffset + 4);
    return dataBytes / (sampleRate * channels * bitsPerSample / 8);
  }

  // Count MPEG Layer III frames, skipping optional ID3 metadata and corrupt padding bytes.
  const bitrateMpeg1 = [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320];
  const bitrateMpeg2 = [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160];
  let offset = 0;
  if (bytes.subarray(0, 3).toString() === 'ID3' && bytes.length >= 10) {
    const tagLength = ((bytes[6] & 0x7f) << 21) | ((bytes[7] & 0x7f) << 14) | ((bytes[8] & 0x7f) << 7) | (bytes[9] & 0x7f);
    offset = 10 + tagLength + ((bytes[5] & 0x10) ? 10 : 0);
  }
  let seconds = 0;
  let frames = 0;
  while (offset + 4 <= bytes.length) {
    const header = bytes.readUInt32BE(offset);
    const version = (header >>> 19) & 0x3;
    const layer = (header >>> 17) & 0x3;
    const bitrateIndex = (header >>> 12) & 0xf;
    const sampleIndex = (header >>> 10) & 0x3;
    const padding = (header >>> 9) & 0x1;
    if ((header >>> 21) !== 0x7ff || version === 1 || layer !== 1 || bitrateIndex === 0 || bitrateIndex === 15 || sampleIndex === 3) {
      offset += 1;
      continue;
    }
    const rates = version === 3 ? [44100, 48000, 32000] : version === 2 ? [22050, 24000, 16000] : [11025, 12000, 8000];
    const sampleRate = rates[sampleIndex];
    const bitrate = (version === 3 ? bitrateMpeg1 : bitrateMpeg2)[bitrateIndex] * 1000;
    const frameLength = Math.floor((version === 3 ? 144 : 72) * bitrate / sampleRate) + padding;
    if (offset + frameLength > bytes.length) break;
    seconds += (version === 3 ? 1152 : 576) / sampleRate;
    frames += 1;
    offset += frameLength;
  }
  return frames ? seconds : undefined;
}

if (FPS !== 30) errors.push(`Expected 30 fps; found ${FPS}.`);
if (DURATION_IN_FRAMES !== 1800) errors.push(`Expected 1800 frames; found ${DURATION_IN_FRAMES}.`);
if (NOISE_DURATION_IN_FRAMES !== 450) errors.push(`Expected the Katana/NOISE cut to be 450 frames; found ${NOISE_DURATION_IN_FRAMES}.`);
if (voiceoverCues.length !== 4) errors.push(`Expected four voiceover cues; found ${voiceoverCues.length}.`);
if (sceneCues.length !== 4) errors.push(`Expected four scene titles; found ${sceneCues.length}.`);

let cursor = 0;
for (const [index, cue] of voiceoverCues.entries()) {
  if (cue.start !== cursor) errors.push(`Voiceover cue ${index + 1} starts at ${cue.start}; expected contiguous start ${cursor}.`);
  if (cue.end <= cue.start) errors.push(`Voiceover cue ${index + 1} has a non-positive frame range.`);
  if (cue.end > DURATION_IN_FRAMES) errors.push(`Voiceover cue ${index + 1} exceeds the composition length.`);
  if (!cue.voiceover.trim()) errors.push(`Voiceover cue ${index + 1} is empty.`);
  if (!cue.audio) errors.push(`Voiceover cue ${index + 1} has no audio asset.`);
  else {
    const audioPath = resolve(projectRoot, 'public', cue.audio);
    if (!existsSync(audioPath)) errors.push(`Voiceover cue ${index + 1} references missing audio: public/${cue.audio}.`);
    else {
      const duration = audioDurationSeconds(audioPath);
      if (duration === undefined) errors.push(`Could not read duration for cue ${index + 1} audio: public/${cue.audio}.`);
      else {
        const cueDuration = (cue.end - cue.start) / FPS;
        if (duration > cueDuration) errors.push(`Cue ${index + 1} narration runs ${duration.toFixed(2)}s, past its ${cueDuration.toFixed(2)}s slot.`);
        const wordsPerMinute = cue.voiceover.trim().split(/\s+/).length / duration * 60;
        if (wordsPerMinute < 75 || wordsPerMinute > 210) errors.push(`Cue ${index + 1} pacing is ${wordsPerMinute.toFixed(0)} words/min; expected 75–210.`);
      }
    }
  }
  cursor = cue.end;
}
if (cursor !== DURATION_IN_FRAMES) errors.push(`Voiceover cues end at ${cursor}; expected ${DURATION_IN_FRAMES}.`);

const rootFile = readFileSync(resolve(projectRoot, 'src/Root.tsx'), 'utf8');
for (const id of ['BrettonWoods-Landscape', 'BrettonWoods-Vertical', 'Katana-Noise-Landscape', 'Katana-Noise-Vertical']) {
  if (!rootFile.includes(id)) errors.push(`Missing required composition: ${id}.`);
}
if (!rootFile.includes('width={1920}') || !rootFile.includes('height={1080}')) errors.push('Landscape dimensions must be 1920x1080.');
if (!rootFile.includes('width={1080}') || !rootFile.includes('height={1920}')) errors.push('Vertical dimensions must be 1080x1920.');

const videoFile = readFileSync(resolve(projectRoot, 'src/Video.tsx'), 'utf8');
for (const token of ['backdropFilter', 'blur(20px)', '#0b0f19', '#ff4500', 'sceneCues']) {
  if (!videoFile.includes(token)) errors.push(`Video implementation is missing required visual standard: ${token}.`);
}
const noiseFile = readFileSync(resolve(projectRoot, 'src/NoiseFilm.tsx'), 'utf8');
for (const token of ['backdropFilter', 'blur(20px)', '#0b0f19', '#ff4500', 'NOISE', 'spring(']) {
  if (!noiseFile.includes(token)) errors.push(`Katana/NOISE implementation is missing required visual element: ${token}.`);
}
if (videoFile.includes('#000000') || noiseFile.includes('#000000')) errors.push('Solid black (#000000) is forbidden.');

const publicAssets = resolve(projectRoot, 'public');
if (existsSync(publicAssets)) {
  // The project currently uses only inline vector artwork. If local media is added,
  // this keeps the sync gate honest by rejecting broken static references.
  const references = [...videoFile.matchAll(/(?:staticFile\(['"]|src=['"])([^'"]+)/g)].map((match) => match[1]);
  for (const reference of references) {
    if (reference.startsWith('http') || reference.startsWith('data:')) continue;
    if (!existsSync(resolve(publicAssets, reference))) errors.push(`Missing referenced public asset: ${reference}.`);
  }
}

if (errors.length) {
  console.error('verify:sync failed:');
  errors.forEach((error) => console.error(`- ${error}`));
  process.exit(1);
}

console.log(`verify:sync passed — ${FPS} fps, ${DURATION_IN_FRAMES} frames, 4 aligned scene/voiceover cues, dual compositions, visual standards, and asset paths checked.`);
