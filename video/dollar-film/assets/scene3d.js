import * as THREE from './three.module.js';
const canvas=document.querySelector('#world');
const renderer=new THREE.WebGLRenderer({canvas, antialias:true,alpha:false,powerPreference:'high-performance'});
renderer.setPixelRatio(1);renderer.setSize(960,540,false);renderer.setClearColor(0x071b17);renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;
const scene=new THREE.Scene();scene.fog=new THREE.FogExp2(0x071b17,.038);
const camera=new THREE.PerspectiveCamera(38,16/9,.1,100);camera.position.set(0,0,10);
scene.add(new THREE.HemisphereLight(0xe4eee2,0x19382a,2.1));
let warm=new THREE.DirectionalLight(0xffd68a,4.2);warm.position.set(-4,7,8);scene.add(warm);
let rim=new THREE.DirectionalLight(0x68d9b0,3.0);rim.position.set(6,3,-2);scene.add(rim);
const matGold=new THREE.MeshStandardMaterial({color:0xcaa45a,metalness:.72,roughness:.34});
const matMint=new THREE.MeshStandardMaterial({color:0x62d2a6,metalness:.3,roughness:.38,emissive:0x0b5138,emissiveIntensity:.6});
const matDark=new THREE.MeshStandardMaterial({color:0x183a2d,metalness:.36,roughness:.52});
const matPaper=new THREE.MeshStandardMaterial({color:0xe7debd,metalness:.12,roughness:.7});
const matDeep=new THREE.MeshStandardMaterial({color:0x102b22,metalness:.3,roughness:.5});
const mesh=(g,m=matGold)=>new THREE.Mesh(g,m);
function line(points,color=0x6ed9b2){let curve=new THREE.CatmullRomCurve3(points.map(p=>new THREE.Vector3(...p)));let tube=mesh(new THREE.TubeGeometry(curve,45,.013,6,false),new THREE.MeshBasicMaterial({color}));return tube}
function textureText(text,fg='#f5e9bd',bg=null){let c=document.createElement('canvas');c.width=512;c.height=512;let x=c.getContext('2d');if(bg){x.fillStyle=bg;x.fillRect(0,0,512,512)}x.fillStyle=fg;x.textAlign='center';x.textBaseline='middle';x.font='bold 340px Georgia';x.fillText(text,256,270);let t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;return t}
const dollarTexture=textureText('$');
function coin(r=1){let g=new THREE.Group();let body=mesh(new THREE.CylinderGeometry(r,r,.22,64),matGold);body.rotation.x=Math.PI/2;g.add(body);let ring=mesh(new THREE.TorusGeometry(r*.86,.025,8,64),matPaper);ring.position.z=.12;g.add(ring);let face=mesh(new THREE.PlaneGeometry(r*1.34,r*1.34),new THREE.MeshBasicMaterial({map:dollarTexture,transparent:true,depthWrite:false}));face.position.z=.14;g.add(face);return g}
function orbit(r,color=0x51b591){let g=mesh(new THREE.TorusGeometry(r,.012,6,90),new THREE.MeshBasicMaterial({color}));g.rotation.x=1.0;g.rotation.y=.2;return g}
function node(r=.13,material=matMint){return mesh(new THREE.IcosahedronGeometry(r,1),material)}
function stack(w=1.0,h=1.4,d=.06){let g=new THREE.Group();for(let i=0;i<4;i++){let p=mesh(new THREE.BoxGeometry(w,h,d),i%2?matPaper:matDark);p.position.set(i*.08,i*.06,-i*.08);p.rotation.z=i*.05;g.add(p)}return g}
function gold(){let g=new THREE.Group();let b=mesh(new THREE.BoxGeometry(2.2,.7,.95),matGold);g.add(b);let top=mesh(new THREE.BoxGeometry(1.94,.04,.75),matPaper);top.position.y=.37;g.add(top);return g}
function building(){let g=new THREE.Group();let base=mesh(new THREE.BoxGeometry(3.2,.18,1.0),matGold);base.position.y=-1.2;g.add(base);let roof=mesh(new THREE.ConeGeometry(1.9,.6,4),matGold);roof.rotation.y=Math.PI/4;roof.position.y=1.1;g.add(roof);for(let i=0;i<4;i++){let c=mesh(new THREE.CylinderGeometry(.15,.15,1.9,12),matPaper);c.position.set((i-1.5)*.75,-.03,0);g.add(c)}return g}
function network(count=8,r=2.15){let group=new THREE.Group(),dots=[];for(let i=0;i<count;i++){let a=i/count*Math.PI*2;let p=[Math.cos(a)*r,Math.sin(a)*r*.58,Math.sin(a*2)*.6];let ball=node(.14,i%3?matMint:matGold);ball.position.set(...p);group.add(ball);group.add(line([[0,0,0],[p[0]*.5,p[1]*.5,p[2]-.5],p],i%3?0x509b7a:0xc2a164));dots.push(ball)}return {group,dots}}
function boxes(){let g=new THREE.Group();for(let i=0;i<7;i++){let x=(i-3)*.72,h=.55+(i%3)*.35;let m=mesh(new THREE.BoxGeometry(.55,h,.55),i%2?matMint:matGold);m.position.set(x,-1.25+h/2,0);g.add(m)}return g}
function container(){let g=new THREE.Group();let body=mesh(new THREE.BoxGeometry(2.2,1.0,.85),matDark);g.add(body);for(let i=0;i<8;i++){let bar=mesh(new THREE.BoxGeometry(.035,.82,.03),matGold);bar.position.set(-.85+i*.24,0,.44);g.add(bar)}return g}
const groups=[], dynamics=[];function newStage(){let g=new THREE.Group();scene.add(g);groups.push(g);dynamics.push([]);return g}function dyn(stage,obj,fn){dynamics[stage].push({obj,fn});return obj}
// Eight separate, depth-sorted scenes; stage motion is evaluated directly from time.
{
 let g=newStage(),c=coin(1.38);c.position.set(1.9,0,0);g.add(c);dyn(0,c,(o,p,t)=>{o.rotation.y=-.5+1.0*p;o.rotation.z=-.15+.18*p;o.scale.setScalar(.85+.17*Math.min(p*2,1));});
 let n=network(9,2.7);n.group.position.set(1.9,0,-.7);g.add(n.group);dyn(0,n.group,(o,p,t)=>{o.rotation.z=t*.12;o.rotation.y=.2*Math.sin(t*.35)});g.add(orbit(3.5));
}
{
 let g=newStage(),c=coin(.72);c.position.set(.55,.1,0);g.add(c);let bar=gold();bar.position.set(3.1,-.1,-.3);bar.rotation.y=-.35;g.add(bar);let n=network(5,1.9);n.group.position.set(.55,.1,-.8);g.add(n.group);g.add(line([[.65,.1,0],[1.4,.3,.1],[2.25,.0,0]],0xd4ad60));
 dyn(1,c,(o,p,t)=>{o.rotation.y=.2*Math.sin(t*.8);o.rotation.z=.15*p});dyn(1,n.group,(o,p,t)=>{o.rotation.z=t*.13});dyn(1,bar,(o,p,t)=>{o.rotation.y=-.4+.22*Math.sin(t*.4)});
}
{
 let g=newStage(),c=coin(1.05);c.position.set(1.2,.15,0);g.add(c);let b=gold();b.position.set(3.45,-.1,-.1);g.add(b);let l1=mesh(new THREE.BoxGeometry(.8,.07,.07),matGold);l1.position.set(2.05,.08,0);g.add(l1);let l2=mesh(new THREE.BoxGeometry(.8,.07,.07),matGold);l2.position.set(2.75,.08,0);g.add(l2);let n=network(8,2.5);n.group.position.set(1.2,.15,-1);g.add(n.group);
 dyn(2,b,(o,p,t)=>{o.position.x=3.45+p*1.2;o.rotation.z=-p*.3});dyn(2,l1,(o,p)=>{o.position.x=2.05-p*.25;o.rotation.z=-p*.35});dyn(2,l2,(o,p)=>{o.position.x=2.75+p*.5;o.rotation.z=p*.4});dyn(2,c,(o,p,t)=>{o.rotation.y=.3*Math.sin(t*.7)});dyn(2,n.group,(o,p,t)=>{o.scale.setScalar(.6+p*.5);o.rotation.z=t*.13});
}
{
 let g=newStage(),bank=building();bank.position.set(2.2,0,-1.5);g.add(bank);let cards=stack(1.15,1.6);cards.position.set(1.3,.1,1);g.add(cards);let bars=boxes();bars.position.set(2,-1.1,-1);g.add(bars);let c=coin(.55);c.position.set(3.6,1.2,.1);g.add(c);
 dyn(3,cards,(o,p,t)=>{o.rotation.y=-.45+Math.sin(t*.7)*.3;o.position.x=1.2+.7*Math.sin(t*.4)});dyn(3,bank,(o,p,t)=>{o.rotation.y=-.3+.25*p});dyn(3,bars,(o,p,t)=>{o.children.forEach((x,i)=>{x.scale.y=.5+.5*Math.abs(Math.sin(t*.8+i))})});
}
{
 let g=newStage(),c=coin(.8);c.position.set(1.6,.2,0);g.add(c);let n=network(3,2.8);n.group.position.set(1.6,.2,-.3);g.add(n.group);let con=container();con.scale.setScalar(.55);con.position.set(.4,1.6,.5);g.add(con);let docs=stack(.8,1);docs.position.set(3.4,1.3,.4);g.add(docs);let bank=building();bank.scale.setScalar(.45);bank.position.set(1.9,-1.5,.4);g.add(bank);
 dyn(4,c,(o,p,t)=>{o.rotation.y=.4*Math.sin(t*.7)});dyn(4,con,(o,p,t)=>{o.position.x=.4+.35*Math.sin(t*.6);o.rotation.y=t*.15});dyn(4,docs,(o,p,t)=>{o.rotation.y=t*.2});dyn(4,bank,(o,p,t)=>{o.rotation.y=.3*Math.sin(t*.5)});dyn(4,n.group,(o,p,t)=>{o.rotation.z=.08*Math.sin(t*.4)});
}
{
 let g=newStage(),c=coin(.95);c.position.set(1.8,.1,0);g.add(c);let n=network(12,2.65);n.group.position.set(1.8,.1,-.4);g.add(n.group);let r=orbit(2.8);r.position.set(1.8,.1,-.4);g.add(r);
 dyn(5,n.group,(o,p,t)=>{o.rotation.z=t*.24;o.rotation.y=Math.sin(t*.28)*.3;o.children.forEach((m,i)=>{if(i%2===0)m.scale.setScalar(.85+.35*Math.abs(Math.sin(t*2+i)))});});dyn(5,r,(o,p,t)=>{o.rotation.y=t*.16;o.rotation.x=.9+t*.12});dyn(5,c,(o,p,t)=>{o.rotation.y=.45*Math.sin(t*.5)});
}
{
 let g=newStage();let n=network(8,2.6);n.group.position.set(1.8,0,-.5);g.add(n.group);let c=coin(1);c.position.set(1.8,0,0);g.add(c);
 for(let i=0;i<3;i++){let d=mesh(new THREE.CylinderGeometry(.48,.48,.14,40),i===0?matPaper:matGold);d.rotation.x=Math.PI/2;d.position.set(.15+i*1.75,-1.75,.5);g.add(d);dyn(6,d,(o,p,t)=>{o.position.y=-1.75+Math.sin(t*.9+i)*.16;o.rotation.z=t*.3+i})}dyn(6,n.group,(o,p,t)=>{o.rotation.z=t*.11});dyn(6,c,(o,p,t)=>{o.rotation.y=.35*Math.sin(t*.45)});
}
{
 let g=newStage(),c=coin(1.2);c.position.set(1.75,0,0);g.add(c);let n=network(12,3.0);n.group.position.set(1.75,0,-.8);g.add(n.group);let r=orbit(2.8);r.position.set(1.75,0,-.5);g.add(r);
 dyn(7,c,(o,p,t)=>{o.rotation.y=.32*Math.sin(t*.5);o.rotation.z=.09*Math.sin(t*.25)});dyn(7,n.group,(o,p,t)=>{o.rotation.z=t*.14;o.rotation.y=Math.sin(t*.25)*.22});dyn(7,r,(o,p,t)=>{o.rotation.y=t*.18;o.rotation.x=1+t*.05});
}
// Dust in depth is decorative, stable and deterministic.
let points=[];for(let i=0;i<160;i++){let k=i*19.73;points.push(Math.sin(k)*8,Math.cos(k*1.31)*4, -1-((i*13)%30)/4)}
let geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.Float32BufferAttribute(points,3));let stars=new THREE.Points(geo,new THREE.PointsMaterial({color:0xb7d5b1,size:.025,transparent:true,opacity:.45}));scene.add(stars);
const starts=[0,6.556,16.568,23.337,30.875,37.281,43.283,49.305], ends=[6.556,16.568,23.337,30.875,37.281,43.283,49.305,58.4];
function renderAt(t){let i=starts.findLastIndex(v=>t>=v);i=Math.max(0,i);let p=Math.min(1,Math.max(0,(t-starts[i])/(ends[i]-starts[i])));groups.forEach((g,j)=>g.visible=j===i);dynamics[i].forEach(({obj,fn})=>fn(obj,p,t));stars.rotation.z=t*.006;camera.position.set(.25*Math.sin(t*.24),.13*Math.sin(t*.31),9.3-.75*Math.sin(Math.PI*p));camera.lookAt(.4,0,0);renderer.render(scene,camera)}
window.addEventListener('hf-seek',e=>renderAt(e.detail.time));renderAt(0);window.__dollar3dReady=true;
