import React from 'react';
import { AbsoluteFill, interpolate } from 'remotion';

const orange = '#ff4500';
const green = '#a3c47a';
const gold = '#d6b56d';
const white = '#f8fafc';

export const ParticleTunnel: React.FC<{ frame: number; width: number; height: number }> = ({ frame, width, height }) => (
  <AbsoluteFill style={{ zIndex: 4, overflow: 'hidden', pointerEvents: 'none' }}>
    {Array.from({ length: 52 }, (_, i) => {
      const seed = i * 91.73 + 17.4;
      const sx = (Math.sin(seed) * 43758.5453 % 1 + 1) % 1;
      const sy = (Math.cos(seed * 1.53) * 24634.6345 % 1 + 1) % 1;
      const rate = 0.004 + (i % 7) * 0.0011;
      const p = ((frame * rate + (i * 0.173)) % 1 + 1) % 1;
      const radius = 0.04 + p * 0.92;
      const x = width * 0.5 + (sx - 0.5) * width * radius;
      const y = height * 0.49 + (sy - 0.5) * height * radius;
      const size = 1 + p * (i % 4 === 0 ? 3.2 : 1.3);
      const alpha = 0.14 + (1 - p) * 0.42;
      const color = i % 11 === 0 ? orange : i % 3 === 0 ? green : white;
      return <div key={i} style={{
        position: 'absolute', left: x, top: y, width: size * (1 + p * 2), height: size,
        borderRadius: 99, background: `linear-gradient(90deg, transparent, ${color})`, opacity: alpha,
        boxShadow: `0 0 ${2 + size * 2}px ${color}`, transform: `translate(-50%,-50%) rotate(${Math.atan2(y - height * 0.49, x - width * 0.5) * 180 / Math.PI}deg)`,
      }} />;
    })}
  </AbsoluteFill>
);

export const OrbitalGlobe: React.FC<{ frame: number; vertical: boolean; width: number; height: number; scene: number }> = ({ frame, vertical, width, height, scene }) => {
  const sceneOpacity = scene === 0 ? 0.42 : scene === 1 ? 0.16 : scene === 2 ? 0.34 : 0.12;
  const size = vertical ? Math.min(width * 0.92, height * 0.34) : Math.min(height * 0.92, width * 0.52);
  const x = vertical ? '50%' : scene === 0 ? '79%' : '52%';
  const y = vertical ? scene === 0 ? '34%' : '50%' : '48%';
  const spin = Math.sin(frame / 95) * 13 + interpolate(frame, [0, 1799], [0, -18]);
  return (
    <div style={{ position: 'absolute', zIndex: 6, left: x, top: y, width: size, height: size, opacity: sceneOpacity, transform: `translate(-50%,-50%) perspective(900px) rotateY(${spin}deg) rotateZ(${Math.sin(frame / 130) * 5}deg)`, transformStyle: 'preserve-3d', filter: 'drop-shadow(0 0 38px rgba(163,196,122,.22))', pointerEvents: 'none' }}>
      <svg width="100%" height="100%" viewBox="0 0 360 360" aria-hidden="true">
        <defs>
          <radialGradient id="dollarEarth" cx="34%" cy="29%"><stop stopColor="#496178"/><stop offset=".52" stopColor="#192736"/><stop offset="1" stopColor="#0d141e"/></radialGradient>
          <clipPath id="earthClip"><circle cx="180" cy="180" r="132" /></clipPath>
        </defs>
        <circle cx="180" cy="180" r="143" fill="none" stroke="rgba(255,69,0,.6)" strokeDasharray="3 14" strokeWidth="1.5" />
        <circle cx="180" cy="180" r="132" fill="url(#dollarEarth)" stroke="rgba(248,250,252,.38)" strokeWidth="1.5" />
        <g clipPath="url(#earthClip)" fill="none" stroke="rgba(214,181,109,.34)" strokeWidth="1.15">
          <ellipse cx="180" cy="180" rx="56" ry="132" />
          <ellipse cx="180" cy="180" rx="103" ry="132" />
          <ellipse cx="180" cy="180" rx="132" ry="43" />
          <ellipse cx="180" cy="180" rx="132" ry="88" />
          <path d="M45 180h270M180 47v266" stroke="rgba(248,250,252,.15)" />
        </g>
        <g clipPath="url(#earthClip)" fill="rgba(163,196,122,.56)">
          <path d="m77 92 28-17 18 8 7 18-13 12-2 20-17 8-7 22-18-5-8-24-13-8 7-19z" />
          <path d="m123 176 18 8 13 22-4 27-16 28-9 33-15-14 3-34-12-22 4-29z" />
          <path d="m171 83 24-12 35 5 22 18-4 19-21 4-13 16-17-8-14 15-16-18-16-3-6-18z" />
          <path d="m211 163 18 4 17 18-5 25-18 8-10 28-16-16 4-25-12-18z" />
        </g>
        <circle cx="180" cy="180" r="132" fill="none" stroke="rgba(248,250,252,.38)" strokeWidth="1" />
        <text x="180" y="197" textAnchor="middle" fill="rgba(248,250,252,.25)" fontFamily="Georgia,serif" fontSize="60" fontWeight="700">$</text>
      </svg>
    </div>
  );
};

export const TreasuryColumns: React.FC<{ frame: number; vertical: boolean; width: number; height: number }> = ({ frame, vertical, width, height }) => {
  if (frame < 750 || frame >= 1350) return null;
  const reveal = interpolate(frame - 750, [0, 80, 410, 600], [0, 1, 0.82, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const bars = [
    { x: 0.13, h: 0.24, delay: 0 }, { x: 0.23, h: 0.34, delay: 5 },
    { x: 0.77, h: 0.31, delay: 9 }, { x: 0.87, h: 0.21, delay: 14 },
  ];
  return (
    <AbsoluteFill style={{ zIndex: 7, pointerEvents: 'none', overflow: 'hidden', opacity: reveal }}>
      {bars.map((bar, i) => {
        const rise = interpolate(frame, [750 + bar.delay, 800 + bar.delay], [0.08, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
        const h = height * bar.h * rise;
        return <div key={i} style={{
          position: 'absolute', left: `${bar.x * 100}%`, top: `${62 - bar.h * 50}%`, width: vertical ? width * 0.055 : width * 0.035, height: h,
          border: '1px solid rgba(214,181,109,.32)', borderRadius: 8,
          background: 'linear-gradient(180deg,rgba(255,241,194,.18),rgba(214,181,109,.035))',
          boxShadow: '0 0 28px rgba(214,181,109,.08),inset 0 0 16px rgba(255,255,255,.06)',
          transform: `translateY(-${h * (1 - rise)}px) perspective(700px) rotateY(${i < 2 ? 14 : -14}deg)`,
          transformOrigin: 'bottom center',
        }}>
          <div style={{ position: 'absolute', top: '14%', left: '18%', right: '18%', height: 1, background: 'rgba(248,250,252,.35)' }} />
          <div style={{ position: 'absolute', top: '28%', left: '18%', right: '18%', height: 1, background: 'rgba(255,69,0,.5)' }} />
        </div>;
      })}
      <div style={{ position: 'absolute', left: '18%', right: '18%', top: '68%', height: 1, background: 'linear-gradient(90deg,transparent,rgba(214,181,109,.48),transparent)' }} />
    </AbsoluteFill>
  );
};

export const ImpactBloom: React.FC<{ frame: number; vertical: boolean }> = ({ frame, vertical }) => {
  const starts = [28, 318, 778, 1372];
  const active = starts.map((start) => ({ start, local: frame - start })).find(({ local }) => local >= -5 && local <= 25);
  if (!active) return null;
  const { local } = active;
  const opacity = interpolate(local, [-5, 0, 4, 15, 25], [0, 0.1, 0.72, 0.2, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const scale = interpolate(local, [-5, 4, 25], [0.02, 1.1, 2.5], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  return (
    <AbsoluteFill style={{ zIndex: 14, pointerEvents: 'none', overflow: 'hidden', opacity, mixBlendMode: 'screen' }}>
      <div style={{ position: 'absolute', left: '50%', top: vertical ? '43%' : '47%', width: vertical ? '80vw' : '72vh', height: vertical ? '80vw' : '72vh', borderRadius: '50%', transform: `translate(-50%,-50%) scale(${scale})`, background: 'radial-gradient(circle,rgba(248,250,252,.76) 0%,rgba(255,69,0,.34) 5%,rgba(214,181,109,.11) 24%,transparent 68%)', filter: 'blur(4px)' }} />
      {Array.from({ length: 10 }, (_, i) => <div key={i} style={{ position: 'absolute', left: '50%', top: vertical ? '43%' : '47%', width: vertical ? '70vw' : '75vw', height: i % 3 === 0 ? 3 : 1, transform: `translate(-50%,-50%) rotate(${i * 18 + 7}deg) scaleX(${scale})`, transformOrigin: 'center', background: i % 2 === 0 ? 'linear-gradient(90deg,transparent,rgba(248,250,252,.46),transparent)' : 'linear-gradient(90deg,transparent,rgba(255,69,0,.32),transparent)', filter: 'blur(1px)' }} />)}
    </AbsoluteFill>
  );
};

export const OpticalTransitions: React.FC<{ frame: number; width: number; height: number; vertical: boolean }> = ({ frame, width, height, vertical }) => {
  const starts = [294, 744, 1344];
  const pulse = starts.map((start) => {
    const local = frame - start;
    return interpolate(local, [0, 5, 14], [0, 0.88, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  }).reduce((max, value) => Math.max(max, value), 0);
  const active = starts.find((start) => frame >= start && frame <= start + 14);
  if (!active) return null;
  const p = interpolate(frame - active, [0, 14], [-1, 1]);
  const size = interpolate(frame - active, [0, 5, 14], [0.01, 1.2, 0.35], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  return (
    <AbsoluteFill style={{ zIndex: 90, overflow: 'hidden', pointerEvents: 'none', opacity: pulse, mixBlendMode: 'screen' }}>
      <div style={{ position: 'absolute', left: `${50 + p * 52}%`, top: '50%', width: width * size, height: height * size, transform: 'translate(-50%,-50%)', borderRadius: '50%', background: 'radial-gradient(circle,rgba(248,250,252,.85) 0%,rgba(255,69,0,.38) 8%,rgba(163,196,122,.15) 24%,transparent 68%)', filter: 'blur(5px)' }} />
      <div style={{ position: 'absolute', inset: 0, background: vertical ? `linear-gradient(180deg,transparent ${42 - p * 55}%,rgba(248,250,252,.7) 50%,rgba(255,69,0,.2) 51%,transparent ${58 - p * 55}%)` : `linear-gradient(90deg,transparent ${42 - p * 55}%,rgba(248,250,252,.7) 50%,rgba(255,69,0,.2) 51%,transparent ${58 - p * 55}%)`, opacity: 0.5 }} />
      <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} style={{ position: 'absolute', inset: 0 }}>
        <rect x="0" y={height * (0.44 + p * 0.25)} width={width} height={height * 0.035} fill="rgba(248,250,252,.3)" />
        <rect x="0" y={height * (0.53 + p * 0.25)} width={width} height={height * 0.009} fill="rgba(255,69,0,.8)" />
      </svg>
    </AbsoluteFill>
  );
};
