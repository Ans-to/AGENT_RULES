import React from 'react';
import { AbsoluteFill, interpolate, spring } from 'remotion';
import { voiceoverCues } from './sync';

type Word = { text: string; color?: string; fontFamily?: string; weight?: number; italic?: boolean };
type TitleProps = {
  frame: number;
  start: number;
  end: number;
  lines: Word[][];
  fontSize: number;
  top: string;
  vertical: boolean;
  width?: string;
  align?: 'center' | 'left';
};

const white = '#f8fafc';
const orange = '#ff4500';

/** Per-glyph spring choreography with elastic compression and a short RGB split on impact. */
export const KineticTitle: React.FC<TitleProps> = ({
  frame, start, end, lines, fontSize, top, vertical, width = '92%', align = 'center',
}) => {
  const fadeOut = interpolate(frame, [end - 18, end], [1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const live = frame >= start && frame < end;
  if (!live) return null;
  const chroma = interpolate(frame, [start, start + 3, start + 10, start + 19], [0, 1, 0.34, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  let glyphNumber = 0;
  const renderedLines = lines.map((line, row) => (
    <div key={row} style={{ display: 'flex', alignItems: 'center', justifyContent: align, gap: fontSize * (vertical ? 0.055 : 0.075), whiteSpace: 'nowrap', lineHeight: 0.89 }}>
      {line.map((word, wordIndex) => (
        <span key={`${row}-${wordIndex}`} style={{ display: 'inline-flex', whiteSpace: 'pre', fontFamily: word.fontFamily ?? 'Arial, Helvetica, sans-serif', fontSize, fontWeight: word.weight ?? 900, fontStyle: word.italic ? 'italic' : 'normal', letterSpacing: '-.055em', color: word.color ?? white }}>
          {[...word.text].map((character, charIndex) => {
            const id = glyphNumber++;
            const localStart = start + row * 7 + wordIndex * 4 + charIndex * 1.25;
            const local = frame - localStart;
            const motion = spring({
              frame: Math.max(0, local), fps: 30,
              config: { stiffness: 190, damping: 20, mass: 0.72 },
            });
            const direction = (id + row) % 2 === 0 ? -1 : 1;
            const x = interpolate(motion, [0, 1], [direction * fontSize * 0.42, 0], { extrapolateRight: 'clamp' });
            const y = interpolate(motion, [0, 1], [direction * fontSize * 0.58, 0], { extrapolateRight: 'clamp' });
            const rotateY = interpolate(motion, [0, 1], [direction * 58, 0], { extrapolateRight: 'clamp' });
            const rotateX = interpolate(motion, [0, 1], [-48, 0], { extrapolateRight: 'clamp' });
            const sx = interpolate(motion, [0, 0.58, 0.82, 1], [0.22, 1.18, 0.94, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
            const sy = interpolate(motion, [0, 0.58, 0.82, 1], [0.72, 0.9, 1.08, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
            const opacity = interpolate(frame, [localStart, localStart + 4], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
            const colorPulse = word.color ? word.color : white;
            const extrusion = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((n) => `0 ${n}px 0 ${n < 4 ? '#b5becb' : n < 7 ? '#697586' : '#283241'}`);
            const aberration = chroma > 0 ? `${chroma * 5}px 0 rgba(255,69,0,${chroma * 0.85}), ${-chroma * 5}px 0 rgba(80,214,255,${chroma * 0.8}), ` : '';
            return (
              <span key={charIndex} style={{
                display: 'inline-block', opacity: opacity * fadeOut,
                transform: `translate3d(${x}px,${y}px,0) rotateY(${rotateY}deg) rotateX(${rotateX}deg) scaleX(${sx}) scaleY(${sy})`,
                transformOrigin: '50% 70%', transformStyle: 'preserve-3d',
                color: colorPulse, WebkitTextStroke: '1px rgba(255,255,255,.72)',
                textShadow: `${aberration}${extrusion.join(', ')}, 0 22px 34px rgba(0,0,0,.7), 0 0 32px rgba(248,250,252,.2)`,
              }}>{character}</span>
            );
          })}
        </span>
      ))}
    </div>
  ));
  return (
    <div style={{ position: 'absolute', top, left: '50%', transform: `translateX(-50%) scale(${interpolate(frame, [start, start + 90, end - 40, end], [1.12, 1, 1.025, 0.92], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' })})`, width, maxWidth: '94%', textAlign: align, opacity: fadeOut, perspective: 1000, transformStyle: 'preserve-3d', pointerEvents: 'none' }}>
      {renderedLines}
    </div>
  );
};

/** Four-word rolling captions; one active word receives a spring-and-color emphasis. */
export const VoiceCaption: React.FC<{ frame: number; vertical: boolean }> = ({ frame, vertical }) => {
  const cue = voiceoverCues.find((item) => frame >= item.start && frame < item.start + item.audioFrames);
  if (!cue) return null;
  const words = cue.voiceover.split(/\s+/);
  const elapsed = frame - cue.start;
  const wordIndex = Math.min(words.length - 1, Math.floor((elapsed / cue.audioFrames) * words.length));
  const groupStart = Math.floor(wordIndex / 4) * 4;
  const group = words.slice(groupStart, groupStart + 4);
  const active = wordIndex - groupStart;
  const springValue = spring({ frame: Math.max(0, elapsed % Math.max(1, cue.audioFrames / words.length)), fps: 30, config: { stiffness: 165, damping: 19, mass: 0.7 } });
  return (
    <AbsoluteFill style={{ zIndex: 72, pointerEvents: 'none' }}>
      <div style={{ position: 'absolute', left: '50%', top: vertical ? '88%' : '88%', transform: 'translate(-50%,-50%)', width: vertical ? '84%' : '74%', display: 'flex', justifyContent: 'center' }}>
        <div style={{
          display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: vertical ? '4px 9px' : '4px 12px',
          padding: vertical ? '12px 16px' : '12px 22px', borderRadius: 15,
          background: 'linear-gradient(135deg,rgba(255,255,255,.12),rgba(255,255,255,.045))',
          border: '1px solid rgba(248,250,252,.18)', boxShadow: '0 16px 42px rgba(0,0,0,.35)',
          backdropFilter: 'blur(20px)', WebkitBackdropFilter: 'blur(20px)',
        }}>
          {group.map((word, i) => (
            <span key={`${groupStart}-${i}`} style={{
              color: i === active ? orange : white, fontSize: vertical ? 14 : 18,
              fontWeight: i === active ? 850 : 550, letterSpacing: '.01em',
              opacity: i > active ? 0.48 : 1,
              transform: i === active ? `scale(${interpolate(springValue, [0, 1], [0.88, 1])})` : 'none',
              textShadow: i === active ? '0 0 18px rgba(255,69,0,.42)' : 'none',
            }}>{word}</span>
          ))}
        </div>
      </div>
    </AbsoluteFill>
  );
};
