"""Rigged human fight: CMU motion capture blended with action clips; Blender 3.4+."""
import bpy,math,os,sys,argparse
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=32;s.eevee.use_gtao=True;s.eevee.gtao_distance=3;s.eevee.gtao_factor=1.3;s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.render.fps=24;s.frame_start=1;s.frame_end=360;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
s.world.color=(.08,.08,.08)
def mat(name,color,rough=.55,metal=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;return m
def cube(name,loc,scale,m):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m);return o
floor=mat('Floor',(.07,.085,.09),.4,.15);wall=mat('Wall',(.035,.05,.065),.75);accent=mat('Columns',(.08,.09,.11),.5)
cube('Floor',(0,0,-.14),(30,30,.25),floor);cube('Rear wall',(0,5,3),(26,.2,6),wall)
for x in (-6,-3,0,3,6):cube('Wall buttress',(x,4.8,2.5),(.16,.35,5),accent)
def area(name,loc,target,power,color,size):
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.color=color;o.data.size=size;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
area('Warm softbox',(-4,-4,5),(0,0,1),1000,(1,.76,.56),5);area('Cool softbox',(4,-1,5),(0,0,1),1100,(.6,.75,1),5);area('Back rim',(0,3,4),(0,0,1),1500,(1,.75,.5),3)
# Attacks begin on these frames. Defender flinches as the punch extends.
events=[(56,0),(127,1),(200,0),(274,1)]
def fighter(path,side,offset):
 before=set(bpy.data.objects);actions=set(bpy.data.actions)
 bpy.ops.import_scene.gltf(filepath=os.path.abspath(path));new=set(bpy.data.objects)-before
 arm=next(o for o in new if o.type=='ARMATURE');newactions=list(set(bpy.data.actions)-actions)
 def action(prefix):return next(a for a in newactions if a.name.startswith(prefix+'_Armature'))
 box=action('Boxing performance');punch=action('Punch');hit=action('Hit from front')
 # The import's motion is on the armature; cache poses, then bake the edited performance.
 bones=list(arm.pose.bones);cache={}
 for kind,act,frames in [('box',box,range(0,360)),('punch',punch,range(0,22)),('hit',hit,range(0,20))]:
  arm.animation_data.action=act;poses=[]
  for f in frames:
   s.frame_set(f)
   poses.append([(b.location.copy(),b.rotation_quaternion.copy(),b.scale.copy()) for b in bones])
  cache[kind]=poses
 arm.animation_data.action=None
 baked=bpy.data.actions.new('Choreographed fighter '+str(side));arm.animation_data.action=baked
 def smoothstep(v):
  v=max(0,min(1,v));return v*v*(3-2*v)
 for f in range(1,361):
  base=cache['box'][(f+offset)%360];other=None;w=0
  for start,who in events:
   if who==side:
    t=f-start
    if 0<=t<22:other=cache['punch'][t];w=smoothstep(t/5)*smoothstep((22-t)/6)
   else:
    t=f-(start+8)
    if 0<=t<20:other=cache['hit'][t];w=smoothstep((t+1)/4)*smoothstep((20-t)/7)
  for i,b in enumerate(bones):
   loc,rot,sc=base[i]
   if other:
    ol,orr,osc=other[i];loc=loc.lerp(ol,w);rot=rot.slerp(orr,w);sc=sc.lerp(osc,w)
   b.rotation_mode='QUATERNION';b.location=loc;b.rotation_quaternion=rot;b.scale=sc
   b.keyframe_insert(data_path='location',frame=f,group=b.name);b.keyframe_insert(data_path='rotation_quaternion',frame=f,group=b.name)
 root=bpy.data.objects.new('Fighter placement '+str(side),None);s.collection.objects.link(root)
 for obj in new:
  if obj.parent is None:obj.parent=root
 root.rotation_euler.z=math.pi/2 if side==0 else -math.pi/2
 root.location=((-0.65 if side==0 else .65),0,-.07)
 # Maintain approximate central spacing by cancelling the recorded hip drift (but not its height).
 for f in range(1,361):
  s.frame_set(f);bpy.context.view_layer.update();hip=arm.matrix_world@arm.pose.bones['Hips'].head
  desired=-.65 if side==0 else .65
  root.location.x += desired-hip.x;root.location.y -= hip.y
  root.keyframe_insert(data_path='location',frame=f)
 return root,arm
fighter('fight-film/humans/fighter_amber.glb',0,0);fighter('fight-film/humans/fighter_blue.glb',1,90)
bpy.ops.object.camera_add(location=(0,-6.7,2.35));cam=bpy.context.object;s.camera=cam;cam.data.lens=44
focus=bpy.data.objects.new('Camera target',None);s.collection.objects.link(focus);focus.location=(0,0,1.0)
c=cam.constraints.new('TRACK_TO');c.target=focus;c.track_axis='TRACK_NEGATIVE_Z';c.up_axis='UP_Y'
for f,pos in [(1,(-.3,-6.9,2.2)),(65,(.2,-6.3,2.25)),(135,(.65,-6.6,2.0)),(205,(-.45,-6.15,2.3)),(280,(.5,-6.4,2.05)),(360,(0,-6.8,2.25))]:
 cam.location=pos;cam.keyframe_insert(data_path='location',frame=f)
for fc in cam.animation_data.action.fcurves:
 for p in fc.keyframe_points:p.handle_left_type=p.handle_right_type='AUTO_CLAMPED'
parser=argparse.ArgumentParser();parser.add_argument('--preview',action='store_true');parser.add_argument('--output',default='fight-film/human-fight/stage.blend');a=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
if a.preview:
 s.render.resolution_percentage=50;os.makedirs('fight-film/human-fight/preview',exist_ok=True)
 for f in (1,50,62,66,72,125,137,147,197,210,220,273,284,295,345):
  s.frame_set(f);s.render.filepath=f'fight-film/human-fight/preview/{f:04d}.png';bpy.ops.render.render(write_still=True)
else:bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(a.output))
