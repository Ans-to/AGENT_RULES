import {Node,type NodeProps} from '@motion-canvas/2d';
import {Scene4Bridge} from './Scene4Bridge';
import {SCENE4_START,SCENE4_END} from './motion';
export class Scene4 extends Node {
  constructor(private readonly bridge:Scene4Bridge,private readonly time:()=>number,props?:NodeProps){super(props??{});}
  protected override draw(context:CanvasRenderingContext2D):void {
    const time=this.time();if(time<SCENE4_START||time>=SCENE4_END)return;
    this.bridge.render(time);this.bridge.drawTo(context,time);
  }
}
