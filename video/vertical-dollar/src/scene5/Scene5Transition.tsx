import {Node,type NodeProps} from '@motion-canvas/2d';
import {GlobalSettings} from '../GlobalSettings';
import {audioManager} from '../audio';
import {Scene5Bridge} from './Scene5Bridge';
import {sampleScene5Transition,SCENE5_END} from './motion';
/** Separate outgoing transition tail; Scene 6 remains unimplemented. */
export class Scene5Transition extends Node {
  constructor(private readonly bridge:Scene5Bridge,private readonly time:()=>number,props?:NodeProps){super(props??{});}
  protected override draw(context:CanvasRenderingContext2D):void {
    const t=this.time(),p=sampleScene5Transition(t);if(!p.active)return;
    this.bridge.render(SCENE5_END-1/GlobalSettings.canvas.fps,p.zoom);this.bridge.drawTo(context,1,(p.zoom-1)/4);
    if(audioManager.visualAt(t).drop?.index===2&&p.flash){const {width,height}=GlobalSettings.canvas;context.fillStyle=GlobalSettings.colors.primary;context.fillRect(-width/2,-height/2,width,height);}
  }
}
