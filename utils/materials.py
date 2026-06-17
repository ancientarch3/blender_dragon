import bpy, sys
from pathlib import Path

def add_color(name, r, g, b, a):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes

    principled = nodes.get('Principled BSDF')

    principled.inputs['Base Color'].default_value = (r, g, b, a)
    principled.inputs['Emission Color'].default_value = (r, g, b, a)
    principled.inputs['Emission Strength'].default_value = 0.55

    principled.inputs['Metallic'].default_value = 0.0
    principled.inputs['Roughness'].default_value = 0.85
    principled.inputs['Specular IOR Level'].default_value = 0.2

    return mat



def create_scales(
        name,
        scales=(13.000, 13.000, 13.000),
        colors=[(0.0, 0.0, 0.0, 1.0), (0.0, 0.037, 0.0, 1.0), (0.0, 0.224, 0.0, 1.0)],
        positions=[0.600, 0.884, 1.000]
):
    # create a material to hold our scales
    scales_mat = bpy.data.materials.new(name=name)
    scales_mat.use_nodes = True
    scales_nodes = scales_mat.node_tree.nodes
    scales_links = scales_mat.node_tree.links

    # create a texture image node
    tex_img_node = scales_nodes.new(type='ShaderNodeTexImage')
    mod_dir = Path(__file__).resolve().parent
    dragon_dir = mod_dir.parent
    file_path = dragon_dir / "scales.jpg"
    scales_image = bpy.data.images.load(str(file_path))
    tex_img_node.image = scales_image
    tex_img_node.projection = 'BOX'

    # create a mapping node
    mapping_node = scales_nodes.new(type='ShaderNodeMapping')
    mapping_node.inputs['Scale'].default_value = scales

    # create a texture coordinate node
    tex_coord_node = scales_nodes.new(type='ShaderNodeTexCoord')
    tex_coord_node.from_instancer = True

    # create a color ramp node
    color_ramp_node = scales_nodes.new(type='ShaderNodeValToRGB')
    cr = color_ramp_node.color_ramp

    # add a new color stop to the color ramp
    cr.elements.new(position=0.5)

    # set the colors and positions for all color stops
    cr.elements[0].color = colors[0]
    cr.elements[1].color = colors[1]
    cr.elements[2].color = colors[2]

    cr.elements[0].position = positions[0]
    cr.elements[1].position = positions[1]
    cr.elements[2].position = positions[2]

    # set the links between the nodes
    scales_links.new(tex_coord_node.outputs['Generated'], mapping_node.inputs['Vector'])
    scales_links.new(mapping_node.outputs['Vector'], tex_img_node.inputs['Vector'])
    scales_links.new(tex_img_node.outputs['Color'], color_ramp_node.inputs['Fac'])

    # get the Principled BSDF node and link the color ramp to it
    principled_bsdf_node = scales_nodes.get('Principled BSDF')
    scales_links.new(color_ramp_node.outputs['Color'], principled_bsdf_node.inputs['Base Color'])

    if 'Subsurface Color' in principled_bsdf_node.inputs:
        scales_links.new(color_ramp_node.outputs['Color'], principled_bsdf_node.inputs['Subsurface Color'])

    if 'Subsurface' in principled_bsdf_node.inputs:
        principled_bsdf_node.inputs['Subsurface'].default_value = 1.0
    elif 'Subsurface Weight' in principled_bsdf_node.inputs:
        principled_bsdf_node.inputs['Subsurface Weight'].default_value = 1.0

    return scales_mat



"""Comments for things that I changed
#def add_color(name, r, g, b, a):
#    mat = bpy.data.materials.new(name=name)
#    mat.use_nodes = True

#    principled_bsdf_node = mat.node_tree.nodes.get('Principled BSDF')
#    principled_bsdf_node.inputs['Base Color'].default_value = (r, g, b, a)
#    principled_bsdf_node.inputs['27'].default_value = (r, g, b, a)
#    principled_bsdf_node.inputs['28'].default_value = 1.0

#    return mat

"""
