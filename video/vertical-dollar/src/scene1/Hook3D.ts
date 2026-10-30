import React, {useLayoutEffect, useMemo} from 'react';
import {createRoot, extend, type RootState} from '@react-three/fiber';
import * as THREE from 'three';
import {FontLoader, type FontData} from 'three/examples/jsm/loaders/FontLoader.js';
import {TextGeometry} from 'three/examples/jsm/geometries/TextGeometry.js';
import fontData from 'three/examples/fonts/helvetiker_bold.typeface.json';
import {gsap} from 'gsap';
import {audioManager} from '../audio';
import {GlobalSettings} from '../GlobalSettings';

extend({AmbientLight: THREE.AmbientLight, PointLight: THREE.PointLight});
const {width, height} = GlobalSettings.canvas;
const dropTime = GlobalSettings.audio.bassDropsSeconds[0];
type Model = {dollar: THREE.Mesh; particles: THREE.Points; starts: Float32Array; velocities: Float32Array; glow: THREE.Mesh};
type HookPose = {cameraZ: number; dollarScale: number; text1: number; text2: number; text3: number; alpha1: number; alpha2: number; alpha3: number; zoom: number};

function makeModel(): Model {
  const font = new FontLoader().parse(fontData as FontData);
  const geometry = new TextGeometry('$', {font, size: 1.3, depth: 0.2, curveSegments: 10, bevelEnabled: true, bevelThickness: 0.025, bevelSize: 0.018, bevelSegments: 3});
  geometry.computeBoundingBox();
  const center = geometry.boundingBox!.getCenter(new THREE.Vector3());
  geometry.translate(-center.x, -center.y, -center.z);
  const dollar = new THREE.Mesh(geometry, new THREE.MeshStandardMaterial({color: '#00ff41', emissive: '#00ff41', emissiveIntensity: 1.7, metalness: .25, roughness: .22}));
  const glow = new THREE.Mesh(new THREE.PlaneGeometry(4, 4), new THREE.ShaderMaterial({transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, uniforms: {uOpacity: {value: .8}}, vertexShader: `varying vec2 vUv; void main(){vUv=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}`, fragmentShader: `varying vec2 vUv; uniform float uOpacity; void main(){float d=length((vUv-.5)*2.); float a=exp(-d*4.)*uOpacity; gl_FragColor=vec4(0.,1.,.16,a);}`}));
  glow.position.z = -.25;
  const vertices = geometry.getAttribute('position');
  const count = 1400, starts = new Float32Array(count * 3), velocities = new Float32Array(count * 3);
  let seed = 321; const rand = () => {seed = (1664525 * seed + 1013904223) >>> 0; return seed / 4294967296;};
  for (let i=0;i<count;i++) {
    const v=Math.floor(rand()*vertices.count), k=i*3;
    starts[k]=vertices.getX(v)*1.2; starts[k+1]=vertices.getY(v)*1.2; starts[k+2]=vertices.getZ(v)*1.2;
    const a=rand()*Math.PI*2, speed=.7+rand()*3.5;
    velocities[k]=Math.cos(a)*speed; velocities[k+1]=Math.sin(a)*speed; velocities[k+2]=(rand()-.3)*2.2;
  }
  const particleGeometry = new THREE.BufferGeometry();
  particleGeometry.setAttribute('position', new THREE.BufferAttribute(starts.slice(), 3).setUsage(THREE.DynamicDrawUsage));
  const particles = new THREE.Points(particleGeometry, new THREE.PointsMaterial({color: '#00ff41', size: .045, transparent: true, opacity: 1, blending: THREE.AdditiveBlending, depthWrite: false}));
  particles.visible=false;
  return {dollar, particles, starts, velocities, glow};
}

/** React component intentionally mounted by R3F into the offscreen WebGL canvas. */
function HookModel({onReady}: {onReady: (model: Model) => void}) {
  const model = useMemo(makeModel, []);
  useLayoutEffect(() => { onReady(model); }, [model, onReady]);
  return React.createElement(React.Fragment, null,
    React.createElement('ambientLight', {intensity: .7}),
    React.createElement('pointLight', {position: [3, 3, 5], color: '#a7ffb7', intensity: 30}),
    React.createElement('primitive', {object: model.glow}),
    React.createElement('primitive', {object: model.dollar}),
    React.createElement('primitive', {object: model.particles}));
}

/** R3F -> render target -> full-screen GLSL composite -> Motion Canvas node. */
export class Hook3DBridge {
  readonly canvas = document.createElement('canvas');
  private readonly hud = document.createElement('canvas');
  private readonly hudContext: CanvasRenderingContext2D;
  private readonly hudTexture: THREE.CanvasTexture;
  private readonly target = new THREE.WebGLRenderTarget(width, height);
  private readonly quadScene = new THREE.Scene();
  private readonly quadCamera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
  private readonly material: THREE.ShaderMaterial;
  private state!: RootState;
  private model!: Model;
  private readonly pose: HookPose = {cameraZ: 10, dollarScale: 0, text1: -500, text2: 0, text3: 500, alpha1: 0, alpha2: 0, alpha3: 0, zoom: 1};
  private readonly timeline: gsap.core.Timeline;

  private constructor() {
    this.canvas.width=width; this.canvas.height=height; this.hud.width=width; this.hud.height=height;
    const context=this.hud.getContext('2d'); if (!context) throw new Error('2D canvas unavailable'); this.hudContext=context;
    this.hudTexture=new THREE.CanvasTexture(this.hud); this.hudTexture.colorSpace=THREE.SRGBColorSpace;
    this.material=new THREE.ShaderMaterial({uniforms: {tScene: {value:this.target.texture}, tHud: {value:this.hudTexture}, uShift: {value:0}, uShake: {value:new THREE.Vector2()}}, vertexShader:`varying vec2 vUv; void main(){vUv=uv;gl_Position=vec4(position,1.);}`, fragmentShader:`
      varying vec2 vUv; uniform sampler2D tScene; uniform sampler2D tHud; uniform float uShift; uniform vec2 uShake;
      vec3 merged(vec2 uv){vec4 bg=texture2D(tScene,uv);vec4 fg=texture2D(tHud,uv);return mix(bg.rgb,fg.rgb,fg.a);}
      void main(){vec2 uv=vUv+uShake;vec2 offset=vec2(uShift,0.);vec3 a=merged(uv+offset),b=merged(uv),d=merged(uv-offset);vec3 c=vec3(a.r,b.g,d.b);float edge=abs(a.g-d.g);c.r+=edge*.25;c.b+=edge*.45;gl_FragColor=vec4(c,1.);
      #include <colorspace_fragment>
      }`});
    this.quadScene.add(new THREE.Mesh(new THREE.PlaneGeometry(2,2),this.material));
    // GSAP is paused and addressed by absolute time, not wall-clock time.
    this.timeline=gsap.timeline({paused:true});
    this.timeline.to(this.pose,{dollarScale:1.2,duration:.4,ease:'back.out(2.5)'},0)
      .to(this.pose,{cameraZ:2,duration:2,ease:'power2.in'},0)
      .to(this.pose,{text1:0,alpha1:1,duration:.65,ease:'power3.out'},2)
      .to(this.pose,{text2:0,alpha2:1,duration:.65,ease:'power3.out'},2.1)
      .to(this.pose,{text3:0,alpha3:1,duration:.65,ease:'power3.out'},2.2)
      .to(this.pose,{zoom:12,cameraZ:.1,duration:3,ease:'power2.in'},5);
  }

  static async create(): Promise<Hook3DBridge> {
    const b=new Hook3DBridge();
    if (document.fonts) await Promise.all([document.fonts.load('900 180px Inter'),document.fonts.ready]);
    const root=createRoot(b.canvas);
    await root.configure({frameloop:'never', dpr:1, size:{width,height,top:0,left:0}, camera:{position:[0,0,10], fov:45, near:.01, far:100}, gl:{antialias:true, preserveDrawingBuffer:true, alpha:false}});
    let resolveModel!: (value: Model)=>void; const ready=new Promise<Model>(resolve=>{resolveModel=resolve;});
    const store=root.render(React.createElement(HookModel,{onReady:resolveModel}));
    b.model=await ready; b.state=store.getState();
    b.state.scene.background=new THREE.Color(GlobalSettings.colors.background);
    return b;
  }

  render(time: number): void {
    const t=Math.max(0,Math.min(8.1,time)); this.timeline.seek(t, false);
    const {dollar,particles,starts,velocities,glow}=this.model;
    dollar.visible=t<2; glow.visible=t<2;
    dollar.scale.setScalar(this.pose.dollarScale); glow.scale.setScalar(Math.max(.001,this.pose.dollarScale));
    particles.visible=t>=2 && t<4.4;
    if (particles.visible) {
      const p=t-2, attr=particles.geometry.getAttribute('position') as THREE.BufferAttribute, arr=attr.array as Float32Array;
      for(let i=0;i<arr.length;i+=3){arr[i]=starts[i]+velocities[i]*p;arr[i+1]=starts[i+1]+velocities[i+1]*p-.18*p*p;arr[i+2]=starts[i+2]+velocities[i+2]*p;}
      attr.needsUpdate=true; (particles.material as THREE.PointsMaterial).opacity=Math.max(0,1-p/2.4); particles.geometry.computeBoundingSphere();
    }
    this.state.camera.position.z=this.pose.cameraZ; this.state.camera.lookAt(0,0,0); this.state.camera.updateProjectionMatrix();
    this.drawHud(t);
    const effect=audioManager.visualAt(time); this.material.uniforms.uShift.value=effect.chromaticShiftPx/width;
    const shake=t>=5 && t<8.1 ? 15 : 0;
    this.material.uniforms.uShake.value.set(Math.sin(t*2*Math.PI*20)*shake/width,Math.cos(t*2*Math.PI*20)*shake/height);
    const gl=this.state.gl; gl.setRenderTarget(this.target);gl.clear();gl.render(this.state.scene,this.state.camera);gl.setRenderTarget(null);gl.clear();gl.render(this.quadScene,this.quadCamera);
  }

  private drawHud(t: number): void {
    const c=this.hudContext;c.clearRect(0,0,width,height);
    if(t<2 || t>=8.1){this.hudTexture.needsUpdate=true;return;}
    c.save(); c.font='900 190px Inter, sans-serif';
    // DOLLAR is centered; the zoom anchor is the centre of its O.
    const whole=c.measureText('DOLLAR').width, left=width/2-whole/2;
    const oCenter=left+c.measureText('D').width+c.measureText('O').width/2;
    const z=this.pose.zoom, anchorX=width/2+(oCenter-width/2)*Math.min(1,Math.max(0,(z-1)/11));c.translate(width/2,height/2);c.scale(z,z);c.translate(-anchorX,-height/2);
    const line=(text:string,y:number,color:string,offset:number,alpha:number,size:number)=>{
      c.globalAlpha=alpha;c.textAlign='center';c.textBaseline='middle';c.font=`900 ${size}px Inter, sans-serif`;c.fillStyle=color;c.shadowColor=color;c.shadowBlur=color==='#FFFFFF'?0:26;c.fillText(text,width/2+offset,y);
    };
    line('WHY IS THE',730,'#FFFFFF',this.pose.text1,this.pose.alpha1,125);
    line('DOLLAR',960,GlobalSettings.colors.primary,this.pose.text2,this.pose.alpha2,190);
    line('KING?',1190,GlobalSettings.colors.secondary,this.pose.text3,this.pose.alpha3,190);
    c.restore();this.hudTexture.needsUpdate=true;
  }
}
