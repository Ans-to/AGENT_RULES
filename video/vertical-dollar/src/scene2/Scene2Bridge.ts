import React, {useLayoutEffect, useMemo} from 'react';
import {createRoot, extend, type RootState} from '@react-three/fiber';
import * as THREE from 'three';
import {GlobalSettings} from '../GlobalSettings';
import {OIL_TEXT, sampleScene2} from './motion';
import {createNetwork} from '../scene3/network';
import {sampleScene3, ROUTE_POINTS} from '../scene3/motion';

extend({AmbientLight: THREE.AmbientLight, PointLight: THREE.PointLight});
const {width, height} = GlobalSettings.canvas;
const green = GlobalSettings.colors.primary;

type Model = {
  balance: THREE.Group; beam: THREE.Group; leftPan: THREE.Group; rightPan: THREE.Group;
  barrel: THREE.Group; globe: THREE.Mesh; particles: THREE.Points;
  starts: Float32Array; ends: Float32Array; velocities: Float32Array;
};

function createBillTexture(): THREE.CanvasTexture {
  const canvas=document.createElement('canvas'); canvas.width=512; canvas.height=256;
  const ctx=canvas.getContext('2d'); if (!ctx) throw new Error('Canvas 2D unavailable');
  ctx.fillStyle='#00ff41';ctx.fillRect(0,0,512,256);
  ctx.strokeStyle='#063d16';ctx.lineWidth=10;ctx.strokeRect(20,20,472,216);
  ctx.strokeStyle='#099c36';ctx.lineWidth=4;ctx.strokeRect(37,37,438,182);
  ctx.fillStyle='#064319';ctx.textAlign='center';ctx.textBaseline='middle';ctx.font='bold 170px sans-serif';ctx.fillText('$',256,128);
  const texture=new THREE.CanvasTexture(canvas);texture.colorSpace=THREE.SRGBColorSpace;return texture;
}

function createModel(): Model {
  const dark=new THREE.MeshStandardMaterial({color:'#343d39',emissive:'#0c1711',emissiveIntensity:.7,metalness:.45,roughness:.42});
  const rim=new THREE.MeshStandardMaterial({color:'#879790',metalness:.55,roughness:.32});
  const frame=new THREE.MeshStandardMaterial({color:'#303a35',metalness:.72,roughness:.28});
  const neon=new THREE.MeshStandardMaterial({color:green,emissive:'#009c28',emissiveIntensity:.6,metalness:.2,roughness:.4});
  const box=(x:number,y:number,z:number,material:THREE.Material) => new THREE.Mesh(new THREE.BoxGeometry(x,y,z),material);
  const cylinder=(r1:number,r2:number,h:number,material:THREE.Material) => new THREE.Mesh(new THREE.CylinderGeometry(r1,r2,h,32),material);
  const balance=new THREE.Group();balance.position.y=-.5;
  const base=box(2.0,.18,.72,frame);base.position.y=-1.55;balance.add(base);
  const baseGlow=box(1.65,.025,.74,neon);baseGlow.position.y=-1.45;balance.add(baseGlow);
  const column=cylinder(.13,.22,2.7,frame);column.position.y=-.18;balance.add(column);
  const pivot=new THREE.Mesh(new THREE.SphereGeometry(.23,20,12),rim);pivot.position.y=1.2;balance.add(pivot);
  const beam=new THREE.Group();beam.position.y=1.2;balance.add(beam);
  const bar=box(3.8,.13,.18,rim);beam.add(bar);
  const buildPan=(x:number) => {
    const anchor=new THREE.Group();anchor.position.x=x;beam.add(anchor);
    const stem=cylinder(.025,.025,.87,rim);stem.position.y=-.45;anchor.add(stem);
    const pan=cylinder(.64,.47,.10,frame);pan.position.y=-.90;anchor.add(pan);
    const ring=new THREE.Mesh(new THREE.TorusGeometry(.61,.025,8,48),neon);ring.rotation.x=Math.PI/2;ring.position.y=-.84;anchor.add(ring);
    return anchor;
  };
  const leftPan=buildPan(-1.7),rightPan=buildPan(1.7);
  const barrel=new THREE.Group();leftPan.add(barrel);
  const body=cylinder(.40,.40,1.05,dark);barrel.add(body);
  for(const y of [-.48,-.25,.25,.48]) {
    const hoop=new THREE.Mesh(new THREE.TorusGeometry(.405,.032,8,48),rim);hoop.rotation.x=Math.PI/2;hoop.position.y=y;barrel.add(hoop);
  }
  for(const y of [-.54,.54]){const cap=cylinder(.39,.39,.035,frame);cap.position.y=y;barrel.add(cap);}
  const bill=new THREE.Group();rightPan.add(bill);bill.position.set(0,-.72,0);
  const billBox=box(1.05,.54,.10,neon);bill.add(billBox);
  const face=new THREE.Mesh(new THREE.PlaneGeometry(1.02,.51),new THREE.MeshBasicMaterial({map:createBillTexture()}));face.position.z=.056;bill.add(face);
  const globeMaterial=new THREE.MeshBasicMaterial({color:green,wireframe:true,transparent:true,opacity:0});
  const globe=new THREE.Mesh(new THREE.IcosahedronGeometry(1.38,2),globeMaterial);globe.position.set(0,.38,0);globe.visible=false;
  const count=1800,starts=new Float32Array(count*3),ends=new Float32Array(count*3),velocities=new Float32Array(count*3);
  let seed=82919;const random=()=>{seed=(1664525*seed+1013904223)>>>0;return seed/4294967296;};
  for(let i=0;i<count;i++){
    const k=i*3,a=random()*Math.PI*2,y=(random()-.5)*1.05;
    starts[k]=Math.cos(a)*.40;starts[k+1]=y;starts[k+2]=Math.sin(a)*.40;
    const v=1-2*(i+.5)/count,longitude=i*2.399963,rad=Math.sqrt(1-v*v);
    ends[k]=1.38*rad*Math.cos(longitude);ends[k+1]=1.38*v;ends[k+2]=1.38*rad*Math.sin(longitude);
    const s=.5+random()*1.4;velocities[k]=Math.cos(a)*s;velocities[k+1]=(random()-.5)*2.4;velocities[k+2]=Math.sin(a)*s;
  }
  const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.BufferAttribute(starts.slice(),3).setUsage(THREE.DynamicDrawUsage));
  const particles=new THREE.Points(geo,new THREE.PointsMaterial({color:green,size:.045,transparent:true,opacity:1,blending:THREE.AdditiveBlending,depthWrite:false}));particles.visible=false;particles.frustumCulled=false;
  return {balance,beam,leftPan,rightPan,barrel,globe,particles,starts,ends,velocities};
}

function Scene2Model({onReady}:{onReady:(model:Model)=>void}) {
  const model=useMemo(createModel,[]);
  useLayoutEffect(()=>{onReady(model);},[model,onReady]);
  return React.createElement(React.Fragment,null,
    React.createElement('ambientLight',{intensity:1.1}),
    React.createElement('pointLight',{position:[-3,4,6],color:'#c5ffcf',intensity:50}),
    React.createElement('pointLight',{position:[4,-1,5],color:green,intensity:20}),
    React.createElement('primitive',{object:model.balance}),
    React.createElement('primitive',{object:model.globe}),
    React.createElement('primitive',{object:model.particles}));
}

/** An independently mounted R3F canvas rendered on demand by Motion Canvas. */
export class Scene2Bridge {
  readonly canvas=document.createElement('canvas');
  private readonly hud=document.createElement('canvas');
  private readonly ctx:CanvasRenderingContext2D;
  private state!:RootState;
  private model!:Model;
  private network!:ReturnType<typeof createNetwork>;
  private constructor(){
    this.canvas.width=width;this.canvas.height=height;this.hud.width=width;this.hud.height=height;
    const context=this.hud.getContext('2d');if(!context)throw new Error('Canvas 2D unavailable');this.ctx=context;
  }
  static async create():Promise<Scene2Bridge>{
    const bridge=new Scene2Bridge();
    if(document.fonts)await Promise.all([document.fonts.load('400 72px "JetBrains Mono"'),document.fonts.ready]);
    const root=createRoot(bridge.canvas);
    await root.configure({frameloop:'never',dpr:1,size:{width,height,top:0,left:0},camera:{position:[0,.4,11],fov:45,near:.05,far:100},gl:{antialias:true,preserveDrawingBuffer:true,alpha:false}});
    let resolve!:(model:Model)=>void;const ready=new Promise<Model>(r=>{resolve=r;});
    const store=root.render(React.createElement(Scene2Model,{onReady:resolve}));
    bridge.model=await ready;bridge.network=createNetwork(bridge.model.globe);bridge.state=store.getState();bridge.state.scene.background=new THREE.Color(GlobalSettings.colors.background);
    return bridge;
  }
  render(time:number):void{
    const pose=sampleScene2(time),m=this.model;
    this.network.group.visible=false;
    (m.particles.material as THREE.PointsMaterial).opacity=1;
    m.beam.rotation.z=pose.tilt;m.leftPan.rotation.z=-pose.tilt;m.rightPan.rotation.z=-pose.tilt;
    m.barrel.position.y=-.27+(1-pose.fall)*3.8;m.barrel.visible=time<15;
    m.balance.scale.setScalar(Math.max(.001,pose.balanceScale));m.balance.visible=pose.balanceScale>0;
    m.balance.updateMatrixWorld(true);
    const origin=new THREE.Vector3();m.barrel.getWorldPosition(origin);
    m.particles.visible=time>=15 && time<18;m.globe.visible=pose.globeVisibility>0;
    (m.globe.material as THREE.MeshBasicMaterial).opacity=pose.globeVisibility*.95;
    m.globe.rotation.y=(time-15)*.18;
    if(m.particles.visible){
      const attr=m.particles.geometry.getAttribute('position') as THREE.BufferAttribute,arr=attr.array as Float32Array;
      const swirl=(time-15)*(1-pose.formation)*2.2,cs=Math.cos(swirl),sn=Math.sin(swirl);
      for(let i=0;i<arr.length;i+=3){
        const x=m.starts[i]+m.velocities[i]*pose.explosion,z=m.starts[i+2]+m.velocities[i+2]*pose.explosion;
        const sx=origin.x+x*cs-z*sn,sy=origin.y+m.starts[i+1]+m.velocities[i+1]*pose.explosion,sz=origin.z+x*sn+z*cs;
        arr[i]=sx*(1-pose.formation)+m.ends[i]*pose.formation;
        arr[i+1]=sy*(1-pose.formation)+(m.ends[i+1]+.38)*pose.formation;
        arr[i+2]=sz*(1-pose.formation)+m.ends[i+2]*pose.formation;
      }
      attr.needsUpdate=true;
    }
    const camera=this.state.camera;camera.position.set(Math.sin(pose.orbit)*11,.4,Math.cos(pose.orbit)*11);camera.lookAt(0,.25,0);camera.updateProjectionMatrix();
    const gl=this.state.gl;gl.setRenderTarget(null);gl.clear();gl.render(this.state.scene,camera);
    this.drawHud(time,pose.textCount,pose.cursorVisible,pose.textOpacity);
  }
  private drawHud(time:number,count:number,cursorVisible:boolean,opacity:number){
    const ctx=this.ctx;ctx.clearRect(0,0,width,height);
    if(time>=12 && time<15.3){
      ctx.save();ctx.font='400 72px "JetBrains Mono", monospace';ctx.textAlign='left';ctx.textBaseline='middle';ctx.globalAlpha=opacity;ctx.fillStyle=green;ctx.shadowColor=green;ctx.shadowBlur=18;
      const fullWidth=ctx.measureText(OIL_TEXT).width;const x=(width-fullWidth)/2;const typed=OIL_TEXT.slice(0,count);ctx.fillText(typed,x,1600);
      if(cursorVisible){const cx=x+ctx.measureText(typed).width+8;ctx.fillRect(cx,1561,10,77);}
      ctx.restore();
    }
  }
  /** Scene 3 reuses this bridge, its exact globe mesh, particles and camera. */
  renderNetwork(time:number):void {
    const pose=sampleScene3(time),m=this.model;
    m.balance.visible=false;m.barrel.visible=false;m.globe.visible=true;
    (m.globe.material as THREE.MeshBasicMaterial).opacity=.95;
    m.globe.rotation.y=(time-15)*.18;
    this.network.group.visible=true;
    this.network.originMarker.visible=pose.lineProgress>0;
    for(const route of this.network.routes){
      route.line.geometry.setDrawRange(0,Math.min(ROUTE_POINTS,Math.floor((ROUTE_POINTS-1)*pose.lineProgress)+1));
      route.offset.value=pose.dashOffset;
      for(const halo of route.halos)halo.geometry.setDrawRange(0,Math.floor((ROUTE_POINTS-1)*pose.lineProgress)*6*6);
      route.endMarker.visible=pose.lineProgress>=.98;
    }
    // Preserve the exact last Scene 2 particle state, then fade particles out.
    const fade=Math.max(0,1-(time-18)/1.2);
    m.particles.visible=fade>0;
    (m.particles.material as THREE.PointsMaterial).opacity=fade;
    if(m.particles.visible){
      const attr=m.particles.geometry.getAttribute('position') as THREE.BufferAttribute,arr=attr.array as Float32Array;
      for(let i=0;i<arr.length;i+=3){arr[i]=m.ends[i];arr[i+1]=m.ends[i+1]+.38;arr[i+2]=m.ends[i+2];}
      attr.needsUpdate=true;
    }
    const camera=this.state.camera;
    camera.position.set(Math.sin(pose.orbit)*11,.4,Math.cos(pose.orbit)*11);
    camera.lookAt(0,.25,0);camera.rotateOnWorldAxis(new THREE.Vector3(0,1,0),pose.whipYaw);camera.updateProjectionMatrix();
    const gl=this.state.gl;gl.setRenderTarget(null);gl.clear();gl.render(this.state.scene,camera);
    this.drawNetworkHud(time,pose.statScale,pose.subProgress);
  }
  /** Exposed for continuity checks; no new globe is created in Scene 3. */
  getSharedGlobe():THREE.Mesh{return this.model.globe;}
  getSharedCamera():THREE.PerspectiveCamera{return this.state.camera as THREE.PerspectiveCamera;}
  private drawNetworkHud(time:number,statScale:number,subProgress:number):void {
    const ctx=this.ctx;ctx.clearRect(0,0,width,height);if(time>=28)return;
    if(time>=22){
      ctx.save();ctx.translate(width/2,930);ctx.scale(statScale,statScale);
      ctx.textAlign='center';ctx.textBaseline='middle';ctx.font='900 270px Inter, sans-serif';
      ctx.fillStyle=green;ctx.shadowColor=green;ctx.shadowBlur=32;ctx.fillText('88%',0,0);ctx.restore();
    }
    if(time>=25){
      ctx.save();ctx.globalAlpha=subProgress;ctx.textAlign='center';ctx.textBaseline='middle';
      ctx.font='900 68px Inter, sans-serif';ctx.fillStyle='#FFFFFF';
      ctx.fillText('OF ALL FX TRADES',width/2,1150+50*(1-subProgress));ctx.restore();
    }
  }
  /** HUD is separately composited after the 3D canvas, without pixel readback. */
  drawTo(context:CanvasRenderingContext2D){
    context.drawImage(this.canvas,-width/2,-height/2,width,height);
    context.drawImage(this.hud,-width/2,-height/2,width,height);
  }
}
