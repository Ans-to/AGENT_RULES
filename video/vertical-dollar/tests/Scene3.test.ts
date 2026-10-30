import {describe,expect,it} from 'vitest';
import {sampleScene2} from '../src/scene2/motion';
import {sampleScene3} from '../src/scene3/motion';
import {createNetwork, geographicDirection} from '../src/scene3/network';
import * as THREE from 'three';

describe('Scene 3 and its transition',()=>{
  it('uses the strict scene interval and separate transition tail',()=>{
    expect(sampleScene3(17.999).active).toBe(false);
    expect(sampleScene3(18).active).toBe(true);
    expect(sampleScene3(27.999).active).toBe(true);
    expect(sampleScene3(28).active).toBe(false);
    expect(sampleScene3(28).transition).toBe(true);
    expect(sampleScene3(28.2).transition).toBe(false);
  });
  it('starts from the exact Scene 2 orbit and reveals routes',()=>{
    expect(sampleScene3(18).orbit).toBeCloseTo(sampleScene2(17.999).orbit);
    expect(sampleScene3(18).lineProgress).toBe(0);
    expect(sampleScene3(18.75).lineProgress).toBeCloseTo(.5);
    expect(sampleScene3(19.5).lineProgress).toBe(1);
    expect(sampleScene3(18).dashOffset).not.toBe(sampleScene3(19.5).dashOffset);
    expect(sampleScene3(27).orbit-sampleScene3(26).orbit).toBeGreaterThan(sampleScene3(20).orbit-sampleScene3(19).orbit);
  });
  it('introduces the elastic statistic and sliding subtext at their exact cues',()=>{
    expect(sampleScene3(21.999).statScale).toBe(0);
    expect(sampleScene3(22).statScale).toBe(0);
    expect(sampleScene3(22.4).statScale).toBeGreaterThan(0);
    expect(sampleScene3(23).statScale).toBeCloseTo(1);
    expect(sampleScene3(24.999).subProgress).toBe(0);
    expect(sampleScene3(25).subProgress).toBe(0);
    expect(sampleScene3(25.65).subProgress).toBeCloseTo(1);
  });
  it('flashes exactly one frame and whips 90 degrees over .2 seconds',()=>{
    expect(sampleScene3(28).flash).toBe(true);
    expect(sampleScene3(28+1/60-1e-5).flash).toBe(true);
    expect(sampleScene3(28+1/60).flash).toBe(false);
    expect(sampleScene3(28).whipYaw).toBe(0);
    expect(sampleScene3(28.1).whipYaw).toBeCloseTo(Math.PI/2/32);
    expect(sampleScene3(28.19999).whipYaw).toBeCloseTo(Math.PI/2,3);
  });
  it('attaches routes to the supplied globe instead of creating another globe',()=>{
    const globe=new THREE.Mesh(new THREE.IcosahedronGeometry(1.38,2),new THREE.MeshBasicMaterial());
    const geometry=globe.geometry;const network=createNetwork(globe);
    expect(globe.geometry).toBe(geometry);expect(network.group.parent).toBe(globe);
    expect(network.routes).toHaveLength(3);
    expect(network.routes.every(r=>r.material instanceof THREE.LineDashedMaterial)).toBe(true);
    expect(geographicDirection(38.9,-77).length()).toBeCloseTo(1);
  });
  it('is deterministic under arbitrary seeks',()=>{
    const before=sampleScene3(25.4);sampleScene3(28.1);sampleScene3(8);expect(sampleScene3(25.4)).toEqual(before);
  });
});
