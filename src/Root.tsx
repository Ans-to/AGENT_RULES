import React from 'react';
import { Composition } from 'remotion';
import { DollarEmpire } from './Video';
import { DURATION_IN_FRAMES, FPS } from './sync';

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
  </>
);
