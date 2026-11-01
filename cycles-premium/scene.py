"""User-provided Cycles animation, prepared for parallel frame rendering.
Camera tracks the scene, text faces the moving camera, and lights aim at the subject.
Original 1920x1080, 24 fps, 360 frames, and 64 Cycles samples are retained.
"""
import bpy, math, sys, argparse
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=64
s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.render.fps=24;s.frame_start=1;s.frame_end=360
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
# Ubuntu runner Blender lacks OpenImageDenoise; render original 64 samples without denoising.
s.cycles.use_denoising=False
if s.world is None:s.world=bpy.data.worlds.new('World')
s.world.use_nodes=True;bg=s.world.node_tree.nodes['Background'];bg.inputs[0].default_value=(.01,.012,.02,1);bg.inputs[1].default_value=.4

def mat(name,col,metal=.9,rough=.15,emit=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*col,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if 'Emission Color' in p.inputs:p.inputs['Emission Color'].default_value=(*col,1);p.inputs['Emission Strength'].default_value=emit
 elif 'Emission' in p.inputs:p.inputs['Emission'].default_value=(*col,1);p.inputs['Emission Strength'].default_value=emit
 return m
gold=mat('Gold',(.95,.72,.22),1,.12);neon=mat('Neon',(.2,.7,1),0,.2,8);dark=mat('Dark',(.04,.04,.05),.3,.4)
bpy.ops.mesh.primitive_plane_add(size=20,location=(0,0,-1.2));bpy.context.object.data.materials.append(dark)
bpy.ops.mesh.primitive_torus_add(major_radius=1.4,minor_radius=.28,location=(0,0,.2));tor=bpy.context.object;tor.name='Gold torus';tor.data.materials.append(gold);bpy.ops.object.shade_smooth();tor.keyframe_insert('rotation_euler',frame=1);tor.rotation_euler.z=math.radians(720);tor.keyframe_insert('rotation_euler',frame=360)
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3,radius=.35,location=(2.2,0,.4));ico=bpy.context.object;ico.name='Neon icosphere';ico.data.materials.append(neon);ico.keyframe_insert('location',frame=1);ico.location=(-2.2,0,.6);ico.keyframe_insert('location',frame=180);ico.location=(2.,.4,.3);ico.keyframe_insert('location',frame=360)
# Follow the original camera path but point at the action; the first frame in the
# supplied script had a zero rotation and looked straight down away from the scene.
bpy.ops.object.empty_add(type='PLAIN_AXES',location=(0,0,.45));target=bpy.context.object;target.name='Camera target'
bpy.ops.object.camera_add(location=(0,-6.5,2.2));cam=bpy.context.object;s.camera=cam;cam.data.lens=35
for f,loc in [(1,(0,-6.5,2.2)),(120,(4.5,-3.2,1.8)),(240,(-3.8,-4,2.6)),(360,(0,-7.2,1.4))]:cam.location=loc;cam.keyframe_insert('location',frame=f)
track=cam.constraints.new('TRACK_TO');track.target=target;track.track_axis='TRACK_NEGATIVE_Z';track.up_axis='UP_Y'

def txt(body,loc,size=.55,f_in=1,f_full=12,f_out=None):
 bpy.ops.object.text_add(location=loc);o=bpy.context.object;o.name='Title '+body;o.data.body=body;o.data.align_x='CENTER';o.data.extrude=.04;o.data.size=size;o.data.materials.append(neon)
 # Blender text normally lies in XY; make it face the animated camera.
 constraint=o.constraints.new('TRACK_TO');constraint.target=cam;constraint.track_axis='TRACK_Z';constraint.up_axis='UP_Y'
 o.scale=(0,0,0);o.keyframe_insert('scale',frame=f_in);o.scale=(1,1,1);o.keyframe_insert('scale',frame=f_full)
 if f_out:o.keyframe_insert('scale',frame=f_out-8);o.scale=(0,0,0);o.keyframe_insert('scale',frame=f_out)
 return o
txt('PREMIUM',(0,0,1.6),.7,1,18,80);txt('MOTION',(0,0,1.6),.7,85,100,160);txt('3D  ·  TYPE  ·  CAM',(0,0,1.6),.38,165,185,250);txt('RENDER READY',(0,0,1.6),.55,255,280,350)
for name,loc,energy,size,color in [('Warm key',(3,-2,4),400,4,(1,.9,.75)),('Cool fill',(-3,1,3),180,3,(.4,.7,1))]:
 bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.name=name;l.data.energy=energy;l.data.size=size;l.data.color=color;l.rotation_euler=(Vector((0,0,.2))-l.location).to_track_quat('-Z','Y').to_euler()
for ob in bpy.data.objects:
 if ob.animation_data and ob.animation_data.action:
  try:
   for fc in ob.animation_data.action.fcurves:
    for k in fc.keyframe_points:k.interpolation='BEZIER';k.handle_left_type=k.handle_right_type='AUTO_CLAMPED'
  except AttributeError:pass
parser=argparse.ArgumentParser();parser.add_argument('--start',type=int,default=1);parser.add_argument('--end',type=int,default=360);parser.add_argument('--output',required=True)
a=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []);s.frame_start=a.start;s.frame_end=a.end;s.render.filepath=a.output;bpy.ops.render.render(animation=True)
