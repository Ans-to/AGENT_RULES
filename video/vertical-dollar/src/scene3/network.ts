import * as THREE from 'three';
import {GlobalSettings} from '../GlobalSettings';
import {ROUTE_POINTS} from './motion';

const RADIUS=1.38;
// Longitude convention is rotated so North America faces the initial camera;
// all points use actual approximate geographic latitude/longitude.
export const LOCATIONS={
  usa:{lat:38.9,lon:-77.0},
  europe:{lat:50.1,lon:8.7},
  asia:{lat:35.7,lon:139.7},
  middleEast:{lat:24.7,lon:46.7},
} as const;
export function geographicDirection(lat:number,lon:number):THREE.Vector3 {
  const phi=THREE.MathUtils.degToRad(lat),lambda=THREE.MathUtils.degToRad(lon+122);
  return new THREE.Vector3(Math.cos(phi)*Math.sin(lambda),Math.sin(phi),Math.cos(phi)*Math.cos(lambda));
}
export type Route={line:THREE.Line; material:THREE.LineDashedMaterial; offset:{value:number}; endMarker:THREE.Mesh; halos:THREE.Mesh[]};

/** Attach the routes to the existing globe so they follow its exact rotation. */
export function createNetwork(globe:THREE.Mesh):{group:THREE.Group;routes:Route[];originMarker:THREE.Mesh} {
  const group=new THREE.Group();globe.add(group);
  const source=geographicDirection(LOCATIONS.usa.lat,LOCATIONS.usa.lon);
  const pointMat=new THREE.MeshBasicMaterial({color:GlobalSettings.colors.primary});
  const markerGeometry=new THREE.SphereGeometry(.055,12,8);
  const marker=(v:THREE.Vector3)=>{const dot=new THREE.Mesh(markerGeometry,pointMat);dot.position.copy(v).multiplyScalar(RADIUS*1.025);group.add(dot);return dot;};
  const originMarker=marker(source);originMarker.scale.setScalar(1.4);
  const targets=[LOCATIONS.europe,LOCATIONS.asia,LOCATIONS.middleEast];
  const routes=targets.map(target=>{
    const dest=geographicDirection(target.lat,target.lon);const points:THREE.Vector3[]=[];
    for(let i=0;i<ROUTE_POINTS;i++){
      const u=i/(ROUTE_POINTS-1);
      const direction=source.clone().lerp(dest,u).normalize();
      points.push(direction.multiplyScalar(RADIUS*(1.035+.26*Math.sin(Math.PI*u))));
    }
    const geometry=new THREE.BufferGeometry().setFromPoints(points);geometry.setDrawRange(0,0);
    // Three.js LineBasicMaterial has no dashSize, gapSize or dash offset.
    // LineDashedMaterial supports the first two; a shader uniform adds offset.
    const offset={value:3};
    const material=new THREE.LineDashedMaterial({color:GlobalSettings.colors.primary,dashSize:.12,gapSize:.05,transparent:true,opacity:1});
    material.onBeforeCompile=shader=>{
      shader.uniforms.uDashOffset=offset;
      shader.vertexShader=shader.vertexShader.replace('varying float vLineDistance;', 'varying float vLineDistance;\nuniform float uDashOffset;')
        .replace('vLineDistance = scale * lineDistance;', 'vLineDistance = scale * lineDistance + uDashOffset;');
    };
    material.customProgramCacheKey=()=> 'scene3-dash-offset-v1';
    const line=new THREE.Line(geometry,material);line.computeLineDistances();group.add(line);
    // Additive translucent tubes give the thin dashed core a visible green halo.
    const curve=new THREE.CatmullRomCurve3(points);
    const halos=[.014,.032].map((radius,index)=>{
      const haloGeometry=new THREE.TubeGeometry(curve,ROUTE_POINTS-1,radius,6,false);
      haloGeometry.setDrawRange(0,0);
      const haloMaterial=new THREE.MeshBasicMaterial({color:GlobalSettings.colors.primary,transparent:true,opacity:index===0?.22:.06,blending:THREE.AdditiveBlending,depthWrite:false});
      const halo=new THREE.Mesh(haloGeometry,haloMaterial);group.add(halo);return halo;
    });
    return {line,material,offset,endMarker:marker(dest),halos};
  });
  group.visible=false;
  return {group,routes,originMarker};
}
