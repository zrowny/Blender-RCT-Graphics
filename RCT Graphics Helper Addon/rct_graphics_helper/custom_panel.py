'''
Copyright (c) 2021 RCT Graphics Helper developers

For a complete list of all authors, please refer to the addon's meta info.
Interested in contributing? Visit https://github.com/oli414/Blender-RCT-Graphics

RCT Graphics Helper is licensed under the GNU General Public License version 3.
'''

import bpy
import math
import os

from bpy.props import CollectionProperty, IntProperty
from bpy.types import UILayout

from . render_operator import *
from . render_task import *
from . import custom_properties
from . json_functions import group_as_dict


def get_render_layers(self, context):
    """Returns a list of names of the currently defined Render Layers."""
    layers_enum = []
    for key in context.scene.render.layers.keys():
        layers_enum.append((key, key, ""))
    return layers_enum


class RenderCustom(RCTRender, bpy.types.Operator):
    """Operator to render custom defined objects."""
    bl_idname = "render.rct_custom"
    bl_label = "Render RCT Custom"
    
    def execute(self, context):
        self.scene = context.scene  # type: bpy.types.Scene
        self.custom_properties = (
            self.scene.rct_graphics_helper_custom_properties)  # type: CustomProperties
        self.renderTask = RenderTask(context, self.custom_properties.image_index)
        json_functions.json_data["properties"] = {}

        angles = AngleSection(False, self.custom_properties.num_angles, 0, 0, 0).angles
        remap = -1
        if not self.custom_properties.is_mask:
            remap = 0
            if self.custom_properties.hasTernaryColour:
                remap = 3
            elif self.custom_properties.hasSecondaryColour:
                remap = 2
            elif self.custom_properties.hasPrimaryColour:
                remap = 1
        
        scene_layers = [i for i in range(20) if self.scene.layers[i]]

        self.renderTask.add(angles, remap, "Normal", scene_layers, self.custom_properties.frameStart,
                            self.custom_properties.num_frames)
        return super().execute(context)

    def finished(self, context):
        
        super().finished(context)
        self.report({'INFO'}, 'RCT Custom render finished.')


class CustomProperties(bpy.types.PropertyGroup):
    """Defines the group of properties for custom defined objects."""
    image_index = bpy.props.IntProperty(
        name="Starting image index",
        description="The first index to use for output images",
        default=0, min=0
    )
    num_angles = bpy.props.IntProperty(
        name="Directions",
        description="The number of direction angles to use for rendering this object. If =2, renders two images at "
        "90 degrees to each other. Otherwise, the angles span 360 degrees",
        default=4, min=1
    )
    hasPrimaryColour = custom_properties.hasPrimaryColour
    hasSecondaryColour = custom_properties.hasSecondaryColour
    hasTernaryColour = custom_properties.hasTernaryColour
    is_mask = bpy.props.BoolProperty(
        name="Mask",
        description=(
            "Use this to render out a flat image mask. used for glass elements. Overrides the remap colors"),
        default=False)
    render_layer = bpy.props.EnumProperty(
        items=get_render_layers,
        name="Render Layer",
        description="The render layer to use for rendering",
    )
    frameStart = bpy.props.IntProperty(
        name="Starting animation frame",
        description=(
            "The first frame of animation to render"),
        default=0, min=0)
    num_frames = bpy.props.IntProperty(
        name="Number of animation frames",
        description=(
            "The number of animation frames to render"),
        default=1, min=1)


class CustomPanel(bpy.types.Panel):
    """Defines the drawing function for the RCT Custom panel"""
    bl_label = "RCT Custom"
    bl_idname = "RENDER_PT_rct_custom"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    @classmethod
    def poll(cls, context: bpy.types.Context):
        general_properties = context.scene.rct_graphics_helper_general_properties
        return general_properties.objectType == "custom"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        custom_properties = scene.rct_graphics_helper_custom_properties  # type: CustomProperties

        row = layout.row()
        row.operator("render.rct_custom", text="Render Custom Object")

        row = layout.row()
        row.prop(custom_properties, "image_index")
        row.prop(custom_properties, "num_angles")
        row = layout.row()
        row.prop(custom_properties, "hasPrimaryColour")
        row.prop(custom_properties, "hasSecondaryColour")
        row.prop(custom_properties, "hasTernaryColour")
        row = layout.row()
        row.prop(custom_properties, "is_mask")
        row.prop(custom_properties, "render_layer")
        row = layout.row()
        row.prop(custom_properties, "frameStart")
        row.prop(custom_properties, "num_frames")
        

def register_custom_panel():
    """Registers the custom panel and properties"""
    bpy.types.Scene.rct_graphics_helper_custom_properties = bpy.props.PointerProperty(
        type=CustomProperties)


def unregister_custom_panel():
    """Registers the custom panel and properties"""
    del bpy.types.Scene.rct_graphics_helper_custom_properties
