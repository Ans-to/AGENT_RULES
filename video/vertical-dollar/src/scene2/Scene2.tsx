import {Node, type NodeProps} from '@motion-canvas/2d';
import {Scene2Bridge} from './Scene2Bridge';
import {SCENE2_START, SCENE2_END} from './motion';

/** Strictly bounded to [8.0, 18.0) in the master timeline. */
export class Scene2 extends Node {
  constructor(private readonly bridge:Scene2Bridge,private readonly time:()=>number,props?:NodeProps){super(props ?? {});}
  protected override draw(context:CanvasRenderingContext2D):void{
    const t=this.time();if(t<SCENE2_START || t>=SCENE2_END)return;
    this.bridge.render(t);this.bridge.drawTo(context);
  }
}
