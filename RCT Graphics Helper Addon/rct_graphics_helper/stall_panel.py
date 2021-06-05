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
from . import json_functions as json_functions


def update_stall(self, context: bpy.types.Context):
    """Run when when various stall properties are updated.
    
    Updates the size preview, render layers, and stall properties that
    may conflict with each other if they are set at the same time."""
    properties = self  # type: StallProperties
    scene = context.scene
    objects = bpy.data.objects

    # Make sure render_layers are set up
    render_layers = scene.render.layers
    render_layers.new("Normal")
    render_layers.new("In Front")
    for render_layer in render_layers:
        if render_layer.name != "Normal" and render_layer.name != "In Front":
            render_layers.remove(render_layer)
    layer_normal = render_layers.get("Normal")
    layer_normal.layers = [i == 0 or i == 10 for i in range(20)]
    layer_normal.use_pass_material_index = True
    layer_front = render_layers.get("In Front")
    layer_front.layers = [i == 0 or i == 10 for i in range(20)]
    layer_front.use_zmask = True
    layer_front.invert_zmask = True

    if properties.type in ("cash_machine", "toilets"):
        properties.height = 32
    elif properties.type in ("first_aid", "information_kiosk"):
        properties.height = 48
    else:
        properties.height = 64
    
    objects.get("RCT_Full_Tile").hide = False
    objects.get("RCT_One_Quarter").hide = True
    objects.get("RCT_Diagonal_1").hide = True
    objects.get("RCT_Diagonal_2").hide = True
    objects.get("RCT_Three_Quarter").hide = True
    objects.get("RCT_Half_Tile").hide = True


def add_stall_properties_json(context):
    """Processes stall properties and adds them to the global JSON"""
    json_properties = json_functions.group_as_dict(context.scene.rct_graphics_helper_stall_properties)
    json_properties.pop("height", None)
    sells1 = json_properties.pop("sells", "none")
    sells2 = json_properties.pop("sells2", "none")
    sells = []
    type = json_properties.get("type")
    raw_car_colours = custom_properties.process_car_colours(context)
    json_properties["carColours"] = raw_car_colours
    if type not in ("toilets", "first_aid", "cash_machine"):
        if sells1 in recolorable_shop_items:
            if sells2 != "none":
                sells.append(sells2)
            sells.append(sells1)
        elif sells1 != "none":
            sells.append(sells1)
            if sells2 != "none":
                sells.append(sells2)
        json_properties["sells"] = sells
    
    json_functions.json_data["properties"] = json_properties


class AddStallMask(bpy.types.Operator):
    """Operator to render stall objects."""
    bl_idname = "object.rct_add_stall_mask"
    bl_label = "Render RCT Stall"

    def execute(self, context):
        scene = context.scene
        objects = bpy.data.objects
        materials = bpy.data.materials
        rct_stall_mask_mesh = bpy.data.meshes.get("RCT_stall_mask_mesh")
        if rct_stall_mask_mesh is None:
            vertices = [(-0.25, -0.25, 0.0), (-0.25, -0.25, 0.5), (-0.25, 0.25, 0.0), (-0.25, 0.25, 0.5),
                        (0.25, -0.25, 0.0), (0.25, -0.25, 0.5), (0.25, 0.25, 0.0), (0.25, 0.25, 0.5)]
            edges = [(0, 1), (1, 3), (3, 2), (2, 0), (4, 5), (5, 7), (7, 6), (6, 4), (0, 4), (1, 5), (2, 6), (3, 7)]
            faces = [(0, 2, 6, 4), (0, 1, 3, 2), (0, 1, 5, 4), (4, 5, 7, 6), (2, 3, 7, 6), (1, 3, 7, 5)]
            rct_stall_mask_mesh = bpy.data.meshes.new("RCT_stall_mask_mesh")
            rct_stall_mask_mesh.from_pydata(vertices, [], faces)
            rct_stall_mask_mesh.update()
        rct_stall_mask = objects.get("RCT_stall_mask")
        if rct_stall_mask is None:
            rct_stall_mask = objects.new("RCT_stall_mask", rct_stall_mask_mesh)
            scene.objects.link(rct_stall_mask)
        rct_stall_mask.location = (-1, 0, 0)
        rct_stall_mask.layers = [i == 1 for i in range(20)]
        rct_mask_mat = materials.get("RCT_mask_material")
        if rct_mask_mat is None:
            rct_mask_mat = materials.new("RCT_mask_material")
        rct_mask_mat.diffuse_color = (0.0, 0.0, 0.0)
        rct_mask_mat.use_transparency = True
        rct_mask_mat.alpha = 0.5
        rct_mask_mat.use_shadeless = True
        rct_mask_mat.use_cast_shadows = False
        rct_mask_mat.use_cast_buffer_shadows = False
        rct_mask_mat.use_cast_approximate = False
        rct_mask_mat.use_raytrace = False
        rct_stall_mask.data.materials.clear()
        rct_stall_mask.data.materials.append(rct_mask_mat)
        scene.layers = [i == 1 or scene.layers[i] for i in range(20)]
        return {"FINISHED"}


class RenderStall(RCTRender, bpy.types.Operator):
    """Operator to render stall objects."""
    bl_idname = "render.rct_stall"
    bl_label = "Render RCT Stall"
    
    def execute(self, context):
        self.scene = context.scene
        self.stall_properties = (
            self.scene.rct_graphics_helper_stall_properties)  # type: StallProperties
        update_stall(self.stall_properties, context)
        self.renderTask = RenderTask(context)

        add_stall_properties_json(context)
        # print("JSON data:\n%s" % json_functions.json_data)
        
        remap = 0
        offset = (0, 15)
        layer_normal = self.scene.render.layers.get("Normal")
        layer_front = self.scene.render.layers.get("In Front")
        self.renderTask.add([Angle(0, 0, 0, 0)], remap, "Normal", [0, 10], offset=(56, 56))
        self.renderTask.add(blank=True)
        self.renderTask.add(blank=True)
        if self.stall_properties.type in ("toilets", "first_aid"):
            angles = AngleSection(False, 4, 0, 0, 0).angles
            layer_normal.layers_zmask = [i == 1 for i in range(20)]
            layer_front.layers_zmask = [i == 1 for i in range(20)]
            self.renderTask.add([angles[0]], remap, "In Front", [0, 1, 10], offset=offset)
            self.renderTask.add(angles[1:3], remap, "Normal", [0, 1, 10], offset=offset)
            self.renderTask.add([angles[3]], remap, "In Front", [0, 1, 10], offset=offset)
            self.renderTask.add(angles[::3], remap, "Normal", [0, 1, 10], offset=offset)
        else:
            angles = AngleSection(False, 4, 0, 0, 180).angles
            layer_normal.layers_zmask = [False for i in range(20)]
            if not self.stall_properties.disablePainting:
                remap = 1
            self.renderTask.add(angles, remap, "Normal", [0, 10], offset=offset)
        return super().execute(context)

    def finished(self, context):
        """Runs when rendering is completely finished."""
        super().finished(context)
        self.report({'INFO'}, 'RCT Stall render finished.')


shop_items = [
    ("none", "No Item", ""),
    ("burger", "Burger", ""),
    ("chips", "Chips", ""),
    ("ice_cream", "Ice Cream", ""),
    ("candyfloss", "Candyfloss", ""),
    ("pizza", "Pizza", ""),
    ("popcorn", "Popcorn", ""),
    ("hot_dog", "Hotdog", ""),
    ("tentacle", "Tentacle", ""),
    ("toffee_apple", "Toffee Apple", ""),
    ("doughnut", "Doughnut", ""),
    ("chicken", "Chicken", ""),
    ("pretzel", "Pretzel", ""),
    ("funnel_cake", "Funnel Cake", ""),
    ("beef_noodles", "Beef Noodles", ""),
    ("fried_rice_noodles", "Fried Rice Noodles", ""),
    ("wonton_soup", "Wonton Soup", ""),
    ("meatball_soup", "Meatball Soup", ""),
    ("sub_sandwich", "Sub Sandwich", ""),
    ("cookie", "Cookie", ""),
    ("roast_sausage", "Roast Sausage", ""),
    ("drink", "Drink", ""),
    ("coffee", "Coffee", ""),
    ("lemonade", "Lemonade", ""),
    ("chocolate", "Chocolate", ""),
    ("iced_tea", "Iced Tea", ""),
    ("fruit_juice", "Fruit Juice", ""),
    ("soybean_milk", "Soybean Milk", ""),
    ("sujeonggwa", "Sujeonggwa", ""),
    ("toy", "Toy", ""),
    ("map", "Map", ""),
    ("photo", "Photo", ""),
    ("voucher", "Voucher", ""),
    ("sunglasses", "Sunglasses", ""),
    ("balloon", "Balloon", ""),
    ("umbrella", "Umbrella", ""),
    ("hat", "Hat", ""),
    ("tshirt", "T-Shirt", "")
]
recolorable_shop_items = ["balloon", "umbrella", "hat", "tshirt"]


def update_sells(self, context):
    if self.sells2 in recolorable_shop_items:
        if self.sells in recolorable_shop_items:
            print("WARNING: Cannot sell two recolorable items.")
            self.sells = "none"
        self.disablePainting = False
    elif self.sells in recolorable_shop_items:
        self.disablePainting = False
    else:
        self.disablePainting = True


class StallProperties(bpy.types.PropertyGroup):
    """Defines the group of properties for stall objects."""
    
    type = bpy.props.EnumProperty(
        items=[("food_stall", "Food Stall", ""),
               ("drink_stall", "Drink Stall", ""),
               ("shop", "Shop", ""),
               ("information_kiosk", "Information Kiosk", ""),
               ("toilets", "Toilets", ""),
               ("cash_machine", "Cash Machine", ""),
               ("first_aid", "First Aid", "")],
        name="Stall type",
        description="The type of this stall.",
        default="food_stall",
        update=update_stall
    )
    
    sells = bpy.props.EnumProperty(
        items=shop_items,
        name="Sells",
        description="First item sold by the shop",
        default="none",
        update=update_sells
    )
    sells2 = bpy.props.EnumProperty(
        items=shop_items,
        name="Sells",
        description="Second item sold by the shop",
        default="none",
        update=update_sells
    )
    disablePainting = bpy.props.BoolProperty(
        name="Disable Painting",
        description="If true, the painting tab is disabled for this object.\n\nOnly used for stalls that sell "
        "things (\"Drink Stalls\", \"Food Stalls\", \"Information Kiosks\", and \"Shops\"), and should only be true"
        "if what it sells is recolorable (and/or if the stall itself is recolorable, but you should probably only do "
        "that if what it sells is recolorable).",
        default=False
    )

    height = custom_properties.height


class StallPanel(bpy.types.Panel):
    """Defines the drawing function for the RCT Stall panel"""
    bl_label = "RCT Stall"
    bl_idname = "RENDER_PT_rct_stall"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    @classmethod
    def poll(cls, context: bpy.types.Context):
        general_properties = context.scene.rct_graphics_helper_general_properties
        return general_properties.objectType == "stall"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        stall_properties = scene.rct_graphics_helper_stall_properties  # type: StallProperties

        row = layout.row()
        row.operator("render.rct_stall", text="Render Stall Object")

        row = layout.row()
        row.prop(stall_properties, "type")
        type = stall_properties.type
        if type in ("toilets", "first_aid"):
            row = layout.row()
            row.operator("object.rct_add_stall_mask", "Add Mask Cube")
        col = layout.column()
        if type in ("toilets", "first_aid", "cash_machine"):
            col.enabled = False
            type_name = stall_properties.bl_rna.properties['type'].enum_items.get(type).name
            row = col.row()
            row.label("%s cannot sell items or be painted" % type_name)
        # else:
        row = col.row()
        row.prop(stall_properties, "disablePainting", toggle=True)
        row = col.row(align=True)
        row.label("Sells:")
        row.prop(stall_properties, "sells", "")
        row.prop(stall_properties, "sells2", "")

        row = col.row()
        row.label("Color Presets:")
        row = col.row()
        subcol = row.column(align=True)
        subcol.template_list("CarColours_UL_List", "", scene, "carColours",
                             scene, "car_colours_index")
        subcol = row.column(align=True)
        subcol.operator("carcolours.actions",
                        icon='ZOOMIN', text="").action = 'ADD'
        subcol.operator("carcolours.actions",
                        icon='ZOOMOUT', text="").action = 'REMOVE'
        subcol.separator()
        subcol.operator("carcolours.actions",
                        icon='TRIA_UP', text="").action = 'UP'
        subcol.operator("carcolours.actions",
                        icon='TRIA_DOWN', text="").action = 'DOWN'


def register_stall_panel():
    """Registers the stall panel and properties"""
    bpy.types.Scene.rct_graphics_helper_stall_properties = bpy.props.PointerProperty(
        type=StallProperties)
    bpy.types.Scene.rct_graphics_helper_stall_properties
    bpy.types.Scene.carColours = custom_properties.carColours
    bpy.types.Scene.car_colours_index = custom_properties.car_colours_index
    bpy.types.Scene.car_colours_single_preset = custom_properties.car_colours_single_preset


def unregister_stall_panel():
    """Unregisters the stall panel and properties"""
    del bpy.types.Scene.rct_graphics_helper_stall_properties
