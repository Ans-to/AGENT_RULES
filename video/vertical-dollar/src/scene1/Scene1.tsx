import {Node, type NodeProps} from '@motion-canvas/2d';
import {Hook3DBridge} from './Hook3D';
import {GlobalSettings} from '../GlobalSettings';

/** Motion Canvas layer for Scene 1; time is supplied by the global timeline. */
export class Scene1 extends Node {
  constructor(private readonly bridge: Hook3DBridge, private readonly time: () => number, props?: NodeProps) { super(props ?? {}); }
  protected override draw(context: CanvasRenderingContext2D): void {
    const t=this.time();
    // The 0.1s drop flash is a transition tail; Scene 2 should overlap at 8.0s.
    if(t < 0 || t >= 8.1) return;
    this.bridge.render(t);
    const {width,height}=GlobalSettings.canvas;
    context.drawImage(this.bridge.canvas,-width/2,-height/2,width,height);
  }
}
