import {makeScene2D, Rect} from '@motion-canvas/2d';
import {usePlayback, waitFor} from '@motion-canvas/core';
import {GlobalSettings} from './GlobalSettings';
import {audioManager} from './audio';
import {Scene1} from './scene1/Scene1';
import {Hook3DBridge} from './scene1/Hook3D';
import {Scene2} from './scene2/Scene2';
import {Scene2Bridge} from './scene2/Scene2Bridge';
import {Scene3} from './scene3/Scene3';
import {Scene3Transition} from './scene3/Scene3Transition';
import {Scene4} from './scene4/Scene4';
import {Scene4Bridge} from './scene4/Scene4Bridge';
import {Scene4Transition} from './scene4/Scene4Transition';
import {Scene5} from './scene5/Scene5';
import {Scene5Bridge} from './scene5/Scene5Bridge';
import {Scene5Transition} from './scene5/Scene5Transition';
import {Scene6} from './scene6/Scene6';
import {Scene6Bridge} from './scene6/Scene6Bridge';

let bridgePromise: Promise<Hook3DBridge> | undefined;
let scene2Promise: Promise<Scene2Bridge> | undefined;
export default makeScene2D(function* (view) {
  view.add(<Rect width={GlobalSettings.canvas.width} height={GlobalSettings.canvas.height} fill={GlobalSettings.colors.background} />);
  // Await mounting before the first frame: asynchronous setup must not render blank.
  bridgePromise ??= Hook3DBridge.create();
  const bridge: Hook3DBridge = yield bridgePromise;
  scene2Promise ??= Scene2Bridge.create();
  const scene2: Scene2Bridge = yield scene2Promise;
  yield audioManager.load();
  const playback=usePlayback();
  // Scene 2 starts at 8.0 under Scene 1’s 0.1s drop-effect tail.
  view.add(new Scene2(scene2,() => playback.time));
  view.add(new Scene1(bridge,() => playback.time));
  view.add(new Scene3(scene2,() => playback.time));
  const scene4=new Scene4Bridge(scene2.getSharedCamera());
  view.add(new Scene4(scene4,() => playback.time));
  view.add(new Scene3Transition(scene2,() => playback.time));
  view.add(new Scene4Transition(() => playback.time));
  const scene5=new Scene5Bridge();
  view.add(new Scene5(scene5,() => playback.time));
  view.add(new Scene6(new Scene6Bridge(),() => playback.time));
  // The outgoing flash/zoom is layered over Scene 6's black reset until 48.3s.
  view.add(new Scene5Transition(scene5,() => playback.time));
  yield* waitFor(GlobalSettings.durationSeconds);
});
