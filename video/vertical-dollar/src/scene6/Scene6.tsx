import {Node,type NodeProps} from '@motion-canvas/2d';
import {GlobalSettings} from '../GlobalSettings';
import {Scene6Bridge} from './Scene6Bridge';
import {sampleScene6} from './motion';
const {width,height}=GlobalSettings.canvas;
export class Scene6 extends Node {
  constructor(private readonly bridge:Scene6Bridge,private readonly time:()=>number,props?:NodeProps){super(props??{});}
  protected override draw(context:CanvasRenderingContext2D):void {
    const t=this.time(),p=sampleScene6(t);if(!p.active)return;
    context.save();context.fillStyle='#000000';context.fillRect(-width/2,-height/2,width,height);
    if(p.reveal>0&&p.contentOpacity>0){
      this.bridge.render(t);context.globalAlpha=p.reveal*p.contentOpacity;context.drawImage(this.bridge.canvas,-width/2,-height/2,width,height);context.globalAlpha=1;
      const lines=[{text:'THERE',color:'#ffffff',size:82,y:1120},{text:'IS NO',color:'#555555',size:82,y:1220},{text:'ALTERNATIVE.',color:GlobalSettings.colors.primary,size:96,y:1330}];
      lines.forEach((line,i)=>{const progress=p.words[i];if(progress<=0)return;context.save();context.globalAlpha=progress*p.contentOpacity;context.textAlign='center';context.textBaseline='middle';context.font=`900 ${line.size}px Inter, sans-serif`;context.fillStyle=line.color;context.fillText(line.text,0,line.y-height/2+30*(1-progress));context.restore();});
    }
    if(p.cta){
      context.save();context.globalAlpha=p.ctaOpacity;context.fillStyle=GlobalSettings.colors.primary;context.shadowColor=GlobalSettings.colors.primary;context.shadowBlur=24;context.beginPath();context.arc(0,0,13*p.dotScale,0,Math.PI*2);context.fill();context.restore();
      context.save();context.globalAlpha=p.followOpacity;context.fillStyle='#ffffff';context.textAlign='center';context.textBaseline='middle';context.font='900 52px Inter, sans-serif';context.fillText('Follow for more.',0,115);context.restore();
    }
    context.restore();
  }
}
