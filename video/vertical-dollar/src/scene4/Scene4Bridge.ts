import * as THREE from 'three';
import {GlobalSettings} from '../GlobalSettings';
import {setWhipEndCamera} from '../scene3/camera';
import {GOLD_COUNT,sampleScene4} from './motion';

const {width,height}=GlobalSettings.canvas;
const green=GlobalSettings.colors.primary;
/** Independent procedural vault scene, rendering through the same camera as Scene 3. */
export class Scene4Bridge {
  readonly canvas=document.createElement('canvas');
  private readonly hud=document.createElement('canvas');
  private readonly ctx:CanvasRenderingContext2D;
  private readonly renderer:THREE.WebGLRenderer;
  private readonly scene=new THREE.Scene();
  private readonly root=new THREE.Group();
  private readonly door=new THREE.Group();
  private readonly doorMaterials:THREE.Material[]=[];
  private readonly bars:THREE.Group[]=[];
  private readonly shield=new THREE.Group();
  private readonly originalPosition=new THREE.Vector3();
  private readonly originalQuaternion=new THREE.Quaternion();
  constructor(private readonly camera:THREE.PerspectiveCamera){
    this.canvas.width=width;this.canvas.height=height;this.hud.width=width;this.hud.height=height;
    const ctx=this.hud.getContext('2d');if(!ctx)throw new Error('Canvas 2D unavailable');this.ctx=ctx;
    this.renderer=new THREE.WebGLRenderer({canvas:this.canvas,antialias:true,alpha:false,preserveDrawingBuffer:true});
    this.renderer.setSize(width,height,false);this.renderer.setPixelRatio(1);this.scene.background=new THREE.Color('#050505');
    setWhipEndCamera(camera);this.originalPosition.copy(camera.position);this.originalQuaternion.copy(camera.quaternion);
    // Build in the terminal camera's local axes: no camera reset or hidden jump.
    this.root.position.copy(new THREE.Vector3(0,0,-10.8).applyQuaternion(this.originalQuaternion).add(this.originalPosition));
    this.root.quaternion.copy(this.originalQuaternion);this.scene.add(this.root);
    this.root.add(new THREE.AmbientLight('#dce7e0',2));
    const light=new THREE.PointLight('#ffffff',95);light.position.set(-3,4,5);this.root.add(light);
    const rimLight=new THREE.PointLight(green,35);rimLight.position.set(4,1,3);this.root.add(rimLight);
    const steel=new THREE.MeshStandardMaterial({color:'#555f60',metalness:.8,roughness:.27});
    const dark=new THREE.MeshStandardMaterial({color:'#202729',metalness:.7,roughness:.4});
    const trim=new THREE.MeshStandardMaterial({color:'#aab5b0',metalness:.85,roughness:.22});
    const gold=new THREE.MeshStandardMaterial({color:'#ffd32d',metalness:.8,roughness:.2,emissive:'#bd8300',emissiveIntensity:.8});
    const addBox=(parent:THREE.Object3D,w:number,h:number,d:number,mat:THREE.Material,x:number,y:number,z:number)=>{const m=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),mat);m.position.set(x,y,z);parent.add(m);return m;};
    // Safe's rear and thick metallic jambs remain after door becomes a cutaway.
    addBox(this.root,4.1,4.3,.3,dark,0,0,-.8);
    for(const x of [-2,2])addBox(this.root,.22,4.55,1.2,steel,x,0,-.3);
    for(const y of [-2.15,2.15])addBox(this.root,4.2,.22,1.2,steel,0,y,-.3);
    addBox(this.root,3.9,.12,1.1,trim,0,-1.33,-.2);
    // Left-hinged box door rotates from -90° to closed, on its own pivot.
    this.door.position.set(-1.9,0,.45);this.root.add(this.door);
    const ds=steel.clone(),dt=trim.clone(),dd=dark.clone();
    this.doorMaterials.push(ds,dt,dd);for(const mat of this.doorMaterials){mat.transparent=true;}
    addBox(this.door,3.8,4.1,.32,ds,1.9,0,0);
    addBox(this.door,3.48,3.78,.08,dd,1.9,0,.19);
    const ring=new THREE.Mesh(new THREE.TorusGeometry(.83,.075,12,48),dt);ring.position.set(1.9,0,.28);this.door.add(ring);
    for(let i=0;i<8;i++){const a=i*Math.PI/4;const bolt=new THREE.Mesh(new THREE.SphereGeometry(.08,12,8),dt);bolt.position.set(1.9+1.35*Math.cos(a),1.45*Math.sin(a),.3);this.door.add(bolt);}
    for(let i=0;i<4;i++){const spoke=addBox(this.door,1.5,.07,.07,dt,1.9,0,.33);spoke.rotation.z=i*Math.PI/4;}
    const hub=new THREE.Mesh(new THREE.CylinderGeometry(.18,.18,.16,20),dt);hub.rotation.x=Math.PI/2;hub.position.set(1.9,0,.37);this.door.add(hub);
    const goldHighlight=new THREE.MeshStandardMaterial({color:'#ffe986',metalness:.8,roughness:.2,emissive:'#a45d00',emissiveIntensity:.5});
    for(let i=0;i<GOLD_COUNT;i++){
      const bar=new THREE.Group();const row=Math.floor(i/3),col=i%3;
      bar.position.set((col-1)*.95,-.96+row*.46,.05);bar.userData.baseY=bar.position.y;
      addBox(bar,.88,.38,.72,gold,0,0,0);
      addBox(bar,.62,.016,.56,goldHighlight,0,.2,0);
      this.root.add(bar);this.bars.push(bar);
    }
    // A translucent extruded shield behind the gold, plus luminous outline.
    const shape=new THREE.Shape();shape.moveTo(0,1.85);shape.lineTo(1.55,1.2);shape.lineTo(1.38,-.45);shape.quadraticCurveTo(1,-1.5,0,-2);shape.quadraticCurveTo(-1,-1.5,-1.38,-.45);shape.lineTo(-1.55,1.2);shape.closePath();
    const face=new THREE.Mesh(new THREE.ExtrudeGeometry(shape,{depth:.06,bevelEnabled:false}),new THREE.MeshBasicMaterial({color:green,transparent:true,opacity:.16,depthWrite:false,side:THREE.DoubleSide}));this.shield.add(face);
    const points=shape.getPoints(40).map(p=>new THREE.Vector3(p.x,p.y,.1));
    const outline=new THREE.Line(new THREE.BufferGeometry().setFromPoints(points),new THREE.LineBasicMaterial({color:green}));this.shield.add(outline);
    const halo=new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(points,true),100,.035,6,true),new THREE.MeshBasicMaterial({color:green,transparent:true,opacity:.34,blending:THREE.AdditiveBlending,depthWrite:false}));this.shield.add(halo);
    this.shield.position.z=-.46;this.root.add(this.shield);
  }
  render(time:number):void {
    const p=sampleScene4(time);
    this.camera.position.copy(this.originalPosition).add(new THREE.Vector3(0,0,-.65*p.push).applyQuaternion(this.originalQuaternion));
    this.camera.quaternion.copy(this.originalQuaternion);this.camera.updateProjectionMatrix();
    this.door.rotation.y=p.doorAngle;
    for(const material of this.doorMaterials){material.opacity=p.doorOpacity;material.depthWrite=p.doorOpacity>.95;}
    this.door.visible=p.doorOpacity>.001;
    this.bars.forEach((bar,i)=>{bar.visible=time>=32+i*.1;bar.position.y=bar.userData.baseY+.93*(1-p.gold[i]);});
    this.shield.visible=time>35;this.shield.scale.setScalar(Math.max(.0001,p.shieldScale));
    this.renderer.render(this.scene,this.camera);
    const ctx=this.ctx;ctx.clearRect(0,0,width,height);
    if(time>=32){ctx.save();ctx.font='400 59px "JetBrains Mono", monospace';ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillStyle=green;ctx.shadowColor=green;ctx.shadowBlur=16;ctx.fillText('US TREASURY BONDS'.slice(0,p.textCount),width/2,580);ctx.restore();}
    if(time>=35){ctx.save();ctx.globalAlpha=p.safeOpacity;ctx.textAlign='center';ctx.textBaseline='middle';ctx.font='900 55px Inter, sans-serif';ctx.fillStyle='#ffffff';ctx.fillText('THE ULTIMATE SAFE HAVEN',width/2,1395);ctx.restore();}
  }
  drawTo(context:CanvasRenderingContext2D,time:number):void{
    const p=sampleScene4(time);context.save();context.translate(p.shake,p.shake*.35);
    context.drawImage(this.canvas,-width/2,-height/2,width,height);context.restore();
    context.drawImage(this.hud,-width/2,-height/2,width,height);
  }
}
