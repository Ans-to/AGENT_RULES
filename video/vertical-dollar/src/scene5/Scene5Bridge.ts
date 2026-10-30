import * as THREE from 'three';
import {FontLoader,type FontData} from 'three/examples/jsm/loaders/FontLoader.js';
import {TextGeometry} from 'three/examples/jsm/geometries/TextGeometry.js';
import fontData from 'three/examples/fonts/helvetiker_bold.typeface.json';
import {GlobalSettings} from '../GlobalSettings';
import {sampleScene5} from './motion';

const {width,height}=GlobalSettings.canvas;
const pink=GlobalSettings.colors.secondary,green=GlobalSettings.colors.primary;
const STARTS=[new THREE.Vector3(-3,0,0),new THREE.Vector3(3,0,0),new THREE.Vector3(0,4.82,0)];
type Challenger={group:THREE.Group;materials:THREE.Material[]};

/** Procedural Three.js scene sampled entirely from absolute time. */
export class Scene5Bridge {
  readonly canvas=document.createElement('canvas');
  private readonly hud=document.createElement('canvas');
  private readonly composite=document.createElement('canvas');
  private readonly ctx:CanvasRenderingContext2D;
  private readonly compositeCtx:CanvasRenderingContext2D;
  private readonly renderer:THREE.WebGLRenderer;
  private readonly scene=new THREE.Scene();
  private readonly camera=new THREE.PerspectiveCamera(45,width/height,.05,100);
  private readonly root=new THREE.Group();
  private readonly challengers:Challenger[]=[];
  private readonly dollar:THREE.Mesh;
  private readonly particles:THREE.Points;
  private readonly velocity:Float32Array;
  private readonly origin:Float32Array;
  constructor(){
    this.canvas.width=this.hud.width=this.composite.width=width;
    this.canvas.height=this.hud.height=this.composite.height=height;
    const ctx=this.hud.getContext('2d'),comp=this.composite.getContext('2d');if(!ctx||!comp)throw new Error('Canvas 2D unavailable');this.ctx=ctx;this.compositeCtx=comp;
    this.renderer=new THREE.WebGLRenderer({canvas:this.canvas,antialias:true,alpha:false,preserveDrawingBuffer:true});this.renderer.setSize(width,height,false);this.renderer.setPixelRatio(1);
    this.scene.background=new THREE.Color('#050505');this.camera.position.set(0,0,10);this.scene.add(this.root);
    this.scene.add(new THREE.AmbientLight('#ffffff',1.5));const light=new THREE.PointLight('#ffffff',80);light.position.set(-3,5,6);this.scene.add(light);
    const font=new FontLoader().parse(fontData as FontData);
    const glyph=(text:string,size:number,material:THREE.Material)=>{
      const geometry=new TextGeometry(text,{font,size,depth:.24,curveSegments:10,bevelEnabled:true,bevelThickness:.025,bevelSize:.015,bevelSegments:2});
      geometry.computeBoundingBox();const c=geometry.boundingBox!.getCenter(new THREE.Vector3());geometry.translate(-c.x,-c.y,-c.z);return new THREE.Mesh(geometry,material);
    };
    const threat=()=>new THREE.MeshStandardMaterial({color:pink,emissive:'#ae003b',emissiveIntensity:.65,metalness:.45,roughness:.26,transparent:true});
    // Currency glyphs are embossed on thick procedural blocks. Pink tint is
    // applied to all three; labels distinguish the nominal red/blue assets.
    const makeBlock=(label:string)=>{
      const group=new THREE.Group(),body=threat(),face=new THREE.MeshBasicMaterial({map:this.makeLabel(label),transparent:true,depthWrite:false});
      const box=new THREE.Mesh(new THREE.BoxGeometry(1.25,1.25,.38),body);group.add(box);
      const panel=new THREE.Mesh(new THREE.PlaneGeometry(1.15,1.15),face);panel.position.z=.201;group.add(panel);
      this.root.add(group);return {group,materials:[body,face]};
    };
    this.challengers.push(makeBlock('¥'),makeBlock('€'));
    const coin=new THREE.Group(),coinMat=threat(),coinFace=new THREE.MeshBasicMaterial({color:'#ff8baa',transparent:true});
    const disc=new THREE.Mesh(new THREE.CylinderGeometry(.66,.66,.28,48),coinMat);disc.rotation.x=Math.PI/2;coin.add(disc);
    const circle=new THREE.Mesh(new THREE.TorusGeometry(.48,.035,8,40),coinFace);circle.position.z=.15;coin.add(circle);
    this.root.add(coin);this.challengers.push({group:coin,materials:[coinMat,coinFace]});
    this.dollar=glyph('$',2.55,new THREE.MeshStandardMaterial({color:green,emissive:'#00cf35',emissiveIntensity:1,metalness:.35,roughness:.22}));this.root.add(this.dollar);
    const count=900;this.origin=new Float32Array(count*3);this.velocity=new Float32Array(count*3);
    let seed=5831;const random=()=>{seed=(1664525*seed+1013904223)>>>0;return seed/4294967296;};
    for(let i=0;i<count;i++){const k=i*3,a=random()*Math.PI*2,s=.7+random()*4;this.origin[k]=(random()-.5)*.45;this.origin[k+1]=(random()-.5)*.45;this.origin[k+2]=(random()-.5)*.35;this.velocity[k]=Math.cos(a)*s;this.velocity[k+1]=Math.sin(a)*s;this.velocity[k+2]=(random()-.5)*2;}
    const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.BufferAttribute(this.origin.slice(),3).setUsage(THREE.DynamicDrawUsage));
    this.particles=new THREE.Points(geometry,new THREE.PointsMaterial({color:pink,size:.055,transparent:true,opacity:1,blending:THREE.AdditiveBlending,depthWrite:false}));this.particles.frustumCulled=false;this.root.add(this.particles);
  }
  private makeLabel(label:string):THREE.CanvasTexture {
    const c=document.createElement('canvas');c.width=c.height=256;const ctx=c.getContext('2d');if(!ctx)throw new Error('Canvas 2D unavailable');
    ctx.clearRect(0,0,256,256);ctx.textAlign='center';ctx.textBaseline='middle';ctx.font='900 180px Inter, sans-serif';ctx.fillStyle='#ffe4ec';ctx.fillText(label,128,136);
    const texture=new THREE.CanvasTexture(c);texture.colorSpace=THREE.SRGBColorSpace;return texture;
  }
  render(time:number,zoom=1):void {
    const p=sampleScene5(time);this.root.scale.setScalar(zoom);
    this.challengers.forEach(({group,materials},i)=>{
      group.position.copy(STARTS[i]).multiplyScalar(1-p.attack);
      group.rotation.y=(time-38)*.3*(i===1?-1:1);group.scale.setScalar(Math.max(.0001,1-p.shatter));group.visible=p.shatter<1;
      for(const m of materials){m.opacity=1-p.shatter;}
    });
    this.dollar.visible=time>=42;this.dollar.position.y=2.157*(1-p.drop); // 500px at z=10 / 45° FOV
    this.particles.visible=time>=42.5&&p.burst<1.8;
    const mat=this.particles.material as THREE.PointsMaterial;mat.opacity=Math.max(0,1-p.burst/1.8);
    if(this.particles.visible){const attr=this.particles.geometry.getAttribute('position') as THREE.BufferAttribute;const arr=attr.array as Float32Array;for(let i=0;i<arr.length;i+=3){arr[i]=this.origin[i]+this.velocity[i]*p.burst;arr[i+1]=this.origin[i+1]+this.velocity[i+1]*p.burst-1.3*p.burst*p.burst;arr[i+2]=this.origin[i+2]+this.velocity[i+2]*p.burst;}attr.needsUpdate=true;}
    this.renderer.render(this.scene,this.camera);
    const ctx=this.ctx;ctx.clearRect(0,0,width,height);
    if(p.textVisible){ctx.save();ctx.translate(width/2,height/2);ctx.scale(zoom,zoom);ctx.translate(p.jitterX,1405-height/2+p.jitterY);ctx.textAlign='center';ctx.textBaseline='middle';ctx.font='900 72px Inter, sans-serif';ctx.lineWidth=5;ctx.strokeStyle=pink;ctx.lineJoin='round';ctx.strokeText('NOT ENOUGH LIQUIDITY',0,0);ctx.fillStyle='#ffffff';ctx.fillText('NOT ENOUGH LIQUIDITY',0,0);ctx.restore();}
    const c=this.compositeCtx;c.clearRect(0,0,width,height);c.drawImage(this.canvas,0,p.impactShake,width,height);c.drawImage(this.hud,0,0,width,height);
  }
  drawTo(context:CanvasRenderingContext2D,fade:number,blur=0):void {
    context.save();context.fillStyle='#000000';context.fillRect(-width/2,-height/2,width,height);
    context.globalAlpha=fade;context.drawImage(this.composite,-width/2,-height/2,width,height);
    // Deterministic radial multi-sample streaks approximate rapid forward motion blur.
    if(blur>0){for(let i=1;i<=6;i++){const scale=1+blur*i*.025;context.globalAlpha=fade*.08;context.drawImage(this.composite,-width*scale/2,-height*scale/2,width*scale,height*scale);}}
    context.restore();
  }
}
