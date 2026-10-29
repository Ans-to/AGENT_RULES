import React from 'react';
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';

type Props = { format: 'landscape' | 'vertical' };

const C = {
  obsidian: '#0b0f19',
  orange: '#ff4500',
  lime: '#c9f36a',
  white: '#f8fafc',
  muted: '#9aa6b8',
};

const easeOut = { extrapolateLeft: 'clamp' as const, extrapolateRight: 'clamp' as const };

function NoiseWorld({ frame, width, height }: { frame: number; width: number; height: number }) {
  const drift = interpolate(frame, [0, 449], [0, -76]);
  const zoom = interpolate(frame, [0, 110, 205, 340, 449], [1.12, 1.08, 1.28, 1.12, 1], easeOut);
  const glow = interpolate(frame, [0, 96, 124, 160, 210, 300, 449], [0.25, 0.35, 1, 0.52, 0.48, 0.38, 0.12], easeOut);
  const gridLines = [];
  for (let i = -12; i <= 12; i++) {
    gridLines.push(
      <line key={`v${i}`} x1={i * 84} y1={-height} x2={i * 84} y2={height * 2} />,
      <line key={`h${i}`} x1={-width} y1={i * 84} x2={width * 2} y2={i * 84} />,
    );
  }
  const anchors = [
    [0.12, 0.42], [0.22, 0.28], [0.34, 0.65], [0.46, 0.38],
    [0.58, 0.59], [0.69, 0.27], [0.81, 0.48], [0.91, 0.34],
    [0.26, 0.79], [0.74, 0.76],
  ];
  const edges = [[0, 1], [1, 3], [2, 3], [3, 4], [3, 5], [4, 6], [5, 7], [2, 8], [6, 9], [8, 9]];
  return (
    <>
      <AbsoluteFill style={{ zIndex: 0, background: `radial-gradient(ellipse at 50% 48%, #17202c 0%, ${C.obsidian} 61%, #090c13 100%)` }} />
      <AbsoluteFill style={{ zIndex: 1, overflow: 'hidden', perspective: 1100 }}>
        <svg
          width={width * 2}
          height={height * 2}
          viewBox={`0 0 ${width * 2} ${height * 2}`}
          style={{
            position: 'absolute', left: -width / 2, top: -height / 2,
            transform: `translate3d(${Math.sin(frame / 70) * 28}px,${drift}px,0) rotateX(58deg) rotateZ(-10deg) scale(${zoom})`,
            transformOrigin: 'center', opacity: 0.52,
          }}
        >
          <g stroke="rgba(166,185,210,.16)" strokeWidth="1">{gridLines}</g>
        </svg>
      </AbsoluteFill>
      <AbsoluteFill style={{ zIndex: 2, pointerEvents: 'none' }}>
        <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} style={{ position: 'absolute', inset: 0 }}>
          <g transform={`translate(${Math.sin(frame / 80) * 24},${drift * 0.18})`}>
            {edges.map(([a, b], i) => (
              <line
                key={`e${i}`}
                x1={anchors[a][0] * width} y1={anchors[a][1] * height}
                x2={anchors[b][0] * width} y2={anchors[b][1] * height}
                stroke={i % 3 === 0 ? 'rgba(201,243,106,.22)' : 'rgba(214,181,109,.15)'}
                strokeWidth="1.2"
              />
            ))}
            {anchors.map(([x, y], i) => {
              const pulse = 0.5 + 0.5 * Math.sin(frame / 18 + i * 1.7);
              const color = i === 3 || i === 6 ? C.orange : C.lime;
              return <g key={`n${i}`}>
                <circle cx={x * width} cy={y * height} r={12 + 8 * pulse} fill={color} opacity={0.04 + 0.07 * pulse} />
                <circle cx={x * width} cy={y * height} r={2 + 2 * pulse} fill={color} opacity={0.5 + 0.45 * pulse} />
              </g>;
            })}
          </g>
        </svg>
      </AbsoluteFill>
      <AbsoluteFill
        style={{
          zIndex: 3,
          background: `radial-gradient(ellipse at ${48 + Math.sin(frame / 34) * 6}% ${48 + Math.cos(frame / 41) * 5}%, rgba(255,69,0,${0.045 * glow}) 0%, transparent 33%), radial-gradient(circle at ${50 + Math.sin(frame / 27) * 4}% 50%, rgba(201,243,106,${0.035 * glow}) 0%, transparent 22%)`,
          pointerEvents: 'none',
        }}
      />
    </>
  );
}

function ParticleField({ frame, width, height }: { frame: number; width: number; height: number }) {
  const reveal = interpolate(frame, [94, 130, 340, 421], [0, 1, 0.72, 0], easeOut);
  return (
    <AbsoluteFill style={{ zIndex: 10, pointerEvents: 'none', overflow: 'hidden' }}>
      {Array.from({ length: 54 }, (_, i) => {
        const seed = i * 127.1 + 31.7;
        const x = ((Math.sin(seed) * 43758.5) % 1 + 1) % 1;
        const y = ((Math.sin(seed * 1.71) * 13421.7) % 1 + 1) % 1;
        const radial = (frame - 112) / 30;
        const centerX = width * 0.5;
        const centerY = height * 0.49;
        const spread = Math.max(0, radial) * (verticalSafe(width, height) ? 39 : 30);
        const px = x * width + (x > 0.5 ? 1 : -1) * spread * (0.35 + x);
        const py = y * height + (y > 0.5 ? 1 : -1) * spread * (0.3 + y);
        const distance = Math.hypot(px - centerX, py - centerY);
        const opacity = reveal * Math.max(0, 0.72 - distance / (Math.max(width, height) * 0.88)) * (0.5 + 0.5 * Math.sin(frame / 9 + i));
        const size = i % 9 === 0 ? 4 : i % 4 === 0 ? 2.5 : 1.5;
        return <div key={i} style={{
          position: 'absolute', left: px, top: py, width: size, height: size,
          borderRadius: '50%', background: i % 5 === 0 ? C.orange : C.white,
          opacity, boxShadow: i % 5 === 0 ? '0 0 16px rgba(255,69,0,.9)' : '0 0 10px rgba(248,250,252,.8)',
          transform: `translate(-50%,-50%) scale(${1 + 0.35 * Math.sin(frame / 12 + i)})`,
        }} />;
      })}
      <div style={{
        position: 'absolute', left: '50%', top: '49%', width: '115%', height: 2,
        transform: `translate(-50%,-50%) rotate(-7deg) scaleX(${interpolate(frame, [105, 123, 172], [0, 1.2, 0], easeOut)})`,
        opacity: interpolate(frame, [105, 124, 171], [0, 0.9, 0], easeOut),
        background: 'linear-gradient(90deg, transparent, rgba(201,243,106,.1), rgba(248,250,252,.95), rgba(255,69,0,.28), transparent)',
        boxShadow: '0 0 30px rgba(248,250,252,.5)',
      }} />
    </AbsoluteFill>
  );
}

function verticalSafe(width: number, height: number) {
  return height > width;
}

function Hud({ frame, vertical }: { frame: number; vertical: boolean }) {
  const alpha = interpolate(frame, [0, 24, 408, 449], [0, 0.8, 0.75, 0], easeOut);
  const progress = interpolate(frame, [0, 449], [0, 100]);
  const edge = vertical ? '8%' : '6%';
  const top = vertical ? '7%' : '8%';
  const bottom = vertical ? '8%' : '8%';
  const labelSize = vertical ? 10 : 12;
  const cornerStyle = (position: React.CSSProperties): React.CSSProperties => ({
    position: 'absolute', width: vertical ? 34 : 46, height: vertical ? 34 : 46,
    borderColor: `rgba(255,69,0,${alpha})`, borderStyle: 'solid', ...position,
  });
  return (
    <AbsoluteFill style={{ zIndex: 25, pointerEvents: 'none', opacity: alpha }}>
      <div style={{ position: 'absolute', top, left: edge, color: C.muted, fontSize: labelSize, letterSpacing: '.22em', fontWeight: 700 }}>SIGNAL STUDY <span style={{ color: C.orange }}>/ 01</span></div>
      <div style={{ position: 'absolute', top, right: edge, color: C.muted, fontSize: labelSize, letterSpacing: '.16em', fontWeight: 700 }}>00:{String(Math.max(0, 15 - Math.floor(frame / 30))).padStart(2, '0' )}</div>
      <div style={cornerStyle({ top, left: edge, borderWidth: '1px 0 0 1px' })} />
      <div style={cornerStyle({ top, right: edge, borderWidth: '1px 1px 0 0' })} />
      <div style={cornerStyle({ bottom, left: edge, borderWidth: '0 0 1px 1px' })} />
      <div style={cornerStyle({ bottom, right: edge, borderWidth: '0 1px 1px 0' })} />
      <div style={{ position: 'absolute', left: edge, right: edge, bottom: vertical ? '5.7%' : '5.8%', height: 1, background: 'rgba(248,250,252,.18)' }}>
        <div style={{ width: `${progress}%`, height: 2, background: C.orange, boxShadow: '0 0 12px rgba(255,69,0,.8)', transform: 'translateY(-.5px)' }} />
      </div>
      <div style={{ position: 'absolute', bottom: vertical ? '3.1%' : '3.3%', left: edge, color: 'rgba(248,250,252,.42)', fontSize: vertical ? 8 : 10, letterSpacing: '.2em' }}>INPUT // ANALOG STATIC</div>
      <div style={{ position: 'absolute', bottom: vertical ? '3.1%' : '3.3%', right: edge, color: 'rgba(248,250,252,.42)', fontSize: vertical ? 8 : 10, letterSpacing: '.2em' }}>FORM // MOTION</div>
    </AbsoluteFill>
  );
}

function GlassTag({ vertical }: { vertical: boolean }) {
  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: vertical ? 11 : 15,
      padding: vertical ? '14px 20px' : '16px 24px',
      borderRadius: 16, border: '1px solid rgba(255,255,255,.18)',
      background: 'linear-gradient(135deg,rgba(255,255,255,.10),rgba(255,255,255,.035))',
      boxShadow: '0 18px 55px rgba(0,0,0,.35),inset 0 1px rgba(255,255,255,.1)',
      backdropFilter: 'blur(20px)', WebkitBackdropFilter: 'blur(20px)',
    }}>
      <span style={{ width: 5, height: vertical ? 22 : 25, borderRadius: 5, background: C.orange, boxShadow: '0 0 12px rgba(255,69,0,.75)' }} />
      <span style={{ color: C.white, fontSize: vertical ? 12 : 15, letterSpacing: '.22em', fontWeight: 800 }}>FIND THE PATTERN</span>
      <span style={{ marginLeft: 4, width: 6, height: 6, borderRadius: '50%', background: C.lime, boxShadow: '0 0 14px rgba(201,243,106,.95)' }} />
    </div>
  );
}

export const NoiseFilm: React.FC<Props> = ({ format }) => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const vertical = format === 'vertical';
  const reveal = spring({ frame: Math.max(0, frame - 106), fps: 30, config: { stiffness: 155, damping: 20, mass: 0.75 } });
  const titleOpacity = interpolate(frame, [100, 116, 408, 449], [0, 1, 1, 0], easeOut);
  const titleScale = interpolate(reveal, [0, 0.55, 1], [1.55, 0.92, 1]);
  const roll = interpolate(frame, [104, 142, 190], [18, 0, 0], easeOut);
  const titleSize = Math.min(width * (vertical ? 0.28 : 0.255), height * (vertical ? 0.21 : 0.39));
  const titleTop = vertical ? '45%' : '47%';
  const subtitleOpacity = interpolate(frame, [230, 250, 345, 382], [0, 1, 1, 0], easeOut);
  const vignette = interpolate(frame, [0, 125, 410, 449], [0.45, 0.15, 0.2, 0.42], easeOut);
  return (
    <AbsoluteFill style={{ backgroundColor: C.obsidian, color: C.white, fontFamily: 'Arial, Helvetica, sans-serif', overflow: 'hidden' }}>
      <NoiseWorld frame={frame} width={width} height={height} />
      <ParticleField frame={frame} width={width} height={height} />
      <AbsoluteFill style={{ zIndex: 15, background: `radial-gradient(ellipse at center, transparent 28%, rgba(3,6,10,${vignette}) 100%)`, pointerEvents: 'none' }} />
      <Hud frame={frame} vertical={vertical} />
      <AbsoluteFill style={{ zIndex: 45, display: 'flex', justifyContent: 'center', alignItems: 'center', pointerEvents: 'none' }}>
        <div style={{ position: 'absolute', top: vertical ? '29%' : '29%', width: '90%', textAlign: 'center', opacity: interpolate(frame, [32, 48, 99, 118], [0, 0.92, 0.85, 0], easeOut), transform: `translateY(${interpolate(frame, [32, 54], [18, 0], easeOut)}px)` }}>
          <div style={{ color: C.muted, fontSize: vertical ? 12 : 15, letterSpacing: '.34em', fontWeight: 700 }}>WHEN THE SIGNAL BREAKS</div>
          <div style={{ width: vertical ? 56 : 74, height: 2, margin: '18px auto 0', background: C.orange, boxShadow: '0 0 16px rgba(255,69,0,.65)' }} />
        </div>
        <div style={{
          position: 'absolute', left: '50%', top: titleTop, width: '94%', textAlign: 'center',
          opacity: titleOpacity, transform: `translate(-50%,-50%) perspective(1000px) rotateX(${roll}deg) scale(${titleScale})`,
          filter: `blur(${interpolate(frame, [104, 124, 150], [8, 0, 0], easeOut)}px)`,
        }}>
          <div style={{
            color: C.white, fontSize: titleSize, lineHeight: 0.82, fontWeight: 900,
            letterSpacing: '-.075em', textTransform: 'uppercase',
            textShadow: '0 1px 0 #dce1e8, 0 2px 0 #b7bec9, 0 3px 0 #8d96a4, 0 4px 0 #6b7482, 0 5px 0 #535c6a, 0 6px 0 #404957, 0 7px 0 #313a47, 0 8px 0 #252d39, 0 9px 0 #1c2430, 0 20px 25px rgba(0,0,0,.75), 0 0 28px rgba(248,250,252,.22)',
            WebkitTextStroke: '1px rgba(255,255,255,.8)',
          }}>NOISE</div>
        </div>
        <div style={{
          position: 'absolute', top: vertical ? '60%' : '68%', left: '50%',
          transform: 'translate(-50%,-50%)', opacity: subtitleOpacity,
        }}>
          <GlassTag vertical={vertical} />
        </div>
      </AbsoluteFill>
      <AbsoluteFill style={{ zIndex: 55, pointerEvents: 'none' }}>
        <div style={{
          position: 'absolute', width: vertical ? 140 : 190, height: vertical ? 140 : 190,
          left: `${interpolate(frame, [118, 200, 300], [31, 62, 69], easeOut)}%`,
          top: `${vertical ? 45 : 47}%`, borderRadius: '50%',
          opacity: interpolate(frame, [112, 128, 155, 225, 244], [0, 0.72, 0.26, 0.5, 0], easeOut),
          background: 'radial-gradient(circle,rgba(201,243,106,.26) 0%,rgba(201,243,106,.1) 18%,transparent 68%)',
          filter: 'blur(4px)', transform: 'translate(-50%,-50%)', mixBlendMode: 'screen',
        }} />
        <div style={{
          position: 'absolute', width: vertical ? 90 : 150, height: vertical ? 90 : 150,
          left: '50%', top: '49%', borderRadius: '50%',
          opacity: interpolate(frame, [112, 124, 140, 184], [0, 0.92, 0.3, 0], easeOut),
          background: 'radial-gradient(circle,rgba(248,250,252,.75) 0%,rgba(255,69,0,.22) 14%,transparent 72%)',
          filter: 'blur(8px)', transform: 'translate(-50%,-50%)', mixBlendMode: 'screen',
        }} />
      </AbsoluteFill>
      <AbsoluteFill style={{ zIndex: 60, pointerEvents: 'none' }}>
        <div style={{ position: 'absolute', top: vertical ? '70%' : '76%', left: '50%', transform: 'translate(-50%,-50%)', textAlign: 'center', opacity: subtitleOpacity * 0.62, color: C.muted, fontSize: vertical ? 10 : 12, letterSpacing: '.28em', fontWeight: 700, whiteSpace: 'nowrap' }}>
          CONTROL THE CHAOS / KEEP THE SIGNAL
        </div>
      </AbsoluteFill>
      <AbsoluteFill style={{ zIndex: 70, pointerEvents: 'none', opacity: interpolate(frame, [420, 449], [1, 0], easeOut), background: 'linear-gradient(180deg,transparent 78%,rgba(4,7,12,.38))' }} />
    </AbsoluteFill>
  );
};
