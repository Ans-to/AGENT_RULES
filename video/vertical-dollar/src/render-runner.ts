import {Renderer,RendererResult,Vector2,type Project} from '@motion-canvas/core';
import project from './project?project';

const query=new URLSearchParams(location.search);
const start=Math.max(0,Number(query.get('start')??0));
const frames=Math.max(2,Math.min(3600-start,Number(query.get('frames')??3600)));
const name=query.get('name')??'project';
const status=document.getElementById('status')!;
const renderer=new Renderer(project as Project);
let result:RendererResult|undefined;
renderer.onFinished.subscribe(value=>{result=value;});
renderer.onFrameChanged.subscribe(value=>{status.textContent=`Rendering frame ${value}`;});
try {
  await renderer.render({name,// Motion Canvas converts seconds to frames with ceil; bias away float rounding up.
    range:[Math.max(0,(start-1e-6)/60),(start+frames-1-1e-6)/60],fps:60,size:new Vector2(1080,1920),resolutionScale:1,colorSpace:'srgb',background:'#050505',exporter:{name:'@motion-canvas/core/image-sequence',options:{fileType:'image/png',quality:100,groupByScene:false}}});
  if(result!==RendererResult.Success)throw new Error(`Motion Canvas renderer failed (result ${result})`);
  status.textContent='Render complete';document.documentElement.dataset.render='complete';
} catch(error){status.textContent=String(error);document.documentElement.dataset.render='error';}
