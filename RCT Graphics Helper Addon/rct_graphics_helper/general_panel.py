'''
Copyright (c) 2021 RCT Graphics Helper developers

For a complete list of all authors, please refer to the addon's meta info.
Interested in contributing? Visit https://github.com/oli414/Blender-RCT-Graphics

RCT Graphics Helper is licensed under the GNU General Public License version 3.
'''

import json
from sys import version
from typing import Iterable
import bpy
import bpy.utils.previews
import math
import os
from . small_scenery_panel import update_small_scenery, set_small_scenery_properties
from . stall_panel import update_stall, set_stall_properties
from . vehicles_panel import update_vehicles, set_vehicles_properties
from . render_task import get_res_path, get_output_path
from . import render_operator as render_operator
from . import custom_properties as custom_properties
from . import json_functions as json_functions
from . custom_properties import create_size_preview, set_property, process_ride_type


def enum_previews_from_directory_items(self, context):
    """Loads preview images from "./preview/", or loads the default image if nothing is rendered"""
    pcoll = render_operator.preview_collections.get("main")  # type: bpy.utils.previews.ImagePreviewCollection

    if not pcoll:
        directory = get_output_path("preview/")
        enum_items = []
        if os.path.exists(directory):
            enum_items = render_operator.preview_dir_update(context)
        if not enum_items:
            default_image = get_res_path("preview.png")
            thumb = pcoll.load("defaultpreviewimage", default_image, 'IMAGE')
            item = ("default_preview_image",
                    "Nothing Rendered Yet", "", thumb.icon_id, 0)
            enum_items.append(item)
        pcoll.my_previews = enum_items

    return pcoll.my_previews


def set_general_properties(context, json_data):
    """Sets the general object properties from the given json_data

    Args:
        context (bpy.types.Context): Context
        json_data (dict): A dictionary containing converted data from a JSON object
    """
    general_properties = context.scene.rct_graphics_helper_general_properties  # type: GeneralProperties
    set_property(general_properties, json_data, 'id')
    set_property(general_properties, json_data, 'originalId')
    set_property(general_properties, json_data, 'authors')
    set_property(general_properties, json_data, 'version')
    set_property(general_properties, json_data, 'sourceGame')
    object_type = json_data.get('objectType', None)
    if object_type == 'ride':
        general_properties.objectType = process_ride_type(json_data)
    elif object_type is not None:
        general_properties.objectType = object_type
    strings = json_data.get("strings", None)
    if strings is not None:
        name = strings.get("name", None)  # type: dict
        if name is not None:
            name_strings = general_properties.name_strings
            name_strings.clear()
            for language, value in name.items():
                entry = general_properties.name_strings.add()  # type: StringsEntry
                entry.language = language
                entry.value = value
        description = strings.get("description", None)
        if description is not None:
            description_strings = general_properties.description_strings
            description_strings.clear()
            for language, value in description.items():
                entry = general_properties.description_strings.add()  # type: StringsEntry
                entry.language = language
                entry.value = value
        capacity = strings.get("capacity", None)
        if capacity is not None:
            capacity_strings = general_properties.capacity_strings
            capacity_strings.clear()
            for language, value in capacity.items():
                entry = general_properties.capacity_strings.add()  # type: StringsEntry
                entry.language = language
                entry.value = value


object_prop_load_warn = "Cannot load object properties."
object_type_unsupported = "Type '%s' is not currently supported. " + object_prop_load_warn
object_prop_load_issue = "Issue loading object properties for type '%s'."
object_functions = {
    "scenery_small": set_small_scenery_properties,
    "stall": set_stall_properties,
    # "flat_ride": set_flat_ride_properties,
    "vehicle": set_vehicles_properties,
    # "footpath": set_footpath_properties,
    # "footpath_banner": set_footpath_banner_properties,
    # "footpath_item": set_footpath_item_properties,
    # "scenery_large": set_scenery_large_properties,
    # "scenery_wall": set_scenery_wall_properties,
    # "scenery_group": set_scenery_group_properties,
    # "park_entrance": set_park_entrance_properties,
    # "water": set_water_properties,
    # "terrain_surface": set_terrain_surface_properties,
    # "terrain_edge": set_terrain_edge_properties,
    # "station": set_station_properties,
    # "music": set_music_properties,
    # "footpath_surface": set_footpath_surface_properties,
    # "footpath_railings": set_footpath_railings_properties
}


class RCTImportJSON(bpy.types.Operator):
    """Imports properties from a user-selected JSON object file"""
    bl_idname = "render.rct_import_json"
    bl_label = "Import Existing JSON"
    
    filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context: bpy.types.Context):
        print(self.filepath)
        json_data = json_functions.read_json_file(self.filepath)
        if json_data is None:
            self.report({'WARNING'}, "JSON file contains no data.")
        elif not isinstance(json_data, dict):
            self.report({'WARNING'}, "JSON file contains invalid data.")
        else:
            print(json_data)
            set_general_properties(context, json_data)
            object_type = context.scene.rct_graphics_helper_general_properties.objectType
            if object_type is None:
                self.report({'WARNING'}, "JSON file has no objectType. " + object_prop_load_warn)
            elif object_type in object_functions.keys():
                warning = object_functions[object_type](context, json_data.get("properties"))
                if warning:
                    self.report({'WARNING'}, warning)
            else:
                self.report({'WARNING'}, object_type_unsupported % object_type)
        return {"FINISHED"}
    
    def invoke(self, context: bpy.types.Context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class RCTCreateRig(bpy.types.Operator):
    """Create rendering rig and size preview"""
    bl_idname = "render.rct_create_rig"
    bl_label = "Create Rendering Rig"

    def execute(self, context):
        print("Creating Rig")
        scene = context.scene
        objects = bpy.data.objects
        lamps = bpy.data.lamps
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                area.spaces[0].show_relationship_lines = False
        rct_rig = objects.get('RCT_Rig')
        if rct_rig is None:
            rct_rig = objects.new("RCT_Rig", None)
            scene.objects.link(rct_rig)
        rct_rig.hide = True
        rct_rig.layers = [i == 10 for i in range(20)]
        rct_vertical_joint = objects.get('RCT_VerticalJoint')
        if rct_vertical_joint is None:
            rct_vertical_joint = objects.new("RCT_VerticalJoint", None)
            scene.objects.link(rct_vertical_joint)
        rct_vertical_joint.parent = rct_rig
        rct_vertical_joint.hide = True
        rct_vertical_joint.layers = [i == 10 for i in range(20)]
        rct_camera = objects.get('RCT_Camera')
        if objects.get('RCT_Camera') is None:
            rct_camera_data = bpy.data.cameras.new("RCT_Camera")
            rct_camera = objects.new("RCT_Camera", rct_camera_data)
            scene.objects.link(rct_camera)
        rct_camera_data = rct_camera.data  # type: bpy.types.Camera
        rct_camera_data.ortho_scale = 5.657
        rct_camera_data.type = "ORTHO"
        rct_camera.location = (-(1/64)+20/math.sqrt(2),
                               -(1/64)+20/math.sqrt(2), 20*math.tan(math.pi/6))
        rct_camera.rotation_euler = [math.pi/3, 0, 3*math.pi/4]
        rct_camera.parent = rct_vertical_joint
        rct_camera.hide_select = True
        rct_camera.layers = [i == 10 for i in range(20)]
        scene.camera = rct_camera
        scene.render.resolution_x = 256
        scene.render.resolution_y = 256
        scene.render.resolution_percentage = 100
        scene.render.alpha_mode = 'TRANSPARENT'
        scene.render.use_antialiasing = False

        light = objects.get('RCT_MainLight')
        # If we don't have a main light, it's probably safe to reset the lights to default. If we do
        # have a main light, leave the lights alone; user may have changed them on purpose.
        if objects.get('RCT_MainLight') is None:
            light_data = lamps.new("RCT_MainLight", "SUN")
            light = objects.new("RCT_MainLight", light_data)
            scene.objects.link(light)
            light_data = light.data  # type: bpy.types.SunLamp
            light_data.energy = 0.9
            light_data.use_specular = False
            light_data.shadow_method = "NOSHADOW"
            light.location = (-16, 14, 12)
            constraint = light.constraints.new("DAMPED_TRACK")  # type: bpy.types.DampedTrackConstraint
            constraint.target = rct_vertical_joint
            constraint.track_axis = "TRACK_NEGATIVE_Z"
            light.parent = rct_vertical_joint
            light.hide = True
            light.layers = [i == 10 for i in range(20)]

            light = objects.get('RCT_Backlight')
            if objects.get('RCT_Backlight') is None:
                light_data = lamps.new("RCT_Backlight", "SPOT")
                light = objects.new("RCT_Backlight", light_data)
                scene.objects.link(light)
                light_data = light.data  # type: bpy.types.SpotLamp
                light_data.energy = 0.1
                light_data.use_specular = False
                light_data.falloff_type = "CONSTANT"
                light_data.shadow_method = "NOSHADOW"
                light.location = (2.5, -23, 14)
                constraint = light.constraints.new("DAMPED_TRACK")  # type: bpy.types.DampedTrackConstraint
                constraint.target = rct_vertical_joint
                constraint.track_axis = "TRACK_NEGATIVE_Z"
                light.parent = rct_vertical_joint
                light.hide = True
                light.layers = [i == 10 for i in range(20)]

            light = objects.get('RCT_FrontFillerLight')
            if objects.get('RCT_FrontFillerLight') is None:
                light_data = lamps.new("RCT_FrontFillerLight", "SPOT")
                light = objects.new("RCT_FrontFillerLight", light_data)
                scene.objects.link(light)
                light_data = light.data  # type: bpy.types.SpotLamp
                light_data.energy = 0.4
                light_data.use_specular = False
                light_data.falloff_type = "CONSTANT"
                light_data.shadow_method = "NOSHADOW"
                light.location = (-5, 18.5, 1.5)
                # type: bpy.types.DampedTrackConstraint
                constraint = light.constraints.new("DAMPED_TRACK")
                constraint.target = rct_vertical_joint
                constraint.track_axis = "TRACK_NEGATIVE_Z"
                light.parent = rct_vertical_joint
                light.hide = True
                light.layers = [i == 10 for i in range(20)]

            light = objects.get('RCT_LightDome')
            if objects.get('RCT_LightDome') is None:
                light_data = lamps.new("RCT_LightDome", "HEMI")
                light = objects.new("RCT_LightDome", light_data)
                scene.objects.link(light)
                light_data = light.data  # type: bpy.types.HemiLamp
                light_data.energy = 0.17
                light_data.use_specular = False
                light.location = (0, 0, 15.5)
                constraint = light.constraints.new("DAMPED_TRACK")  # type: bpy.types.DampedTrackConstraint
                constraint.target = rct_vertical_joint
                constraint.track_axis = "TRACK_NEGATIVE_Z"
                light.parent = rct_vertical_joint
                light.hide = True
                light.layers = [i == 10 for i in range(20)]

            light = objects.get('RCT_ShadowCaster')
            if objects.get('RCT_ShadowCaster') is None:
                light_data = lamps.new("RCT_ShadowCaster", "SUN")
                light = objects.new("RCT_ShadowCaster", light_data)
                scene.objects.link(light)
                light_data = light.data  # type: bpy.types.SunLamp
                light_data.energy = 1.5
                light_data.use_specular = False
                light_data.use_only_shadow = True
                light_data.shadow_method = "RAY_SHADOW"
                light_data.shadow_ray_sample_method = "CONSTANT_QMC"
                light_data.shadow_ray_samples = 1
                light_data.shadow_soft_size = 1.2
                light.location = (-16, 14, 12)
                constraint = light.constraints.new("DAMPED_TRACK")  # type: bpy.types.DampedTrackConstraint
                constraint.target = rct_vertical_joint
                constraint.track_axis = "TRACK_NEGATIVE_Z"
                light.parent = rct_vertical_joint
                light.hide = True
                light.layers = [i == 10 for i in range(20)]

            light = objects.get('RCT_SideFillerLight')
            if objects.get('RCT_SideFillerLight') is None:
                light_data = lamps.new("RCT_SideFillerLight", "SPOT")
                light = objects.new("RCT_SideFillerLight", light_data)
                scene.objects.link(light)
                light_data = light.data  # type: bpy.types.SpotLamp
                light_data.energy = 0.15
                light_data.use_specular = False
                light_data.falloff_type = "CONSTANT"
                light_data.shadow_method = "NOSHADOW"
                light.location = (18, 1.5, 8)
                constraint = light.constraints.new("DAMPED_TRACK")  # type: bpy.types.DampedTrackConstraint
                constraint.target = rct_vertical_joint
                constraint.track_axis = "TRACK_NEGATIVE_Z"
                light.parent = rct_vertical_joint
                light.hide = True
                light.layers = [i == 10 for i in range(20)]

            light = objects.get('RCT_SpecularLight')
            if objects.get('RCT_SpecularLight') is None:
                light_data = lamps.new("RCT_SpecularLight", "SPOT")
                light = objects.new("RCT_SpecularLight", light_data)
                scene.objects.link(light)
                light_data = light.data  # type: bpy.types.SpotLamp
                light_data.energy = 0.3
                light_data.falloff_type = "CONSTANT"
                light_data.shadow_method = "NOSHADOW"
                light.location = (-16, 14, 12)
                constraint = light.constraints.new("DAMPED_TRACK")  # type: bpy.types.DampedTrackConstraint
                constraint.target = rct_vertical_joint
                constraint.track_axis = "TRACK_NEGATIVE_Z"
                light.parent = rct_vertical_joint
                light.hide = True
                light.layers = [i == 10 for i in range(20)]
        
        scene.layers = [scene.layers[i] or i == 10 for i in range(20)]
        
        create_size_preview(context)
        update_object_type(context.scene.rct_graphics_helper_general_properties, context)

        return {"FINISHED"}


def update_shadows(self, context):
    """Enables/disables the shadow caster depending on the state of the "Cast Shadows" checkbox"""
    shadow_caster = bpy.data.lamps.get('RCT_ShadowCaster', None)
    if shadow_caster is None:
        print("WARNING: Rendering Rig does not exist.")
        self["cast_shadows"] = True
        return None
    if self.cast_shadows:
        shadow_caster.shadow_method = "RAY_SHADOW"
        shadow_caster.use_diffuse = True
    else:
        shadow_caster.shadow_method = "NOSHADOW"
        shadow_caster.use_diffuse = False
    return


def update_object_type(self, context):
    """Runs update function for the given object type"""
    if self.objectType == "scenery_small":
        small_scenery_properties = context.scene.rct_graphics_helper_small_scenery_properties
        update_small_scenery(small_scenery_properties, context)
    elif self.objectType == "vehicle":
        vehicles_properties = context.scene.rct_graphics_helper_vehicles_properties
        update_vehicles(vehicles_properties, context)
    elif self.objectType == 'stall':
        stall_properties = context.scene.rct_graphics_helper_stall_properties
        update_stall(stall_properties, context)


# String entries
##############################################

class StringsEntries_OT_actions(bpy.types.Operator):
    """Buttons to add/remove/move a string entry."""
    bl_idname = "stringentries.actions"
    bl_label = "List Actions"
    bl_description = "Add/Remove\n\nMove Up/Down"
    bl_options = {'REGISTER'}

    args = bpy.props.StringProperty(
        name="Action,Type",
        description="")

    def invoke(self, context: bpy.types.Context, event):
        properties = context.scene.rct_graphics_helper_general_properties
        action, string_type = self.args.split(',')
        index = getattr(properties, string_type + "_strings_index")
        strings = getattr(properties, string_type + "_strings")

        try:
            item = strings[index]
        except IndexError:
            pass
        else:
            if action == 'DOWN' and index < len(strings) - 1:
                strings.move(index, index+1)
                setattr(properties, string_type + "_strings_index", index + 1)

            elif action == 'UP' and index >= 1:
                strings.move(index, index-1)
                setattr(properties, string_type + "_strings_index", index + 1)

            elif action == 'REMOVE':
                if index != 0:
                    setattr(properties, string_type + "_strings_index", index + 1)
                strings.remove(index)

        if action == 'ADD':
            item = strings.add()
            setattr(properties, string_type + "_strings_index", len(strings)-1)

        return {"FINISHED"}


class StringsEntries_UL_List(bpy.types.UIList):
    """Defines the drawing function for each string entry item"""
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            split = layout.split(0.4)
            split.prop(item, "language", text="")
            # split.label(str(item.value))
            split.prop(item, "value", "")
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="strings")


class StringsEntry(bpy.types.PropertyGroup):
    """Defines a string entry item. Has a "language" and a "value"."""
    language = bpy.props.EnumProperty(
        items=[
            ("ar-EG", "Arabic (experimental)", "ar-EG"),
            ("ca-ES", "Catalan", "ca-ES"),
            ("zh-CN", "Chinese (Simplified)", "zh-CN"),
            ("zh-TW", "Chinese (Traditional)", "zh-TW"),
            ("cs-CZ", "Czech", "cs-CZ"),
            ("da-DK", "Danish", "da-DK"),
            ("de-DE", "German", "de-DE"),
            ("en-GB", "English (UK)", "en-GB"),
            ("en-US", "English (US)", "en-US"),
            ("eo-OO", "Esperanto", "eo-OO"),
            ("es-ES", "Spanish", "es-ES"),
            ("fr-FR", "French", "fr-FR"),
            ("it-IT", "Italian", "it-IT"),
            ("ja-JP", "Japanese", "ja-JP"),
            ("ko-KR", "Korean", "ko-KR"),
            ("hu-HU", "Hungarian", "hu-HU"),
            ("nl-NL", "Dutch", "nl-NL"),
            ("nb-NO", "Norwegian", "nb-NO"),
            ("pl-PL", "Polish", "pl-PL"),
            ("pt-BR", "Portuguese (BR)", "pt-BR"),
            ("ru-RU", "Russian", "ru-RU"),
            ("fi-FI", "Finnish", "fi-FI"),
            ("sv-SE", "Swedish", "sv-SE"),
            ("tr-TR", "Turkish", "tr-TR"),
            ("vi-VN", "Vietnamese", "vi-VN")],
        name="Language",
        description=(
            "The language/locale of this string entry"),
        default="en-GB")
    value = bpy.props.StringProperty(
        name="String",
        description="The string to use for this language",
        default=""
    )


# General Properties and Panel
##############################

class GeneralProperties(bpy.types.PropertyGroup):
    """Defines the group of general properties for all object types."""
    id = bpy.props.StringProperty(
        name="OpenRCT2 ID",
        description="OpenRCT2 id of the object. This should be formatted as objectsource.objecttype.objectname."
        "This value MUST be universally unique.",
        default="my.scenery_small.object"
    )
    authors = bpy.props.StringProperty(
        name="Authors",
        description="Authors of this object. Separate multiple authors with a comma.",
        default="OpenRCT2 developers"
    )
    version = bpy.props.StringProperty(
        name="Version",
        description="Version of the object.",
        default="1.0"
    )
    originalId = bpy.props.StringProperty(
        name="Original ID",
        description="For converted objects, this represents the original DAT header. The three sections are "
        "the flags, name, and checksum. Leave this blank for new (not converted) objects.",
        default=""
    )
    sourceGame = bpy.props.StringProperty(
        name="Source Game",
        description=(
            "The source(s) of the object. Separate multiple sources with a comma.\n\nSources must be one of:\n"
            "'rct1', 'rct1aa', 'rct1ll', 'rct2', 'rct2ww', 'rct2tt', 'official', or 'custom'\n(Anything else "
            "is registered as custom by OpenRCT2)"),
        default="custom"
    )
    objectType = bpy.props.EnumProperty(
        items=[
            ("custom", "Custom", "Creates an object with custom properties"),
            ("stall", "Stall", "Creates a Stall object"),
            ("flat_ride", "Flat Ride", "Creates a Flat Ride object"),
            ("vehicle", "Ride Vehicles", "Creates a Ride Vehicles object"),
            ("footpath_item", "Footpath Item", "Creates a Footpath Item object"),
            ("scenery_small", "Small Scenery", "Creates a Small Scenery object"),
            ("scenery_large", "Large Scenery", "Creates a Large Scenery object"),
            ("scenery_wall", "Wall", "Creates a Wall object"),
            ("scenery_group", "Scenery Group", "Creates a Scenery Group object"),
            ("park_entrance", "Park Entrance", "Creates a Park Entrance object"),
            ("terrain_surface", "Terrrain Surface",
             "Creates a Terrrain Surface object"),
            ("terrain_edge", "Terrrain Edge", "Creates a Terrrain Edge object"),
            ("station", "Station", "Creates a Station object"),
            ("footpath_surface", "Footpath Surface",
             "Creates a Footpath Surface object"),
            ("footpath_railings", "Footpath Railings",
             "Creates a Footpath Railings object"),
        ],
        name="Type",
        description=(
            "Selects the object type to create."),
        default="scenery_small",
        update=update_object_type
    )
    name_strings = bpy.props.CollectionProperty(
        type=StringsEntry,
        name="Name Strings",
        description=("Contains the name of the object in all the different supported languages."))
    name_strings_index = bpy.props.IntProperty(default=0)
    description_strings = bpy.props.CollectionProperty(
        type=StringsEntry,
        name="Description Strings",
        description=("Contains a short description of the object in all the different supported languages."))
    description_strings_index = bpy.props.IntProperty(default=0)
    capacity_strings = bpy.props.CollectionProperty(
        type=StringsEntry,
        name="Capacity Strings",
        description=("For rides, this contains text describing the capacity in all the different supported languages."))
    capacity_strings_index = bpy.props.IntProperty(default=0)

    dither_threshold = bpy.props.FloatProperty(
        name="Dither Threshold",
        description="A value from 0 to 1 that controls how strongly to apply the dithering. 0 disables dithering",
        min=0.00, max=1.00, step=10, precision=2, default=0.30)
    edge_darkening = bpy.props.FloatProperty(
        name="Edge Darkening",
        description="Applies a post-processing darkening around the edges of the rendered sprite. 0 disables",
        min=0.0, soft_max=1.0, step=10, precision=1, default=0.0)
    cast_shadows = bpy.props.BoolProperty(
        name="Cast Shadows",
        description="Controls whether or not the render contains shadows. Should be disabled for vehicles",
        default=True,
        update=update_shadows)


class GeneralPanel(bpy.types.Panel):
    """Defines the drawing function for the RCT General panel"""
    bl_label = "RCT General"
    bl_idname = "RENDER_PT_rct_general"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        wm = context.window_manager
        general_properties = scene.rct_graphics_helper_general_properties
        row = layout.row()
        row.operator("render.rct_import_json")
        # Draw previews
        row = layout.row()
        col = row.column()
        col.label("Preview")
        col.template_icon_view(wm, "my_previews", show_labels=True, scale=3.0)
        col.prop(wm, "my_previews", text="")
        # Set up render rig button
        row = layout.row()
        row.operator("render.rct_create_rig", text="Set Up Rendering Rig")
        # Basic object properties
        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(general_properties, "id")
        row = col.row(align=True)
        row.prop(general_properties, "originalId")
        row = col.row(align=True)
        row.prop(general_properties, "authors")
        row = col.row(align=True)
        row.prop(general_properties, "sourceGame")
        row = layout.row().split(0.6, align=True)
        row.prop(general_properties, "objectType")
        row.prop(general_properties, "version")
        
        box = layout.box()

        row = box.row()
        row.prop(
            scene, "rct_strings_expanded",
            icon="TRIA_DOWN" if scene.rct_strings_expanded else "TRIA_RIGHT",
            icon_only=True, emboss=False
        )
        row.label(text="Strings")
        if scene.rct_strings_expanded:
            # Name Strings
            col = box.column()
            head = col.row()
            head.label("Name:")
            sub = col.row()
            subcol = sub.column(align=True)
            subcol.template_list("StringsEntries_UL_List", "", general_properties, "name_strings",
                                 general_properties, "name_strings_index", rows=3)
            subcol = sub.column(align=True)
            subcol.operator("stringentries.actions", icon='ZOOMIN', text="").args = 'ADD,name'
            subcol.operator("stringentries.actions", icon='ZOOMOUT', text="").args = 'REMOVE,name'
            subcol.separator()
            subcol.operator("stringentries.actions", icon='TRIA_UP', text="").args = 'UP,name'
            subcol.operator("stringentries.actions", icon='TRIA_DOWN', text="").args = 'DOWN,name'
            # Description Strings
            col = box.column()
            head = col.row()
            head.label("Description:")
            sub = col.row()
            subcol = sub.column(align=True)
            subcol.template_list("StringsEntries_UL_List", "", general_properties, "description_strings",
                                 general_properties, "description_strings_index", rows=3)
            subcol = sub.column(align=True)
            subcol.operator("stringentries.actions", icon='ZOOMIN', text="").args = 'ADD,description'
            subcol.operator("stringentries.actions", icon='ZOOMOUT', text="").args = 'REMOVE,description'
            subcol.separator()
            subcol.operator("stringentries.actions", icon='TRIA_UP', text="").args = 'UP,description'
            subcol.operator("stringentries.actions", icon='TRIA_DOWN', text="").args = 'DOWN,description'
            # Capacity Strings
            col = box.column()
            head = col.row()
            head.label("Capacity:")
            sub = col.row()
            subcol = sub.column(align=True)
            subcol.template_list("StringsEntries_UL_List", "", general_properties, "capacity_strings",
                                 general_properties, "capacity_strings_index", rows=3)
            subcol = sub.column(align=True)
            subcol.operator("stringentries.actions", icon='ZOOMIN', text="").args = 'ADD,capacity'
            subcol.operator("stringentries.actions", icon='ZOOMOUT', text="").args = 'REMOVE,capacity'
            subcol.separator()
            subcol.operator("stringentries.actions", icon='TRIA_UP', text="").args = 'UP,capacity'
            subcol.operator("stringentries.actions", icon='TRIA_DOWN', text="").args = 'DOWN,capacity'
        
        # Render Settings
        layout.label("Render Settings:")
        row = layout.row()
        row.prop(general_properties, "dither_threshold")
        row.prop(general_properties, "edge_darkening")
        row = layout.row()
        row.prop(general_properties, "cast_shadows")


# Hacky way to have code run on initialization
##############################################


def collhack(scene):
    """Runs initial code for initialization of this panel"""
    print("Initializing")
    bpy.app.handlers.scene_update_pre.remove(collhack)
    bpy.ops.render.rct_create_rig()
    update_object_type(
        scene.rct_graphics_helper_general_properties, bpy.context)


def register_general_panel():
    """Registers the general panel and general properties"""
    pcoll = render_operator.preview_collections.setdefault("main", bpy.utils.previews.new())
    bpy.types.WindowManager.my_previews = bpy.props.EnumProperty(
        items=enum_previews_from_directory_items)
    bpy.types.Scene.rct_strings_expanded = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.rct_graphics_helper_general_properties = bpy.props.PointerProperty(
        type=GeneralProperties)
    bpy.app.handlers.scene_update_pre.append(collhack)
    bpy.app.handlers.load_post.append(collhack)


def unregister_general_panel():
    """Unregisters the general panel and general properties"""
    render_operator.removePreviews()
    del bpy.types.WindowManager.my_previews
    del bpy.types.Scene.rct_graphics_helper_general_properties
