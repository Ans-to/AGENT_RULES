import {Node, type NodeProps} from '@motion-canvas/2d';
import {Scene2Bridge} from '../scene2/Scene2Bridge';
import {SCENE3_START,SCENE3_END} from './motion';

/** Scene 3 draws the very same globe and renderer created for Scene 2. */
export class Scene3 extends Node {
  constructor(private readonly bridge:Scene2Bridge,private readonly time:()=>number,props?:NodeProps){super(props ?? {});}
  protected override draw(context:CanvasRenderingContext2D):void{
    const t=this.time();if(t<SCENE3_START || t>=SCENE3_END)return;
    this.bridge.renderNetwork(t);this.bridge.drawTo(context);
  }
}
