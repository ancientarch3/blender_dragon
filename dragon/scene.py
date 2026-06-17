import bpy, bmesh
import mathutils
from .utils.mode import ensure_edit_mode, ensure_object_mode
from .utils.verts import deselect_all_verts, extrude_vert, set_use_root
from .utils.mesh import create_object, set_active_object, set_flat_shading
from .utils.modifiers import add_skin_modifier, add_subsurf_modifier, add_mirror_modifier, add_solidify_modifier, apply_modifiers
from .utils.materials import add_color, create_scales
from mathutils import Vector
from .utils.armature import set_bone_rotation

wf_indices = []


# OSRS

def apply_osrs_look():
    set_flat_shading('DragonBody')
    set_flat_shading('DragonLegs')
    set_flat_shading('DragonClaws')
    set_flat_shading('DragonWingBones')
    set_flat_shading('DragonWebbing')
    set_flat_shading('DragonHorns')
    set_flat_shading('DragonSplines')
    set_flat_shading('DragonEyes')
    set_flat_shading('DragonEyelids')


# dragon parts

def build_dragon():
    create_dragon_body()
    create_dragon_legs()
    create_dragon_wings()
    create_dragon_wing_webbing()
    create_dragon_horns()
    create_dragon_splines()
    create_dragon_eyes()
    create_dragon_claws()
    add_dragon_colors()
    add_dragon_scales()
    apply_osrs_look()
    create_wing_armature()
    create_wing_animation()
    

# Creates the main dragon body by starting at the snout and extruding backward

def create_dragon_body():
    body_vert_indices = []
    
    body_mesh, body_obj = create_object('DragonBodyMesh', 'DragonBody')

    set_active_object(body_obj)
    ensure_edit_mode()
    bm = bmesh.from_edit_mesh(body_mesh)

    # Starting point for the snout
    v0 = bm.verts.new((0, 6.5, 4.5))
    bm.verts.index_update()
    body_vert_indices.append(v0.index)

    # shape snout, body
    translate_coords = [
        (0, -1.8, -0.20),
        (0, -1.2, -1.35),
        (0, -1.5, -0.85),
        (0, -2.0, -0.2),
        (0, -2.0, 0.3),
        (0, -2.0, -0.8),
        (0, -3.0, -1.0),
        (0, -2.5, -0.4),
    ]

    deselect_all_verts(bm)
    cv = v0
    for tc in translate_coords:
        v = extrude_vert(bm, cv, tc)
        if v:
            bm.verts.index_update()
            body_vert_indices.append(v.index)
            cv = v
            bmesh.update_edit_mesh(body_mesh, loop_triangles=False, destructive=False)

    body_obj.data.update()
    ensure_object_mode()

    add_mirror_modifier()
    add_skin_modifier()
    add_subsurf_modifier(levels=1)

    # thickness of body
    radii = [
        (0.50, 0.75),
        (0.85, 0.55),
        (1.05, 0.95),
        (1.95, 1.50),
        (1.3, 1.1),
        (1.4, 1.3),
        (1.0, 0.8),
        (0.4, 0.4),
        (0.1, 0.1),
    ]

    skin_layer = body_obj.data.skin_vertices[0].data
    for i, r in zip(body_vert_indices, radii):
        skin_layer[i].radius = r

    body_obj.data.update()
    bpy.context.view_layer.update()


# Creates the front and back legs as separate vertex
def create_dragon_legs():
    leg_mesh, leg_obj = create_object('DragonLegsMesh', 'DragonLegs')

    set_active_object(leg_obj)

    add_mirror_modifier()
    add_skin_modifier()

    subsurf = leg_obj.modifiers.new(name="Subsurf", type='SUBSURF')
    subsurf.levels = 1

    # leg values, and thickness
    legs = [
        {
            "start": (0.75, 1.2, 2.3),
            "steps": [
                (0.00,  0.00, -1.85),
                (0.00,  0.12, -0.70),
                (0.00,  0.38,  0.00),
            ],
            "radii": [
                (0.72, 0.72),
                (0.52, 0.52),
                (0.28, 0.22),
                (0.24, 0.16),
            ]
        },
        {
            "start": (0.90, -2.0, 2.3),
            "steps": [
                (0.00,  0.00, -2.10),
                (0.00,  0.14, -0.78),
                (0.00,  0.38,  0.00),
            ],
            "radii": [
                (0.90, 0.90),
                (0.62, 0.62),
                (0.34, 0.26),
                (0.28, 0.18),
            ]
        }
    ]

    for leg in legs:
        add_leg(leg_obj, leg["start"], leg["steps"], leg["radii"], is_root=True)


# Adds one leg by extruding
def add_leg(obj, start_coords, steps, radii, is_root=False):
    set_active_object(obj)

    ensure_edit_mode()
    me = obj.data
    bm = bmesh.from_edit_mesh(me)
    bm.verts.ensure_lookup_table()

    skin_layer = bm.verts.layers.skin.verify()

    current_v = bm.verts.new(start_coords)
    leg_verts = [current_v]

    if is_root:
        current_v[skin_layer].use_root = True

    for offset in steps:
        new_pos = (
            current_v.co[0] + offset[0],
            current_v.co[1] + offset[1],
            current_v.co[2] + offset[2]
        )
        next_v = bm.verts.new(new_pos)
        bm.edges.new((current_v, next_v))
        current_v = next_v
        leg_verts.append(current_v)

    bm.verts.index_update()
    indices = [v.index for v in leg_verts]

    bmesh.update_edit_mesh(me, loop_triangles=False, destructive=False)
    ensure_object_mode()

    skin_data = obj.data.skin_vertices[0].data
    for idx, r_val in zip(indices, radii):
        skin_data[idx].radius = r_val

    obj.data.update()
    bpy.context.view_layer.update()


# Creates the wing bone structure
def create_dragon_wings():
    wb_mesh, wb_obj = create_object('DragonWingBonesMesh', 'DragonWingBones')

    set_active_object(wb_obj)

    add_mirror_modifier()
    add_skin_modifier()
    add_subsurf_modifier(levels=1)

    ensure_edit_mode()
    wbme = wb_obj.data
    wbbm = bmesh.from_edit_mesh(wbme)

    v_shoulder = wbbm.verts.new((0.55, 1.95, 3.15))
    v_elbow = extrude_vert(wbbm, v_shoulder, (1.95, -0.20, 1.40))
    v_tip = extrude_vert(wbbm, v_elbow, (2.55, 0.15, -0.25))

    # wing fingers
    finger_offsets = [
        (0.80, -3.40, -2.90),
        (1.95, -2.55, -2.15),
        (2.85, -1.25, -1.15)
    ]

    finger_verts = []
    for offset in finger_offsets:
        vf = extrude_vert(wbbm, v_elbow, offset)
        if vf:
            finger_verts.append(vf)

    wbbm.verts.index_update()
    skin_layer = wbbm.verts.layers.skin.verify()

    for v in wbbm.verts:
        v[skin_layer].use_root = (v == v_shoulder)

    v_shoulder[skin_layer].radius = (0.28, 0.28)
    v_elbow[skin_layer].radius = (0.16, 0.16)
    v_tip[skin_layer].radius = (0.03, 0.03)

    for vf in finger_verts:
        vf[skin_layer].radius = (0.02, 0.02)

    bmesh.update_edit_mesh(wbme)
    ensure_object_mode()

    bpy.context.view_layer.update()


# wing webbing / fingers
def create_dragon_wing_webbing():
    web_mesh, web_obj = create_object('DragonWebbingMesh', 'DragonWebbing')
    
    set_active_object(web_obj)
    ensure_edit_mode()
    bm = bmesh.from_edit_mesh(web_mesh)

    # wing bone coor
    elbow = (2.50, 1.75, 4.55)
    shoulder = (0.55, 1.95, 3.15)

    tips_coords = [
        (3.30, -1.65, 1.65),
        (4.45, -0.80, 2.40),
        (5.35, 0.50, 3.40),
        (4.90, 2.50, 4.10)
    ]

    v_elbow = bm.verts.new(elbow)
    v_shoulder = bm.verts.new(shoulder)
    v_tips = [bm.verts.new(co) for co in tips_coords]

    bm.faces.new((v_shoulder, v_elbow, v_tips[0]))

    for i in range(len(v_tips) - 1):
        bm.faces.new((v_elbow, v_tips[i], v_tips[i + 1]))

    bmesh.update_edit_mesh(web_mesh)
    ensure_object_mode()

    add_mirror_modifier()

    solid = web_obj.modifiers.new(name="Solidify", type='SOLIDIFY')
    solid.thickness = 0.02

    add_subsurf_modifier(levels=1)

    bpy.context.view_layer.update()


# horn then mirror on other side
def create_dragon_horns():
    ensure_object_mode()
    horn_indices = []

    horn_mesh, horn_obj = create_object('DragonHornsMesh', 'DragonHorns')

    set_active_object(horn_obj)
    ensure_edit_mode()
    hmesh = horn_obj.data
    hbmesh = bmesh.from_edit_mesh(hmesh)

    hbmesh.verts.ensure_lookup_table()

    v0 = hbmesh.verts.new((0.5, 4.5, 4.8))
    hbmesh.verts.index_update()
    horn_indices.append(v0.index)

    cv = v0

    # horn points
    horn_translate_coords = [
        (0.2, 0.3, -1.0),
        (0.1, 0.3, 1.0),
        (0.05, 0.3, 1.2),
        (0.03, 0.25, 0.55)  
    ]

    for htc in horn_translate_coords:
        v = extrude_vert(hbmesh, cv, htc)
        if v:
            hbmesh.verts.index_update()
            horn_indices.append(v.index)
            cv = v

    skin_layer = hbmesh.verts.layers.skin.verify()
    for v in hbmesh.verts:
        v[skin_layer].use_root = (v.index == horn_indices[0])

    bmesh.update_edit_mesh(hmesh)
    ensure_object_mode()

    add_skin_modifier()
    add_subsurf_modifier(levels=1)
    add_mirror_modifier()

    horn_radii = [
        (0.30, 0.30),
        (0.24, 0.24),
        (0.16, 0.16),
        (0.07, 0.07),
        (0.01, 0.01)
    ]

    skin_layer = horn_obj.data.skin_vertices[0].data

    for i, r in zip(horn_indices, horn_radii):
        skin_layer[i].radius = r

    horn_obj.data.update()
    bpy.context.view_layer.update()


# spikes down body
def create_dragon_splines():
    ensure_object_mode()

    spike_data = [
        (3.6, 4.0, 1.0),
        (2.7, 3.2, 1.6),
        (1.8, 3.1, 1.6),
        (1.0, 3.0, 1.5),
        (0.2, 3.0, 1.5),
        (-0.6, 3.0, 1.4),
        (-1.6, 3.0, 1.3),
        (-2.6, 2.7, 1.3),
        (-3.6, 2.2, 1.5),
        (-4.6, 1.8, 1.4),
        (-5.8, 1.3, 1.35),
        (-7.0, 0.6, 1.3),
        (-8.4, 0.3, 1.2),
    ]

    spike_base_half_width = 0.2

    spline_mesh, spline_obj = create_object('DragonSplinesMesh', 'DragonSplines')

    set_active_object(spline_obj)
    ensure_edit_mode()
    splme = spline_obj.data
    splbm = bmesh.from_edit_mesh(splme)

    for y, base_z, height in spike_data:
        v_front = splbm.verts.new((0, y + spike_base_half_width, base_z))
        v_back = splbm.verts.new((0, y - spike_base_half_width, base_z))
        v_peak = splbm.verts.new((0, y, base_z + height))
        splbm.faces.new((v_front, v_back, v_peak))

    bmesh.update_edit_mesh(splme)
    ensure_object_mode()

    add_solidify_modifier(thickness=0.04, offset=0)

    spline_obj.data.update()
    bpy.context.view_layer.update()


# eye mesh
def create_dragon_eyes():
    ensure_object_mode()
    eye_mesh, eye_obj = create_object('DragonEyesMesh', 'DragonEyes')

    set_active_object(eye_obj)
    ensure_edit_mode()
    bpy.ops.mesh.primitive_ico_sphere_add(enter_editmode=False, align='WORLD', location=(0.4, 5.3, 4.8), scale=(0.2, 0.2, 0.2))

    ensure_object_mode()
    sub1_mod = add_subsurf_modifier(levels = 5)
    mirr_mod = add_mirror_modifier()

    eyelid_mesh, eyelid_obj = create_object('DragonEyelidsMesh', 'DragonEyelids')

    set_active_object(eyelid_obj)
    ensure_edit_mode()
    elme = eyelid_obj.data
    elbm = bmesh.from_edit_mesh(elme)

    eyelid_indices = []

    # eyelid placement
    eyelid_coords = [
        (0.24, 5.28, 4.79),
        (0.40, 5.27, 4.81),
        (0.56, 5.28, 4.79),

        (0.25, 5.39, 4.90),
        (0.40, 5.36, 5.00),
        (0.55, 5.39, 4.90)
    ]

    elbm.verts.ensure_lookup_table()

    eyelid_faces = [
        [0, 1, 4, 3],
        [1, 2, 5, 4],
    ]

    for co in eyelid_coords:
        v = elbm.verts.new(co)
        elbm.verts.index_update()
        eyelid_indices.append(v.index)

    for fi in eyelid_faces:
        deselect_all_verts(elbm)
        for i in range(0, len(fi)):
            vi = fi[i]
            elbm.verts[vi].select = True

        bpy.ops.mesh.edge_face_add()
        deselect_all_verts(elbm)
    
    ensure_object_mode()
    sub2_mod = add_subsurf_modifier(levels = 3)
    mir2_mod = add_mirror_modifier()


# claws or the legs
def create_dragon_claws():
    claw_mesh, claw_obj = create_object('DragonClawsMesh', 'DragonClaws')

    set_active_object(claw_obj)
    add_mirror_modifier()
    add_skin_modifier()
    add_subsurf_modifier(levels=1)

    foot_claw_sets = [
        {
            "foot_coords": (0.75, 1.60, -0.25),
            "claws": [
                {"start_offset": (-0.08, 0.00, 0.00), "segments": [(0.00, 0.18, -0.08), (0.00, 0.18, -0.09), (0.00, 0.12, -0.07)]},
                {"start_offset": ( 0.00, 0.02, 0.00), "segments": [(0.00, 0.22, -0.10), (0.00, 0.20, -0.10), (0.00, 0.13, -0.08)]},
                {"start_offset": ( 0.08, 0.00, 0.00), "segments": [(0.00, 0.18, -0.08), (0.00, 0.18, -0.09), (0.00, 0.12, -0.07)]},
            ]
        },
        {
            "foot_coords": (0.90, -1.57, -0.58),
            "claws": [
                {"start_offset": (-0.08, 0.00, 0.00), "segments": [(0.00, 0.18, -0.08), (0.00, 0.18, -0.09), (0.00, 0.12, -0.07)]},
                {"start_offset": ( 0.00, 0.02, 0.00), "segments": [(0.00, 0.22, -0.10), (0.00, 0.20, -0.10), (0.00, 0.13, -0.08)]},
                {"start_offset": ( 0.08, 0.00, 0.00), "segments": [(0.00, 0.18, -0.08), (0.00, 0.18, -0.09), (0.00, 0.12, -0.07)]},
            ]
        }
    ]

    for foot_set in foot_claw_sets:
        for claw in foot_set["claws"]:
            add_claw(
                claw_obj,
                foot_coords=foot_set["foot_coords"],
                start_offset=claw["start_offset"],
                segment_offsets=claw["segments"]
            )


# add one claw
def add_claw(obj, foot_coords, start_offset, segment_offsets):
    set_active_object(obj)

    ensure_edit_mode()
    me = obj.data
    bm = bmesh.from_edit_mesh(me)
    bm.verts.ensure_lookup_table()

    skin_layer = bm.verts.layers.skin.verify()
    new_indices = []

    base_pos = (
        foot_coords[0] + start_offset[0],
        foot_coords[1] + start_offset[1],
        foot_coords[2] + start_offset[2]
    )

    claw_base = bm.verts.new(base_pos)
    claw_base[skin_layer].use_root = True

    bm.verts.index_update()
    new_indices.append(claw_base.index)

    cv = claw_base
    for offset in segment_offsets:
        next_pos = (
            cv.co.x + offset[0],
            cv.co.y + offset[1],
            cv.co.z + offset[2]
        )

        next_v = bm.verts.new(next_pos)
        bm.edges.new((cv, next_v))
        cv = next_v

        bm.verts.index_update()
        new_indices.append(cv.index)

    bmesh.update_edit_mesh(me, loop_triangles=False, destructive=False)
    ensure_object_mode()

    skin_data = obj.data.skin_vertices[0].data

    # claw thickness
    claw_radii = [
        (0.11, 0.07),
        (0.08, 0.05),
        (0.04, 0.025),
        (0.01, 0.008),
    ]

    for idx, radius in zip(new_indices, claw_radii):
        skin_data[idx].radius = radius

    obj.data.update()
    bpy.context.view_layer.update()


# colors for dragon parts
def add_dragon_colors():
    body_mat = add_color('MithrilBody', 0.45, 0.52, 0.78, 1.0)
    dark_body_mat = add_color('MithrilDark', 0.32, 0.38, 0.62, 1.0)
    wing_bone_mat = add_color('WingBoneBlue', 0.25, 0.30, 0.50, 1.0)
    wing_web_mat = add_color('WingWebDark', 0.15, 0.20, 0.28, 1.0)
    claw_mat = add_color('ClawBlack', 0.02, 0.02, 0.02, 1.0)
    eye_mat = add_color('EyeRed', 0.75, 0.08, 0.05, 1.0)

    bpy.data.objects['DragonBody'].data.materials.append(body_mat)
    bpy.data.objects['DragonLegs'].data.materials.append(dark_body_mat)
    bpy.data.objects['DragonSplines'].data.materials.append(body_mat)
    bpy.data.objects['DragonHorns'].data.materials.append(dark_body_mat)

    bpy.data.objects['DragonWingBones'].data.materials.append(wing_bone_mat)
    bpy.data.objects['DragonWebbing'].data.materials.append(wing_web_mat)

    bpy.data.objects['DragonEyes'].data.materials.append(eye_mat)
    bpy.data.objects['DragonClaws'].data.materials.append(claw_mat)


# scale mats
def add_dragon_scales():
    mat = create_scales(
        name='DragonBodyScales',
        scales=(2.7, 10, 10),
        colors=[
            (0.25, 0.30, 0.50, 1.0),
            (0.45, 0.52, 0.78, 1.0),
            (0.60, 0.68, 0.90, 1.0)
        ],
        positions=[0.55, 0.82, 1.0]
    )
    body_obj = apply_modifiers('DragonBody')
    body_obj.data.materials[0] = mat

    wb_mat = create_scales(
        name='DragonWingBoneScales',
        colors=[
            (0.18, 0.22, 0.40, 1.0),
            (0.30, 0.36, 0.60, 1.0),
            (0.48, 0.54, 0.80, 1.0)
        ]
    )
    wb_obj = apply_modifiers('DragonWingBones')
    wb_obj.data.materials[0] = wb_mat

    leg_mat = create_scales(
        name='DragonLegScales',
        scales=(3, 3, 3),
        colors=[
            (0.22, 0.28, 0.48, 1.0),
            (0.38, 0.45, 0.70, 1.0),
            (0.55, 0.62, 0.85, 1.0)
        ]
    )
    leg_obj = apply_modifiers('DragonLegs')
    leg_obj.data.materials[0] = leg_mat

    el_scales_mat = create_scales(
        name='DragonEyelidScales',
        scales=(0.500, 0.900, 3.000),
        colors=[
            (0.30, 0.36, 0.58, 1.0),
            (0.48, 0.55, 0.78, 1.0),
            (0.65, 0.72, 0.92, 1.0)
        ]
    )
    eyelid_obj = apply_modifiers('DragonEyelids')
    eyelid_obj.data.materials.append(el_scales_mat)

    spl_scales_mat = create_scales(
        name='DragonSpikeScales',
        scales=(2.000, 1.000, 3.000),
        colors=[
            (0.35, 0.42, 0.65, 1.0),
            (0.55, 0.62, 0.85, 1.0),
            (0.75, 0.82, 0.95, 1.0)
        ]
    )
    spline_obj = apply_modifiers('DragonSplines')
    spline_obj.data.materials[0] = spl_scales_mat


# Creates the wing armature bones
def create_wing_armature():
    ensure_object_mode()

    wb_obj = bpy.data.objects.get('DragonWingBones')
    web_obj = bpy.data.objects.get('DragonWebbing')

    if wb_obj is None:
        print("DragonWingBones not found")
        return None

    # match wing mesh
    shoulder = Vector((0.55, 1.95, 3.15))
    elbow    = Vector((2.50, 1.75, 4.55))
    tip      = Vector((5.05, 1.90, 4.30))

    finger_1 = Vector((3.30, -1.65, 1.65))
    finger_2 = Vector((4.45, -0.80, 2.40))
    finger_3 = Vector((5.35,  0.50, 3.40))

    bpy.ops.object.armature_add(location=(0, 0, 0))
    arm_obj = bpy.context.object
    arm_obj.name = 'WingArmature'
    arm_obj.data.name = 'WingArmatureData'

    bpy.context.view_layer.objects.active = arm_obj
    ensure_edit_mode()

    edit_bones = arm_obj.data.edit_bones

    if "Bone" in edit_bones:
        edit_bones.remove(edit_bones["Bone"])

    # Main wing bones are created first, then the finger bones branch from the elbow
    bone_root = edit_bones.new("wing_root.R")
    bone_root.head = shoulder
    bone_root.tail = elbow

    bone_tip = edit_bones.new("wing_tip.R")
    bone_tip.head = elbow
    bone_tip.tail = tip
    bone_tip.parent = bone_root
    bone_tip.use_connect = True

    bone_f1 = edit_bones.new("wing_finger_1.R")
    bone_f1.head = elbow
    bone_f1.tail = finger_1
    bone_f1.parent = bone_root

    bone_f2 = edit_bones.new("wing_finger_2.R")
    bone_f2.head = elbow
    bone_f2.tail = finger_2
    bone_f2.parent = bone_root

    bone_f3 = edit_bones.new("wing_finger_3.R")
    bone_f3.head = elbow
    bone_f3.tail = finger_3
    bone_f3.parent = bone_root

    ensure_object_mode()

    # mirror mod
    bpy.context.view_layer.objects.active = arm_obj
    arm_obj.select_set(True)
    ensure_edit_mode()
    bpy.ops.armature.select_all(action='SELECT')
    bpy.ops.armature.symmetrize()
    ensure_object_mode()

    bpy.ops.object.select_all(action='DESELECT')

    if wb_obj is not None:
        wb_obj.select_set(True)
    if web_obj is not None:
        web_obj.select_set(True)

    arm_obj.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj

    # Parents the wing bones and webbing to the armature so they move with it
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.update()

    return arm_obj


# Animates the wings by rotating the armature bones at different frames
def create_wing_animation():
    arm = bpy.data.objects.get('WingArmature')

    bpy.context.view_layer.objects.active = arm
    arm.select_set(True)
    bpy.ops.object.mode_set(mode='POSE')

    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 120

    # animation frames
    flap_frames = [1, 15, 30, 45, 60, 75, 90, 105, 120]

    for frame in flap_frames:
        bpy.context.scene.frame_set(frame)

        # Resets the bone
        for bone in arm.pose.bones:
            bone.rotation_mode = 'XYZ'
            bone.rotation_euler = (0, 0, 0)

        # Down stroke
        if frame in [15, 45, 75, 105]:
            set_bone_rotation(arm, 'wing_root.R', -25, -10, 35)
            set_bone_rotation(arm, 'wing_tip.R', -20, 0, 20)
            set_bone_rotation(arm, 'wing_finger_1.R', -15, -5, 20)
            set_bone_rotation(arm, 'wing_finger_2.R', -15, 0, 15)
            set_bone_rotation(arm, 'wing_finger_3.R', -15, 5, 10)

            set_bone_rotation(arm, 'wing_root.L', -25, 10, -35)
            set_bone_rotation(arm, 'wing_tip.L', -20, 0, -20)
            set_bone_rotation(arm, 'wing_finger_1.L', -15, 5, -20)
            set_bone_rotation(arm, 'wing_finger_2.L', -15, 0, -15)
            set_bone_rotation(arm, 'wing_finger_3.L', -15, -5, -10)

        # Up stroke
        elif frame in [30, 60, 90, 120]:
            set_bone_rotation(arm, 'wing_root.R', 20, -5, -25)
            set_bone_rotation(arm, 'wing_tip.R', 15, 0, -15)
            set_bone_rotation(arm, 'wing_finger_1.R', 10, -5, -10)
            set_bone_rotation(arm, 'wing_finger_2.R', 10, 0, -8)
            set_bone_rotation(arm, 'wing_finger_3.R', 10, 5, -5)

            set_bone_rotation(arm, 'wing_root.L', 20, 5, 25)
            set_bone_rotation(arm, 'wing_tip.L', 15, 0, 15)
            set_bone_rotation(arm, 'wing_finger_1.L', 10, 5, 10)
            set_bone_rotation(arm, 'wing_finger_2.L', 10, 0, 8)
            set_bone_rotation(arm, 'wing_finger_3.L', 10, -5, 5)

        # rotate bones
        for bone in arm.pose.bones:
            bone.keyframe_insert(data_path='rotation_euler', frame=frame)

    bpy.ops.object.mode_set(mode='OBJECT')
