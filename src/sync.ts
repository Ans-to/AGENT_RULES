export const FPS = 30;
export const DURATION_IN_FRAMES = 1800;
export const NOISE_DURATION_IN_FRAMES = 450;

export type Cue = {
  start: number;
  end: number;
  voiceover: string;
  audio: string;
};

export const voiceoverCues: Cue[] = [
  {
    start: 0,
    end: 300,
    audio: 'audio/part-1-hook.mp3',
    voiceover:
      "If you buy oil in Saudi Arabia, a coffee in Tokyo, or shoes in Italy... chances are, you're paying in one currency.",
  },
  {
    start: 300,
    end: 750,
    audio: 'audio/part-2-origin.mp3',
    voiceover:
      "Back in 1944, at Bretton Woods, war-torn nations tied their currencies to the US dollar—because America held most of the world's gold. Even when we left the gold standard, the world stayed.",
  },
  {
    start: 750,
    end: 1350,
    audio: 'audio/part-3-liquidity.mp3',
    voiceover:
      "Why? Because of trust, liquidity, and depth. The US financial markets are so massive and stable that global banks and governments keep trillions in US Treasury bonds as their ultimate safety net.",
  },
  {
    start: 1350,
    end: 1800,
    audio: 'audio/part-4-crown.mp3',
    voiceover:
      "It gives America immense economic power—and immense responsibility. Love it or hate it... for now, the greenback holds the crown.",
  },
];

export const sceneCues = [
  { start: 0, end: 300, title: "GLOBAL TRADE" },
  { start: 300, end: 750, title: "1944: THE PIVOT" },
  { start: 750, end: 1350, title: "LIQUIDITY & TRUST" },
  { start: 1350, end: 1800, title: "ECONOMIC POWER" },
];
