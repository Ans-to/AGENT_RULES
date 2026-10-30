import {makeProject} from '@motion-canvas/core';
import '@fontsource/inter/900.css';
import '@fontsource/jetbrains-mono/400.css';
import {audioManager} from './audio';
import main from './main?scene';

export default makeProject({scenes: [main], audio: await audioManager.createProcessedTrack()});
