import bpy,math,os,json
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=16;s.render.resolution_x=800;s.render.resolution_y=600;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.frame_end=360
s.world.color=(.16,.16,.16)
bpy.ops.import_scene.gltf(filepath=os.path.abspath('fight-film/humans/The_Gangster.glb'))
arm=next(o for o in bpy.data.objects if o.type=='ARMATURE')
root=bpy.data.objects.new('fighter root',None);s.collection.objects.link(root)
for o in list(bpy.context.selected_objects):
 if o.parent is None:o.parent=root
root.rotation_euler.z=math.pi/2
bpy.ops.mesh.primitive_plane_add(size=200);floor=bpy.context.object;floor.location.z=-.02
m=bpy.data.materials.new('floor');m.diffuse_color=(.2,.2,.2,1);floor.data.materials.append(m)
def area(loc,power,size):
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.size=size;o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
area((0,-4,5),800,5);area((2,2,4),500,4)
bpy.ops.object.camera_add(location=(.5,-5.2,2.0));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,1.0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=3.4;s.camera=cam
joints={}
os.makedirs('fight-film/human-test/poses',exist_ok=True)
for frame in range(1,360,24):
 s.frame_set(frame);bpy.context.view_layer.update()
 positions={}
 for b in ['Hips','Head','RightHand','LeftHand','RightFoot','LeftFoot']:
  positions[b]=[round(v,3) for v in arm.matrix_world @ arm.pose.bones[b].head]
 joints[frame]=positions
 s.render.filepath=f'fight-film/human-test/poses/{frame:04}.png';bpy.ops.render.render(write_still=True)
with open('fight-film/human-test/joints.json','w') as f:json.dump(joints,f,indent=2)
