import * as THREE from 'three';
import {GlobalSettings} from '../GlobalSettings';
import {sampleScene6} from './motion';
const {width,height}=GlobalSettings.canvas;
const green=GlobalSettings.colors.primary;

/** Procedural neon crown, rendered independently of earlier cameras. */
export class Scene6Bridge {
  readonly canvas=document.createElement('canvas');
  private readonly renderer:THREE.WebGLRenderer;
  private readonly scene=new THREE.Scene();
  private readonly camera=new THREE.PerspectiveCamera(42,width/height,.1,100);
  private readonly crown=new THREE.Group();
  constructor(){
    this.canvas.width=width;this.canvas.height=height;
    this.renderer=new THREE.WebGLRenderer({canvas:this.canvas,antialias:true,alpha:true,preserveDrawingBuffer:true});this.renderer.setSize(width,height,false);this.renderer.setPixelRatio(1);
    this.camera.position.set(0,0,9);this.scene.add(this.crown);
    this.scene.add(new THREE.AmbientLight('#caffd5',1));const light=new THREE.PointLight('#baffca',45);light.position.set(3,4,5);this.scene.add(light);
    const mat=new THREE.MeshStandardMaterial({color:green,emissive:'#00aa2c',emissiveIntensity:1,metalness:.55,roughness:.22,side:THREE.DoubleSide});
    const segments=10,outer=1.5,inner=1.22;const positions:number[]=[];
    const triangle=(a:number[],b:number[],c:number[])=>positions.push(...a,...b,...c);
    for(let i=0;i<segments;i++){
      const a=i*2*Math.PI/segments,b=(i+1)*2*Math.PI/segments;
      const h1=i%2===0?1.05:.20,h2=(i+1)%2===0?1.05:.20;
      const v=(r:number,angle:number,y:number)=>[r*Math.cos(angle),y,r*Math.sin(angle)];
      const o0=v(outer,a,-.65),o1=v(outer,b,-.65),o2=v(outer,b,h2),o3=v(outer,a,h1);
      const i0=v(inner,a,-.65),i1=v(inner,b,-.65),i2=v(inner,b,h2),i3=v(inner,a,h1);
      triangle(o0,o1,o2);triangle(o0,o2,o3);triangle(i0,i2,i1);triangle(i0,i3,i2);triangle(o3,o2,i2);triangle(o3,i2,i3);
      if(i%2===0){const tip=new THREE.Mesh(new THREE.SphereGeometry(.105,12,8),mat);tip.position.set(outer*Math.cos(a),h1,outer*Math.sin(a));this.crown.add(tip);}
    }
    const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));geometry.computeVertexNormals();this.crown.add(new THREE.Mesh(geometry,mat));
    const ring=new THREE.Mesh(new THREE.TorusGeometry(1.38,.12,12,64),mat);ring.rotation.x=Math.PI/2;ring.position.y=-.65;this.crown.add(ring);
    const halo=new THREE.Mesh(new THREE.PlaneGeometry(5.2,5.2),new THREE.ShaderMaterial({transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,uniforms:{},vertexShader:'varying vec2 vUv;void main(){vUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',fragmentShader:'varying vec2 vUv;void main(){float d=length((vUv-.5)*2.);gl_FragColor=vec4(0.,1.,.255,exp(-d*5.)*.4);}'}));halo.position.z=-1.7;this.crown.add(halo);
    this.crown.position.y=.9;
  }
  render(time:number):void {const p=sampleScene6(time);this.crown.rotation.y=p.crownRotation;this.crown.scale.setScalar(Math.max(.00001,p.crownScale));this.renderer.render(this.scene,this.camera);}
}
