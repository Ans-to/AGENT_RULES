"""15s vertical Blender promo adapted from the user-provided script.
Run: blender -b --python tech-promo/scene.py -- --start 1 --end 90 --output /tmp/frames/
Voiceover lines are intentionally metadata only; this render has no audio.
"""
import bpy
import math
import sys
import argparse

W,H,FPS=1080,1920,30
START,END=1,450
BG=(.03,.03,.05,1); BLUE=(.10,.65,1.,1); PINK=(1.,.25,.45,1); GREEN=(.20,.90,.45,1)
DARK=(.08,.08,.10,1); WHITE=(1.,1.,1.,1); MUTED=(.50,.57,.66,1)
VOICEOVER_LINES={
 'scene_1':'Stop writing boring Python scripts by hand.',
 'scene_2':'Just describe the task.',
 'scene_3':'The agent writes it, tests it, and runs it.',
 'scene_4':'Rename files, clean data, export reports, done in seconds.',
 'scene_5':'Try your first automation free today.',
}

def clean():
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)

def mat(name,color,strength=1):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;n.clear();o=n.new('ShaderNodeOutputMaterial');e=n.new('ShaderNodeEmission');e.inputs['Color'].default_value=color;e.inputs['Strength'].default_value=strength;m.node_tree.links.new(e.outputs[0],o.inputs['Surface']);return m

def show(obj,start,end):
 # Exact shot visibility: later geometry must never appear in earlier shots.
 obj.hide_render=True;obj.keyframe_insert(data_path='hide_render',frame=1)
 obj.hide_render=False;obj.keyframe_insert(data_path='hide_render',frame=max(1,start))
 if end<=450:
  obj.hide_render=True;obj.keyframe_insert(data_path='hide_render',frame=end)
 if obj.animation_data and obj.animation_data.action:
  for fc in obj.animation_data.action.fcurves:
   for kp in fc.keyframe_points:kp.interpolation='CONSTANT'

def panel(name,x,z,w,h,material,start,end,y=0):
 mesh=bpy.data.meshes.new(name);mesh.from_pydata([(-w/2,0,-h/2),(w/2,0,-h/2),(w/2,0,h/2),(-w/2,0,h/2)],[],[(0,1,2,3)]);mesh.update()
 obj=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(obj);obj.location=(x,y,z);obj.data.materials.append(material);show(obj,start,end);return obj

def text(name,body,x,z,size,material,start,end,align='CENTER',y=-.15):
 curve=bpy.data.curves.new(name,'FONT');curve.body=body;curve.size=size;curve.align_x=align;curve.align_y='CENTER';curve.space_line=1.15
 obj=bpy.data.objects.new(name,curve);bpy.context.scene.collection.objects.link(obj);obj.location=(x,y,z);obj.rotation_euler=(math.pi/2,0,0);obj.data.materials.append(material);show(obj,start,end);return obj

def circle(name,x,z,r,material,start,end,y=-.05):
 mesh=bpy.data.meshes.new(name);n=64;vs=[(r*math.cos(i*2*math.pi/n),0,r*math.sin(i*2*math.pi/n)) for i in range(n)];mesh.from_pydata(vs,[],[tuple(range(n))]);mesh.update();obj=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(obj);obj.location=(x,y,z);obj.data.materials.append(material);show(obj,start,end);return obj

def accent_in(obj,start):
 obj.scale=(.001,)*3;obj.keyframe_insert(data_path='scale',frame=max(1,start))
 obj.scale=(1.,)*3;obj.keyframe_insert(data_path='scale',frame=start+10)

def build():
 clean();s=bpy.context.scene;s.render.resolution_x=W;s.render.resolution_y=H;s.render.resolution_percentage=100;s.render.fps=FPS;s.frame_start=START;s.frame_end=END
 try:s.render.engine='BLENDER_EEVEE_NEXT'
 except (TypeError,ValueError):s.render.engine='BLENDER_EEVEE'
 if hasattr(s,'eevee'):s.eevee.taa_render_samples=8
 s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.film_transparent=False
 try:s.view_settings.view_transform='Standard';s.view_settings.look='Medium High Contrast'
 except (TypeError,ValueError):pass
 world=bpy.data.worlds.new('World_Background');world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=BG;s.world=world
 cam=bpy.data.cameras.new('MainCamera');cam.type='ORTHO';cam.ortho_scale=15.8;obj=bpy.data.objects.new('MainCamera',cam);s.collection.objects.link(obj);obj.location=(0,-20,0);obj.rotation_euler=(math.pi/2,0,0);s.camera=obj
 for f,v in ((1,16),(75,14.8),(360,14.8),(450,16)):
  cam.ortho_scale=v;cam.keyframe_insert(data_path='ortho_scale',frame=f)
 blue=mat('Primary',BLUE);pink=mat('Accent',PINK);green=mat('Success',GREEN);dark=mat('Panel',DARK);white=mat('Text',WHITE);muted=mat('Muted',MUTED)
 # 1. Hook: terminal panels, explicitly limited to the first shot.
 for i,z in enumerate((2.4,.8,-.8)):
  panel('TerminalPanel_'+str(i),0,z,6.5,1.20,dark,1,75)
  panel('TerminalStripe_'+str(i),-2.9,z,.1,.85,pink,1,75,y=-.08)
  text('TerminalCode_'+str(i),('import os','for file in files:','    # repeat again')[i],-2.6,z,.39,muted,1,75,'LEFT')
 text('Caption_Scene1','Manual Python = slow',0,-5.4,.65,pink,1,75)
 # 2. Plain-language prompt and AI symbol.
 a=circle('AI_Icon',0,2.7,.85,blue,75,165);accent_in(a,75)
 text('AI_Text','AI',0,2.7,.58,white,75,165,y=-.19)
 panel('PromptPanel',0,.25,6.7,1.55,dark,75,165)
 text('Prompt_Scene2','Rename 500 files\nand export CSV',0,.25,.47,white,75,165)
 text('Caption_Scene2','Describe it in\nplain English',0,-5.1,.63,blue,75,165)
 # 3. Vertical layout preserves the 9:16 frame and the three-stage sequence.
 for i,label in enumerate(('Write','Test','Run')):
  f=165+i*22;z=2.5-i*2.0
  card=panel('Card_'+label,0,z,4.4,1.32,dark,f,270);accent_in(card,f)
  panel('CardAccent_'+label,-1.95,z,.12,.96,blue if i<2 else green,f,270,y=-.08)
  text('CardLabel_'+label,label,0,z,.62,white,f,270)
 text('Caption_Scene3','Write -> Test -> Run',0,-5.25,.67,green,165,270)
 # 4. Result panels and timer (shown only during result).
 for x,label in ((-1.7,'FILES'),(1.7,'CSV')):
  panel(label+'_Panel',x,1.2,2.9,3.9,dark,270,360)
  text(label+'_Heading',label,x,2.45,.48,white,270,360)
  for j in range(4):panel(label+'_line_'+str(j),x,1.6-j*.55,2.0,.06,muted,270,360,y=-.08)
  text(label+'_check','DONE',x,-.2,.36,green,270,360)
 text('Timer_Scene4','00:08',0,-2.1,.75,green,270,360)
 text('Caption_Scene4','Done in seconds',0,-5.25,.68,green,270,360)
 # 5. Placeholder branding and CTA are exactly the user's supplied copy.
 logo=circle('Logo_Placeholder',0,2.8,.95,blue,360,451);accent_in(logo,360)
 text('LogoText_Scene5','[PRODUCT NAME]',0,.75,.60,white,360,451)
 panel('Button_Scene5',0,-1.1,4.1,1.05,pink,370,451)
 text('Button_Label','Start free',0,-1.1,.55,white,370,451)
 text('Caption_Scene5','Try your first\nautomation free ->',0,-5.1,.60,blue,360,451)
 return s

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--start',type=int,default=1);ap.add_argument('--end',type=int,default=450);ap.add_argument('--output',required=True);args=ap.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
 s=build();s.frame_start=args.start;s.frame_end=args.end;s.render.filepath=args.output;bpy.ops.render.render(animation=True)
if __name__=='__main__':main()
