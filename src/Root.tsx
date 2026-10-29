import React from 'react';
import { Composition } from 'remotion';
import { DollarEmpire } from './Video';
import { NoiseFilm } from './NoiseFilm';
import { DURATION_IN_FRAMES, FPS, NOISE_DURATION_IN_FRAMES } from './sync';

export const RemotionRoot: React.FC = () => (
  <>
    <Composition
      id="BrettonWoods-Landscape"
      component={DollarEmpire}
      durationInFrames={DURATION_IN_FRAMES}
      fps={FPS}
      width={1920}
      height={1080}
      defaultProps={{ format: 'landscape' as const }}
    />
    <Composition
      id="BrettonWoods-Vertical"
      component={DollarEmpire}
      durationInFrames={DURATION_IN_FRAMES}
      fps={FPS}
      width={1080}
      height={1920}
      defaultProps={{ format: 'vertical' as const }}
    />
    <Composition
      id="Katana-Noise-Landscape"
      component={NoiseFilm}
      durationInFrames={NOISE_DURATION_IN_FRAMES}
      fps={FPS}
      width={1920}
      height={1080}
      defaultProps={{ format: 'landscape' as const }}
    />
    <Composition
      id="Katana-Noise-Vertical"
      component={NoiseFilm}
      durationInFrames={NOISE_DURATION_IN_FRAMES}
      fps={FPS}
      width={1080}
      height={1920}
      defaultProps={{ format: 'vertical' as const }}
    />
  </>
);
