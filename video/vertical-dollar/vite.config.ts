import {defineConfig} from 'vite';
import motionCanvas from '@motion-canvas/vite-plugin';
export default defineConfig({
  plugins: [motionCanvas.default(), {name:'modern-audio-output',enforce:'post',config:()=>({build:{target:'esnext'}})}],
  server: {host: '0.0.0.0', allowedHosts: true},
});
