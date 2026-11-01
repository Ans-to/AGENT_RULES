"""THE LONG WAY HOME — original 15s cinematic Blender short.
Four location/shot setups, a modelled spacecraft, terrain and procedural planets.
Frames are rendered independently in GitHub Actions.
"""
import bpy,math,random,argparse,sys
from mathutils import Vector
random.seed(482)
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
world=bpy.data.worlds.new('Deep space');world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.001,.003,.01,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.08;s.world=world
s.use_nodes=True;n=s.node_tree.nodes;n.clear();r=n.new('CompositorNodeRLayers');gl=n.new('CompositorNodeGlare');gl.glare_type='FOG_GLOW';gl.quality='HIGH';gl.threshold=1.6;gl.size=7;out=n.new('CompositorNodeComposite');s.node_tree.links.new(r.outputs['Image'],gl.inputs['Image']);s.node_tree.links.new(gl.outputs['Image'],out.inputs['Image'])
def metal(name,col,metallic=.7,rough=.3):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Metallic'].default_value=metallic;p.inputs['Roughness'].default_value=rough;return m
def emit(name,col,power):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;n.clear();e=n.new('ShaderNodeEmission');e.inputs['Color'].default_value=(*col,1);e.inputs['Strength'].default_value=power;o=n.new('ShaderNodeOutputMaterial');m.node_tree.links.new(e.outputs[0],o.inputs['Surface']);return m
def textured(name,colors,scale,rough=.7):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF');p.inputs['Roughness'].default_value=rough;tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=scale;tex.inputs['Detail'].default_value=4;tex.inputs['Roughness'].default_value=.7;ramp=n.new('ShaderNodeValToRGB')
 ramp.color_ramp.elements[0].position=.25;ramp.color_ramp.elements[0].color=(*colors[0],1);ramp.color_ramp.elements[1].position=.78;ramp.color_ramp.elements[1].color=(*colors[2],1);ramp.color_ramp.elements.new(.50).color=(*colors[1],1)
 l.new(tex.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs['Color'],p.inputs['Base Color']);b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=.16;b.inputs['Distance'].default_value=.08;l.new(tex.outputs['Fac'],b.inputs['Height']);l.new(b.outputs['Normal'],p.inputs['Normal']);return m
shipmat=metal('Pearl titanium',(.32,.41,.46),.8,.27);dark=metal('Graphite',(.018,.029,.039),.72,.3);glass=metal('Cockpit smoked glass',(.016,.07,.10),.6,.12)
engine=emit('Ion exhaust',(.12,.7,1),8);marker=emit('Navigation light',(1,.28,.08),4);stars=emit('Starlight',(.8,.9,1),1.8);sunmat=emit('Distant warm sun',(1,.55,.2),5);titles=emit('Title ivory',(1,.88,.65),1.6)
rock=textured('Basalt and sand',[(.015,.02,.03),(.10,.13,.16),(.34,.24,.16)],3.3);planetmat=textured('Azure ocean and continents',[(.004,.018,.065),(.02,.13,.18),(.26,.35,.28)],3.0,.6);moonmat=textured('Rugged moon',[(.014,.018,.03),(.08,.075,.08),(.25,.19,.14)],4.2,.82)
def key(obj,f,**kwargs):
 for k,v in kwargs.items():setattr(obj,k,v);obj.keyframe_insert(data_path=k,frame=f)
def smooth(obj):
 if obj.animation_data and obj.animation_data.action:
  try:
   for f in obj.animation_data.action.fcurves:
    for p in f.keyframe_points:p.interpolation='BEZIER';p.handle_left_type=p.handle_right_type='AUTO_CLAMPED'
  except AttributeError:pass
def look(obj,target):obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
def sphere(name,loc,r,material,seg=48):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=seg,ring_count=24,radius=r,location=loc);o=bpy.context.object;o.name=name;o.data.materials.append(material);bpy.ops.object.shade_smooth();return o
def cube(name,loc,scale,material,bevel=0):
 bpy.ops.mesh.primitive_cube_add(location=loc);o=bpy.context.object;o.name=name;o.scale=scale;o.data.materials.append(material)
 if bevel:m=o.modifiers.new('Edge highlights','BEVEL');m.width=bevel;m.segments=3
 return o
def mesh(name,verts,faces,material):
 d=bpy.data.meshes.new(name);d.from_pydata(verts,[],faces);d.update();o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.data.materials.append(material);return o
def area(name,loc,target,col,energy,size):
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;o.data.energy=energy;o.data.color=col;o.data.size=size;look(o,target)
def camera(name,offset,start,end,first,last,target,lens):
 bpy.ops.object.empty_add(type='PLAIN_AXES',location=(offset+target[0],target[1],target[2]));looktarget=bpy.context.object
 bpy.ops.object.camera_add(location=(offset+first[0],first[1],first[2]));c=bpy.context.object;c.name=name;c.data.lens=lens;con=c.constraints.new('TRACK_TO');con.target=looktarget;con.track_axis='TRACK_NEGATIVE_Z';con.up_axis='UP_Y'
 key(c,start,location=(offset+first[0],first[1],first[2]));key(c,end,location=(offset+last[0],last[1],last[2]));smooth(c)
 marker=s.timeline_markers.new(name,frame=start);marker.camera=c;return c
def background(offset,seed):
 rng=random.Random(seed);verts=[];faces=[]
 for i in range(260):
  x=offset+rng.uniform(-19,19);y=rng.uniform(13,20);z=rng.uniform(-2,12);r=rng.uniform(.012,.033) if i%19 else .055
  q=len(verts);verts.extend([(x-r,y,z-r),(x+r,y,z-r),(x+r,y,z+r),(x-r,y,z+r)]);faces.append((q,q+1,q+2,q+3))
 mesh('Deep star field',verts,faces,stars)
def spacecraft(offset,loc,scale,start,end,travel):
 bpy.ops.object.empty_add(type='PLAIN_AXES',location=(offset+loc[0],loc[1],loc[2]));root=bpy.context.object;root.name='The explorer';root.scale=(scale,)*3
 def part(obj,xyz):obj.parent=root;obj.location=xyz;return obj
 # A narrow aerodynamic fuselage, split cockpit, paired swept wings, engines and navigation lights.
 fus=part(sphere('Ceramic fuselage',(0,0,0),1,shipmat,32),(0,0,0));fus.scale=(1.45,.24,.20)
 cockpit=part(sphere('Cockpit glazing',(0,0,0),1,glass,32),(.55,0,.14));cockpit.scale=(.45,.19,.16)
 wingverts=[(-.3,-.14,0),(-1.0,-1.1,-.06),(-1.3,-1.05,-.06),(-.9,-.1,0),(-.3,.14,0),(-1.,1.1,-.06),(-1.3,1.05,-.06),(-.9,.1,0)]
 part(mesh('Swept wings',wingverts,[(0,1,2,3),(4,5,6,7)],shipmat),(0,0,0))
 for y in (-.38,.38):
  o=part(sphere('Engine housing',(0,0,0),1,dark,24),(-.91,y,-.01));o.scale=(.43,.12,.12)
  o=part(sphere('Ion engine',(0,0,0),1,engine,24),(-1.32,y,-.01));o.scale=(.09,.11,.11)
  o=part(sphere('Wingtip beacon',(0,0,0),.05,marker,16),(-1.05,y*2.7,-.02))
 for x in (-.3,0,.3):part(cube('Hull panel',(0,0,0),(.11,.245,.018),dark),(x,0,.18))
 key(root,start,location=(offset+loc[0],loc[1],loc[2]),rotation_euler=(.06,-.08,.05));key(root,end,location=(offset+loc[0]+travel[0],loc[1]+travel[1],loc[2]+travel[2]),rotation_euler=(-.04,.04,-.10));smooth(root);return root
def planet(name,offset,loc,r,material,start,end):
 o=sphere(name,(offset+loc[0],loc[1],loc[2]),r,material,64);key(o,start,rotation_euler=(.12,0,0));key(o,end,rotation_euler=(.12,.15,.4));smooth(o);return o
# shot 1 — the explorer crosses a textured alien horizon.
O=0;background(O,1)
N=100;verts=[];faces=[]
for j in range(N):
 y=-10+j*25/(N-1)
 for i in range(N):
  x=-18+i*36/(N-1);h=-3.1+.48*math.sin(x*.43+y*.35)+.3*math.cos(y*.73-x*.2)+.15*math.sin(x*1.1+y*.8)+1.2*math.exp(-((x+7)**2+(y-7)**2)/40)
  verts.append((x,y,h))
for j in range(N-1):
 for i in range(N-1):q=j*N+i;faces.append((q,q+1,q+1+N,q+N))
mesh('Alien terrain',verts,faces,rock)
planet('Distant moon',O,(8,12,7),2.1,moonmat,1,80)
spacecraft(O,(-2,0,.6),1.0,1,80,(3.5,0,.3));area('Dawn across mountains',(O-5,-3,8),(O,0,-1),(1,.48,.25),2000,8);area('Cold sky rim',(O+4,5,6),(O,0,0),(.15,.5,1),1800,7)
camera('01 · The departure',O,1,80,(-5,-11,3),(-2,-10,2.5),(0,0,.3),38)
# shot 2 — an immense blue world, with the explorer passing it.
O=100;background(O,2);planet('Ocean world',O,(1,3,1),3.2,planetmat,81,165)
sphere('Remote sun',(O-7,8,5),1.0,sunmat)
spacecraft(O,(-4,-2,-.4),.56,81,165,(6,.2,1.2));area('Planet sunlight',(O-6,-5,7),(O+1,3,1),(1,.68,.4),2600,8);area('Planet sky fill',(O+5,-2,3),(O+1,3,1),(.2,.45,1),1000,7)
camera('02 · The crossing',O,81,165,(-1,-17,3.2),(1,-16,2.4),(0,2,1),40)
# shot 3 — a high-contrast eclipse as the craft enters its shadow.
O=200;background(O,3);sphere('Eclipse corona',(O+1.45,6,1.4),3.2,sunmat,64);planet('Eclipse silhouette',O,(0,2,1),3.05,moonmat,166,269)
spacecraft(O,(-4.3,-3,-.5),.45,166,269,(7.7,0,1.5));area('Eclipse edge light',(O+8,3,5),(O,2,1),(1,.42,.15),1200,6);area('Faint fill',(O-3,-5,3),(O,2,1),(.13,.25,.4),250,8)
camera('03 · The eclipse',O,166,269,(-2,-17,2.8),(1,-16,2.2),(0,2,1),40)
# shot 4 — the first light appears at the rim of a vast new world.
O=300;background(O,4);planet('Home horizon',O,(0,5,-4),6.2,planetmat,270,360);sphere('New dawn sun',(O+3.6,11,1),1.4,sunmat)
spacecraft(O,(-4,-1,1.4),.52,270,360,(6.5,.5,.25));area('Dawn key',(O+6,-2,8),(O,5,-2),(1,.51,.25),2700,9);area('Atmospheric fill',(O-5,-2,4),(O,5,-2),(.15,.45,.8),850,8)
c=camera('04 · A new dawn',O,270,360,(-.5,-18,3.0),(.3,-17,2.8),(0,3,0),40)
# Camera-parented end typography, kept within the safe frame.
cu=bpy.data.curves.new('Title','FONT');cu.body='A  N E W  D A W N';cu.align_x='CENTER';cu.align_y='CENTER';cu.size=.25;obj=bpy.data.objects.new('Closing title',cu);s.collection.objects.link(obj);obj.parent=c;obj.location=(0,-1.22,-6);obj.data.materials.append(titles)
key(obj,270,scale=(.001,)*3);key(obj,300,scale=(.001,)*3);key(obj,320,scale=(1,)*3);smooth(obj)
s.camera=next(o for o in bpy.data.objects if o.type=='CAMERA' and o.name.startswith('01'))
parser=argparse.ArgumentParser();parser.add_argument('--start',type=int,default=1);parser.add_argument('--end',type=int,default=360);parser.add_argument('--output',required=True)
a=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []);s.frame_start=a.start;s.frame_end=a.end;s.render.filepath=a.output;s.frame_set(a.start);bpy.ops.render.render(animation=True)
