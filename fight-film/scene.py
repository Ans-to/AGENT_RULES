"""CONTACT: original, joint-animated two-character 15-second fight.
Each limb is a mesh constrained between independently animated joints.
Renderable in chunks with Blender: --start N --end N --output DIR.
"""
import bpy,math,random,sys,argparse
from mathutils import Vector
random.seed(431)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.render.fps=24;s.frame_start=1;s.frame_end=360
try:s.render.engine='BLENDER_EEVEE_NEXT'
except (TypeError,ValueError):s.render.engine='BLENDER_EEVEE'
if hasattr(s,'eevee'):s.eevee.taa_render_samples=32
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
try:s.view_settings.view_transform='AgX'
except (TypeError,ValueError):pass
try:s.view_settings.look='AgX - Medium High Contrast'
except (TypeError,ValueError):pass
world=bpy.data.worlds.new('Night studio');world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.006,.009,.015,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.28;s.world=world
s.use_nodes=True;n=s.node_tree.nodes;n.clear();r=n.new('CompositorNodeRLayers');g=n.new('CompositorNodeGlare');g.glare_type='FOG_GLOW';g.threshold=2.4;g.quality='HIGH';g.size=6;o=n.new('CompositorNodeComposite');s.node_tree.links.new(r.outputs['Image'],g.inputs['Image']);s.node_tree.links.new(g.outputs['Image'],o.inputs['Image'])
def mat(name,col,metallic=0,rough=.4):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*col,1);p.inputs['Metallic'].default_value=metallic;p.inputs['Roughness'].default_value=rough;return m
def emit(name,col,strength):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;n.clear();e=n.new('ShaderNodeEmission');e.inputs['Color'].default_value=(*col,1);e.inputs['Strength'].default_value=strength;o=n.new('ShaderNodeOutputMaterial');m.node_tree.links.new(e.outputs[0],o.inputs['Surface']);return m
bronze=mat('Warm fighter jacket',(.31,.085,.035),.15,.38);blue=mat('Cool fighter jacket',(.022,.16,.23),.16,.38);pants=mat('Graphite trousers',(.025,.032,.041),.05,.52);shoes=mat('Boots',(.023,.02,.019),.1,.34);skin=mat('Skin',(.44,.24,.15),0,.48);skin2=mat('Skin two',(.30,.16,.12),0,.50);hair=mat('Hair',(.025,.018,.016),0,.56);eye=mat('Eyes',(.009,.008,.008),0,.5);gold=mat('Stage trim',(.46,.27,.10),.75,.3);floor=mat('Stage stone',(.035,.045,.055),.38,.33);wall=mat('Backdrop',(.012,.017,.024),.25,.6);spark=emit('Impact spark',(1,.69,.32),4)
def sphere(name,loc,scale,material):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=16,radius=1,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;o.data.materials.append(material);bpy.ops.object.shade_smooth();return o
def cylinder(name,loc,radius,depth,material):
 bpy.ops.mesh.primitive_cylinder_add(vertices=96,radius=radius,depth=depth,location=loc);o=bpy.context.object;o.name=name;o.data.materials.append(material);b=o.modifiers.new('Soft bevel','BEVEL');b.width=.06;b.segments=3;bpy.ops.object.shade_smooth();return o
def cube(name,loc,scale,material,bevel=.05):
 bpy.ops.mesh.primitive_cube_add(location=loc);o=bpy.context.object;o.name=name;o.scale=scale;o.data.materials.append(material)
 if bevel:b=o.modifiers.new('Machined edges','BEVEL');b.width=bevel;b.segments=3
 return o
def key(o,frame,path,value):setattr(o,path,value);o.keyframe_insert(data_path=path,frame=frame)
def smooth(o):
 if o.animation_data and o.animation_data.action:
  try:
   for fc in o.animation_data.action.fcurves:
    for p in fc.keyframe_points:p.interpolation='BEZIER';p.handle_left_type=p.handle_right_type='AUTO_CLAMPED'
  except AttributeError:pass
def empty(name,loc=(0,0,0),parent=None):
 o=bpy.data.objects.new(name,None);s.collection.objects.link(o);o.location=loc
 if parent:o.parent=parent
 return o
def capsule(name,a,b,radius,material):
 # Mesh's local Y extends from 0 to 1. STRETCH_TO joins it to both animated joints.
 bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,radius=1);o=bpy.context.object;o.name=name
 for v in o.data.vertices:
  x,y,z=v.co;v.co=(x*radius,(z+1)*.5,y*radius)
 o.data.materials.append(material);bpy.ops.object.shade_smooth()
 c=o.constraints.new('COPY_LOCATION');c.target=a
 c=o.constraints.new('STRETCH_TO');c.target=b;c.rest_length=1.0;c.volume='NO_VOLUME';return o
def child_sphere(name,joint,scale,material,offset=(0,0,0)):
 o=sphere(name,(0,0,0),scale,material);o.parent=joint;o.location=offset;return o
def area(name,loc,target,color,power,size):
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.color=color;o.data.size=size;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
# Raised physical platform and a subdued architectural background.
cylinder('Circular fighting stage',(0,0,-.22),5.2,.35,floor);cylinder('Stage lower rim',(0,0,-.38),5.25,.06,gold)
for x in (-4.5,-3.1,3.1,4.5):cube('Back pillar',(x,4,2.0),(.15,.28,2.4),wall,.07)
cube('Rear wall',(0,4.7,2),(8,.2,3),wall,.0)
area('Warm key',(-3,-4,5),(0,0,1),(1,.68,.42),900,5);area('Cool fill',(4,-1,5),(0,0,1),(.32,.62,1),1050,5);area('Rim light',(0,3,4),(0,0,1),(1,.85,.58),1200,4)
# Frames: anticipation, contact, recovery, counter, kick, dodge, finishing strike.
frames=[1,35,60,78,94,104,112,130,148,160,171,190,212,228,238,255,270,278,288,310,335,360]
rootA=[-.92,-.87,-.78,-.71,-.64,-.58,-.58,-.70,-.74,-.79,-.82,-.83,-.87,-.90,-.94,-.90,-.77,-.66,-.68,-.79,-.83,-.83]
rootB=[.92,.87,.78,.72,.67,.62,.72,.73,.67,.62,.68,.71,.67,.62,.66,.74,.73,.69,.82,.87,.87,.87]

def base(f):
 return {'hip':(0,0,1.0),'chest':(0,0,1.52),'head':(0,0,1.83),
 'nearShoulder':(0,-.20,1.47),'nearElbow':(f*.22,-.24,1.28),'nearHand':(f*.40,-.25,1.44),
 'farShoulder':(0,.20,1.47),'farElbow':(-f*.16,.23,1.25),'farHand':(f*.20,.22,1.42),
 'nearHip':(0,-.13,.99),'nearKnee':(f*.18,-.14,.52),'nearFoot':(f*.34,-.15,.12),
 'farHip':(0,.13,.99),'farKnee':(-f*.20,.14,.52),'farFoot':(-f*.36,.15,.12)}

def pose(kind,f):
 d=base(f)
 if kind=='windup':d.update(chest=(-f*.07,0,1.46),head=(-f*.09,0,1.77),nearElbow=(-f*.25,-.24,1.37),nearHand=(-f*.37,-.23,1.52),nearKnee=(f*.25,-.14,.50))
 if kind=='punch':d.update(chest=(f*.12,0,1.50),head=(f*.10,0,1.82),nearShoulder=(f*.12,-.2,1.45),nearElbow=(f*.62,-.21,1.54),nearHand=(f*1.03,-.20,1.75),nearKnee=(f*.32,-.14,.51),nearFoot=(f*.43,-.15,.12),farKnee=(-f*.28,.14,.54),farFoot=(-f*.46,.15,.12))
 if kind=='recoil':d.update(chest=(-f*.13,0,1.43),head=(-f*.20,0,1.74),nearShoulder=(-f*.13,-.20,1.40),farShoulder=(-f*.13,.20,1.40),nearElbow=(-f*.1,-.25,1.20),nearHand=(f*.16,-.25,1.31),nearKnee=(-f*.24,-.14,.48))
 if kind=='block':d.update(nearElbow=(f*.23,-.24,1.42),nearHand=(f*.20,-.22,1.72),farElbow=(f*.06,.22,1.36),farHand=(f*.25,.2,1.66),head=(-f*.07,0,1.8))
 if kind=='kick':d.update(chest=(-f*.13,0,1.47),head=(-f*.16,0,1.78),nearShoulder=(-f*.13,-.2,1.42),farShoulder=(-f*.13,.2,1.42),nearKnee=(f*.58,-.14,1.02),nearFoot=(f*1.10,-.14,1.05),farKnee=(-f*.15,.14,.52),farFoot=(-f*.18,.15,.12),nearElbow=(-f*.3,-.24,1.3),nearHand=(-f*.48,-.2,1.38))
 if kind=='duck':d.update(hip=(-f*.06,0,.72),chest=(-f*.22,0,1.09),head=(-f*.3,0,1.35),nearShoulder=(-f*.22,-.2,1.06),farShoulder=(-f*.22,.2,1.06),nearKnee=(f*.24,-.14,.40),farKnee=(-f*.27,.14,.38),nearElbow=(-f*.2,-.2,.9),nearHand=(f*.08,-.24,1.07))
 return d
A=['guard','guard','guard','windup','windup','punch','guard','guard','block','recoil','guard','guard','block','recoil','duck','duck','windup','punch','guard','guard','guard','guard']
B=['guard','guard','guard','guard','guard','recoil','recoil','guard','windup','punch','guard','guard','windup','kick','guard','guard','guard','recoil','recoil','guard','guard','guard']
def fighter(name,f,coat,complexion,roots,kinds):
 root=empty(name+' root'); joints={k:empty(name+' '+k,parent=root) for k in base(f)}
 for idx,frame in enumerate(frames):
  p=pose(kinds[idx],f);key(root,frame,'location',(roots[idx],0,0))
  for k,j in joints.items():key(j,frame,'location',p[k])
 smooth(root)
 for j in joints.values():smooth(j)
 capsule(name+' torso',joints['hip'],joints['chest'],.25,coat);child_sphere(name+' pelvis',joints['hip'],(.22,.20,.16),pants)
 capsule(name+' neck',joints['chest'],joints['head'],.08,complexion)
 for prefix in ('near','far'):
  capsule(name+' upper arm',joints[prefix+'Shoulder'],joints[prefix+'Elbow'],.095,coat)
  capsule(name+' forearm',joints[prefix+'Elbow'],joints[prefix+'Hand'],.08,complexion)
  child_sphere(name+' fist',joints[prefix+'Hand'],(.11,.09,.09),coat)
  capsule(name+' thigh',joints[prefix+'Hip'],joints[prefix+'Knee'],.12,pants)
  capsule(name+' shin',joints[prefix+'Knee'],joints[prefix+'Foot'],.085,pants)
  child_sphere(name+' boot',joints[prefix+'Foot'],(.16,.09,.07),shoes,(f*.06,0,0))
 h=joints['head'];child_sphere(name+' face',h,(.155,.145,.20),complexion);child_sphere(name+' hair',h,(.16,.145,.105),hair,(0,0,.12));child_sphere(name+' nose',h,(.045,.05,.04),complexion,(f*.15,0,.015))
 child_sphere(name+' visible eye',h,(.026,.016,.022),eye,(f*.10,-.12,.055))
 return root
fighter('Ember',1,bronze,skin,rootA,A);fighter('Slate',-1,blue,skin2,rootB,B)
# Short, non-obscuring bursts placed precisely at contact moments.
for hit,x,z in [(104,.55,1.72),(160,-.68,1.72),(228,-.65,1.05),(278,.70,1.72)]:
 for i in range(9):
  a=2*math.pi*i/9;obj=sphere('Impact spark',(x,-.18,z),(.025,.025,.025),spark);key(obj,1,'scale',(.001,)*3);key(obj,hit-1,'scale',(.001,)*3);key(obj,hit,'scale',(.028,)*3);key(obj,hit,'location',(x,-.18,z));key(obj,hit+7,'location',(x+.26*math.cos(a),-.18,z+.26*math.sin(a)));key(obj,hit+8,'scale',(.001,)*3);smooth(obj)
# Continuous camera movement; orientation targets center of action and never cuts.
bpy.ops.object.camera_add(location=(0,-7.2,2.3));cam=bpy.context.object;s.camera=cam;cam.data.lens=46
focus=empty('Camera aim',(0,0,1.0));con=cam.constraints.new('TRACK_TO');con.target=focus;con.track_axis='TRACK_NEGATIVE_Z';con.up_axis='UP_Y'
for f,loc in [(1,(0,-8,2.7)),(70,(-.4,-7,2.45)),(125,(.6,-6.8,2.35)),(190,(-.65,-7.0,2.35)),(250,(.35,-6.9,2.3)),(310,(0,-7.8,2.55)),(360,(0,-8,2.7))]:key(cam,f,'location',loc)
smooth(cam)
parser=argparse.ArgumentParser();parser.add_argument('--start',type=int,default=1);parser.add_argument('--end',type=int,default=360);parser.add_argument('--output',required=True);a=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []);s.frame_start=a.start;s.frame_end=a.end;s.render.filepath=a.output;bpy.ops.render.render(animation=True)
