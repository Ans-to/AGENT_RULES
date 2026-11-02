import bpy,os,json
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=os.path.abspath('fight-film/humans/The_Gangster.glb'))
objects=[]
for o in bpy.data.objects:
 d={'name':o.name,'type':o.type,'location':list(o.location),'scale':list(o.scale),'rotation':list(o.rotation_euler)}
 if o.animation_data: d['action']=o.animation_data.action.name if o.animation_data.action else None;d['tracks']=[{'name':n.name,'mute':n.mute,'strips':[{'name':s.name,'action':s.action.name,'start':s.frame_start,'end':s.frame_end} for s in n.strips]} for n in o.animation_data.nla_tracks]
 if o.type=='ARMATURE':d['bones']=[b.name for b in o.data.bones]
 objects.append(d)
with open('fight-film/human-test/import-info.json','w') as f: json.dump({'objects':objects,'actions':[(a.name,list(a.frame_range)) for a in bpy.data.actions]},f,indent=2)
