#modifiers.py

import bpy
from .mode import ensure_object_mode

def add_skin_modifier():
    #adds a skin modifier to the active object and returns the modifier
    bpy.ops.object.modifier_add(type='SKIN')
    obj = bpy.context.object
    mod = obj.modifiers[-1]
    return mod

def add_subsurf_modifier(levels = 1):
#adds a subdivision surface modifier to the active object and returns the modifier
    bpy.ops.object.modifier_add(type='SUBSURF')
    obj = bpy.context.object
    mod = obj.modifiers[-1]
    mod.levels = levels
    return mod


def add_mirror_modifier(
    #adds a mirror modifier to the active object and returns the modifier
    use_axis = (True, False, False),
    use_bisect_axis = (True, False, False),
    use_bisect_flip_axis = (False, False, False),
    use_clip = True,
    merge_threshold = 0.0001,
    use_mirror_vertex_groups = True
):

# Add a mirror modifier and return the modifier
    bpy.ops.object.modifier_add(type='MIRROR')
    obj = bpy.context.object
    mod = obj.modifiers[-1]
    mod.use_axis = use_axis
    mod.use_bisect_axis = use_bisect_axis
    mod.use_bisect_flip_axis = use_bisect_flip_axis
    mod.use_clip = use_clip
    mod.merge_threshold = merge_threshold
    mod.use_mirror_vertex_groups = use_mirror_vertex_groups
    return mod


#solidify modifier
def add_solidify_modifier(thickness = 0.1, offset = -1):
    #adds a solidify modifier to the active object and returns the modifier
    bpy.ops.object.modifier_add(type='SOLIDIFY')
    obj = bpy.context.object
    mod = obj.modifiers[-1]
    mod.thickness = thickness
    mod.offset = offset
    return mod

def apply_modifiers(obj_name):
    ensure_object_mode()
    obj = bpy.data.objects.get(obj_name)
    bpy.context.view_layer.objects.active = obj
    
    for m in obj.modifiers:
        bpy.ops.object.modifier_apply(modifier=m.name)

    return obj
