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

from . render_operator import RCTRender
from . render_task import *
from . import custom_properties as custom_properties
from . custom_properties import set_property
from . import json_functions as json_functions


def update_small_scenery(self, context: bpy.types.Context):
    """Run when when various small scenery properties are updated.
    
    Updates the size preview, render layers, and small scenery properties that
    may conflict with each other if they are set at the same time."""
    properties = self  # type: SmallSceneryProperties
    scene = context.scene

    update_shape(self, context)

    # Make sure render_layers are set up
    render_layers = scene.render.layers
    render_layers.new("Normal")
    render_layers.new("Glass")
    for render_layer in render_layers:
        if render_layer.name != "Normal" and render_layer.name != "Glass":
            render_layers.remove(render_layer)
    layer_normal = render_layers.get("Normal")
    layer_normal.layers = [i == 0 or i == 10 for i in range(20)]
    layer_normal.layers_zmask = [False for i in range(20)]
    layer_normal.use_pass_material_index = True
    layer_glass = render_layers.get("Glass")
    for i in range(20):
        layer_glass.layers[i] = False
        layer_glass.layers_zmask[i] = False
    layer_glass.layers = [i == 1 or i == 10 for i in range(20)]
    layer_glass.layers_zmask = [i == 0 for i in range(20)]

    # Configure special properties
    if properties.hasGlass:
        properties["isAnimated"] = False
        scene.frame_set(0)
        scene.frame_end = 0
    elif properties.isAnimated:
        if properties.animation_type == "use_frame_offsets":
            if properties.SMALL_SCENERY_FLAG_VISIBLE_WHEN_ZOOMED:
                properties["SMALL_SCENERY_FLAG17"] = False
                properties["hasOverlayImage"] = True
            elif properties.SMALL_SCENERY_FLAG17:
                properties["SMALL_SCENERY_FLAG_VISIBLE_WHEN_ZOOMED"] = False
                properties["hasOverlayImage"] = True
            else:
                properties["hasOverlayImage"] = False
            update_frameOffset_index(properties, bpy.context)
        else:
            properties["SMALL_SCENERY_FLAG17"] = False
            properties["SMALL_SCENERY_FLAG_VISIBLE_WHEN_ZOOMED"] = False
            properties["hasOverlayImage"] = True


def update_shape(self, context):
    """Updates the size preview based on the selected shape."""
    properties = self  # type: SmallSceneryProperties
    shape = properties.shape
    objects = bpy.data.objects
    scene = bpy.context.scene
    custom_properties.update_height(self, context)
    if shape != "4/4":
        properties.SMALL_SCENERY_FLAG_VOFFSET_CENTRE = False
        properties.prohibitWalls = False
        objects.get("RCT_Full_Tile").hide = True
    else:
        objects.get("RCT_Full_Tile").hide = False
    if shape != "1/4":
        properties.SMALL_SCENERY_FLAG27 = False
        objects.get("RCT_One_Quarter").hide = True
    else:
        objects.get("RCT_One_Quarter").hide = False
    if shape == "4/4+D":
        objects.get("RCT_Diagonal_1").hide = False
        objects.get("RCT_Diagonal_2").hide = False
    else:
        objects.get("RCT_Diagonal_1").hide = True
        objects.get("RCT_Diagonal_2").hide = True
    if shape == "3/4+D":
        objects.get("RCT_Three_Quarter").hide = False
    else:
        objects.get("RCT_Three_Quarter").hide = True
    if shape == "2/4":
        objects.get("RCT_Half_Tile").hide = False
    else:
        objects.get("RCT_Half_Tile").hide = True


def update_FLAG17(self, context):
    """Disables "Animated When Zoom" if "Static First Images" is set"""
    properties = self  # type: SmallSceneryProperties
    if properties.SMALL_SCENERY_FLAG17:
        properties["SMALL_SCENERY_FLAG_VISIBLE_WHEN_ZOOMED"] = False
    update_small_scenery(self, context)


# Frame Offsets
################

def update_frameOffset_index(self, context):
    """Runs when the selected frame offset changes."""
    properties = context.scene.rct_graphics_helper_small_scenery_properties
    frameOffsets = properties.frameOffsets
    if len(frameOffsets) > 0:
        frame = frameOffsets[self.frameOffsets_index].value
        if properties.SMALL_SCENERY_FLAG17 or properties.SMALL_SCENERY_FLAG_VISIBLE_WHEN_ZOOMED:
            frame += 1
        if frame > context.scene.frame_end:
            context.scene.frame_end = frame
        bpy.context.scene.frame_set(frame)


class FrameOffsets_OT_actions(bpy.types.Operator):
    """Buttons to add/remove/move a frame offset entry."""
    bl_idname = "frameoffsets.actions"
    bl_label = "List Actions"
    bl_description = "Add\nAdd Current Frame\nRemove\n\nMove Up\nMove Down\n\nAuto Fill"
    bl_options = {'REGISTER'}

    action = bpy.props.EnumProperty(
        items=(
            ('UP', "Up", ""),
            ('DOWN', "Down", ""),
            ('REMOVE', "Remove", ""),
            ('ADD', "Add", ""),
            ('ADDCURRENT', "Add current frame", ""),
            ('AUTO', "Auto fill", "")))

    def invoke(self, context: bpy.types.Context, event):
        properties = context.scene.rct_graphics_helper_small_scenery_properties
        index = properties.frameOffsets_index

        try:
            item = properties.frameOffsets[index]
        except IndexError:
            pass
        else:
            if self.action == 'DOWN' and index < len(properties.frameOffsets) - 1:
                item_next = properties.frameOffsets[index+1].value
                properties.frameOffsets.move(index, index+1)
                properties.frameOffsets_index += 1
                info = 'Item "%s" moved to position %d' % (
                    item.value, properties.frameOffsets_index + 1)
                self.report({'INFO'}, info)

            elif self.action == 'UP' and index >= 1:
                item_prev = properties.frameOffsets[index-1].value
                properties.frameOffsets.move(index, index-1)
                properties.frameOffsets_index -= 1
                info = 'Item "%s" moved to position %d' % (
                    item.value, properties.frameOffsets_index + 1)
                self.report({'INFO'}, info)

            elif self.action == 'REMOVE':
                info = 'Item "%s" removed from list' % (
                    properties.frameOffsets[index].value)
                if index != 0:
                    properties.frameOffsets_index -= 1
                properties.frameOffsets.remove(index)
                self.report({'INFO'}, info)

        if self.action == 'ADD':
            item = properties.frameOffsets.add()
            scene = bpy.context.scene
            new_value = properties.frameOffsets[index].value + 1
            item.value = new_value
            properties.frameOffsets_index = len(properties.frameOffsets)-1
            info = '"%s" added to list' % (new_value)
            self.report({'INFO'}, info)

        if self.action == 'ADDCURRENT':
            item = properties.frameOffsets.add()
            frame = context.scene.frame_current
            if properties.SMALL_SCENERY_FLAG17 or properties.SMALL_SCENERY_FLAG_VISIBLE_WHEN_ZOOMED:
                frame -= 1
            item.value = frame
            properties.frameOffsets_index = len(properties.frameOffsets)-1
            info = 'Current frame "%s" added to list' % (item.value)
            self.report({'INFO'}, info)

        if self.action == 'AUTO':
            for i in range(0, len(properties.frameOffsets)):
                properties.frameOffsets.remove(0)
            properties.frameOffsets_index = 0
            for i in range(0, context.scene.frame_end + 1):
                item = properties.frameOffsets.add()
                item.value = i
            properties.frameOffsets_index = len(properties.frameOffsets)-1
            info = '%s items added to list' % len(properties.frameOffsets)
            self.report({'INFO'}, info)

        return {"FINISHED"}


class FrameOffsets_UL_List(bpy.types.UIList):
    """Defines the drawing function for each frame offset item"""
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            split = layout.split(0.4)
            split.label(str(index) + ":")
            # split.label(str(item.value))
            split.prop(item, "value", "", emboss=False)
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="FrameOffsets")


def set_frame_offset_item(self, val):
    """Runs when a frame offset value is set.
    
    Makes sure the value is at least 0, and if it's greater than the number of
    blender frames (adding one if the first frame is a static image), increases
    the number of blender frames to match."""
    scene = bpy.context.scene
    # type: SmallSceneryProperties
    properties = scene.rct_graphics_helper_small_scenery_properties
    end = bpy.context.scene.frame_end
    bpy.context.scene.frame_start = 0
    if val < 0:
        val = 0
    testval = val
    if properties.SMALL_SCENERY_FLAG17 or properties.SMALL_SCENERY_FLAG_VISIBLE_WHEN_ZOOMED:
        testval += 1
    if testval > end:
        scene.frame_end = testval

    self['value'] = val
    update_frameOffset_index(properties, bpy.context)


def get_frame_offset_item(self):
    """Returns the value of a frame offset item"""
    return self['value']


def get_num_frames(self):
    """Returns the number of frame offsets that are specified."""
    return len(self.frameOffsets)


class FrameOffsetsItem(bpy.types.PropertyGroup):
    """Defines a frame offset item. Has a "value"."""
    value = bpy.props.IntProperty(
        name="Frame Offset",
        description=(
            "For animated objects that don't use one of the special animation modes, this list (of frame "
            "indexes) makes up the animation sequence for this object. These are indexes into the list of images, "
            "starting at zero, where each index is for a set of 4 images (for the 4 angles)."),
        default=0,
        set=set_frame_offset_item,
        get=get_frame_offset_item)


def add_small_scenery_properties_json(context):
    """Processes small scenery properties and adds them to the global JSON"""
    json_properties = json_functions.group_as_dict(context.scene.rct_graphics_helper_small_scenery_properties)
    json_properties.pop("frameOffsets_index", None)
    if json_properties.get("hasGlass", None):
        json_properties.pop("isAnimated", None)
    if not json_properties.get("isAnimated", None):
        json_properties.pop("SMALL_SCENERY_FLAG_VISIBLE_WHEN_ZOOMED", None)
        json_properties.pop("SMALL_SCENERY_FLAG17", None)
        json_properties.pop("hasOverlayImage", None)
        json_properties.pop("SMALL_SCENERY_FLAG_COG", None)
        json_properties.pop("animationDelay", None)
        json_properties.pop("animation_type", None)
        json_properties.pop("animationMask", None)
        json_properties.pop("frameOffsets", None)
    elif json_properties.get("animation_type", None) != "use_frame_offsets":
        json_properties.pop("SMALL_SCENERY_FLAG17", None)
        json_properties.pop("SMALL_SCENERY_FLAG_VISIBLE_WHEN_ZOOMED", None)
        json_properties["hasOverlayImage"] = True
        json_properties[json_properties["animation_type"]] = True
        json_properties.pop("animation_type", None)
    else:
        frame_offsets = []
        raw_frame_offsets = json_properties.get("frameOffsets", None)
        if raw_frame_offsets is not None:
            for raw_frame_offset in raw_frame_offsets:
                frame_offsets.append(raw_frame_offset.get("value", 0))
        json_properties["frameOffsets"] = frame_offsets
    if json_properties.get("shape", None) != "4/4":
        json_properties.pop("SMALL_SCENERY_FLAG_VOFFSET_CENTRE", None)
        json_properties.pop("prohibitWalls", None)
    if json_properties.get("shape", None) != "1/4":
        json_properties.pop("SMALL_SCENERY_FLAG27", None)
    if json_properties.get("sceneryGroup", None) == "":
        json_properties.pop("sceneryGroup", None)
    json_functions.json_data["properties"] = json_properties


def set_small_scenery_properties(context, json_data):
    """Sets the small scenery properties from the given data

    Args:
        context (bpy.types.Context): Context
        json_data (dict): The `properties` field of a JSON object

    Returns:
        str: If not empty, a warning message to display.
    """
    warning = ""
    
    properties = context.scene.rct_graphics_helper_small_scenery_properties  # type: SmallSceneryProperties
    set_property(properties, json_data, 'height')
    set_property(properties, json_data, 'cursor')
    set_property(properties, json_data, 'price')
    set_property(properties, json_data, 'removalPrice')
    set_property(properties, json_data, 'sceneryGroup')
    set_property(properties, json_data, 'hasPrimaryColour', False)
    set_property(properties, json_data, 'hasSecondaryColour', False)
    set_property(properties, json_data, 'hasGlass', False)
    set_property(properties, json_data, 'shape')
    set_property(properties, json_data, 'SMALL_SCENERY_FLAG_VOFFSET_CENTRE', False)
    set_property(properties, json_data, 'prohibitWalls', False)
    set_property(properties, json_data, 'SMALL_SCENERY_FLAG27', False)
    set_property(properties, json_data, 'requiresFlatSurface', False)
    set_property(properties, json_data, 'isStackable', False)
    set_property(properties, json_data, 'hasNoSupports', False)
    set_property(properties, json_data, 'allowSupportsAbove', False)
    set_property(properties, json_data, 'supportsHavePrimaryColour', False)
    set_property(properties, json_data, 'isRotatable', False)
    set_property(properties, json_data, 'isTree', False)
    set_property(properties, json_data, 'canWither', False)
    set_property(properties, json_data, 'canBeWatered', False)
    if set_property(properties, json_data, 'isAnimated', False):
        frameOffsets = json_data.get('frameOffsets', None)
        if frameOffsets is not None:
            properties.animation_type = 'use_frame_offsets'
            properties.frameOffsets.clear()
            for frame in frameOffsets:
                item = properties.frameOffsets.add()
                item.value = frame
            set_property(properties, json_data, 'SMALL_SCENERY_FLAG17', False)
            set_property(properties, json_data, 'SMALL_SCENERY_FLAG_VISIBLE_WHEN_ZOOMED', False)
            set_property(properties, json_data, 'hasOverlayImage', False)
            set_property(properties, json_data, 'SMALL_SCENERY_FLAG_COG', False)
            set_property(properties, json_data, 'animationDelay', False)
            set_property(properties, json_data, 'animationMask', False)
        elif json_data.get('SMALL_SCENERY_FLAG_FOUNTAIN_SPRAY_1', False):
            properties.animation_type = 'SMALL_SCENERY_FLAG_FOUNTAIN_SPRAY_1'
            set_property(properties, json_data, 'SMALL_SCENERY_FLAG_VISIBLE_WHEN_ZOOMED', False)
            set_property(properties, json_data, 'hasOverlayImage')
        elif json_data.get('SMALL_SCENERY_FLAG_FOUNTAIN_SPRAY_4', False):
            properties.animation_type = 'SMALL_SCENERY_FLAG_FOUNTAIN_SPRAY_4'
            set_property(properties, json_data, 'SMALL_SCENERY_FLAG_VISIBLE_WHEN_ZOOMED', False)
            set_property(properties, json_data, 'hasOverlayImage', False)
        elif json_data.get('isClock', False):
            properties.animation_type = 'isClock'
            set_property(properties, json_data, 'SMALL_SCENERY_FLAG_VISIBLE_WHEN_ZOOMED', False)
            set_property(properties, json_data, 'hasOverlayImage', False)
        elif json_data.get('SMALL_SCENERY_FLAG_SWAMP_GOO', False):
            properties.animation_type = 'SMALL_SCENERY_FLAG_SWAMP_GOO'
            set_property(properties, json_data, 'SMALL_SCENERY_FLAG_VISIBLE_WHEN_ZOOMED', False)
            set_property(properties, json_data, 'hasOverlayImage', False)
        else:
            warning = "JSON has \"isAnimated\" set but does not specify an animation type."
    return warning


class RenderSmallScenery(RCTRender, bpy.types.Operator):
    """Operator to render small scenery objects."""
    bl_idname = "render.rct_small_scenery"
    bl_label = "Render RCT Small Scenery"
    
    def execute(self, context):
        self.scene = context.scene
        self.small_scenery_properties = (
            self.scene.rct_graphics_helper_small_scenery_properties)  # type: SmallSceneryProperties
        update_small_scenery(self.small_scenery_properties, context)
        self.renderTask = RenderTask(context)

        add_small_scenery_properties_json(context)
        # print("JSON data:\n%s" % json_functions.json_data)
        angles = AngleSection(False, 4, 0, 0, 0).angles
        if not self.small_scenery_properties.isAnimated:
            remap = 0
            if self.small_scenery_properties.hasSecondaryColour:
                remap = 2
            elif self.small_scenery_properties.hasPrimaryColour:
                remap = 1
            self.renderTask.add(angles, remap, "Normal", [0, 10])
            if self.small_scenery_properties.hasGlass:
                self.renderTask.add(angles, -1, "Glass", [0, 1, 10])
        elif self.small_scenery_properties.animation_type == "use_frame_offsets":
            remap = 0
            if self.small_scenery_properties.hasSecondaryColour:
                remap = 2
            elif self.small_scenery_properties.hasPrimaryColour:
                remap = 1
            self.renderTask.add(angles, remap, "Normal", [0, 10], 0, context.scene.frame_end)
        return super().execute(context)

    def finished(self, context):
        """Runs when rendering is completely finished."""
        super().finished(context)
        self.report({'INFO'}, 'RCT Small Scenery render finished.')


class SmallSceneryProperties(bpy.types.PropertyGroup):
    """Defines the group of properties for small scenery objects."""
    previews = None
    
    height = custom_properties.height
    cursor = custom_properties.cursor
    price = custom_properties.price
    removalPrice = custom_properties.removalPrice
    sceneryGroup = bpy.props.StringProperty(
        name="Group ID",
        description="OpenRCT2 id of the primary scenery group this object should be included in.")

    hasPrimaryColour = custom_properties.hasPrimaryColour
    hasSecondaryColour = custom_properties.hasSecondaryColour
    hasTernaryColour = custom_properties.hasTernaryColour
    hasGlass = bpy.props.BoolProperty(
        name="Has Glass",
        description=(
            "True for objects that have translucent glass elements. You should separate all the glass parts and set "
            "them to be visible on the `Glass` RenderLayer (i.e., move them to layer[1], and put the solid parts on "
            "layer[0] for the `Normal` RenderLayer). The glass images are just a flat mask, so the material doesn't "
            "matter, as long as it's solid.\n\nGlass always uses the primary color, so keep that in mind if you use "
            "the primary remap for the solid parts."),
        default=False,
        update=update_small_scenery)

    shape = bpy.props.EnumProperty(
        items=[
            ("1/4", "1/4 Tile", ""),
            ("2/4", "1/2 Tile", ""),
            ("4/4+D", "Diagonal", ""),
            ("3/4+D", "3/4 Tile", ""),
            ("4/4", "Full Tile", "")
        ],
        name="Shape",
        description="The shape of this object.",
        default="4/4",
        update=update_shape)
    SMALL_SCENERY_FLAG_VOFFSET_CENTRE = bpy.props.BoolProperty(
        name="Fills Tile",
        description=(
            "This flag should be true for any object that fills the entire tile. One of the effects "
            "of this is that if this object is above flower gardens, it blocks rain from watering them (and "
            "resetting their withering status). Not sure what this does otherwise. Object editor calls it "
            "\"Overlap\" and claims it has to do with drawing priority, especially for objects that extend "
            "all the way to the edge."),
        default=False)
    prohibitWalls = bpy.props.BoolProperty(
        name="Prohibit Walls",
        description=(
            "If true, no walls can be placed against this object on the same tile."),
        default=False)
    SMALL_SCENERY_FLAG27 = bpy.props.BoolProperty(
        name="1/4 Support",
        description=(
            "A quarter-tile object with this flag set will block supports in the same way that a "
            "full-tile object would. Only Pole (SUPPLEG1.DAT) has this flag enabled in RCT2."),
        default=False)

    requiresFlatSurface = bpy.props.BoolProperty(
        name="Requires Flat",
        description=("If true, this object can only be built on flat ground."),
        default=False)
    isStackable = bpy.props.BoolProperty(
        name="Is Stackable",
        description=(
            "If true, this object can be placed in the air or above water (i.e., by holding shift)."),
        default=False)
    hasNoSupports = bpy.props.BoolProperty(
        name="No Supports",
        description=(
            "True for objects that don't have supports when they are placed in the air."),
        default=False)
    allowSupportsAbove = bpy.props.BoolProperty(
        name="Supports Above",
        description=(
            "If true, supports from other objects will be built on top of this one."),
        default=False)
    supportsHavePrimaryColour = bpy.props.BoolProperty(
        name="Supports Have Primary",
        description=(
            "If true, the supports for this item will be painted the primary color as well. "
            "This is very useful for objects that are themselves support structures."),
        default=False)
    isRotatable = bpy.props.BoolProperty(
        name="Is Rotatable",
        description=(
            "When true, user can set rotation, otherwise rotation is automatic. This is usually "
            "used for foliage, for example."),
        default=False)
    isTree = bpy.props.BoolProperty(
        name="Is Tree",
        description=(
            "Obviously, this flag is true for trees. This is used in scenarios where tree removal "
            "is forbidden. This flag was not explicitly present in vanilla RCT2. Instead, all small scenery "
            "objects above a certain height (64) were considered trees. OpenRCT2 uses this behavior when loading "
            "DAT objects."),
        default=False)

    canWither = bpy.props.BoolProperty(
        name="Can Wither",
        description=(
            "If true, this object ages/withers over time (used for flower gardens). This requires "
            "two more sets of 4 angles, for the first and second level of aging."),
        default=False)
    canBeWatered = bpy.props.BoolProperty(
        name="Can Be Watered",
        description=(
            "This is used in conjunction with `canWither` (again, intended for flower gardens). If "
            "true, staff members (who are told to water plants) will water this object. The aging/withering "
            "process will be reset whenever this happens. It will also be reset whenever it precipitates, unless "
            "it is blocked above by an object with `SMALL_SCENERY_FLAG_VOFFSET_CENTRE` set (i.e, full tiles)."),
        default=False)

    # Animation fields
    isAnimated = bpy.props.BoolProperty(
        name="Is Animated",
        description=(
            "If true, this object is animated. It may have an animation sequence defined by frameOffsets, "
            "or it may use one of the other special animation modes (SMALL_SCENERY_FLAG_FOUNTAIN_SPRAY_1, "
            "SMALL_SCENERY_FLAG_FOUNTAIN_SPRAY_4, isClock, or SMALL_SCENERY_FLAG_SWAMP_GOO)"),
        default=False,
        update=update_small_scenery)
    animation_type = bpy.props.EnumProperty(
        items=[
            ("use_frame_offsets", "Frame Offsets", "Use a list of frame offsets"),
            ("SMALL_SCENERY_FLAG_FOUNTAIN_SPRAY_1", "Fountain 1", (
                "True for objects that use the first special "
                "fountain animation mode. This requires four frames of animation (4 angles each) that are "
                "overlayed on top of the base images.")),
            ("SMALL_SCENERY_FLAG_FOUNTAIN_SPRAY_4", "Fountain 4", (
                "True for objects that use the second special "
                "fountain animation mode. This requires nine extra sets of images (4 angles each) that are "
                "overlayed on top of the base images. The first set is a static overlay. The next four sets "
                "are a 4-frame animation that is overlayed on top of the base images, but underneath the static "
                "overlay. The next four sets are another 4-frame animation, that is overlayed on top of everything. "
                "So the layering order is the base set, the first 4-animation on top, then a static overlay on top "
                "of that, and then the second 4-frame animation on top.\n\nThe only vanilla object that uses this "
                "mode is the Cupid Fountains (TQF.DAT), and it allows the static centerpiece to be rendered "
                "separately, between the sets of animated fountains.")),
            ("isClock", "Clock", (
                "True for objects that use the real-time special animation mode for the clock "
                "(TCK.DAT). This requires a bunch of extra images. First is a static overlay (4 angles, with both "
                "hands pointing at 12) that's used just for previewing. After that is 60 images, which are 60 "
                "frames of the minute hand going around the clock, and then another 48 frames of the hour hand "
                "doing the same, all starting facing the upper right and continuing around, well, clockwise of "
                "course. (Note that these are not duplicated for all 4 angles, the game just offsets by the right "
                "amount to account for direction).")),
            ("SMALL_SCENERY_FLAG_SWAMP_GOO", "Swamp Goo", (
                "True for objects that use the special animation mode "
                "for swamp goo (TSG.DAT). This is just a 16 frame animation from a single angle."))
        ],
        name="Animation Type",
        description=(
            "Selects the animation mode to use for this object. `Frame Offsets` is the normal mode. The "
            "other 4 are special modes."),
        default="use_frame_offsets",
        update=update_small_scenery)
    hasOverlayImage = bpy.props.BoolProperty(
        name="Has Overlay Image",
        description=(
            "If true, the second set of 4 angles are also drawn (on top) when previewing. This should be used when "
            "`Animate While Zoomed` or `Static First Images` is set."),
        default=False)
    frameOffsets = bpy.props.CollectionProperty(
        type=FrameOffsetsItem,
        name="Frame Offsets",
        description=(
            "For animated objects that don't use one of the special animation modes, this list (of frame "
            "indexes) makes up the animation sequence for this object. These are indexes into the list of images, "
            "starting at zero, where each index is for a set of 4 images (for the 4 angles)."),)
    frameOffsets_index = bpy.props.IntProperty(
        default=0, update=update_frameOffset_index)
    animationDelay = bpy.props.IntProperty(
        name="Animation Delay",
        description=(
            "Divides the animation speed in half this many times. For example, if this value was 1, 2, "
            "or 3, the animation would update every 2 ticks, every 4 ticks, or every 8 ticks, respectively. At normal "
            "speed, the game targets a rate of 40 ticks per second."),
        default=0, min=0)
    animationMask = bpy.props.IntProperty(
        name="Animation Mask",
        description=(
            "A bitmask used to set when the animation loops. Calculate this by choosing the desired "
            "animation length as a power of 2 and then subtracting one. If this value is greater than numFrames-1, "
            "the animation will have an extra delay before repeating.\n\nFor example, if a smoothly looping animation"
            " is 16 frames long, this value should be 15."),
        default=15, min=1)
    numFrames = bpy.props.IntProperty(
        name="Number of frames",
        description=(
            "Number of frames specified for the animation (equal to length of Frame Offsets list)"),
        default=16, min=1, get=get_num_frames)
    SMALL_SCENERY_FLAG_VISIBLE_WHEN_ZOOMED = bpy.props.BoolProperty(
        name="Animate When Zoomed",
        description=(
            "True for animated objects that continue to animate when zoomed out.\n\nWhen this is set for objects with "
            "frame-offset animations, the first set of images are only used for previewing, "
            "and are not drawn when placed. The rest of the images are the actual animation frames "
            "that frameOffsets indexes into."),
        default=False, update=update_small_scenery)
    SMALL_SCENERY_FLAG17 = bpy.props.BoolProperty(
        name="Static First Images",
        description=(
            "This is only used for animated objects that do not have `Animate When Zoomed` set. For these objects, "
            "the game *always* draws the first image set. Normally, the images for these objects contain _only_ the "
            "animation frames, so this would mean that the first frame is always drawn, and then the animation is "
            "drawn on top of that, which may cause problems.\n\nIf this flag is true, this object instead has the "
            "first four images separated out as a base set of images, and the animation frames only start after that "
            "(just like objects with `Animate When Zoomed` set, or the special fountain modes). This means that you "
            "make the first 4 images blank and then *only* the animation is drawn (and enable `Has Overlay Image` so "
            "the first animation frame is drawn for the preview).\n\nIn the end, this flag is only useful if you "
            "*really* don't want the object animating when zoomed out."),
        default=False, update=update_FLAG17)
    SMALL_SCENERY_FLAG_COG = bpy.props.BoolProperty(
        name="Sync Across Map",
        description=(
            "True for frame-offset-animated objects whose animations should be synchronized across the entire map. "
            "Normally, the timing of these animations are offset depending on the tile the object is on, but this flag "
            "disables that behavior so the animations always play in-sync. Used for the `cog` objects in vanilla."),
        default=False)


class SmallSceneryPanel(bpy.types.Panel):
    """Defines the drawing function for the RCT Small Scenery panel"""
    bl_label = "RCT Small Scenery"
    bl_idname = "RENDER_PT_rct_small_scenery"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    @classmethod
    def poll(cls, context: bpy.types.Context):
        general_properties = context.scene.rct_graphics_helper_general_properties
        return general_properties.objectType == "scenery_small"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        small_scenery_properties = scene.rct_graphics_helper_small_scenery_properties  # type: SmallSceneryProperties
        
        row = layout.row()
        row.operator("render.rct_small_scenery", text="Render Small Scenery Object")

        row = layout.row().split(0.33, align=True)
        row.label("Price:")
        row.prop(small_scenery_properties, "price", text="Place")
        row.prop(small_scenery_properties, "removalPrice", text="Removal")

        row = layout.row()
        row.prop(small_scenery_properties, "cursor")
        row.prop(small_scenery_properties, "height")

        row = layout.row()
        row.prop(small_scenery_properties, "sceneryGroup")

        row = layout.row(align=True)
        row.prop(small_scenery_properties, "hasPrimaryColour", toggle=True)
        row.prop(small_scenery_properties, "hasSecondaryColour", toggle=True)
        row.separator()
        row.prop(small_scenery_properties, "hasGlass", toggle=True)

        layout.label("Shape:")
        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(small_scenery_properties, "shape", text="")
        row.prop(small_scenery_properties, "SMALL_SCENERY_FLAG_VOFFSET_CENTRE", toggle=True)
        row.prop(small_scenery_properties, "prohibitWalls", toggle=True)
        row = col.row(align=True)
        row.prop(small_scenery_properties, "SMALL_SCENERY_FLAG27", toggle=True)
        row.prop(small_scenery_properties, "requiresFlatSurface", toggle=True)
        row.prop(small_scenery_properties, "isStackable", toggle=True)
        row = col.row(align=True)
        row.prop(small_scenery_properties, "hasNoSupports", toggle=True)
        row.prop(small_scenery_properties, "allowSupportsAbove", toggle=True)
        row.prop(small_scenery_properties, "supportsHavePrimaryColour", toggle=True)
        row = col.row(align=True)
        row.prop(small_scenery_properties, "isRotatable", toggle=True)
        row.prop(small_scenery_properties, "isTree", toggle=True)
        row = col.row(align=True)
        row.prop(small_scenery_properties, "canWither", toggle=True)
        row.prop(small_scenery_properties, "canBeWatered", toggle=True)

        # Animation properties
        row = layout.row()
        if small_scenery_properties.hasGlass:
            row.enabled = False
        row.prop(small_scenery_properties, "isAnimated")
        sub = row.column()
        if not small_scenery_properties.isAnimated:
            sub.enabled = False
        sub.prop(small_scenery_properties, "animation_type", "Type")
        if small_scenery_properties.isAnimated:
            box = layout.box()
            col = box.column()
            if small_scenery_properties.animation_type == "use_frame_offsets":
                # Frame offset fields
                row = col.split(0.5, align=True)
                leftcol = row.column()
                leftcol.label("Animation Properties")
                # Properties about the first images
                sub = leftcol.box().column(align=True)
                sub.prop(small_scenery_properties, "SMALL_SCENERY_FLAG_VISIBLE_WHEN_ZOOMED", toggle=True),
                sub.prop(small_scenery_properties, "SMALL_SCENERY_FLAG17", toggle=True),
                sub.separator()
                sub.prop(small_scenery_properties, "hasOverlayImage", toggle=True)
                # Rest of the properties
                leftcol.prop(small_scenery_properties, "SMALL_SCENERY_FLAG_COG", toggle=True),
                leftcol.prop(small_scenery_properties, "animationDelay")
                leftcol.label(
                    "Speed: " + str(int(40/(1 << small_scenery_properties.animationDelay))) + " fps")
                leftcol.prop(small_scenery_properties, "animationMask")
                leftcol.separator()
                leftcol.prop(small_scenery_properties, "numFrames", emboss=False, slider=True)

                # List of frame offsets
                rightcol = row.column()
                righthead = rightcol.row()
                righthead.label("Frame Offsets")
                if (small_scenery_properties.SMALL_SCENERY_FLAG17
                        or small_scenery_properties.SMALL_SCENERY_FLAG_VISIBLE_WHEN_ZOOMED):
                    righthead.label("(offset by 1)")
                sub = rightcol.row()
                subcol = sub.column(align=True)
                subcol.template_list("FrameOffsets_UL_List", "", small_scenery_properties, "frameOffsets",
                                     small_scenery_properties, "frameOffsets_index")
                subcol = sub.column(align=True)
                subcol.operator("frameoffsets.actions",
                                icon='ZOOMIN', text="").action = 'ADD'
                subcol.operator("frameoffsets.actions",
                                icon='PLUS', text="").action = 'ADDCURRENT'
                subcol.operator("frameoffsets.actions",
                                icon='ZOOMOUT', text="").action = 'REMOVE'
                subcol.separator()
                subcol.operator("frameoffsets.actions",
                                icon='TRIA_UP', text="").action = 'UP'
                subcol.operator("frameoffsets.actions",
                                icon='TRIA_DOWN', text="").action = 'DOWN'
                subcol.separator()
                subcol.operator("frameoffsets.actions",
                                icon='FILE_REFRESH', text="").action = 'AUTO'
            elif small_scenery_properties.animation_type == "SMALL_SCENERY_FLAG_FOUNTAIN_SPRAY_1":
                row = col.row()
                row.prop(small_scenery_properties, "hasOverlayImage")
                row.prop(small_scenery_properties, "SMALL_SCENERY_FLAG_VISIBLE_WHEN_ZOOMED")
            elif small_scenery_properties.animation_type == "SMALL_SCENERY_FLAG_FOUNTAIN_SPRAY_4":
                row = col.row()
                row.prop(small_scenery_properties, "hasOverlayImage")
                row.prop(small_scenery_properties, "SMALL_SCENERY_FLAG_VISIBLE_WHEN_ZOOMED")
            elif small_scenery_properties.animation_type == "isClock":
                row = col.row()
                row.prop(small_scenery_properties, "hasOverlayImage")
                row.prop(small_scenery_properties, "SMALL_SCENERY_FLAG_VISIBLE_WHEN_ZOOMED")
            elif small_scenery_properties.animation_type == "SMALL_SCENERY_FLAG_SWAMP_GOO":
                row = col.row()
                row.prop(small_scenery_properties, "hasOverlayImage")
                row.prop(small_scenery_properties, "SMALL_SCENERY_FLAG_VISIBLE_WHEN_ZOOMED")


def register_small_scenery_panel():
    """Registers the small scenery panel and properties"""
    bpy.types.Scene.rct_graphics_helper_small_scenery_properties = bpy.props.PointerProperty(
        type=SmallSceneryProperties)


def unregister_small_scenery_panel():
    """Unregisters the small scenery panel and properties"""
    del bpy.types.Scene.rct_graphics_helper_small_scenery_properties
