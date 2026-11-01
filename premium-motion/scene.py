"""User's NOVA premium motion graphics, adapted only for frame-chunk rendering.
Usage: blender -b --python scene.py -- --start 1 --end 90 --output /path/frames/
"""
import bpy
import math
import argparse
import sys
from mathutils import Vector, Matrix

FPS=30; END_FRAME=450
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.frame_start=1;scene.frame_end=END_FRAME;scene.render.fps=FPS
scene.render.resolution_x=1920;scene.render.resolution_y=1080;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB'
try:scene.render.engine='BLENDER_EEVEE_NEXT'
except (TypeError,ValueError):scene.render.engine='BLENDER_EEVEE'
# Limit software-render samples for GitHub-hosted CPU runners.
if hasattr(scene,'eevee'):scene.eevee.taa_render_samples=8
try:scene.view_settings.look='AgX - Medium High Contrast'
except (TypeError,ValueError):pass
scene.use_nodes=True;nodes=scene.node_tree.nodes;links=scene.node_tree.links;nodes.clear()
rl=nodes.new('CompositorNodeRLayers');glare=nodes.new('CompositorNodeGlare');glare.glare_type='FOG_GLOW';glare.quality='HIGH';glare.threshold=.7;glare.size=7
lens=nodes.new('CompositorNodeLensdist');lens.inputs['Distortion'].default_value=.008;lens.inputs['Dispersion'].default_value=.012
comp=nodes.new('CompositorNodeComposite');links.new(rl.outputs['Image'],glare.inputs['Image']);links.new(glare.outputs['Image'],lens.inputs['Image']);links.new(lens.outputs['Image'],comp.inputs['Image'])
if scene.world is None:scene.world=bpy.data.worlds.new('World')
scene.world.color=(.003,.005,.012);scene.world.use_nodes=True;world_bg=scene.world.node_tree.nodes.get('Background');world_bg.inputs['Color'].default_value=(.002,.004,.012,1);world_bg.inputs['Strength'].default_value=.18

def emission_mat(name,color,strength=3):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;n.clear();o=n.new('ShaderNodeOutputMaterial');e=n.new('ShaderNodeEmission');e.inputs['Color'].default_value=color;e.inputs['Strength'].default_value=strength;m.node_tree.links.new(e.outputs['Emission'],o.inputs['Surface']);return m

def metal_mat(name,color,metallic=.9,roughness=.2):
 m=bpy.data.materials.new(name);m.use_nodes=True;bsdf=m.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Base Color'].default_value=color;bsdf.inputs['Metallic'].default_value=metallic;bsdf.inputs['Roughness'].default_value=roughness;return m
BLACK=metal_mat('Obsidian',(.006,.009,.02,1),.75,.24);SILVER=metal_mat('Chrome',(.17,.22,.32,1),.95,.12)
CYAN=emission_mat('Electric Cyan',(.01,.65,1.,1),4);PINK=emission_mat('Neon Pink',(1.,.025,.30,1),4);WHITE=emission_mat('Clean White',(.92,.97,1.,1),2.6)
DIM_CYAN=emission_mat('Dim Grid Cyan',(.01,.20,.34,1),.5);DARK_PANEL=metal_mat('Transition Black',(.004,.006,.015,1),.65,.18)

def smooth(obj):
 if obj.animation_data and obj.animation_data.action:
  try:
   for curve in obj.animation_data.action.fcurves:
    for point in curve.keyframe_points:point.interpolation='BEZIER';point.handle_left_type='AUTO_CLAMPED';point.handle_right_type='AUTO_CLAMPED'
  except AttributeError:pass

def key(obj,frame,loc=None,scale=None,rot=None):
 for path,val in [('location',loc),('scale',scale),('rotation_euler',rot)]:
  if val is not None:setattr(obj,path,val);obj.keyframe_insert(data_path=path,frame=frame)

def look(obj,target):obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()

def cube(name,loc,scale,material,bevel=.08):
 bpy.ops.mesh.primitive_cube_add(location=loc);o=bpy.context.object;o.name=name;o.scale=scale;o.data.materials.append(material)
 if bevel>0:m=o.modifiers.new('Soft premium edges','BEVEL');m.width=bevel;m.segments=4
 return o

def text(name,value,loc,size,material,extrude=.03):
 bpy.ops.object.text_add(location=loc);o=bpy.context.object;o.name=name;o.data.body=value;o.data.align_x='CENTER';o.data.align_y='CENTER';o.data.size=size;o.data.extrude=extrude;o.data.bevel_depth=.008;o.data.bevel_resolution=3;o.data.materials.append(material);return o

def pop(o,start,arrive,leave,rise=.7):
 base=o.location.copy();key(o,start,loc=(base.x,base.y-rise,base.z),scale=(.001,)*3);key(o,arrive,loc=base,scale=(1,)*3);key(o,leave,loc=base,scale=(1,)*3);key(o,leave+9,loc=(base.x,base.y+rise,base.z),scale=(.001,)*3);smooth(o)

bpy.ops.mesh.primitive_plane_add(size=60,location=(0,0,-1.15));floor=bpy.context.object;floor.name='Dark reflective background';floor.data.materials.append(BLACK)
grid=bpy.data.objects.new('Moving background grid',None);bpy.context.collection.objects.link(grid)
for i in range(-10,11):
 a=cube('Grid X',(i,0,-1.05),(.012,13,.008),DIM_CYAN,0);b=cube('Grid Y',(0,i,-1.05),(13,.012,.008),DIM_CYAN,0);a.parent=grid;b.parent=grid
key(grid,1,loc=(0,-1.2,0),rot=(0,0,0));key(grid,END_FRAME,loc=(0,1.2,0),rot=(0,0,math.radians(3)));smooth(grid)
bpy.ops.object.camera_add(location=(0,-.3,14));camera=bpy.context.object;camera.data.lens=30;camera.data.dof.use_dof=False;scene.camera=camera
for frame,loc in [(1,(0,-.4,14.5)),(90,(.5,-.6,13.5)),(180,(-.7,.3,13.)),(270,(1.3,-1.1,12.2)),(360,(-.8,.4,13.4)),(450,(0,-.2,14.))]:
 camera.location=loc
 # Stable world-up framing prevents a near-overhead camera from rolling wildly.
 forward=(Vector((0,0,0))-camera.location).normalized();right=forward.cross(Vector((0,1,0))).normalized();up=right.cross(forward).normalized();camera.rotation_euler=Matrix((right,up,-forward)).transposed().to_quaternion().to_euler()
 camera.keyframe_insert(data_path='location',frame=frame);camera.keyframe_insert(data_path='rotation_euler',frame=frame)
smooth(camera)
for name,loc,energy,color,size in [('Cyan key light',(5,-4,7),1300,(.15,.75,1),5),('Pink rim light',(-5,2,5),1000,(1,.04,.25),4),('Soft white light',(0,4,8),900,(.55,.7,1),5)]:
 bpy.ops.object.light_add(type='AREA',location=loc);light=bpy.context.object;light.name=name;light.data.energy=energy;light.data.color=color;light.data.shape='DISK';light.data.size=size;look(light,(0,0,0))

def transition(frame,accent):
 for i in range(13):
  x=-12+i*2;slat=cube('Diagonal transition slat',(x,0,7),(.01,10,.12),accent if i%3==0 else DARK_PANEL,.05);slat.rotation_euler[2]=math.radians(-13)
  for f,s in [(frame+i,.01),(frame+9+i,1.15),(frame+19+i,1.15),(frame+28+i,.01)]:key(slat,f,scale=(s,10,.12))
  smooth(slat)
  # Do not leave tiny strips visible throughout unrelated scenes.
  slat.hide_render=True;slat.keyframe_insert(data_path='hide_render',frame=1)
  slat.hide_render=False;slat.keyframe_insert(data_path='hide_render',frame=frame+i)
  slat.hide_render=True;slat.keyframe_insert(data_path='hide_render',frame=frame+29+i)
transition(92,CYAN);transition(220,PINK);transition(340,CYAN)
for i,char in enumerate('NOVA'):
 o=text('Logo '+char,char,(-3.3+i*2.2,.4,.15),2.65,WHITE,.05);pop(o,7+i*4,20+i*4,76,.9)
tag=text('Intro tag','MOTION / DESIGN / FUTURE',(0,-2.15,.12),.38,CYAN);pop(tag,27,38,78,.4)
line=cube('Intro underline',(0,-1.25,.12),(.001,.035,.025),PINK,.02)
for f,v in [(25,.001),(41,4.7),(75,4.7),(84,.001)]:key(line,f,scale=(v,.035,.025))
smooth(line)
for name,body,loc,size,material,start,arrive,leave,rise in [
 ('Kinetic small heading',"WE DON'T",(0,3,.15),.55,PINK,108,120,200,.45),('FOLLOW','FOLLOW',(0,.9,.16),2.35,WHITE,118,134,202,1),('TRENDS','TRENDS.',(0,-1.45,.16),2.25,CYAN,142,160,204,1),('Kinetic caption','WE CREATE THE VISUAL LANGUAGE.',(0,-3.35,.15),.32,WHITE,168,180,205,.35)]:
 o=text(name,body,loc,size,material,.04 if name in ('FOLLOW','TRENDS') else .03);pop(o,start,arrive,leave,rise)
for i,x in enumerate([-5.4,5.4]):
 o=cube('Kinetic accent block',(x,.3,-.3),(.22,2.7,.12),PINK if i==0 else CYAN,.08)
 for f,loc,sc in [(115,(x,-4.5,-.3),(.22,.001,.12)),(140,(x,.3,-.3),(.22,2.7,.12)),(200,(x,.3,-.3),(.22,2.7,.12)),(214,(x,4.5,-.3),(.22,.001,.12))]:key(o,f,loc=loc,scale=sc)
 smooth(o)
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=5,radius=1.45,location=(0,0,.25));orb=bpy.context.object;orb.name='Chrome hero sphere';orb.data.materials.append(SILVER);bpy.ops.object.shade_smooth()
key(orb,232,scale=(.001,)*3);key(orb,255,scale=(1,)*3,rot=(0,0,0));key(orb,335,scale=(1,)*3,rot=tuple(math.radians(v) for v in (260,130,360)));key(orb,347,scale=(.001,)*3);smooth(orb)
for i,radius in enumerate([2.25,2.85,3.55]):
 bpy.ops.mesh.primitive_torus_add(major_radius=radius,minor_radius=.045 if i!=1 else .07,major_segments=96,minor_segments=16,location=(0,0,.15));ring=bpy.context.object;ring.name='Orbit ring';ring.data.materials.append(CYAN if i!=1 else PINK)
 r1=(math.radians(i*24),math.radians(i*17),0);r2=tuple(math.radians(v) for v in (300+i*30,150+i*20,360+i*80))
 for f,sc,rot in [(235+i*3,(.001,)*3,r1),(258+i*3,(1,)*3,r1),(336,(1,)*3,r2),(348,(.001,)*3,r2)]:key(ring,f,scale=sc,rot=rot)
 smooth(ring)
for name,value,loc,size,material,start,arrive,leave,rise in [('Object title','DESIGNED',(0,3.35,.15),.70,WHITE,250,264,329,.45),('Object subtitle','FOR THE NEXT DIMENSION',(0,-3.35,.15),.38,CYAN,262,276,328,.35)]:o=text(name,value,loc,size,material);pop(o,start,arrive,leave,rise)
for i in range(10):
 a=(i/10)*math.tau;x=math.cos(a)*5;y=math.sin(a)*3.2;o=cube('Floating chrome fragment',(x,y,.2),(.18,.18,.18),SILVER,.06);r1=(0,0,a);r2=(math.radians(180),math.radians(120),a+math.radians(250))
 for f,sc,rot in [(242,(.001,)*3,r1),(265,(.18,)*3,r1),(334,(.18,)*3,r2),(347,(.001,)*3,r2)]:key(o,f,scale=sc,rot=rot)
 smooth(o)
for name,value,loc,size,material,start,arrive,leave,rise in [('Final top label','NOVA STUDIO PRESENTS',(0,3.2,.18),.42,PINK,360,382,442,.4),('MOVE','MOVE',(0,.9,.20),2.75,WHITE,370,392,443,.9),('BEYOND','BEYOND.',(0,-1.45,.20),2.20,CYAN,382,404,444,.9),('Website','YOURBRAND.COM',(0,-3.55,.18),.30,WHITE,408,420,446,.25)]:o=text(name,value,loc,size,material,.05 if name in ('MOVE','BEYOND') else .03);pop(o,start,arrive,leave,rise)
line=cube('Final underline',(0,-2.65,.18),(.001,.045,.03),PINK,.02)
for f,v in [(400,.001),(418,5.2),(447,5.2)]:key(line,f,scale=(v,.045,.03))
smooth(line)
try:scene.render.use_motion_blur=True
except Exception:pass

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--start',type=int,default=1);parser.add_argument('--end',type=int,default=450);parser.add_argument('--output',required=True)
 args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []);scene.frame_start=args.start;scene.frame_end=args.end;scene.render.filepath=args.output;scene.frame_set(args.start);bpy.ops.render.render(animation=True)
if __name__=='__main__':main()
