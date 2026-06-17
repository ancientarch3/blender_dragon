# dragon/__init__.py

from .utils.cleanup import clear_scene
from .utils.verts import deselect_all_verts, extrude_vert, set_use_root
from .utils.mesh import create_object, set_active_object, set_flat_shading
from .utils.modifiers import add_skin_modifier, add_subsurf_modifier, add_mirror_modifier, add_solidify_modifier, apply_modifiers
from .utils.materials import add_color
from .utils.mode import ensure_object_mode, ensure_edit_mode, set_mode

from .scene import (
    build_dragon, create_dragon_body, create_dragon_legs, add_leg,
    create_dragon_wings, create_dragon_wing_webbing,
    create_dragon_horns, create_dragon_splines,
    create_dragon_eyes, create_dragon_claws, add_claw,
    create_wing_armature, create_wing_animation
)

__all__ = [
    'build_dragon', 'create_dragon_body', 'create_dragon_legs', 'add_leg',
    'create_dragon_wings', 'create_dragon_wing_webbing',
    'create_dragon_horns', 'create_dragon_splines',
    'create_dragon_eyes', 'create_dragon_claws', 'add_claw',
    'create_wing_armature', 'create_wing_animation',

    'clear_scene', 'deselect_all_verts', 'extrude_vert', 'set_use_root',
    'create_object', 'set_active_object', 'set_flat_shading',
    'add_skin_modifier', 'add_subsurf_modifier', 'add_mirror_modifier',
    'add_solidify_modifier', 'apply_modifiers',
    'add_color',
    'ensure_object_mode', 'ensure_edit_mode', 'set_mode'
]
