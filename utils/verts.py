#verts.py

import bpy

def deselect_all_verts(bm):
    # Verify bm is Bmesh

    if not bm or not hasattr(bm, 'verts'):
        raise ValueError('Expected a valid Bmesh object')
    
    bm.verts.ensure_lookup_table()
    for v in bm.verts:
        v.select = False

    bm.select_history.clear()

def extrude_vert(mesh, vert, translate_coords): #translate_coords = how much we moved to the new point
    deselect_all_verts(mesh)
    vert.select = True
    bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":translate_coords})
    mesh.verts.index_update()
    mesh.verts.ensure_lookup_table()
    new_vert = next((v for v in mesh.verts if v.select), None)
    return new_vert


def set_use_root(use_root_index, vert_indices, mesh):
    if not mesh or not hasattr(mesh, 'verts'):
        raise ValueError('Expected a valid Bmesh object')
    
    skin_layer = mesh.verts.layers.skin.verify()
    mesh.verts.ensure_lookup_table()
    for i in vert_indices:
        mesh.verts[i][skin_layer].use_root = False

    #m.verts.ensure_lookup_table()
    mesh.verts[use_root_index][skin_layer].use_root = True
