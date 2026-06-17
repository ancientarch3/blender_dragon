# mesh.py
# create's object in Scene collection

import bpy
from .mode import ensure_object_mode

def create_object(mesh_name, obj_name):
    mesh = bpy.data.meshes.new(mesh_name)
    obj = bpy.data.objects.new(obj_name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    return mesh, obj

def set_active_object(obj):
    ensure_object_mode()
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

def set_flat_shading(obj_name):
    obj = bpy.data.objects[obj_name]
    mesh = obj.data

    for poly in mesh.polygons:
        poly.use_smooth = False
