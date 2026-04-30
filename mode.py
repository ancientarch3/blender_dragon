#mode.py

import bpy

def set_mode(mode):
    #switch to a specific mode
    #ignore if the mode we want is already set
    if bpy.context.mode != mode:
        try:
            bpy.ops.object.mode_set(mode=mode)
        except RuntimeError:
            if mode != 'OBJECT':
                raise

def ensure_object_mode():
    set_mode('OBJECT')

def ensure_edit_mode():
    set_mode('EDIT')

def ensure_pose_mode():
    set_mode('POSE')