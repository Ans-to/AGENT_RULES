import {Node,type NodeProps} from '@motion-canvas/2d';
import {GlobalSettings} from '../GlobalSettings';
import {sampleScene4Transition} from './motion';
/** The outgoing image fades to black before Scene 5 begins. */
export class Scene4Transition extends Node {
  constructor(private readonly time:()=>number,props?:NodeProps){super(props??{});}
  protected override draw(context:CanvasRenderingContext2D):void {
    const t=this.time();const transition=sampleScene4Transition(t);if(!transition.active)return;
    const {width,height}=GlobalSettings.canvas;context.save();context.globalAlpha=transition.black;context.fillStyle='#000000';context.fillRect(-width/2,-height/2,width,height);context.restore();
  }
}
