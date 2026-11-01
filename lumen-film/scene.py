"""LUMEN: an original 15-second cinematic Blender motion piece.
Render chunks: blender -b --python scene.py -- --start 1 --end 30 --output /tmp/frames/
"""
import bpy,math,random,sys,argparse
from mathutils import Vector
random.seed(31)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.render.fps=24;s.frame_start=1;s.frame_end=360
try:s.render.engine='BLENDER_EEVEE_NEXT'
except (TypeError,ValueError):s.render.engine='BLENDER_EEVEE'
if hasattr(s,'eevee'):s.eevee.taa_render_samples=24
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
try:s.view_settings.view_transform='AgX'
except (TypeError,ValueError):pass
try:s.view_settings.look='AgX - Medium High Contrast'
except (TypeError,ValueError):pass
world=bpy.data.worlds.new('Midnight');world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.004,.009,.022,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.18;s.world=world
s.use_nodes=True;n=s.node_tree.nodes;n.clear();r=n.new('CompositorNodeRLayers');g=n.new('CompositorNodeGlare');g.glare_type='FOG_GLOW';g.quality='HIGH';g.threshold=1.3;g.size=7;o=n.new('CompositorNodeComposite');s.node_tree.links.new(r.outputs['Image'],g.inputs['Image']);s.node_tree.links.new(g.outputs['Image'],o.inputs['Image'])

def metal(name,color,metallic=.85,rough=.22):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metallic;p.inputs['Roughness'].default_value=rough;return m

def emit(name,color,strength):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;n.clear();o=n.new('ShaderNodeOutputMaterial');e=n.new('ShaderNodeEmission');e.inputs['Color'].default_value=(*color,1);e.inputs['Strength'].default_value=strength;m.node_tree.links.new(e.outputs[0],o.inputs['Surface']);return m
ink=metal('Black ceramic',(.012,.026,.043),.7,.23);titanium=metal('Champagne titanium',(.62,.41,.18),.9,.2);silver=metal('Brushed silver',(.3,.42,.49),.95,.24)
cyan=emit('Aurora cyan',(.025,.56,.70),2.8);warm=emit('Warm champagne',(.96,.52,.17),3);white=emit('Warm ivory type',(1,.91,.73),2.3)

def smooth(obj):
 if obj.animation_data and obj.animation_data.action:
  try:
   for f in obj.animation_data.action.fcurves:
    for k in f.keyframe_points:k.interpolation='BEZIER';k.handle_left_type=k.handle_right_type='AUTO_CLAMPED'
  except AttributeError:pass

def keys(o,frame,loc=None,rot=None,scale=None):
 for path,v in [('location',loc),('rotation_euler',rot),('scale',scale)]:
  if v is not None:setattr(o,path,v);o.keyframe_insert(data_path=path,frame=frame)

def aim(o,target):o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()

def sphere(name,loc,radius,material,sub=3):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=24,radius=radius,location=loc);o=bpy.context.object;o.name=name;o.data.materials.append(material);bpy.ops.object.shade_smooth();return o

def torus(name,loc,major,minor,material):
 bpy.ops.mesh.primitive_torus_add(major_radius=major,minor_radius=minor,major_segments=128,minor_segments=12,location=loc);o=bpy.context.object;o.name=name;o.data.materials.append(material);bpy.ops.object.shade_smooth();return o

def area(name,loc,target,color,energy,size):
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;o.data.energy=energy;o.data.color=color;o.data.shape='DISK';o.data.size=size;aim(o,target)

# A real three-dimensional stage, with a beveled circular plinth.
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-1.7));bpy.context.object.name='Infinite charcoal stage';bpy.context.object.data.materials.append(ink)
bpy.ops.mesh.primitive_cylinder_add(vertices=96,radius=2.6,depth=.19,location=(0,0,-1.58));plinth=bpy.context.object;plinth.name='Machined pedestal';plinth.data.materials.append(ink);bevel=plinth.modifiers.new('precision bevel','BEVEL');bevel.width=.09;bevel.segments=3;bpy.ops.object.shade_smooth()
torus('Pedestal rim',(0,0,-1.48),2.45,.016,titanium)
torus('Pedestal inner light',(0,0,-1.465),2.13,.012,cyan)
# A solid glowing heart wrapped in a fine metallic geodesic cage.
core=sphere('Luminous core',(0,0,.8),.72,cyan)
keys(core,1,scale=(.02,)*3);keys(core,26,scale=(1.08,)*3);keys(core,50,scale=(1,)*3);smooth(core)
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=.83,location=(0,0,.8));cage=bpy.context.object;cage.name='Sculpted core cage';cage.data.materials.append(titanium);wire=cage.modifiers.new('Delicate wire','WIREFRAME');wire.thickness=.018;wire.use_replace=True
keys(cage,1,scale=(.01,)*3,rot=(0,0,0));keys(cage,35,scale=(1,)*3,rot=(.2,.1,.25));keys(cage,360,scale=(1,)*3,rot=(1.0,.65,4.8));smooth(cage)
# Independent orbital bands, camera and satellites all have real 3D keyframes.
for i,(radius,thickness,material,rot) in enumerate([(1.22,.035,titanium,(.38,.25,0)),(1.58,.025,cyan,(1.13,.18,.7)),(1.96,.035,titanium,(.45,1.15,.3)),(2.28,.018,warm,(1.0,.75,1.1))]):
 ring=torus('Orbit %02d'%i,(0,0,.8),radius,thickness,material);start=8+i*7
 keys(ring,1,scale=(.001,)*3,rot=rot);keys(ring,start,scale=(.001,)*3,rot=rot);keys(ring,start+24,scale=(1,)*3,rot=rot)
 keys(ring,360,scale=(1,)*3,rot=(rot[0]+(1 if i%2 else -1)*2.1,rot[1]+1.5,rot[2]+(1 if i%2 else -1)*5.8));smooth(ring)
for i in range(9):
 angle=2*math.pi*i/9;rad=1.4+(i%3)*.35;anchor=bpy.data.objects.new('Satellite orbit',None);s.collection.objects.link(anchor);anchor.location=(0,0,.8);anchor.rotation_euler=(.5+i*.12,.4,angle)
 keys(anchor,1,rot=(.5+i*.12,.4,angle));keys(anchor,360,rot=(.5+i*.12,.4,angle+(5.8 if i%2 else -5.0)));smooth(anchor)
 dot=sphere('Orbiting glint',(0,0,0),.045 if i%3 else .075,warm if i%2 else cyan);dot.parent=anchor;dot.location=(rad,0,0)
 keys(dot,1,scale=(.001,)*3);keys(dot,35+i*3,scale=(1,)*3);smooth(dot)
area('Cyan softbox',(4,-3,5),(0,0,.5),(.18,.75,1),1200,5)
area('Warm rim',(-4,1,4),(0,0,.7),(1,.55,.22),1450,4)
area('Overhead softbox',(0,4,6),(0,0,.5),(.65,.8,1),1100,5)
# Slight orbit and controlled push; TRACK_TO keeps the centerpiece framed.
bpy.ops.object.empty_add(type='PLAIN_AXES',location=(0,0,.4));target=bpy.context.object;target.name='Camera look target'
bpy.ops.object.camera_add(location=(0,-11.5,4.3));cam=bpy.context.object;cam.name='Cinematic camera';s.camera=cam;cam.data.lens=42
constraint=cam.constraints.new('TRACK_TO');constraint.target=target;constraint.track_axis='TRACK_NEGATIVE_Z';constraint.up_axis='UP_Y'
for f,loc in [(1,(0,-12.8,4.9)),(110,(1.7,-11.4,4.2)),(230,(-1.5,-11.7,3.6)),(360,(0,-13.5,4.5))]:keys(cam,f,loc=loc)
smooth(cam)
# Type is camera-relative, ensuring it remains sharp, aligned and safely framed.
def title(name,body,loc,size,start,full,leave=None):
 cu=bpy.data.curves.new(name,'FONT');cu.body=body;cu.size=size;cu.align_x='CENTER';cu.align_y='CENTER';cu.extrude=.001;obj=bpy.data.objects.new(name,cu);s.collection.objects.link(obj);obj.parent=cam;obj.location=loc;obj.data.materials.append(white)
 keys(obj,1,scale=(.001,)*3);keys(obj,start,scale=(.001,)*3);keys(obj,full,scale=(1,)*3)
 if leave:keys(obj,leave-10,scale=(1,)*3);keys(obj,leave,scale=(.001,)*3)
 smooth(obj);return obj
title('Opening line','A SPARK IN THE DARK',(0,1.38,-6),.17,8,28,100)
title('Hero title','L U M E N',(0,-1.12,-6),.48,257,284)
title('Closing line','A LITTLE LIGHT GOES A LONG WAY',(0,-1.50,-6),.145,280,304)
parser=argparse.ArgumentParser();parser.add_argument('--start',type=int,default=1);parser.add_argument('--end',type=int,default=360);parser.add_argument('--output',required=True)
a=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []);s.frame_start=a.start;s.frame_end=a.end;s.render.filepath=a.output;bpy.ops.render.render(animation=True)
