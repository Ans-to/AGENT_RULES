import {Node,type NodeProps} from '@motion-canvas/2d';
import {GlobalSettings} from '../GlobalSettings';
import {audioManager} from '../audio';
import {Scene2Bridge} from '../scene2/Scene2Bridge';
import {sampleScene3,SCENE3_END,TRANSITION_END} from './motion';

/** Transition is separate from Scene 3's strict [18, 28) interval. */
export class Scene3Transition extends Node {
  constructor(private readonly bridge:Scene2Bridge,private readonly time:()=>number,props?:NodeProps){super(props ?? {});}
  protected override draw(context:CanvasRenderingContext2D):void{
    const t=this.time();if(t<SCENE3_END)return;
    if(t>=TRANSITION_END)return;
    this.bridge.renderNetwork(t);this.bridge.drawTo(context);
    // Use the second global cue, not a frame counter started from playback.
    if(audioManager.visualAt(t).drop?.index===1 && sampleScene3(t).flash){
      const {width,height}=GlobalSettings.canvas;
      context.fillStyle='#FFFFFF';context.fillRect(-width/2,-height/2,width,height);
    }
  }
}
