"""
Dot Writes the Words — Blender 4.x procedural motion-graphics opener.
Run: blender -b --python scripts/dot_writes_opening.py -- --output output/dot_writes_opening.mp4
Set OPENING_TEXT to change the phrase. No external footage or paid assets.
"""
import bpy, math, os, sys
from mathutils import Vector

def arg_after(flag, default):
    try: return sys.argv[sys.argv.index(flag) + 1]
    except (ValueError, IndexError): return default

OUT = os.path.abspath(arg_after("--output", "output/dot_writes_opening.mp4"))
TEXT = os.environ.get("OPENING_TEXT", "IDEAS CHANGE EVERYTHING").upper()[:42]
FPS, W, H, DURATION = 30, 1920, 1080, 8
END = FPS * DURATION

# Compact single-line vector alphabet. Coordinates are normalized to a 1x1 cell.
G = {
'A':[(0,0),(0.5,1),(1,0),(-1,-1),(0.25,0.42),(0.75,0.42)],
'B':[(0,0),(0,1),(0.55,1),(0.9,0.85),(0.55,0.55),(0,0.55),(0.62,0.55),(0.95,0.32),(0.7,0),(0,0)],
'C':[(0.95,0.88),(0.7,1),(0.25,0.95),(0.02,0.68),(0,0.28),(0.28,0.02),(0.75,0),(1,0.14)],
'D':[(0,0),(0,1),(0.45,1),(0.88,0.75),(1,0.35),(0.7,0.05),(0,0)],
'E':[(1,1),(0,1),(0,0),(1,0),(0,0.52),(0.78,0.52)],
'F':[(0,0),(0,1),(1,1),(0,0.52),(0.78,0.52)],
'G':[(0.95,0.85),(0.7,1),(0.25,0.95),(0,0.62),(0.04,0.2),(0.35,0),(0.82,0.06),(1,0.35),(0.62,0.35)],
'H':[(0,0),(0,1),(-1,-1),(1,1),(1,0),(-1,-1),(0,0.5),(1,0.5)],
'I':[(0.15,1),(0.85,1),(-1,-1),(0.5,1),(0.5,0),(-1,-1),(0.15,0),(0.85,0)],
'J':[(0.15,1),(1,1),(-1,-1),(0.75,1),(0.75,0.2),(0.55,0),(0.2,0.05),(0,0.25)],
'K':[(0,0),(0,1),(-1,-1),(1,1),(0,0.48),(1,0)],
'L':[(0,1),(0,0),(1,0)],
'M':[(0,0),(0,1),(0.5,0.48),(1,1),(1,0)],
'N':[(0,0),(0,1),(1,0),(1,1)],
'O':[(0.5,1),(0.85,0.85),(1,0.5),(0.85,0.12),(0.5,0),(0.15,0.12),(0,0.5),(0.15,0.85),(0.5,1)],
'P':[(0,0),(0,1),(0.65,1),(1,0.8),(0.8,0.55),(0,0.55)],
'Q':[(0.5,1),(0.85,0.85),(1,0.5),(0.85,0.12),(0.5,0),(0.15,0.12),(0,0.5),(0.15,0.85),(0.5,1),(-1,-1),(0.58,0.25),(1,0)],
'R':[(0,0),(0,1),(0.65,1),(1,0.8),(0.8,0.55),(0,0.55),(-1,-1),(0.5,0.55),(1,0)],
'S':[(0.95,0.85),(0.7,1),(0.2,0.9),(0.05,0.7),(0.2,0.55),(0.8,0.45),(0.98,0.25),(0.8,0.05),(0.25,0),(0,0.15)],
'T':[(0,1),(1,1),(-1,-1),(0.5,1),(0.5,0)],
'U':[(0,1),(0,0.25),(0.2,0),(0.75,0),(1,0.25),(1,1)],
'V':[(0,1),(0.45,0),(1,1)],
'W':[(0,1),(0.2,0),(0.5,0.55),(0.8,0),(1,1)],
'X':[(0,1),(1,0),(-1,-1),(0,0),(1,1)],
'Y':[(0,1),(0.5,0.52),(1,1),(-1,-1),(0.5,0.52),(0.5,0)],
'Z':[(0,1),(1,1),(0,0),(1,0)],
'0':[(0.5,1),(1,0.8),(1,0.2),(0.5,0),(0,0.2),(0,0.8),(0.5,1)],
'1':[(0.2,0.75),(0.5,1),(0.5,0)],
'2':[(0,0.8),(0.2,1),(0.8,1),(1,0.8),(0,0)],
'3':[(0,1),(0.8,1),(0.5,0.55),(0.9,0.5),(1,0.2),(0.75,0),(0,0.08)],
'4':[(0.8,0),(0.8,1),(0,0.32),(1,0.32)],
'5':[(1,1),(0.1,1),(0.1,0.55),(0.75,0.55),(1,0.3),(0.8,0),(0,0.05)],
'6':[(0.9,0.9),(0.4,1),(0.05,0.55),(0,0.2),(0.3,0),(0.8,0.05),(1,0.3),(0.8,0.55),(0.1,0.55)],
'7':[(0,1),(1,1),(0.35,0)],
'8':[(0.5,0.52),(0.1,0.75),(0.2,1),(0.8,1),(0.9,0.75),(0.5,0.52),(0.1,0.25),(0.2,0),(0.8,0),(0.9,0.25),(0.5,0.52)],
'9':[(0.9,0.45),(0.2,0.45),(0,0.7),(0.2,1),(0.7,1),(1,0.7),(0.9,0.2),(0.5,0)],
'.':[(0.5,0.03),(0.51,0.04)], ':':[(0.5,0.75),(0.51,0.76),(-1,-1),(0.5,0.12),(0.51,0.13)],
'!':[(0.5,1),(0.5,0.28),(-1,-1),(0.5,0.04),(0.51,0.05)],
'?':[(0.05,0.8),(0.25,1),(0.75,1),(1,0.78),(0.5,0.48),(0.5,0.28),(-1,-1),(0.5,0.04),(0.51,0.05)],
}

# Reset to a deterministic scene.
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for datablocks in (bpy.data.curves, bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
    pass
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in bpy.app.build_options.__dir__() else 'BLENDER_EEVEE'
scene.render.resolution_x=W; scene.render.resolution_y=H; scene.render.resolution_percentage=100
scene.render.fps=FPS; scene.frame_start=1; scene.frame_end=END
scene.render.image_settings.file_format='FFMPEG'; scene.render.ffmpeg.format='MPEG4'; scene.render.ffmpeg.codec='H264'
scene.render.filepath=OUT; scene.render.resolution_percentage=100
scene.world.color=(0.003,0.006,0.016)
scene.view_settings.view_transform='Standard'

def emission(name, color, strength=1.0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    n=m.node_tree.nodes; n.clear(); out=n.new('ShaderNodeOutputMaterial'); e=n.new('ShaderNodeEmission')
    e.inputs['Color'].default_value=(*color,1); e.inputs['Strength'].default_value=strength
    m.node_tree.links.new(e.outputs[0],out.inputs['Surface']); return m

ink=emission('Electric cyan ink',(0.08,0.78,1.0),2.0)
dotmat=emission('Writing point',(0.72,0.96,1.0),5.0)
white=emission('Headline',(0.82,0.92,1.0),1.15)
muted=emission('Subheadline',(0.18,0.35,0.48),0.8)
dark=emission('Backdrop',(0.004,0.012,0.027),0.5)

# Orthographic front-facing 2D stage; XY are screen coordinates, Z provides subtle layering.
bpy.ops.object.camera_add(location=(0,0,24))
cam=bpy.context.object; cam.name='Opening Camera'; cam.data.type='ORTHO'; cam.data.ortho_scale=18.0; scene.camera=cam

def line_obj(name, points, material, bevel=0.012):
    cu=bpy.data.curves.new(name,'CURVE'); cu.dimensions='3D'; cu.resolution_u=1; cu.bevel_depth=bevel; cu.resolution_u=2
    sp=cu.splines.new('POLY'); sp.points.add(len(points)-1)
    for p,co in zip(sp.points,points): p.co=(co[0],co[1],co[2] if len(co)>2 else 0,1)
    ob=bpy.data.objects.new(name,cu); scene.collection.objects.link(ob); ob.data.materials.append(material); return ob

# Restrained technical-grid background.
for x in range(-9,10):
    ob=line_obj('Grid vertical',[(x,-5.1,-1),(x,5.1,-1)],muted,0.002)
    ob.data.bevel_depth=0.001
for y in range(-5,6):
    ob=line_obj('Grid horizontal',[(-9,y,-1),(9,y,-1)],muted,0.002); ob.data.bevel_depth=0.001
# Center guide line and small framing corners.
line_obj('Baseline',[(-7.7,-1.65,-0.5),(7.7,-1.65,-0.5)],ink,0.006)

# Layout: vector letters are drawn as a single continuous route; pen lifts travel invisibly between glyph strokes.
def build_route(text):
    glyph_w, gap, wordgap = 0.46, 0.17, 0.48
    total=sum((glyph_w+gap if c!=' ' else wordgap) for c in text)-gap
    x=-total/2; route=[]
    for c in text:
        if c==' ': x+=wordgap; continue
        strokes=G.get(c)
        if not strokes: x+=glyph_w+gap; continue
        current=[]
        def flush():
            nonlocal current
            if current:
                if route: route.append(None)  # pen lift, dot travels to next stroke without drawing
                route.extend(current); current=[]
        for px,py in strokes:
            if px == -1 and py == -1: flush(); continue
            current.append((x+px*glyph_w, -0.35+py*0.82, 0.12))
        flush(); x+=glyph_w+gap
    return route

# Fit text width to camera; preserve the hand-drawn vector style.
route=build_route(TEXT)
xs=[p[0] for p in route if p]
width=max(xs)-min(xs) if xs else 1
scale=min(1.0, 14.2/max(width,1))
route=[(p[0]*scale,p[1]*scale,p[2]) if p else None for p in route]
# Continuous animation path includes tiny invisible travel between pen lifts.
path=[]; prev=None
for p in route:
    if p is None: prev=None; continue
    if prev is not None: path.append(p)
    else: path.append(p)
    prev=p
# Separate stroke objects for each stroke, reveal using bevel_factor_end.
strokes=[]; current=[]
for p in route:
    if p is None:
        if len(current)>1: strokes.append(current)
        current=[]
    else: current.append(p)
if len(current)>1: strokes.append(current)
# Normalize stroke animation duration by line length.
lengths=[]
for s in strokes:
    lengths.append(sum((Vector(b)-Vector(a)).length for a,b in zip(s,s[1:])))
total_len=sum(lengths) or 1
cursor=0.0
for i,(pts,L) in enumerate(zip(strokes,lengths)):
    ob=line_obj('Ink stroke %03d'%i,pts,ink,0.014)
    ob.data.bevel_factor_start=0.0
    start=1+int(cursor/total_len*FPS*4.8); finish=1+int((cursor+L)/total_len*FPS*4.8)
    ob.data.bevel_factor_end=0.0; ob.data.keyframe_insert(data_path='bevel_factor_end',frame=start)
    ob.data.bevel_factor_end=1.0; ob.data.keyframe_insert(data_path='bevel_factor_end',frame=max(start+1,finish))
    cursor+=L
# Dot animates across the stroke centers, tracing the same stroke path.
bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=0.075, location=(strokes[0][0] if strokes else (0,0,0)))
dot=bpy.context.object; dot.name='Luminous writing dot'; dot.data.materials.append(dotmat)
# Position keyframes allocated by cumulative route length, with brief holds on pen-lift transitions.
cum=0; all_segments=[]
for s in strokes:
    for a,b in zip(s,s[1:]):
        all_segments.append((a,b,(Vector(b)-Vector(a)).length))
total_path=sum(seg[2] for seg in all_segments) or 1
for a,b,L in all_segments:
    f0=1+int(cum/total_path*FPS*4.8); cum+=L; f1=1+int(cum/total_path*FPS*4.8)
    dot.location=a; dot.keyframe_insert(data_path='location',frame=f0)
    dot.location=b; dot.keyframe_insert(data_path='location',frame=max(f0+1,f1))
# Tail/glow-like aura: small transparent-free emissive rings that stay tasteful.
for frame in range(1,END+1):
    scene.frame_set(frame)
    if frame < FPS*4.9:
        dot.hide_render=False
    else:
        dot.hide_render=True
# Title and supporting copy fade in after the writing completes.
def text_obj(body,name,size,loc,material):
    cu=bpy.data.curves.new(name,'FONT'); cu.body=body; cu.size=size; cu.align_x='CENTER'; cu.extrude=0
    ob=bpy.data.objects.new(name,cu); scene.collection.objects.link(ob); ob.location=loc; ob.data.materials.append(material); return ob
title=text_obj(TEXT,'Final title',0.58,(0,-2.65,0.2),white)
title.data.size=0.58
for frame,val in [(1,0.0),(FPS*4,0.0),(FPS*5.3,1.0)]:
    title.data.alpha=val if hasattr(title.data,'alpha') else 1.0
    title.scale=(0.92,0.92,0.92) if val==0 else (1,1,1)
    title.keyframe_insert(data_path='scale',frame=frame)
sub=text_obj('A STORY IN MOTION','Subline',0.19,(0,-3.28,0.2),muted)
for frame,sc in [(1,(0,0,0)),(FPS*5.3,(0,0,0)),(FPS*6.2,(1,1,1))]:
    sub.scale=sc; sub.keyframe_insert(data_path='scale',frame=frame)
# Slightly ease all keyframes.
for ob in scene.objects:
    if ob.animation_data and ob.animation_data.action:
        for fc in ob.animation_data.action.fcurves:
            for kp in fc.keyframe_points: kp.interpolation='BEZIER'
scene.render.image_settings.color_mode='RGB'
scene.render.ffmpeg.constant_rate_factor='MEDIUM'; scene.render.ffmpeg.ffmpeg_preset='GOOD'
scene.frame_set(1)
os.makedirs(os.path.dirname(OUT) or '.',exist_ok=True)
bpy.ops.render.render(animation=True)
print('RENDER_OK:',OUT)
