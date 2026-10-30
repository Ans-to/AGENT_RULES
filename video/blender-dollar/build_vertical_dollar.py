"""Build the 60-second vertical Dollar film in Blender 4.2+.

In Blender's Scripting workspace, open this file and press Run Script. This
creates a NEW scene named DollarFilm and does not render automatically.
In GitHub Actions it uses EEVEE and automatically renders a PNG sequence.
Set DOLLAR_BUILD_ONLY=1 for a headless setup-only smoke test.

Frame 1 = 0.000 seconds. Frames 1..3600 = exactly 60 seconds at 60 fps.
All images, fonts and assets are procedural or built into Blender. The generated
HDR float world image is packed into the .blend. No network downloads required.
The script creates visuals only: there is no narration or soundtrack in this file.

Translation note: The orbit and whip use the numeric source formulas, mapped
from Three.js Y-up to Blender Z-up, and Scene 4 uses the whip endpoint camera.
Some original GSAP easing/particles and text layouts are approximated with
Blender curves; this is not a pixel-identical recreation of the WebGL film.
"""
import bpy
import math
import random
import os
import tempfile
from array import array
from mathutils import Vector, Quaternion

# Configuration: change these before running the script.
SCENE_NAME = 'DollarFilm'
FPS = 60
CI_MODE = os.environ.get('GITHUB_ACTIONS', '').lower() == 'true'
SAMPLES = 128               # Cycles; use 256 for final quality.
CI_SAMPLES = 8              # EEVEE render samples for software CPU runners.
RENDER_DIRECTORY = os.environ.get('DOLLAR_FRAMES_DIR', '//dollar_frames/')
SEED = 82919
random.seed(SEED)


def frame(t):
    return 1 + round(t * FPS)


def action_curves(obj):
    """Blender 4.2-4.3 legacy Actions and 4.4+/5.x slotted Actions."""
    animation = obj.animation_data
    if not animation or not animation.action:
        return None
    if hasattr(animation, 'action_slot') and animation.action_slot:
        from bpy_extras.anim_utils import action_get_channelbag_for_slot
        channelbag = action_get_channelbag_for_slot(animation.action, animation.action_slot)
        if channelbag:
            return channelbag.fcurves
    return getattr(animation.action, 'fcurves', None)


def set_curve(obj, path, t, value, interpolation='BEZIER'):
    setattr(obj, path, value)
    obj.keyframe_insert(data_path=path, frame=frame(t))
    curves = action_curves(obj)
    if curves is not None:
        for fc in curves:
            if fc.data_path == path:
                for kp in fc.keyframe_points:
                    if abs(kp.co.x - frame(t)) < 0.01:
                        kp.interpolation = interpolation
                        if interpolation == 'BEZIER':
                            kp.handle_left_type = 'AUTO_CLAMPED'
                            kp.handle_right_type = 'AUTO_CLAMPED'


def animate(obj, path, keys, interpolation='BEZIER'):
    for t, value in keys:
        set_curve(obj, path, t, value, interpolation)


def visible_between(obj, start, end):
    # Replace any prior window; used when a stage contains later entrances.
    curves = action_curves(obj)
    if curves is not None:
        for curve in list(curves):
            if curve.data_path == 'hide_render':
                curves.remove(curve)
    # Constant visibility avoids hiding children due to zero-scale geometry.
    set_curve(obj, 'hide_render', 0, start > 0, 'CONSTANT')
    set_curve(obj, 'hide_render', start, False, 'CONSTANT')
    if end < 60:
        set_curve(obj, 'hide_render', end, True, 'CONSTANT')
    obj.hide_viewport = False


def mat(name, color, metallic=0, roughness=.35, emission=0, coat=0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = roughness
    for key in ('Coat Weight', 'Clearcoat'):
        if key in p.inputs:
            p.inputs[key].default_value = coat
            break
    if emission:
        key = 'Emission Color' if 'Emission Color' in p.inputs else 'Emission'
        p.inputs[key].default_value = (*color, 1)
        p.inputs['Emission Strength'].default_value = emission
    return m


def assign(obj, material):
    obj.data.materials.append(material)
    return obj


def link(obj):
    scene.collection.objects.link(obj)
    return obj


def empty(name, loc=(0, 0, 0), parent=None):
    obj = link(bpy.data.objects.new(name, None))
    obj.location = loc
    if parent:
        obj.parent = parent
    return obj


def cube(name, loc, size, material, parent=None, bevel=.04):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
    o = bpy.context.object
    o.name = name
    o.parent = parent
    o.location = loc
    o.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod = o.modifiers.new('Machined edge radius', 'BEVEL')
        mod.width = bevel
        mod.segments = 4
        mod.limit_method = 'ANGLE'
        normal = o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
        normal.keep_sharp = True
    assign(o, material)
    return o


def cylinder(name, loc, radius, depth, material, parent=None, vertices=96, axis='Z', bevel=.025):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth)
    o = bpy.context.object
    o.name = name
    o.parent = parent
    o.location = loc
    if axis == 'Y':
        o.rotation_euler[0] = math.pi / 2
    elif axis == 'X':
        o.rotation_euler[1] = math.pi / 2
    if bevel:
        mod = o.modifiers.new('Soft machined edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        o.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    for face in o.data.polygons:
        face.use_smooth = True
    assign(o, material)
    return o


def sphere(name, loc, radius, material, parent=None, segments=24, rings=12):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, radius=radius)
    o = bpy.context.object
    o.name = name
    o.parent = parent
    o.location = loc
    for poly in o.data.polygons:
        poly.use_smooth = True
    assign(o, material)
    return o


def line(name, points, radius, material, parent=None):
    curve = bpy.data.curves.new(name, 'CURVE')
    curve.dimensions = '3D'
    curve.resolution_u = 16
    curve.bevel_depth = radius
    curve.bevel_resolution = 3
    spline = curve.splines.new('POLY')
    spline.points.add(len(points)-1)
    for point, co in zip(spline.points, points):
        point.co = (*co, 1)
    obj = link(bpy.data.objects.new(name, curve))
    obj.parent = parent
    assign(obj, material)
    return obj


def text(name, body, loc, size, material, parent=None, align='CENTER'):
    data = bpy.data.curves.new(name, 'FONT')
    data.body = body
    data.align_x = align
    data.align_y = 'CENTER'
    data.size = size
    data.extrude = .015 * size
    data.bevel_depth = .003 * size
    data.bevel_resolution = 3
    data.resolution_u = 16
    obj = link(bpy.data.objects.new(name, data))
    obj.parent = parent
    obj.location = loc
    assign(obj, material)
    return obj


def area(name, loc, target, power, color, size, parent=None):
    data = bpy.data.lights.new(name, 'AREA')
    data.energy = power
    data.color = color
    data.shape = 'RECTANGLE'
    data.size = size[0]
    data.size_y = size[1]
    obj = link(bpy.data.objects.new(name, data))
    obj.parent = parent
    obj.location = loc
    obj.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return obj


def make_stage(name, matrix=None):
    root = empty(name)
    if matrix is not None:
        root.matrix_world = matrix
    return root


def show_tree(root, start, end):
    visible_between(root, start, end)
    for o in root.children_recursive:
        visible_between(o, start, end)


def rig(root):
    # Light positions use the stage's camera-local x/y/z coordinates.
    area('KEY softbox', (-4, 5, 6), (0, 0, 0), 650, (1, .87, .67), (5, 4), root)
    area('FILL softbox', (4, 1, 4), (0, 0, 0), 280, (.52, .72, 1), (4, 5), root)
    area('NEON GREEN rim', (2, 4, -4), (0, 0, 0), 850, (0, 1, .051), (3, 4), root)


def overlay(body, y, size, material, start, end, name=None, x=0):
    # Camera local axes: x right, y up, -z in front of camera.
    o = text(name or body, body, (x, y, -7), size, material, camera)
    bpy.context.view_layer.update()
    if o.dimensions.x > 2.7:
        o.data.size *= 2.7 / o.dimensions.x
    visible_between(o, start, end)
    return o


def pop(obj, t, duration=.55):
    base = tuple(obj.scale)
    animate(obj, 'scale', [(t, (.001,)*3), (t+.75*duration, tuple(v*1.1 for v in base)), (t+duration, base)])


def float_world():
    # Real equirectangular HDR environment texture, procedurally generated.
    # Bright panels above 1.0 provide distinct reflections; camera rays see black.
    w, h = 512, 256
    pixels = array('f')
    def panel(u, v, cx, cy, sx, sy):
        return math.exp(-(((u-cx)/sx)**8 + ((v-cy)/sy)**8))
    for j in range(h):
        v = j/(h-1)
        for i in range(w):
            u = i/(w-1)
            key = 5.0*panel(u,v,.25,.48,.055,.22)
            fill = 2.0*panel(u,v,.62,.5,.10,.13)
            rim = 3.0*panel(u,v,.87,.5,.035,.23)
            base = .025 + .08*v
            pixels.extend((base+key+fill*.8, base+key*.92+fill*.9+rim, base+key*.8+fill+rim*.15, 1.0))
    img = bpy.data.images.new('Packed procedural HDR studio', width=w, height=h, alpha=True, float_buffer=True)
    img.pixels.foreach_set(pixels)
    img.update()
    # Pack as OpenEXR so values above 1 survive packing (PNG would clip HDR).
    fd, exr_path = tempfile.mkstemp(prefix='dollar_studio_', suffix='.exr')
    os.close(fd)
    try:
        img.filepath_raw = exr_path
        img.file_format = 'OPEN_EXR'
        img.save()
        img.pack()
    finally:
        if os.path.exists(exr_path):
            os.remove(exr_path)
    world = bpy.data.worlds.new('Dark camera / HDR studio reflections')
    world.use_nodes = True
    n = world.node_tree.nodes
    n.clear()
    links = world.node_tree.links
    out = n.new('ShaderNodeOutputWorld')
    env = n.new('ShaderNodeTexEnvironment')
    env.image = img
    bg = n.new('ShaderNodeBackground')
    bg.inputs['Strength'].default_value = .8
    black = n.new('ShaderNodeBackground')
    black.inputs['Color'].default_value = (.001, .001, .001, 1)
    path = n.new('ShaderNodeLightPath')
    mix = n.new('ShaderNodeMixShader')
    links.new(env.outputs['Color'], bg.inputs['Color'])
    links.new(path.outputs['Is Camera Ray'], mix.inputs[0])
    links.new(bg.outputs[0], mix.inputs[1])
    links.new(black.outputs[0], mix.inputs[2])
    links.new(mix.outputs[0], out.inputs['Surface'])
    return world


# Create a new scene rather than deleting anything from the open .blend.
if bpy.context.window:
    scene = bpy.data.scenes.new(SCENE_NAME)
    bpy.context.window.scene = scene
elif bpy.app.background:
    # A background context may have no window. Reuse its active factory scene
    # so mesh operators link to the correct scene and view layer.
    scene = bpy.context.scene
    scene.name = SCENE_NAME
    for obj in list(scene.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
else:
    raise RuntimeError('No active Blender scene is available.')
if CI_MODE:
    scene.render.engine = 'BLENDER_EEVEE' if bpy.app.version >= (5, 0, 0) else 'BLENDER_EEVEE_NEXT'
    if hasattr(scene, 'eevee') and hasattr(scene.eevee, 'taa_render_samples'):
        scene.eevee.taa_render_samples = CI_SAMPLES
    scene.cycles.use_denoising = False
else:
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = SAMPLES
    scene.cycles.use_denoising = True
scene.render.resolution_x = 1080
scene.render.resolution_y = 1920
scene.render.resolution_percentage = 100
scene.render.fps = FPS
scene.render.fps_base = 1
# Each CI worker evaluates the complete original timeline but renders only its
# assigned inclusive range. Local interactive builds always retain all frames.
if CI_MODE:
    try:
        first_frame = int(os.environ.get('DOLLAR_FRAME_START', '1'))
        last_frame = int(os.environ.get('DOLLAR_FRAME_END', '3600'))
    except ValueError as exc:
        raise ValueError('Chunk frame bounds must be integers') from exc
    if not 1 <= first_frame <= last_frame <= 3600:
        raise ValueError('Chunk must satisfy 1 <= start <= end <= 3600')
    scene.frame_start, scene.frame_end = first_frame, last_frame
else:
    scene.frame_start, scene.frame_end = 1, 3600
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
if CI_MODE:
    RENDER_DIRECTORY = os.path.abspath(RENDER_DIRECTORY)
    os.makedirs(RENDER_DIRECTORY, exist_ok=True)
    RENDER_DIRECTORY = os.path.join(RENDER_DIRECTORY, '')
scene.render.filepath = RENDER_DIRECTORY
scene.render.use_file_extension = True
scene.render.use_motion_blur = True
# Blender's shutter is measured in frames: 0.5 frames == 180 degrees.
scene.render.motion_blur_shutter = .5
if hasattr(scene.render, 'motion_blur_position'):
    scene.render.motion_blur_position = 'CENTER'
scene.world = float_world()
try:
    scene.view_settings.view_transform = 'AgX'
except TypeError:
    pass
# Restrained compositor glow. Blender 5 replaced scene.node_tree with a
# compositor node group and moved glare settings to node inputs.
if bpy.app.version >= (5, 0, 0):
    tree = bpy.data.node_groups.new('Dollar compositor', 'CompositorNodeTree')
    scene.compositing_node_group = tree
    tree.interface.new_socket(name='Image', in_out='OUTPUT', socket_type='NodeSocketColor')
    comp = tree.nodes.new('NodeGroupOutput')
else:
    scene.use_nodes = True
    tree = scene.node_tree
    tree.nodes.clear()
    comp = tree.nodes.new('CompositorNodeComposite')
rl = tree.nodes.new('CompositorNodeRLayers')
glow = tree.nodes.new('CompositorNodeGlare')
if hasattr(glow, 'glare_type'):
    glow.glare_type = 'FOG_GLOW'
elif 'Glare Type' in glow.inputs:
    try:
        glow.inputs['Glare Type'].default_value = 'FOG_GLOW'
    except (TypeError, ValueError):
        pass  # Keep the version's default if its menu identifiers differ.
if hasattr(glow, 'quality'):
    glow.quality = 'HIGH'
if 'Threshold' in glow.inputs:
    glow.inputs['Threshold'].default_value = 1.5
else:
    glow.threshold = 1.5
if 'Strength' in glow.inputs:
    glow.inputs['Strength'].default_value = .12
elif hasattr(glow, 'mix'):
    glow.mix = -.88
tree.links.new(rl.outputs['Image'], glow.inputs['Image'])
tree.links.new(glow.outputs['Image'], comp.inputs['Image'])

GOLD = mat('24k gold - reflective', (.83,.47,.075), 1, .2, coat=1)
STEEL = mat('Brushed vault steel', (.19,.23,.25), 1, .2, coat=1)
DARK = mat('Blackened steel', (.025,.035,.038), .88, .27)
WHITE = mat('White typography', (1,1,1), emission=2.3)
GREEN = mat('Neon #00FF41', (0,1,.051), emission=3)
PINK = mat('Neon #FF0055', (1,0,.091), emission=3)
GRAY = mat('Muted type', (.20,.20,.20), emission=.7)

cam_data = bpy.data.cameras.new('Dollar camera')
cam_data.lens = 50
cam_data.sensor_fit = 'VERTICAL'
cam_data.sensor_height = 36
cam_data.clip_start = .01
cam_data.clip_end = 300
camera = link(bpy.data.objects.new('Dollar camera', cam_data))
scene.camera = camera
camera.rotation_mode = 'QUATERNION'
# A camera looking down -Z with local +Y up; Z-axis zoom is literal.
q_front = Quaternion((1,0,0,0))


def key_camera(t, position, rotation, interpolation='BEZIER'):
    set_curve(camera, 'location', t, position, interpolation)
    set_curve(camera, 'rotation_quaternion', t, rotation, interpolation)


def look_at(pos, target):
    return (Vector(target)-Vector(pos)).to_track_quat('-Z','Y')

# Scene 1: source Z zoom from 10 to 2 at 2s, then toward 0.1 by 8s.
key_camera(0, (0,0,10), q_front)
key_camera(2, (0,0,2), q_front)
key_camera(5, (0,0,2), q_front)
key_camera(7.983333, (0,0,.1), q_front, 'CONSTANT')
# Scenes 2/3: Three.js (x,y,z) -> Blender (x,-z,y); preserves world up.
def orbit_pose(t):
    if t < 18:
        x = max(0, min(1, (t-15)/2.8))
        e = 4*x*x*x if x < .5 else 1-((-2*x+2)**3)/2
        angle = math.pi/4*e
    else:
        age = max(0, min(10,t-18))
        angle = math.pi/4 + .0125*age*age
    pos = Vector((math.sin(angle)*11, -math.cos(angle)*11, .4))
    rot = look_at(pos, (0,0,.25))
    if t >= 28:
        u = max(0, min(1,(t-28)/.2))
        rot = Quaternion((0,0,1), math.pi/2*u**5) @ rot
    return pos, rot
# Dense analytic sampling reproduces the orbit and fifth-power whip.
for f in range(frame(8), frame(28.2)+1):
    t = (f-1)/FPS
    pos, rot = orbit_pose(t)
    key_camera(t, pos, rot, 'LINEAR')
end_pos, end_rot = orbit_pose(28.2)
# Scene 4 preserves the precise end position and rotation. Camera then pushes .65.
key_camera(28.2, end_pos, end_rot)
key_camera(32, end_pos, end_rot)
key_camera(33.2, end_pos + end_rot @ Vector((0,0,-.65)), end_rot)
key_camera(37.983333, end_pos + end_rot @ Vector((0,0,-.65)), end_rot, 'CONSTANT')
# Scene 5 and Scene 6 separate shots.
key_camera(38, (0,0,10), q_front)
key_camera(47.983333, (0,0,10), q_front)
key_camera(48.283333, (0,0,2), q_front, 'CONSTANT')
key_camera(48.3, (0,0,9), q_front)
key_camera(59.983333, (0,0,9), q_front)

# --- Scene 1 [0, 8.1): dollar -> particles and headline --------------------
s1 = make_stage('01 HOOK')
rig(s1)
dollar = text('Hook 3D dollar', '$', (0,0,0), 2.0, GREEN, s1)
pop(dollar, 0, .4)
show_tree(s1, 0, 2.0)
# Three headline lines keep the established 2 / 2.1 / 2.2s entrances.
for i,(body,y,material,size) in enumerate([
        ('WHY IS THE', .90, WHITE, .58), ('DOLLAR',0,GREEN,.90), ('KING?',-.92,PINK,.90)]):
    o = overlay(body,y,size,material,2+i*.1,8.1,'Hook '+body)
    animate(o, 'location', [(2+i*.1,((-2.4 if i==0 else (2.4 if i==2 else 0)),y,-7)), (2.65+i*.1,(0,y,-7))])
    pop(o,2+i*.1,.5)
    animate(o, 'scale', [(5,(1,1,1)), (8,(12,12,12))])
# Burst dots are real geometry and follow the 2s breakup.
burst1 = make_stage('01 dollar particles')
for i in range(100):
    a = random.random()*2*math.pi
    r = random.uniform(.1,.8)
    o = sphere('Hook particle', (r*math.cos(a),r*math.sin(a),0), .025, GREEN, burst1, 12, 6)
    v = Vector((math.cos(a)*random.uniform(1,4), math.sin(a)*random.uniform(1,4), random.uniform(-1,1)))
    p = o.location.copy()
    animate(o,'location',[(2,p),(3.2,p+v)])
show_tree(burst1,2,4)

# --- Scene 2 [8, 18): oil/balance transforms to globe ---------------------
s2 = make_stage('02 BALANCE')
s2.rotation_euler.x=math.pi/2  # stage local Y-up -> Blender world Z-up
rig(s2)
balance = empty('Balance assembly', parent=s2)
cube('Balance base', (0,-1.75,0), (2.5,.18,.75), STEEL, balance)
cylinder('Balance column', (0,-.25,0), .14, 2.8, STEEL, balance, axis='Y')
beam = empty('Tilting balance beam', (0,1.15,0), balance)
cube('Balance beam', (0,0,0), (4.0,.14,.2), STEEL, beam)
for x in (-1.7,1.7):
    line('Pan suspension',[(x,0,0),(x,-.9,0)],.024,STEEL,beam)
    cylinder('Pan', (x,-.95,0), .63,.12,STEEL,beam,axis='Y')
barrel = empty('Oil barrel falling',(-1.7,2.6,0),beam)
cylinder('Oil barrel', (0,0,0), .40,1.05,DARK,barrel,axis='Y')
for y in (-.47,-.23,.23,.47):
    cylinder('Barrel reinforcing hoop',(0,y,0),.43,.045,STEEL,barrel,axis='Y')
text('Barrel mark','OIL',(0,0,.415),.27,WHITE,barrel)
cube('Dollar bill', (1.7,-.65,0), (1.05,.54,.1), GREEN,beam)
text('Bill sign','$',(1.7,-.65,.07),.45,DARK,beam)
animate(barrel,'location',[(8,(-1.7,2.6,0)),(8.85,(-1.7,-.35,0)),(9.05,(-1.7,.05,0)),(9.2,(-1.7,-.35,0))])
animate(beam,'rotation_euler',[(8.45,(0,0,0)),(9.1,(0,0,.30))])
animate(balance,'scale',[(15.05,(1,1,1)),(15.85,(.001,)*3)])
show_tree(s2,8,15.85)
# Typewriter: individual extruded characters staggered at 14 characters/sec.
phrase='> OIL = DOLLARS'
for i,ch in enumerate(phrase):
    if ch==' ': continue
    o=overlay(ch,-2.0,.38,GREEN,12+i/14,15.3,'Oil text %02d'%i, x=(i-(len(phrase)-1)/2)*.25)
    pop(o,12+i/14,.12)
# Wireframe globe persists into Scene 3; same object, not a substitute.
s23 = make_stage('02-03 SHARED GLOBE')
s23.rotation_euler.x=math.pi/2
rig(s23)
globe = sphere('Shared FX globe',(0,.38,0),1.38,GREEN,s23,64,32)
wire = globe.modifiers.new('Geographic lattice','WIREFRAME')
wire.thickness = .008
wire.use_replace = True
animate(globe,'scale',[(15.35,(.001,)*3),(16.6,(1,1,1))])
animate(globe,'rotation_euler',[(15,(0,0,0)),(28.2,(0,0,(28.2-15)*.18))], 'LINEAR')
show_tree(s23,15.35,28.2)
# Particle transition: deterministic positions and explicit keyframes.
cloud = make_stage('02 oil-to-globe particles')
cloud.rotation_euler.x=math.pi/2
for i in range(180):
    a=random.uniform(0,2*math.pi);z=random.uniform(-1,1);r=math.sqrt(1-z*z)
    p0=Vector((-1.7+random.uniform(-.4,.4),-.5+random.uniform(-.5,.5),random.uniform(-.4,.4)))
    p1=p0+Vector((random.uniform(-2,2),random.uniform(-2,2),random.uniform(-1,1)))
    p2=Vector((1.38*r*math.cos(a),.38+1.38*z,1.38*r*math.sin(a)))
    o=sphere('Transition particle',p0,.022,GREEN,cloud,12,6)
    animate(o,'location',[(15,p0),(15.75,p1),(17.4,p2)])
show_tree(cloud,15,19.2)
# Arc curves grow over the shared globe from the USA to three regions.
network = empty('FX arcs',parent=globe)
def direction(lat,lon):
    p=math.radians(lat);l=math.radians(lon+122)
    return Vector((math.cos(p)*math.sin(l),math.sin(p),math.cos(p)*math.cos(l)))
a=direction(38.9,-77)
for lat,lon in [(50.1,8.7),(35.7,139.7),(24.7,46.7)]:
    b=direction(lat,lon)
    pts=[]
    for i in range(65):
        u=i/64
        pts.append(tuple((a.lerp(b,u)).normalized()*(1.38*(1.035+.26*math.sin(math.pi*u)))))
    route=line('FX trade route',pts,.012,GREEN,network)
    route.data.bevel_factor_end=0
    route.data.keyframe_insert(data_path='bevel_factor_end',frame=frame(18))
    route.data.bevel_factor_end=1
    route.data.keyframe_insert(data_path='bevel_factor_end',frame=frame(19.5))
    visible_between(route,18,28.2)
    endpoint=sphere('Market node',tuple(b*(1.38*1.025)),.05,WHITE,network)
    visible_between(endpoint,19.5,28.2)
stat=overlay('88%', .35, 1.35, GREEN,22,28,'FX statistic')
pop(stat,22,.9)
sub=overlay('OF ALL FX TRADES',-.55,.34,WHITE,25,28,'FX explanatory line')
animate(sub,'location',[(25,(0,-.85,-7)),(25.65,(0,-.55,-7))])

# --- Scene 4 [28.2, 38): bank vault; parented to exact final whip pose ------
from mathutils import Matrix
stage4_matrix = Matrix.Translation(end_pos + end_rot @ Vector((0,0,-10.8))) @ end_rot.to_matrix().to_4x4()
s4 = make_stage('04 VAULT, continuous camera',stage4_matrix)
rig(s4)
area('Vault specular strip',(-1,2,4),(0,-.5,0),450,(1,.81,.47),(3,.6),s4)
# Camera-local XY is the front face, local +Z points toward camera.
cube('Vault rear', (0,0,-.8),(4.3,4.5,.25),DARK,s4)
for x in (-2.0,2.0): cube('Vault jamb',(x,0,-.2),(.28,4.6,1.1),STEEL,s4)
for y in (-2.15,2.15): cube('Vault jamb',(0,y,-.2),(4.25,.28,1.1),STEEL,s4)
cube('Vault shelf',(0,-1.3,-.1),(4.0,.12,1.0),STEEL,s4)
# Hinged circular door: cylinders and boolean-cut bolt holes.
hinge=empty('Door hinge',(-1.9,0,.50),s4)
door=cylinder('Circular vault door',(1.9,0,0),1.84,.32,STEEL,hinge,vertices=128)
# Boolean holes in the door plate (evaluated at render time).
for i in range(8):
    a=i*2*math.pi/8
    cutter=cylinder('Bolt bore cutter',(1.9+1.55*math.cos(a),1.55*math.sin(a),0),.085,.6,DARK,hinge,vertices=24,bevel=0)
    cutter.hide_render=True
    cutter.hide_set(True)
    mod=door.modifiers.new('Precision bolt bore %02d'%i,'BOOLEAN')
    mod.operation='DIFFERENCE';mod.object=cutter
    cylinder('Inset bolt head',(1.9+1.55*math.cos(a),1.55*math.sin(a),.17),.065,.06,GOLD,hinge,vertices=32)
cylinder('Door wheel boss',(1.9,0,.22),.23,.18,STEEL,hinge)
for i in range(8):
    a=i*math.pi/4
    line('Wheel spoke',[(1.9,0,.34),(1.9+1.0*math.cos(a),1.0*math.sin(a),.34)],.045,STEEL,hinge)
    sphere('Wheel grip',(1.9+1.02*math.cos(a),1.02*math.sin(a),.34),.09,GOLD,hinge)
# Source uses -90 degrees to closed over 28.0-28.6.
animate(hinge,'rotation_euler',[(28,(0,-math.pi/2,0)),(28.6,(0,0,0))])
# Animate the door out at 31.8-32.6 for the cutaway; bars remain.
animate(hinge,'scale',[(31.8,(1,1,1)),(32.6,(.001,)*3)])
gold_items=[]
for i in range(6):
    row,col=divmod(i,3);x=(col-1)*.94;y=-.96+row*.46
    bar=cube('Gold ingot %02d'%i,(x,y+.93,.05),(.87,.38,.69),GOLD,s4,bevel=.065)
    animate(bar,'location',[(32+i*.1,(x,y+.93,.05)),(32.48+i*.1,(x,y-.05,.05)),(32.6+i*.1,(x,y,.05))])
    # Engraved-style inset stamp, positioned on the front-facing face.
    stamp=text('Ingot hallmark','999.9',(0,0,.351),.12,DARK,bar)
    gold_items.append((bar,stamp,i))
# Shield outline scales in as in the source.
shield=empty('Safe-haven shield',(0,0,-.45),s4)
line('Shield edge',[(0,1.8,0),(1.45,1.15,0),(1.3,-.4,0),(0,-1.9,0),(-1.3,-.4,0),(-1.45,1.15,0),(0,1.8,0)],.025,GREEN,shield)
pop(shield,35,.8)
show_tree(s4,28.2,37.8)
for bar,stamp,i in gold_items:
    visible_between(bar,32+i*.1,37.8)
    visible_between(stamp,32+i*.1,37.8)
# Fix cutter visibility AFTER show_tree, which otherwise keys all children.
for o in hinge.children:
    if o.name.startswith('Bolt bore cutter'):
        o.animation_data_clear();o.hide_render=True;o.hide_set(True)
bonds=overlay('US TREASURY BONDS',1.45,.31,GREEN,32,37.8,'Treasury bonds')
safe=overlay('THE ULTIMATE SAFE HAVEN',-1.5,.30,WHITE,35,37.8,'Safe haven')
pop(safe,35,.7)

# --- Scene 5 [38, 48.3): challengers -> dollar impact and text -------------
s5=make_stage('05 CHALLENGERS')
rig(s5)
for i,(label,start) in enumerate([('¥',(-3,0,0)),('€',(3,0,0)),('₿',(0,4.82,0))]):
    root=empty('Currency challenger '+label,start,s5)
    if i<2:
        cube('Currency block',(0,0,0),(1.25,1.25,.38),PINK,root,bevel=.1)
    else:
        cylinder('Crypto coin',(0,0,0),.66,.28,PINK,root,vertices=96)
    text('Currency mark '+label,label,(0,0,.21),.8,WHITE,root)
    animate(root,'location',[(38,start),(42.5,(0,0,0))])
    animate(root,'scale',[(42.5,(1,1,1)),(42.75,(.001,)*3)])
strike=text('Dominant dollar','$',(0,2.1,0),2.55,GREEN,s5)
animate(strike,'location',[(42,(0,2.1,0)),(42.5,(0,0,0))])
show_tree(s5,38,48.3)
visible_between(strike,42,48.3)
shards=make_stage('05 collision shards')
for i in range(100):
    a=random.random()*math.tau;speed=random.uniform(.5,4)
    o=cube('Collision shard',(0,0,0),(.07,.07,.07),PINK,shards,bevel=.01)
    animate(o,'location',[(42.5,(0,0,0)),(44.3,(math.cos(a)*speed,math.sin(a)*speed-1.5,random.uniform(-1,1)))])
    animate(o,'scale',[(42.5,(1,1,1)),(44.3,(.001,)*3)])
show_tree(shards,42.5,44.3)
liquidity=overlay('NOT ENOUGH LIQUIDITY',-1.6,.36,WHITE,45,48.3,'Liquidity warning')
pop(liquidity,45,.25)

# --- Scene 6 [48.3,60): crown, declaration and call-to-action --------------
s6=make_stage('06 CROWN')
rig(s6)
crown=empty('Rotating crown',(0,.9,0),s6)
# High-segment, thick ring and five triangular prongs.
cylinder('Crown base',(0,-.55,0),1.3,.23,GREEN,crown,vertices=128,axis='Y')
for i in range(5):
    a=i*math.tau/5
    x=1.22*math.sin(a);z=1.22*math.cos(a)
    line('Crown prong',[(x,-.5,z),(x*.75,.25,z*.75),(x,1.05,z)],.085,GREEN,crown)
    sphere('Crown jewel',(x,1.05,z),.12,WHITE,crown)
animate(crown,'scale',[(48.3,(.001,)*3),(49.1,(1.1,)*3),(49.3,(1,)*3)])
animate(crown,'rotation_euler',[(48.3,(0,0,0)),(60,(0,math.tau,0))],'LINEAR')
show_tree(s6,48.3,57.35)
for i,(body,y,material,size) in enumerate([('THERE',-.65,WHITE,.45),('IS NO',-1.05,GRAY,.45),('ALTERNATIVE.',-1.50,GREEN,.49)]):
    o=overlay(body,y,size,material,53+i*.2,57.35,'Closing '+body)
    animate(o,'location',[(53+i*.2,(0,y-.22,-7)),(53.6+i*.2,(0,y,-7))])
    pop(o,53+i*.2,.6)
dot=overlay('•',.05,.42,GREEN,57,60,'Pulsing CTA dot')
for i in range(3):
    animate(dot,'scale',[(57+i,(1,1,1)),(57.5+i,(1.3,1.3,1.3)),(58+i,(1,1,1))])
follow=overlay('Follow for more.',-.55,.28,WHITE,57,60,'Follow CTA')
pop(follow,57,1)

# Single-frame hard flashes. Camera-facing plane is self-lit and independent of lighting.
def flash(name, material, t):
    o=cube(name,(0,0,-1),(.8,1.2,.001),material,camera,bevel=0)
    # The plane is sized above the camera frustum at z=-1.
    visible_between(o,t,t+1/FPS)
    return o
flash('28s white flash',WHITE,28)
flash('48s green flash',GREEN,48)
scene.frame_set(1)
print('Built scene %r: frames 1..3600, 1080x1920, 60 fps, engine %s.' % (scene.name,scene.render.engine))
print('Motion blur shutter 0.5 frame = 180 degrees where supported by the engine.')
if CI_MODE and os.environ.get('DOLLAR_BUILD_ONLY') != '1':
    print('GitHub Actions: rendering frames', scene.frame_start, 'through', scene.frame_end, 'to', scene.render.filepath, flush=True)
    bpy.ops.render.render(animation=True, scene=scene.name)
else:
    print('No frames rendered. Save the .blend and use the optional block below.')

# -------------------------------------------------------------------------
# OPTIONAL RENDER BLOCK -- run separately in Blender's Python Console after
# executing this script and saving the .blend.  This produces 0001.png through
# 3600.png in the specified directory. It can take many hours or longer.
#
# import bpy
# s = bpy.data.scenes['DollarFilm']
# s.render.filepath = bpy.path.abspath('//dollar_frames/')  # save .blend first
# bpy.context.window.scene = s
# bpy.ops.render.render(animation=True, scene=s.name)
# -------------------------------------------------------------------------
