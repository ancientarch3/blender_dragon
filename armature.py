#armature.py

import bpy
from math import radians

def set_bone_rotation(arm_obj, bone_name, x_deg=0, y_deg=0, z_deg=0):
    bpy.context.view_layer.objects.active = arm_obj
    bone = arm_obj.pose.bones[bone_name]
    bone.rotation_mode = 'XYZ'
    bone.rotation_euler = (
        radians(x_deg),
        radians(y_deg),
        radians(z_deg)
    )