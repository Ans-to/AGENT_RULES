import {Node,type NodeProps} from '@motion-canvas/2d';
import {Scene5Bridge} from './Scene5Bridge';
import {sampleScene5} from './motion';
export class Scene5 extends Node {
  constructor(private readonly bridge:Scene5Bridge,private readonly time:()=>number,props?:NodeProps){super(props??{});}
  protected override draw(context:CanvasRenderingContext2D):void {
    const t=this.time(),p=sampleScene5(t);if(!p.active)return;
    this.bridge.render(t);this.bridge.drawTo(context,p.fade);
  }
}
