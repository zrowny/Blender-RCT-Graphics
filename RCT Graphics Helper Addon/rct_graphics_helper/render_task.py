'''
Copyright (c) 2021 RCT Graphics Helper developers

For a complete list of all authors, please refer to the addon's meta info.
Interested in contributing? Visit https://github.com/oli414/Blender-RCT-Graphics

RCT Graphics Helper is licensed under the GNU General Public License version 3.
'''

from collections import namedtuple
from enum import Enum
import bpy
import math
import os
import subprocess
import shutil

from bpy.types import PARTICLE_PT_velocity
from . json_functions import JsonImage
from . import json_functions


def get_res_path(path):
    """Returns the absolute path of something in the Add-on's `res` folder

    Args:
        path (str): A path to something in the Add-on's `res` folder
    """
    script_file = os.path.realpath(__file__)
    directory = os.path.dirname(script_file) + "/res/"
    return directory + path


def get_output_path(path):
    """Returns the absolute path of something in the .blend's `output` folder

    Args:
        path (str): the path of something in the `output` folder
    """
    rawpath = bpy.path.abspath("//output/" + path)  # type: str
    return rawpath


def rename(filename, new_filename):
    """Renames a file, replacing if the new name already exists

    Args:
        filename (str): Absolute path to the file
        new_filename (str): Absolute path with the file's new name
    """
    filename = os.path.normpath(filename)
    new_filename = os.path.normpath(new_filename)
    try:
        if os.path.exists(new_filename):
            os.remove(new_filename)
    except:
        print("Cannot rename %s, perhaps %s is in use? Continuing with old image" % (
            bpy.path.relpath(filename), bpy.path.relpath(new_filename)))
        return
    os.rename(filename, new_filename)


def config_compositor_nodes(render_layer="Normal"):
    """Configures the compositing nodes for separating saving remappable layers

    Args:
        render_layer (str, optional): The name of the Render Layer to use for compositing.
        Defaults to "Normal".
    """
    scene = bpy.context.scene
    scene.use_nodes = True
    tree = scene.node_tree
    groups = bpy.data.node_groups
    links = tree.links

    rct_remap_out = groups.get("RCT_RemapOutput")
    if rct_remap_out is None:
        rct_remap_out = groups.new("RCT_RemapOutput", 'CompositorNodeTree')
        group_links = rct_remap_out.links
        inputs_node = rct_remap_out.nodes.new('NodeGroupInput')
        inputs_node.location = (0, -400)
        rct_remap_out.inputs.new('NodeSocketColor', "Image")
        rct_remap_out.inputs.new('NodeSocketInt', "ID Value")
        rct_remap_out.inputs[0].default_value = [0.0, 0.0, 0.0, 0.0]
        rct_remap_out.inputs[1].default_value = -1
        file_out_node = rct_remap_out.nodes.new(
            'CompositorNodeOutputFile')  # type: bpy.types.CompositorNodeOutputFile
        file_out_node.location = (800, -250)
        file_out_node.base_path = "//output/TMP/"
        file_out_node.file_slots[0].path = "noremap/"
        for i in range(1, 4):
            file_out_node.file_slots.new("remap%s/" % i)
        
        id_node = rct_remap_out.nodes.new('CompositorNodeIDMask')  # type: bpy.types.CompositorNodeIDMask
        id_node.index = 0
        id_node.location = (175, 50)
        alpha_node = rct_remap_out.nodes.new('CompositorNodeSetAlpha')  # type: bpy.types.CompositorNodeSetAlpha
        alpha_node.location = (500, 0)
        separate_node = rct_remap_out.nodes.new('CompositorNodeSepRGBA')  # type: bpy.types.CompositorNodeSepRGBA
        separate_node.location = (175, -100)
        math_node = rct_remap_out.nodes.new('CompositorNodeMath')  # type: bpy.types.CompositorNodeMath
        math_node.location = (400, 0)
        math_node.operation = 'MINIMUM'
        
        group_links.new(input=inputs_node.outputs[0], output=alpha_node.inputs[0])
        group_links.new(input=inputs_node.outputs[0], output=separate_node.inputs[0])
        group_links.new(input=inputs_node.outputs[1], output=id_node.inputs[0])
        group_links.new(input=id_node.outputs[0], output=math_node.inputs[0])
        group_links.new(input=separate_node.outputs['A'], output=math_node.inputs[1])
        group_links.new(input=math_node.outputs[0], output=alpha_node.inputs[1])
        group_links.new(input=alpha_node.outputs[0], output=file_out_node.inputs[0])
        for i in range(1, 4):
            id_node = rct_remap_out.nodes.new('CompositorNodeIDMask')  # type: bpy.types.CompositorNodeIDMask
            id_node.index = i
            id_node.location = (300, i * -250)
            alpha_node = rct_remap_out.nodes.new('CompositorNodeSetAlpha')  # type: bpy.types.CompositorNodeSetAlpha
            alpha_node.location = (500, i * -250)
            group_links.new(input=inputs_node.outputs[0], output=alpha_node.inputs[0])
            group_links.new(input=inputs_node.outputs[1], output=id_node.inputs[0])
            group_links.new(input=id_node.outputs[0], output=alpha_node.inputs[1])
            group_links.new(input=alpha_node.outputs[0], output=file_out_node.inputs[i])
            
    for node in tree.nodes:
        tree.nodes.remove(node)
    
    render_layers = tree.nodes.new('CompositorNodeRLayers')  # type: bpy.types.CompositorNodeRLayers
    rct_remap_out_node = tree.nodes.new('CompositorNodeGroup')  # type: bpy.types.CompositorNodeGroup
    rct_remap_out_node.node_tree = rct_remap_out
    rct_remap_out_node.location = (250, 0)
    links.new(render_layers.outputs[0], rct_remap_out_node.inputs[0])
    links.new(render_layers.outputs.get("IndexMA"), rct_remap_out_node.inputs[1])
    render_layers.layer = render_layer


class Angle(namedtuple("Angle", ["rot", "x", "y", "z"])):
    """Describes a tuple of angles. All angles are in degrees

    Args:
        rot (float): Vertical rotation around the object. Defaults to 0.
        x (float): Rotation around x-axis (pitch). Defaults to 0.
        y (float): Rotation around y-axis (roll). Defaults to 0.
        z (float): Rotation around z-axis (yaw). Defaults to 0.
    """
    __slots__ = ()


class AngleSection(namedtuple("AngleSection", ["is_diagonal", "num_angles", "x", "y", "z"])):
    """Describes a section of angles. All angles are in degrees

    Args:
        is_diagonal (boolean): Vertical rotation around the object. Defaults to 0.
        num_angles (int): Vertical rotation around the object. Defaults to 0.
        x (float): Rotation around x-axis (pitch). Defaults to 0.
        y (float): Rotation around y-axis (roll). Defaults to 0.
        z (float): Rotation around z-axis (yaw). Defaults to 0.
    """
    __slots__ = ()

    @property
    def angles(self):
        angles = []
        rot = 0
        if self.is_diagonal:
            rot = 45
        rot_step = 0
        if self.num_angles == 2:
            rot_step = 90
        else:
            rot_step = 360 / self.num_angles
        for i in range(self.num_angles):
            angles.append(Angle(rot, self.x, self.y, self.z))
            rot += rot_step
        return angles


def render(context, filename):
    """Renders a frame in blender, outputting with the given filename"""
    bpy.data.scenes['Scene'].render.filepath = "//output/TMP/" + filename
    bpy.ops.render.render(write_still=True)
    return


def rotate_for_vertical_joint(x, y, modifier=1):
    '''Returns a list of x and y

    :param x: X offset
    :type x: float
    :param y: Y offset
    :type y: float
    :param modifier: Scales
    :type modifier: float

    '''

    vertical_joint = bpy.data.objects['RCT_VerticalJoint']
    if vertical_joint is None:
        return False
    angle = -vertical_joint.rotation_euler[2] * modifier
    return [round(x * math.cos(angle) - y * math.sin(angle)),
            round(x * math.sin(angle) + y * math.cos(angle))]


def position_cookie_cutter(context, x, y, left, right, enable):
    """Positions the cookie cutter object."""
    cookie_cutter = bpy.data.objects['CookieCutter']
    if cookie_cutter is None:
        return False
    cookie_cutter_floor = bpy.data.objects['CookieCutterFloor']
    if cookie_cutter_floor is None:
        return False
    vertical_joint = bpy.data.objects['VerticalJoint']
    if vertical_joint is None:
        return False
    cookie_cutter_floor.hide_render = not enable
    angle = vertical_joint.rotation_euler[2]
    cookie_cutter.location[1] = - \
        (x * math.cos(angle) - y * math.sin(angle)) * 4
    cookie_cutter.location[0] = - \
        (x * math.sin(angle) + y * math.cos(angle)) * 4
    cookie_cutter.location[2] = 0

    cookie_cutter_l = bpy.data.objects['CookieCutterLeft']
    if cookie_cutter_l is None:
        return False
    cookie_cutter_l.hide_render = not left
    cookie_cutter_r = bpy.data.objects['CookieCutterRight']
    if cookie_cutter_r is None:
        return False
    cookie_cutter_r.hide_render = not right
    return True


def rotate_rig(angle: Angle):
    """Rotates the RCT rig to the specified angles

    Args:
        angle (Angle): A (named) tuple containing (rot, x, y, z) in degrees

    Returns:
        boolean: True if rig was rotated
    """
    
    object = bpy.data.objects['RCT_Rig']
    if object is None:
        return False
    if type(angle) != Angle:
        angle = Angle._make(angle)
    object.rotation_euler = (math.radians(angle.x), math.radians(angle.y), math.radians(angle.z))
    vJoint = bpy.data.objects['RCT_VerticalJoint']  # type: bpy.types.Object
    vJoint.rotation_euler = (0, 0, math.radians(angle.rot))
    return True


def reset_rig():
    """Resets the RCT rig angle"""
    rotate_rig((0, 0, 0, 0))


def post_render(images_start, total_images, remap, context, offset=(0, 0)):
    """Runs the post render palettization process

    Args:
        images_start (int): Index of the starting image
        total_images (int): Total number of images to process
        remap (int): -1 for mask; 0 for no remap colors; 1, 2, or 3 for remap
        context (bpy.types.Context): bpy context
    """
    gmic = "gmic"
    gmic_script_path = get_res_path("remap.gmic")
    
    no_remap_palette_path = get_res_path("noremap1.png")
    full_palette_path = get_res_path("full.png")
    preview_path = get_output_path("preview/")
    images_path = get_output_path("images/")
    if not os.path.exists(preview_path):
        os.mkdir(preview_path)
    if not os.path.exists(images_path):
        os.mkdir(images_path)
    
    dither_threshold = context.scene.rct_graphics_helper_general_properties.dither_threshold
    edge_darkening = context.scene.rct_graphics_helper_general_properties.edge_darkening
    blur_amount = 0
    positions = []
    if remap > 0:
        if remap == 2:
            no_remap_palette_path = get_res_path("noremap2.png")
        if remap == 3:
            no_remap_palette_path = get_res_path("noremap3.png")
        remap1_palette_path = get_res_path("remap1.png")
        remap2_palette_path = get_res_path("remap2.png")
        remap3_palette_path = get_res_path("remap3.png")
        remap1_images = []
        remap2_images = []
        remap3_images = []
        noremap_images = []

        # Cut off Blender's frame number
        base_path = get_output_path("TMP/noremap/")
        old_image_names = os.listdir(base_path)
        for old_image_name in old_image_names:
            new_image_path = base_path + old_image_name[:10]
            rename(base_path + old_image_name, new_image_path)
            noremap_images.append(new_image_path)
        # Do the same for all applicable remap images
        base_path = get_output_path("TMP/remap1/")
        old_image_names = os.listdir(base_path)
        for old_image_name in old_image_names:
            new_image_path = base_path + old_image_name[:10]
            rename(base_path + old_image_name, new_image_path)
            remap1_images.append(new_image_path)
        if remap > 1:
            base_path = get_output_path("TMP/remap2/")
            old_image_names = os.listdir(base_path)
            for old_image_name in old_image_names:
                new_image_path = base_path + old_image_name[:10]
                rename(base_path + old_image_name, new_image_path)
                remap2_images.append(new_image_path)
            if remap > 2:
                base_path = get_output_path("TMP/remap3/")
                old_image_names = os.listdir(base_path)
                for old_image_name in old_image_names:
                    new_image_path = base_path + old_image_name[:10]
                    rename(base_path + old_image_name, new_image_path)
                    remap3_images.append(new_image_path)
        
        # Palettize with gmic...
        process = subprocess.run([
            gmic, '-verbose', '0', no_remap_palette_path, *noremap_images, gmic_script_path,
            'IndexAllNoRemap[^0]', '[0],%s,%s,%s' % (dither_threshold, edge_darkening, blur_amount),
            '-OutputOffset[^0]', '%s,%s' % (images_start, get_output_path('TMP/noremap/Indexed'))])
        # print("the commandline is {}".format(subprocess.list2cmdline(process.args)))
        process = subprocess.run([
            gmic, '-verbose', '0', remap1_palette_path, *remap1_images, gmic_script_path,
            'IndexAllRemap[^0]', '[0],%s,%s,%s' % (dither_threshold, edge_darkening, blur_amount),
            '-OutputOffset[^0]', '%s,%s' % (images_start, get_output_path('TMP/remap1/Indexed'))])
        if remap > 1:
            process = subprocess.run([
                gmic, '-verbose', '0', remap2_palette_path, *remap2_images, gmic_script_path,
                'IndexAllRemap[^0]', '[0],%s,%s,%s' % (dither_threshold, edge_darkening, blur_amount),
                '-OutputOffset[^0]', '%s,%s' % (images_start, get_output_path('TMP/remap2/Indexed'))])
            if remap > 2:
                process = subprocess.run([
                    gmic, '-verbose', '0', remap3_palette_path, *remap3_images, gmic_script_path,
                    'IndexAllRemap[^0]', '[0],%s,%s,%s' % (dither_threshold, edge_darkening, blur_amount),
                    '-OutputOffset[^0]', '%s,%s' % (images_start, get_output_path('TMP/remap3/Indexed'))])

        for animation_frame in range(images_start, total_images + images_start):
            indexed_paths = [get_output_path("TMP/noremap/Indexed%s.png" % animation_frame)]
            indexed_paths.append(get_output_path("TMP/remap1/Indexed%s.png" % animation_frame))
            if remap > 1:
                indexed_paths.append(get_output_path("TMP/remap2/Indexed%s.png" % animation_frame))
                if remap > 2:
                    indexed_paths.append(get_output_path("TMP/remap3/Indexed%s.png" % animation_frame))
            out_path = get_output_path("images/%s.png" % animation_frame)
            preview_image = get_output_path("preview//%s.png" % animation_frame)
            process = subprocess.run([gmic, '-verbose', '0', full_palette_path, *indexed_paths, gmic_script_path,
                                     'Compose[^0]', '[0]', '-o[1]', out_path, '-o[2]', preview_image],
                                     stdout=subprocess.PIPE)
            # print("the commandline is {}".format(subprocess.list2cmdline(process.args)))
            a = process.stdout.decode('utf-8')[:-1]
            positions.extend(a.split('\n'))
    
    elif remap == 0:
        for animation_frame in range(images_start, total_images + images_start):
            frame = str(animation_frame).zfill(6)
            image_path = get_output_path("TMP/" + frame + ".png")
            process = subprocess.run([
                gmic, '-verbose', '0', full_palette_path, no_remap_palette_path, image_path, gmic_script_path,
                'IndexAllNoRemap[2]', '[1],{},{},{}'.format(dither_threshold, edge_darkening, blur_amount),
                'Compose[2]', '[0]', '-o[2]', get_output_path('images/%s.png' % animation_frame), '-o[3]',
                get_output_path('preview/%s.png' % animation_frame)], stdout=subprocess.PIPE)
            
            a = process.stdout.decode('utf-8')[:-1]
            positions.extend(a.split('\n'))
    # Create mask image from alpha
    else:
        images = []
        for animation_frame in range(images_start, total_images + images_start):
            frame = str(animation_frame).zfill(6)
            images.append(get_output_path("TMP/" + frame + ".png"))
        process = subprocess.run([
            gmic, '-verbose', '0', *images, gmic_script_path, '-Mask', '55', '-OutputOffset',
            '%s,%s' % (images_start, images_path), '-OutputOffset',
            '%s,%s' % (images_start, preview_path)], stdout=subprocess.PIPE)
        a = process.stdout.decode('utf-8')[:-1]
        positions.extend(a.split('\n'))
    
    json_images = json_functions.json_data.get("images", [])
    for i in range(total_images):
        path = "images/%s.png" % (i + images_start)
        # print("Position %s: %s" % (i + images_start, positions[i]))
        x, y = positions[i].split(',')
        json_images.append(JsonImage(path, int(x) + offset[0], int(y) + offset[1]))

    # print(json_images)
    json_functions.json_data["images"] = json_images
    # output_path = get_output_path(context, index)


RenderTaskSection = namedtuple(
    'RenderTaskSection',
    'angles remap render_layer scene_layers animation_index animation_count x_tiles y_tiles blank offset')


class RenderTaskSectionWorker(object):
    """Defines a worker that renders an image in a section on each step."""
    blank = False  # If true, just add a blank image instead of rendering
    
    angles = []  # List of Angles
    angle_index = 0  # Curent index into list of Angles
    total_angles = 4  # Total Angles to render

    anim_start = 0  # The starting animation frame
    anim_index = 0  # Current animation frame
    total_anim = 1  # Total animation frames to render

    x_index = 0  # Current indexes into tile grid
    y_index = 0  #
    total_x = 1  # Total tiles (x and y)
    total_y = 1  #

    images_start = 0  # Starting index to use for images out
    image_index = 0  # Current index to use for an image
    total_images = 1  # Total images to render

    status = "CREATED"
    context = None  # type: bpy.context
    render_layer = ""
    remap = 0
    offset = (0, 0)

    scene_layers = []
    has_sub_tiles = False

    def __init__(self, section_in: RenderTaskSection, out_index_start, context):
        self.blank = section_in.blank
        self.images_start = out_index_start
        self.image_index = self.images_start
        if not self.blank:
            self.angles = section_in.angles
            self.remap = section_in.remap
            self.render_layer = section_in.render_layer
            self.scene_layers = section_in.scene_layers
            self.anim_start = section_in.animation_index
            self.total_anim = section_in.animation_count
            self.total_x = section_in.x_tiles
            self.total_y = section_in.y_tiles
            self.offset = section_in.offset
            self.frame = None
            self.angle_index = 0
            self.total_angles = len(self.angles)
            self.anim_index = self.anim_start
            self.total_images = self.total_angles * self.total_anim * self.total_x * self.total_y
            self.status = "CREATED"
            self.context = context
            self.x_index = 0
            self.y_index = 0
            self.has_sub_tiles = self.total_x > 1 or self.total_y > 1
            config_compositor_nodes(self.render_layer)

    def step(self):
        if self.blank:
            json_images = json_functions.json_data.get("images", [])
            json_images.append("")
            json_functions.json_data["images"] = json_images
            self.image_index += 1
            self.status = "FINISHED"
            return "FINISHED"
        if self.angle_index == self.total_angles:
            self.angle_index = 0
            self.anim_index += 1
        if self.anim_index == self.total_anim:
            self.anim_index = self.anim_start
            self.x_index += 1
        if self.has_sub_tiles:
            if self.x_index == self.total_x:
                self.x_index = 0
                self.y_index += 1
            if self.y_index == self.total_y:
                self.y_index = 0
        
        # print("Current index: %s (going to %s), with %s total images this run" % (
        #     self.image_index, self.images_start + self.total_images - 1, self.total_images))

        # Set up scene for this image
        rotate_rig(self.angles[self.angle_index])
        self.context.scene.frame_set(self.anim_index)
        if self.has_sub_tiles:
            pass

        # Set up render
        self.context.scene.layers = [i in self.scene_layers for i in range(20)]
        render_layers = self.context.scene.render.layers
        for layer in render_layers:
            layer.use = False
        render_layers.get(self.render_layer).use = True
        if self.remap > 0:
            self.context.scene.use_nodes = True
            self.context.scene.node_tree.nodes.get("Render Layers").layer = self.render_layer
            file_out_node = bpy.data.node_groups.get('RCT_RemapOutput').nodes["File Output"]
            filename = str(self.image_index).zfill(6) + ".png"
            file_out_node.file_slots[0].path = "noremap/" + filename
            file_out_node.file_slots[1].path = "remap1/" + filename
            file_out_node.file_slots[2].path = "remap2/" + filename
            file_out_node.file_slots[3].path = "remap3/" + filename
            render(self.context, filename)
        else:
            self.context.scene.use_nodes = False
            filename = str(self.image_index).zfill(6) + ".png"
            render(self.context, filename)

        self.angle_index += 1
        self.image_index += 1
        if self.image_index >= self.total_images + self.images_start:
            # print("Finished: %s out of %s total" % (self.image_index, self.total_images))
            post_render(self.images_start, self.total_images, self.remap, self.context, self.offset)
            self.status = "FINISHED"
            return "FINISHED"
        self.status = "RUNNING"
        return "RUNNING"


class RenderTask(object):
    """Defines a list of render "sections" to use for rendering."""
    out_index = 0
    sections = []
    section_index = 0
    status = "CREATED"
    section_task = None
    context = None
    use_antialiasing = False

    def __init__(self, context, out_index_start=0):
        """Creates a new RenderTask object

        :param out_index_start: index to use for first rendered image
        :type rotAngle: int
        """

        self.out_index = out_index_start
        self.sections = []
        self.section_index = 0
        self.status = "CREATED"
        self.section_task = None
        self.context = context
        self.use_antialiasing = context.scene.render.use_antialiasing

    def add(self, angles=[Angle(0, 0, 0, 0)], remap=0, render_layer="", scene_layers=[0, 10],
            animation_frame_index=0, animation_frame_count=1, x_tiles=1, y_tiles=1, blank=False, offset=(0, 0)):
        """Adds a render task section

        Args:
            angles (list[Angle], optional): list of Angles for this section
            remap (int, optional): If >0, the number of remappable colors. If 0, a normal image
                with no remappable colors. If -1, renders a flat mask. Defaults to 0.
            render_layer (str, optional): Name of the render layer to use. Defaults to "".
            scene_layers (list[int], optional): List of the scene layers to have enabled for this
                section. Defaults to [0, 10].
            frame_index (int, optional): Index to use for first rendered image. Defaults to 0.
            frame_count (int, optional): Number of frames to render. Defaults to 1.
            x_tiles (int, optional): (for large scenery) The number of tiles in the x direction
                to render. Defaults to 1.
            y_tiles (int, optional): (for large scenery) The number of tiles in the y direction
                to render. Defaults to 1.
            blank (boolean, optional): If set, all other options are ignored and a blank image is
                added instead.
        """
        
        self.sections.append(
            RenderTaskSection(angles, remap, render_layer, scene_layers,
                              animation_frame_index, animation_frame_count, x_tiles, y_tiles, blank, offset))

    def step(self):
        if self.section_task is None:
            # print(self.sections)
            if self.sections == []:
                self.status = "FINISHED"
                return "FINISHED"
            section = self.sections[self.section_index]
            self.section_task = RenderTaskSectionWorker(section, self.out_index, self.context)

        result = self.section_task.step()
        self.out_index = self.section_task.image_index

        if result == "FINISHED":
            self.section_task = None
            self.section_index += 1

            if self.section_index == len(self.sections):
                self.status = "FINISHED"
                return "FINISHED"
