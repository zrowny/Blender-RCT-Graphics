'''
Copyright (c) 2021 RCT Graphics Helper developers

For a complete list of all authors, please refer to the addon's meta info.
Interested in contributing? Visit https://github.com/oli414/Blender-RCT-Graphics

RCT Graphics Helper is licensed under the GNU General Public License version 3.
'''

from sys import version
import bpy
import bpy.utils.previews
import math
import os
from . small_scenery_panel import update_small_scenery
from . render_task import get_res_path, get_output_path
from . import render_operator as render_operator
from . custom_properties import create_size_preview


def enum_previews_from_directory_items(self, context):
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


class RCTCreateRig(bpy.types.Operator):
    bl_idname = "render.rct_create_rig"
    bl_label = "Create Rendering Rig"

    def execute(self, context):
        scene = bpy.context.scene
        objects = bpy.data.objects
        lamps = bpy.data.lamps
        rct_rig = objects.get('RCT_Rig')
        if rct_rig is None:
            rct_rig = objects.new("RCT_Rig", None)
            scene.objects.link(rct_rig)
        rct_vertical_joint = objects.get('RCT_VerticalJoint')
        if rct_vertical_joint is None:
            rct_vertical_joint = objects.new("RCT_VerticalJoint", None)
            scene.objects.link(rct_vertical_joint)
        rct_vertical_joint.parent = rct_rig
        rct_camera = objects.get('RCT_Camera')
        if objects.get('RCT_Camera') is None:
            rct_camera_data = bpy.data.cameras.new("RCT_Camera")
            rct_camera = objects.new("RCT_Camera", rct_camera_data)
            scene.objects.link(rct_camera)
        rct_camera_data = rct_camera.data  # type: bpy.types.Camera
        rct_camera_data.ortho_scale = 5.657
        rct_camera_data.type = "ORTHO"
        rct_camera.location = ((1/64)-20/math.sqrt(2),
                               (1/64)-20/math.sqrt(2), 20*math.tan(math.pi/6))
        rct_camera.rotation_euler = [math.pi/3, 0, -math.pi/4]
        rct_camera.parent = rct_vertical_joint
        scene.camera = rct_camera

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
            light.location = (16, -14, 12)
            constraint = light.constraints.new("DAMPED_TRACK")  # type: bpy.types.DampedTrackConstraint
            constraint.target = rct_vertical_joint
            constraint.track_axis = "TRACK_NEGATIVE_Z"
            light.parent = rct_vertical_joint
            light.hide = True

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
                light.location = (-2.5, 23, 14)
                constraint = light.constraints.new("DAMPED_TRACK")  # type: bpy.types.DampedTrackConstraint
                constraint.target = rct_vertical_joint
                constraint.track_axis = "TRACK_NEGATIVE_Z"
                light.parent = rct_vertical_joint
                light.hide = True

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
                light.location = (5, -18.5, 1.5)
                # type: bpy.types.DampedTrackConstraint
                constraint = light.constraints.new("DAMPED_TRACK")
                constraint.target = rct_vertical_joint
                constraint.track_axis = "TRACK_NEGATIVE_Z"
                light.parent = rct_vertical_joint
                light.hide = True

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
                light.location = (16, -14, 12)
                constraint = light.constraints.new("DAMPED_TRACK")  # type: bpy.types.DampedTrackConstraint
                constraint.target = rct_vertical_joint
                constraint.track_axis = "TRACK_NEGATIVE_Z"
                light.parent = rct_vertical_joint
                light.hide = True

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
                light.location = (-18, -1.5, 8)
                constraint = light.constraints.new("DAMPED_TRACK")  # type: bpy.types.DampedTrackConstraint
                constraint.target = rct_vertical_joint
                constraint.track_axis = "TRACK_NEGATIVE_Z"
                light.parent = rct_vertical_joint
                light.hide = True

            light = objects.get('RCT_SpecularLight')
            if objects.get('RCT_SpecularLight') is None:
                light_data = lamps.new("RCT_SpecularLight", "SPOT")
                light = objects.new("RCT_SpecularLight", light_data)
                scene.objects.link(light)
                light_data = light.data  # type: bpy.types.SpotLamp
                light_data.energy = 0.3
                light_data.falloff_type = "CONSTANT"
                light_data.shadow_method = "NOSHADOW"
                light.location = (16, -14, 12)
                constraint = light.constraints.new("DAMPED_TRACK")  # type: bpy.types.DampedTrackConstraint
                constraint.target = rct_vertical_joint
                constraint.track_axis = "TRACK_NEGATIVE_Z"
                light.parent = rct_vertical_joint
                light.hide = True
        
        create_size_preview()

        return {"FINISHED"}


def ToggleShadows(self, context):
    shadow_caster = bpy.data.lamps['ShadowCasterLamp']
    if shadow_caster is None:
        return False
    print(shadow_caster.shadow_method)
    if self.cast_shadows:
        shadow_caster.shadow_method = "RAY_SHADOW"
        shadow_caster.use_diffuse = True
    else:
        shadow_caster.shadow_method = "NOSHADOW"
        shadow_caster.use_diffuse = False
    return


def update_object_type(self, context):
    if self.objectType == "scenery_small":
        small_scenery_properties = context.scene.rct_graphics_helper_small_scenery_properties
        update_small_scenery(small_scenery_properties, context)
    pass


class StringsEntries_OT_actions(bpy.types.Operator):
    """Move items up and down, add and remove"""
    bl_idname = "stringentries.actions"
    bl_label = "List Actions"
    bl_description = "Add\nRemove\n\nMove Up\nMove Down"
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


class GeneralProperties(bpy.types.PropertyGroup):
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
            ("ride", "Ride", "Creates a Ride object"),
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
        name="Object Type",
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
        default=False,
        update=ToggleShadows)


class GeneralPanel(bpy.types.Panel):
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
        col = row.column()
        col.label("Preview")
        col.template_icon_view(wm, "my_previews", show_labels=True, scale=3.0)
        col.prop(wm, "my_previews", text="")
        row = layout.row()
        row.operator("render.rct_create_rig", text="Set Up Rendering Rig")

        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(general_properties, "id")
        row = col.row(align=True)
        row.prop(general_properties, "originalId")
        row = col.row(align=True)
        row.prop(general_properties, "authors")
        row = col.row(align=True)
        row.prop(general_properties, "sourceGame")
        
        row = layout.row().split(0.7, align=True)
        row.prop(general_properties, "objectType")
        row.prop(general_properties, "version")

        col = layout.column()
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

        col = layout.column()
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

        col = layout.column()
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

        row = layout.row()
        row.prop(general_properties, "dither_threshold")
        row.prop(general_properties, "edge_darkening")
        row = layout.row()
        row.prop(general_properties, "cast_shadows")


def collhack(scene):
    bpy.app.handlers.scene_update_pre.remove(collhack)
    update_object_type(
        scene.rct_graphics_helper_general_properties, bpy.context)


def register_general_panel():
    pcoll = render_operator.preview_collections.setdefault("main", bpy.utils.previews.new())
    bpy.types.WindowManager.my_previews = bpy.props.EnumProperty(
        items=enum_previews_from_directory_items)
    bpy.types.Scene.rct_graphics_helper_general_properties = bpy.props.PointerProperty(
        type=GeneralProperties)
    bpy.app.handlers.scene_update_pre.append(collhack)


def unregister_general_panel():
    render_operator.removePreviews()
    del bpy.types.WindowManager.my_previews
    del bpy.types.Scene.rct_graphics_helper_general_properties
