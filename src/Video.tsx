import React from 'react';
import {
  AbsoluteFill,
  Audio,
  interpolate,
  Sequence,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import { sceneCues, voiceoverCues } from './sync';

type Props = { format: 'landscape' | 'vertical' };
type SceneIndex = 0 | 1 | 2 | 3;

const palette = {
  obsidian: '#0b0f19',
  orange: '#ff4500',
  white: '#f8fafc',
  muted: '#a7b2c4',
  gold: '#d6b56d',
  green: '#a3c47a',
};

const GlassCard: React.FC<{
  children: React.ReactNode;
  style?: React.CSSProperties;
  accent?: string;
}> = ({ children, style, accent = 'rgba(255,255,255,.16)' }) => (
  <div
    style={{
      background: 'linear-gradient(135deg, rgba(255,255,255,.105), rgba(255,255,255,.035))',
      border: `1px solid ${accent}`,
      borderRadius: 22,
      boxShadow: '0 28px 90px rgba(0,0,0,.30), inset 0 1px 0 rgba(255,255,255,.10)',
      backdropFilter: 'blur(20px)',
      WebkitBackdropFilter: 'blur(20px)',
      ...style,
    }}
  >
    {children}
  </div>
);

const Kicker: React.FC<{ children: React.ReactNode; style?: React.CSSProperties }> = ({
  children,
  style,
}) => (
  <div
    style={{
      fontSize: 14,
      fontWeight: 700,
      letterSpacing: '.24em',
      color: palette.orange,
      textTransform: 'uppercase',
      ...style,
    }}
  >
    {children}
  </div>
);

function Grid({ frame, width, height }: { frame: number; width: number; height: number }) {
  const phase = frame / 30;
  const stabilization = interpolate(frame, [1660, 1799], [1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const driftX = (Math.sin(phase * 0.15) * 34 + (frame / 30) * -5) * stabilization;
  const driftY = (Math.cos(phase * 0.12) * 24 + (frame / 30) * 7) * stabilization;
  const lines = [];
  for (let i = -14; i <= 14; i++) {
    lines.push(
      <line key={`a${i}`} x1={i * 80} y1={-height} x2={i * 80} y2={height * 2} />,
      <line key={`b${i}`} x1={-width} y1={i * 80} x2={width * 2} y2={i * 80} />,
    );
  }
  const nodes = [
    [0.18, 0.34], [0.28, 0.63], [0.40, 0.26], [0.53, 0.48], [0.63, 0.32],
    [0.76, 0.57], [0.86, 0.30], [0.36, 0.79], [0.69, 0.76], [0.12, 0.73],
  ];
  const links = [[0, 2], [2, 3], [3, 4], [4, 6], [1, 3], [3, 5], [5, 8], [7, 8], [9, 1], [2, 4], [1, 7]];
  return (
    <AbsoluteFill style={{ zIndex: 1, overflow: 'hidden', perspective: 1200 }}>
      <svg
        width={width * 2}
        height={height * 2}
        viewBox={`0 0 ${width * 2} ${height * 2}`}
        style={{ position: 'absolute', left: -width * 0.5, top: -height * 0.5, transform: `translate3d(${driftX}px,${driftY}px,0) rotateX(58deg) rotateZ(-12deg) scale(1.2)`, transformOrigin: 'center', opacity: 0.48 }}
      >
        <g stroke="rgba(157,177,207,.12)" strokeWidth="1">{lines}</g>
      </svg>
      <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} style={{ position: 'absolute', inset: 0 }}>
        <g transform={`translate(${driftX * 0.36},${driftY * 0.28})`}>
          {links.map(([a, b], i) => (
            <line
              key={i}
              x1={nodes[a][0] * width}
              y1={nodes[a][1] * height}
              x2={nodes[b][0] * width}
              y2={nodes[b][1] * height}
              stroke={i % 3 === 0 ? 'rgba(163,196,122,.17)' : 'rgba(214,181,109,.13)'}
              strokeWidth="1.2"
            />
          ))}
          {nodes.map(([x, y], i) => {
            const pulse = 0.55 + 0.45 * Math.sin(frame / 19 + i * 1.3);
            const color = i % 3 === 0 ? palette.green : palette.gold;
            return (
              <g key={i}>
                <circle cx={x * width} cy={y * height} r={10 + pulse * 6} fill={color} opacity={0.05 + pulse * 0.06} />
                <circle cx={x * width} cy={y * height} r={2 + pulse * 1.6} fill={color} opacity={0.55 + pulse * 0.4} />
              </g>
            );
          })}
        </g>
      </svg>
    </AbsoluteFill>
  );
}

function GlobalBackdrop({ frame, width, height }: { frame: number; width: number; height: number }) {
  const scene = frame < 300 ? 0 : frame < 750 ? 1 : frame < 1350 ? 2 : 3;
  const emphasis = [0.2, 0.65, 0.32, 0.5][scene];
  const breathing = 1 + Math.sin(frame / 90) * 0.03;
  const pullback = interpolate(frame, [1350, 1799], [1.2, 1], { extrapolateRight: 'clamp' });
  return (
    <>
      <AbsoluteFill style={{ zIndex: 0, background: `radial-gradient(ellipse at 50% 48%, #18202c 0%, ${palette.obsidian} 60%, #080b12 100%)` }} />
      <Grid frame={frame} width={width} height={height} />
      <AbsoluteFill
        style={{
          zIndex: 2,
          background: `radial-gradient(ellipse at ${50 + Math.sin(frame / 110) * 7}% ${44 + Math.cos(frame / 130) * 6}%, rgba(255,69,0,${0.025 + emphasis * 0.035}) 0%, transparent 42%)`,
          transform: `scale(${breathing * pullback})`,
          pointerEvents: 'none',
        }}
      />
      <AbsoluteFill style={{ zIndex: 3, background: 'linear-gradient(90deg, rgba(5,8,14,.22), transparent 22%, transparent 78%, rgba(5,8,14,.22))', pointerEvents: 'none' }} />
    </>
  );
}

const VaultBar: React.FC<{ scale: number }> = ({ scale }) => (
  <svg width={190 * scale} height={118 * scale} viewBox="0 0 190 118" aria-hidden="true">
    <defs>
      <linearGradient id="goldTop" x1="0" x2="1" y1="0" y2="1"><stop stopColor="#fff0b9"/><stop offset="1" stopColor="#d0a853"/></linearGradient>
      <linearGradient id="goldSide" x1="0" x2="1"><stop stopColor="#8e6c31"/><stop offset="1" stopColor="#d6b56d"/></linearGradient>
      <filter id="goldGlow"><feGaussianBlur stdDeviation="7" /></filter>
    </defs>
    <ellipse cx="96" cy="99" rx="70" ry="13" fill="#e5b84e" opacity=".3" filter="url(#goldGlow)" />
    <path d="M31 52 69 23 158 36 119 66Z" fill="url(#goldTop)" />
    <path d="M31 52 119 66 119 97 31 81Z" fill="#bc9349" />
    <path d="M119 66 158 36 158 67 119 97Z" fill="url(#goldSide)" />
    <path d="m53 52 37-22M61 82l45 8" stroke="rgba(255,255,255,.34)" strokeWidth="2" />
    <text x="94" y="62" textAnchor="middle" fill="#725321" fontSize="12" fontWeight="800" letterSpacing="3">FINE GOLD</text>
  </svg>
);

const GlobeMark: React.FC<{ size: number }> = ({ size }) => (
  <svg width={size} height={size} viewBox="0 0 180 180" aria-hidden="true">
    <defs><radialGradient id="orb" cx="35%" cy="28%"><stop stopColor="#36506a"/><stop offset="1" stopColor="#111a27"/></radialGradient></defs>
    <circle cx="90" cy="90" r="70" fill="url(#orb)" stroke="rgba(255,255,255,.24)" strokeWidth="1.5" />
    <ellipse cx="90" cy="90" rx="31" ry="70" fill="none" stroke="rgba(214,181,109,.34)" strokeWidth="1" />
    <ellipse cx="90" cy="90" rx="59" ry="28" fill="none" stroke="rgba(214,181,109,.25)" strokeWidth="1" />
    <path d="M23 78Q90 103 157 78M31 113Q90 92 149 113" fill="none" stroke="rgba(255,255,255,.16)" />
    <path d="M44 54 70 63 77 79 67 87 72 101 60 113 47 105 38 82ZM102 33 126 40 139 57 131 69 116 65 110 82 95 75 87 56ZM102 93 117 98 126 115 117 136 104 130 97 110Z" fill="rgba(163,196,122,.46)" />
    <circle cx="90" cy="90" r="75" fill="none" stroke="rgba(255,69,0,.24)" strokeWidth="1" strokeDasharray="3 10" />
  </svg>
);

const CrownMark: React.FC<{ size: number }> = ({ size }) => (
  <svg width={size} height={size * 0.62} viewBox="0 0 240 148" aria-hidden="true">
    <defs><linearGradient id="crown" x1="0" x2="1" y1="0" y2="1"><stop stopColor="#fff0bf"/><stop offset=".48" stopColor="#d3ad61"/><stop offset="1" stopColor="#76592f"/></linearGradient></defs>
    <path d="m28 43 48 31 44-54 45 54 48-31-22 76H50Z" fill="url(#crown)" stroke="rgba(255,241,194,.7)" strokeWidth="2" />
    <path d="M50 120h141v15H50z" fill="#9d783c" />
    <circle cx="28" cy="40" r="8" fill="#ffe9aa"/><circle cx="120" cy="18" r="8" fill="#ffe9aa"/><circle cx="213" cy="40" r="8" fill="#ffe9aa"/>
    <path d="M73 91h94" stroke="rgba(255,255,255,.34)" strokeWidth="2" />
  </svg>
);

function CardCopy({ label, detail, big, accent = palette.orange }: { label: string; detail?: string; big?: string; accent?: string }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10, textAlign: 'left' }}>
      <Kicker style={{ color: accent }}>{label}</Kicker>
      {big && <div style={{ color: palette.white, fontSize: 'clamp(30px, 4.3vw, 76px)', lineHeight: 0.98, fontWeight: 800, letterSpacing: '-.045em' }}>{big}</div>}
      {detail && <div style={{ color: palette.muted, fontSize: 'clamp(15px, 1.2vw, 21px)', fontWeight: 500, letterSpacing: '.06em', lineHeight: 1.45 }}>{detail}</div>}
    </div>
  );
}

function Timed({
  start, end, frame, children, mode = 'pop', vertical,
}: {
  start: number; end: number; frame: number; children: React.ReactNode; mode?: 'pop' | 'slide' | 'flicker'; vertical: boolean;
}) {
  const local = frame - start;
  const entrance = spring({ frame: Math.max(0, local), fps: 30, config: { stiffness: mode === 'pop' ? 150 : 120, damping: mode === 'pop' ? 20 : 24, mass: mode === 'pop' ? 0.8 : 1.05 } });
  const opacity = interpolate(frame, [start, start + (mode === 'flicker' ? 15 : 13), end - 14, end], [0, 1, 1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const flicker = mode === 'flicker' && local < 24 ? (local % 5 < 3 ? 0.42 : 1) : 1;
  const translateY = mode === 'slide' ? interpolate(entrance, [0, 1], [vertical ? 38 : 52, 0]) : interpolate(entrance, [0, 1], [22, 0]);
  const scale = mode === 'pop' ? interpolate(entrance, [0, 1], [0.86, 1]) : 1;
  return (
    <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', opacity: opacity * flicker, transform: `translate3d(0,${translateY}px,0) scale(${scale})`, pointerEvents: 'none' }}>
      {children}
    </div>
  );
}

function SceneContent({ frame, vertical, width, height }: { frame: number; vertical: boolean; width: number; height: number }) {
  const heroSize = Math.min(width * (vertical ? 0.094 : 0.073), height * (vertical ? 0.083 : 0.15));
  const cardWidth = vertical ? '82%' : 'min(760px, 72%)';
  const top = vertical ? '27%' : '22%';
  const cardTop = vertical ? '62%' : '72%';
  const heroStyle: React.CSSProperties = {
    width: '90%', maxWidth: 1600, textAlign: 'center', color: palette.white,
    fontSize: heroSize, fontWeight: 850, lineHeight: 0.95, letterSpacing: '-.055em',
    textShadow: '0 8px 45px rgba(0,0,0,.52)', textWrap: 'balance',
  };
  const eyebrowStyle: React.CSSProperties = { position: 'absolute', top: vertical ? '17%' : '17%', width: '100%', textAlign: 'center' };
  const cardCenter: React.CSSProperties = { position: 'absolute', left: '50%', top: cardTop, transform: 'translate(-50%,-50%)', width: cardWidth };
  const entrance = (mode: 'pop' | 'slide' | 'flicker') => mode;
  return (
    <AbsoluteFill style={{ zIndex: 20, overflow: 'hidden' }}>
      {/* Scene one: spring-pop title, clean trading statistic */}
      {frame >= 0 && frame < 300 && <>
        <Timed start={30} end={294} frame={frame} mode={entrance('pop')} vertical={vertical}>
          <div style={heroStyle}>GLOBAL<br />TRADE</div>
        </Timed>
        <Timed start={90} end={290} frame={frame} mode="flicker" vertical={vertical}>
          <div style={eyebrowStyle}><Kicker>THE WORLD SETTLES HERE</Kicker></div>
        </Timed>
        <Timed start={90} end={294} frame={frame} mode="slide" vertical={vertical}>
          <GlassCard style={{ ...cardCenter, padding: vertical ? '24px 26px' : '25px 36px' }}>
            <CardCopy label="UNIVERSAL DENOMINATION" detail="The dollar appears on one side of roughly 88% of global FX trades." />
          </GlassCard>
        </Timed>
        <Timed start={180} end={295} frame={frame} mode="pop" vertical={vertical}>
          <GlassCard accent="rgba(255,69,0,.4)" style={{ position: 'absolute', top: vertical ? '76%' : '79%', left: '50%', transform: 'translateX(-50%)', padding: '17px 26px', display: 'flex', alignItems: 'center', gap: 14, whiteSpace: 'nowrap' }}>
            <span style={{ color: palette.orange, fontSize: 28, fontWeight: 800 }}>88%</span>
            <span style={{ color: palette.white, fontSize: vertical ? 12 : 15, letterSpacing: '.12em', fontWeight: 700 }}>OF FX TRADES INVOLVE USD</span>
          </GlassCard>
        </Timed>
      </>}
      {/* Scene two: spatial history card and minimal gold abstraction */}
      {frame >= 300 && frame < 750 && <>
        <Timed start={320} end={744} frame={frame} mode="slide" vertical={vertical}>
          <div style={{ ...heroStyle, top, left: '50%', transform: 'translateX(-50%)', position: 'absolute' }}><span style={{ color: palette.orange }}>1944:</span> THE PIVOT</div>
        </Timed>
        <Timed start={450} end={744} frame={frame} mode="pop" vertical={vertical}>
          <GlassCard style={{ ...cardCenter, top: vertical ? '59%' : '61%', width: vertical ? '76%' : 'min(680px,66%)', padding: vertical ? '20px 22px' : '22px 34px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 15 }}>
            <CardCopy label="BRETTON WOODS" big="BACKED BY GOLD" detail="A new monetary order, anchored to the dollar." />
            <VaultBar scale={vertical ? 0.75 : 1.08} />
          </GlassCard>
        </Timed>
        <Timed start={600} end={744} frame={frame} mode="flicker" vertical={vertical}>
          <GlassCard style={{ ...cardCenter, top: vertical ? '78%' : '80%', width: vertical ? '78%' : 'min(660px,62%)', padding: vertical ? '17px 22px' : '20px 32px' }}>
            <CardCopy label="THE WORLD STAYED" detail="FIXED PARITY  /  SOVEREIGN PEGGING" accent={palette.gold} />
          </GlassCard>
        </Timed>
      </>}
      {/* Scene three: market-network zoom, one decisive Treasury metric */}
      {frame >= 750 && frame < 1350 && <>
        <Timed start={780} end={1344} frame={frame} mode="slide" vertical={vertical}>
          <div style={{ ...heroStyle, top, left: '50%', transform: 'translateX(-50%)', position: 'absolute' }}>LIQUIDITY<br />&amp; TRUST</div>
        </Timed>
        <Timed start={960} end={1340} frame={frame} mode="pop" vertical={vertical}>
          <GlassCard accent="rgba(255,69,0,.44)" style={{ ...cardCenter, top: vertical ? '62%' : '64%', width: vertical ? '76%' : 'min(700px,68%)', padding: vertical ? '28px' : '34px 48px', textAlign: 'center' }}>
            <Kicker style={{ textAlign: 'center' }}>A DEEP, LIQUID MARKET</Kicker>
            <div style={{ color: palette.white, fontSize: vertical ? 58 : 82, lineHeight: 1, fontWeight: 850, letterSpacing: '-.055em', marginTop: 12 }}>$27T<span style={{ color: palette.orange }}>+</span></div>
            <div style={{ color: palette.muted, fontSize: vertical ? 13 : 18, letterSpacing: '.18em', fontWeight: 700, marginTop: 10 }}>U.S. TREASURY MARKET</div>
          </GlassCard>
        </Timed>
        <Timed start={1140} end={1345} frame={frame} mode="flicker" vertical={vertical}>
          <GlassCard style={{ ...cardCenter, top: vertical ? '82%' : '81%', width: vertical ? '80%' : 'min(720px,72%)', padding: vertical ? '17px 22px' : '20px 32px', display: 'flex', alignItems: 'center', gap: 16 }}>
            <GlobeMark size={vertical ? 50 : 58} />
            <CardCopy label="THE ULTIMATE SAFETY NET" detail="Global central bank reserves" accent={palette.gold} />
          </GlassCard>
        </Timed>
      </>}
      {/* Scene four: crown reveal and restrained outro */}
      {frame >= 1350 && <>
        <Timed start={1380} end={1558} frame={frame} mode="pop" vertical={vertical}>
          <div style={heroStyle}>ECONOMIC<br />POWER</div>
        </Timed>
        <Timed start={1560} end={1799} frame={frame} mode="slide" vertical={vertical}>
          <div style={{ position: 'absolute', top: vertical ? '28%' : '24%', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: vertical ? 18 : 24, width: '92%' }}>
            <CrownMark size={vertical ? 174 : 238} />
            <div style={{ ...heroStyle, fontSize: Math.min(width * (vertical ? 0.078 : 0.061), height * (vertical ? 0.074 : 0.13)), width: '100%' }}>THE KING OF<br />CURRENCIES</div>
          </div>
        </Timed>
        <Timed start={1700} end={1799} frame={frame} mode="flicker" vertical={vertical}>
          <div style={{ position: 'absolute', top: vertical ? '57%' : '62%', width: '100%', textAlign: 'center' }}>
            <GlassCard accent="rgba(255,69,0,.36)" style={{ display: 'inline-block', padding: vertical ? '12px 24px' : '14px 30px' }}>
              <Kicker style={{ fontSize: vertical ? 13 : 16 }}>FOR NOW...</Kicker>
            </GlassCard>
          </div>
        </Timed>
      </>}
      <AbsoluteFill style={{ zIndex: 80, pointerEvents: 'none' }}>
        <div style={{ position: 'absolute', bottom: vertical ? '4.2%' : '5.4%', left: vertical ? '9%' : '6.3%', right: vertical ? '9%' : '6.3%', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12 }}>
          <Kicker style={{ color: 'rgba(248,250,252,.48)', fontSize: vertical ? 9 : 11, letterSpacing: '.2em' }}>DOLLAR EMPIRE</Kicker>
          <div style={{ height: 1, flex: 1, background: 'linear-gradient(90deg, rgba(255,69,0,.5), rgba(255,255,255,.05))' }} />
          <span style={{ color: 'rgba(248,250,252,.48)', fontSize: vertical ? 9 : 11, letterSpacing: '.15em', fontWeight: 700 }}>{sceneCues[frame < 300 ? 0 : frame < 750 ? 1 : frame < 1350 ? 2 : 3].title}</span>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
}

export const DollarEmpire: React.FC<Props> = ({ format }) => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const vertical = format === 'vertical';
  const transition = interpolate(frame, [1700, 1799], [1, 0.1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  return (
    <AbsoluteFill style={{ backgroundColor: palette.obsidian, color: palette.white, fontFamily: 'Arial, Helvetica, sans-serif' }}>
      <Audio src={staticFile('audio/ambient-bed.wav')} volume={0.7} />
      {voiceoverCues.map((cue) => (
        <Sequence key={cue.audio} from={cue.start} durationInFrames={cue.end - cue.start}>
          <Audio src={staticFile(cue.audio)} volume={0.96} />
        </Sequence>
      ))}
      <AbsoluteFill style={{ opacity: transition }}>
        <GlobalBackdrop frame={frame} width={width} height={height} />
        <SceneContent frame={frame} vertical={vertical} width={width} height={height} />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
