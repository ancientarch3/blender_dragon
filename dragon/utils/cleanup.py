#cleanup.py

import bpy

def clear_scene():
    
    #remove all objects from the scene
    objects = list(bpy.data.objects)
    for obj in objects:
        bpy.data.objects.remove(obj, do_unlink=True)

    #remove any orphans
    for datablock in (
        bpy.data.meshes, bpy.data.materials, bpy.data.textures,
        bpy.data.images, bpy.data.curves, bpy.data.armatures,
        bpy.data.grease_pencils
    ):
        for datab in list(datablock):
            datablock.remove(datab)
