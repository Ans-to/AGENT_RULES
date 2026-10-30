import {describe,it,expect} from 'vitest';
import * as THREE from 'three';
import {sampleScene3} from '../src/scene3/motion';
import {setWhipEndCamera} from '../src/scene3/camera';
import {DOOR_IMPACT,sampleScene4,sampleScene4Transition,spring} from '../src/scene4/motion';

describe('Scene 4 absolute-time motion and camera continuity',()=>{
  it('is active only from 28 through 38 seconds',()=>{
    expect(sampleScene4(27.999).active).toBe(false);expect(sampleScene4(28).active).toBe(true);
    expect(sampleScene4(37.999).active).toBe(true);expect(sampleScene4(38).active).toBe(false);
  });
  it('starts at the actual Scene 3 whip endpoint, not the origin',()=>{
    const camera=new THREE.PerspectiveCamera();setWhipEndCamera(camera);
    const s=sampleScene3(28);const expected=new THREE.PerspectiveCamera();
    expected.position.set(Math.sin(s.orbit)*11,.4,Math.cos(s.orbit)*11);expected.lookAt(0,.25,0);
    expected.rotateOnWorldAxis(new THREE.Vector3(0,1,0),Math.PI/2);
    expect(camera.position.distanceTo(expected.position)).toBeLessThan(1e-10);
    expect(camera.quaternion.angleTo(expected.quaternion)).toBeLessThan(1e-7);
    expect(camera.position.length()).toBeGreaterThan(10);
  });
  it('slams from -90° to zero, triggering a 10px shake at impact',()=>{
    expect(sampleScene4(28).doorAngle).toBeCloseTo(-Math.PI/2);
    expect(sampleScene4(DOOR_IMPACT).doorAngle).toBeCloseTo(0);
    expect(sampleScene4(DOOR_IMPACT-1e-5).shake).toBe(0);
    expect(sampleScene4(DOOR_IMPACT).shake).toBeCloseTo(10);
    expect(sampleScene4(DOOR_IMPACT+1/30).shake).toBeLessThan(0);
    expect(sampleScene4(29.1).shake).toBe(0);
  });
  it('stagger-drops six bars from 32s and types the requested label',()=>{
    expect(sampleScene4(32).gold.every(v=>v===0)).toBe(true);
    const p=sampleScene4(32.25);expect(p.gold[0]).toBeGreaterThan(p.gold[1]);expect(p.gold[2]).toBeGreaterThan(0);expect(p.gold[3]).toBe(0);
    expect(sampleScene4(32).textCount).toBe(0);expect(sampleScene4(34).textCount).toBe('US TREASURY BONDS'.length);
    expect(sampleScene4(31.99).push).toBe(0);expect(sampleScene4(33.2).push).toBeCloseTo(1);
  });
  it('uses the specified physical spring, with overshoot capped at 1.1',()=>{
    expect(spring(0)).toBe(0);expect(sampleScene4(35).shieldScale).toBe(0);
    expect(sampleScene4(35.01).shieldScale).toBeGreaterThan(0);
    expect(sampleScene4(35.36).shieldScale).toBeCloseTo(1.1);
    expect(sampleScene4(37).shieldScale).toBeCloseTo(1,3);
    expect(sampleScene4(35).safeOpacity).toBe(0);expect(sampleScene4(35.7).safeOpacity).toBeCloseTo(1);
  });
  it('fades the outgoing scene to black before 38s',()=>{
    expect(sampleScene4Transition(37.799).active).toBe(false);
    expect(sampleScene4Transition(37.8).black).toBe(0);
    expect(sampleScene4Transition(37.9).black).toBeCloseTo(.5);
    expect(sampleScene4Transition(38).active).toBe(false);
  });
  it('is deterministic when sampled out of order',()=>{
    const p=sampleScene4(35.3);sampleScene4(28.3);sampleScene4(37.9);expect(sampleScene4(35.3)).toEqual(p);
  });
});
