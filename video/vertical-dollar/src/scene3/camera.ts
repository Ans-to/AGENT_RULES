import * as THREE from 'three';
import {sampleScene3} from './motion';

/** Exact mathematical endpoint of the 28.0–28.2s world-Y whip. */
export function setWhipEndCamera(camera:THREE.PerspectiveCamera):void {
  const orbit=sampleScene3(28).orbit;
  camera.position.set(Math.sin(orbit)*11,.4,Math.cos(orbit)*11);
  camera.lookAt(0,.25,0);
  camera.rotateOnWorldAxis(new THREE.Vector3(0,1,0),Math.PI/2);
  camera.updateProjectionMatrix();
}
