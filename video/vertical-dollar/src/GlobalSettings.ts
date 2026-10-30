/** Centralized dimensions, palette and storyboard timing. */
export const GlobalSettings = {
  canvas: {width: 1080, height: 1920, aspectRatio: '9:16', fps: 60},
  durationSeconds: 60,
  colors: {background: '#050505', primary: '#00FF41', secondary: '#FF0055', white: '#FFFFFF'},
  typography: {headline: {family: 'Inter', weight: 900, uppercase: true}, code: {family: 'JetBrains Mono', weight: 400}},
  audio: {genre: 'Dark synthwave / phonk', bpm: 120, bassDropsSeconds: [8, 28, 48], track: 'src/audio/placeholder.wav'},
  scenes: [
    {id: 'hook', start: 0, end: 8}, {id: 'petrodollar', start: 8, end: 18},
    {id: 'network', start: 18, end: 28, label: '88% OF ALL FX TRADES'},
    {id: 'trust', start: 28, end: 38}, {id: 'challengers', start: 38, end: 48}, {id: 'outro', start: 48, end: 60},
  ],
} as const;
