'''
Copyright (c) 2021 RCT Graphics Helper developers

For a complete list of all authors, please refer to the addon's meta info.
Interested in contributing? Visit https://github.com/oli414/Blender-RCT-Graphics

RCT Graphics Helper is licensed under the GNU General Public License version 3.
'''

import bpy
from bpy.types import Action, EnumProperty, Property, bpy_struct
from . json_functions import group_as_dict


# Processing Ride type
#######################

ride_type_stall = ("food_stall", "drink_stall", "shop", "information_kiosk", "toilets", "cash_machine", "first_aid")
ride_type_vehicle = (
    "spiral_rc", "stand_up_rc", "suspended_swinging_rc", "inverted_rc", "junior_rc", "miniature_railway", "monorail",
    "mini_suspended_rc", "boat_hire", "wooden_wild_mouse", "steeplechase", "car_ride", "launched_freefall",
    "bobsleigh_rc", "observation_tower", "looping_rc", "dinghy_slide", "mine_train_rc", "chairlift", "corkscrew_rc",
    "maze", "go_karts", "log_flume", "river_rapids", "reverse_freefall_rc", "lift", "vertical_drop_rc", "ghost_train",
    "twister_rc", "wooden_rc", "side_friction_rc", "steel_wild_mouse", "multi_dimension_rc", "flying_rc",
    "virginia_reel", "splash_boats", "mini_helicopters", "lay_down_rc", "suspended_monorail", "reverser_rc",
    "heartline_twister_rc", "mini_golf", "giga_rc", "roto_drop", "monorail_cycles", "compact_inverted_rc",
    "water_coaster", "air_powered_vertical_rc", "inverted_hairpin_rc", "submarine_ride", "river_rafts",
    "inverted_impulse_rc", "mini_rc", "mine_ride", "lim_launched_rc", "hypercoaster", "hyper_twister",
    "monster_trucks", "spinning_wild_mouse", "classic_mini_rc", "hybrid_rc", "single_rail_rc")
ride_type_flat = (
    "circus", "crooked_house", "dodgems", "ferris_wheel", "flying_saucers", "haunted_house", "merry_go_round",
    "space_rings", "spiral_slide", "3d_cinema", "enterprise", "magic_carpet", "motion_simulator", "swinging_ship",
    "swinging_inverter_ship", "top_spin", "twist", )


def process_ride_type(json_data):
    properties = json_data.get('properties', None)
    if properties is not None:
        type = properties.get('type', None)
        if isinstance(type, list):
            type = type[0]
        if type in ride_type_stall:
            return 'stall'
        if type in ride_type_flat:
            return 'flat_ride'
        if type in ride_type_vehicle:
            return 'vehicle'
    return None


def set_property(properties, json_data, property, default=None):
    """Safely sets a given property in a PropertyGroup from the given data

    Args:
        properties (bpy.types.PropertyGroup): The group to set a property in
        json_data (dict): A dict from which to take a property
        property (str): The key of the property to use
        default (Any, optional): A default value to use if `property` does not
            exist in `json_data`. If `None`, the property will not be updated
            if it doesn't exist in `json_data`

    Returns:
        Any: The value that was actually set in `properties`
    """
    value = json_data.get(property, None)
    if value is None:
        if default is not None:
            value = default
        else:
            return None
    elif isinstance(value, list):
        value = ", ".join(value)
    setattr(properties, property, value)
    # print("%s: %s" % (property, value))
    return value


def create_size_preview():
    """Generates the meshes and objects to show the size "preview"."""
    scene = bpy.context.scene
    objects = bpy.data.objects
    lamps = bpy.data.lamps
    rct_size_preview = objects.get("RCT_Size_Preview")
    if rct_size_preview is None:
        rct_size_preview = objects.new("RCT_Size_Preview", None)
        scene.objects.link(rct_size_preview)
    rct_size_preview.hide = True
    rct_size_preview.hide_select = True
    rct_size_preview.layers = [i == 10 for i in range(20)]

    rct_box_mesh = bpy.data.meshes.get("RCT_preview_cube")
    if rct_box_mesh is None:
        vertices = [(-0.5, -0.5, 0.0), (-0.5, -0.5, 1.0), (-0.5, 0.5, 0.0), (-0.5, 0.5, 1.0),
                    (0.5, -0.5, 0.0), (0.5, -0.5, 1.0), (0.5, 0.5, 0.0), (0.5, 0.5, 1.0)]
        edges = [(0, 1), (1, 3), (3, 2), (2, 0), (4, 5), (5, 7), (7, 6), (6, 4), (0, 4), (1, 5), (2, 6), (3, 7)]
        rct_box_mesh = bpy.data.meshes.new("RCT_preview_cube")
        rct_box_mesh.from_pydata(vertices, edges, [])
        rct_box_mesh.update()
    rct_box = objects.get("RCT_Full_Tile")
    if rct_box is None:
        rct_box = objects.new("RCT_Full_Tile", rct_box_mesh)
        scene.objects.link(rct_box)
    rct_box.hide_select = True
    rct_box.scale = (1.0, 1.0, 0.025516)
    rct_box.location = (0, 0, 0)
    rct_box.parent = rct_size_preview
    rct_box.layers = [i == 10 for i in range(20)]

    rct_box = objects.get("RCT_Half_Tile")
    if rct_box is None:
        rct_box = objects.new("RCT_Half_Tile", rct_box_mesh)
        scene.objects.link(rct_box)
    rct_box.hide_select = True
    rct_box.scale = (0.5, 1, 0.025516)
    rct_box.location = (0.25, 0, 0)
    rct_box.parent = rct_size_preview
    rct_box.layers = [i == 10 for i in range(20)]

    rct_box = objects.get("RCT_One_Quarter")
    if rct_box is None:
        rct_box = objects.new("RCT_One_Quarter", rct_box_mesh)
        scene.objects.link(rct_box)
    rct_box.hide_select = True
    rct_box.scale = (0.5, 0.5, 0.025516)
    rct_box.location = (0, 0, 0)
    rct_box.parent = rct_size_preview
    rct_box.layers = [i == 10 for i in range(20)]

    rct_box = objects.get("RCT_Diagonal_1")
    if rct_box is None:
        rct_box = objects.new("RCT_Diagonal_1", rct_box_mesh)
        scene.objects.link(rct_box)
    rct_box.hide_select = True
    rct_box.scale = (0.5, 0.5, 0.025516)
    rct_box.location = (-0.25, 0.25, 0.)
    rct_box.parent = rct_size_preview
    rct_box.layers = [i == 10 for i in range(20)]

    rct_box = objects.get("RCT_Diagonal_2")
    if rct_box is None:
        rct_box = objects.new("RCT_Diagonal_2", rct_box_mesh)
        scene.objects.link(rct_box)
    rct_box.hide_select = True
    rct_box.scale = (0.5, 0.5, 0.025516)
    rct_box.location = (0.25, -0.25, 0)
    rct_box.parent = rct_size_preview
    rct_box.layers = [i == 10 for i in range(20)]

    rct_box = objects.get("RCT_Three_Quarter")
    if rct_box is None:
        vertices = [(0.0, 0.0, 0.0), (0.0, 0.0, 1.0), (0.5, 0.5, 0.0), (0.5, 0.5, 1.0),
                    (0.0, -0.5, 0.0), (0.0, -0.5, 1.0), (0.5, -0.5, 0.0), (0.5, -0.5, 1.0),
                    (-0.5, 0.0, 0.0), (-0.5, 0.0, 1.0), (-0.5, 0.5, 0.0), (-0.5, 0.5, 1.0)]
        edges = [(0, 1), (3, 2), (4, 5), (6, 7), (5, 7), (3, 7), (1, 5), (8, 9), (9, 11), (11, 10),
                 (3, 11), (1, 9), (2, 10), (8, 10), (0, 8), (2, 6), (0, 4), (4, 6)]
        rct_box_mesh = bpy.data.meshes.new("RCT_preview_three_quarters")
        rct_box_mesh.from_pydata(vertices, edges, [])
        rct_box_mesh.update()
        rct_box = objects.new("RCT_Three_Quarter", rct_box_mesh)
        scene.objects.link(rct_box)
    rct_box.hide_select = True
    rct_box.scale = (1, 1, 0.025516)
    rct_box.location = (0, 0, 0)
    rct_box.parent = rct_size_preview
    rct_box.layers = [i == 10 for i in range(20)]
    scene.layers = [scene.layers[i] or i == 10 for i in range(20)]

    return rct_size_preview


def update_height(self, context):
    """Updates the height of the size preview."""
    # rct_size_preview = bpy.data.objects.get('RCT_Size_Preview')
    # if rct_size_preview is None:
    rct_size_preview = create_size_preview()
    rct_size_preview.scale = (1, 1, self.height)


def update_colors(self, context):
    """Runs when remap colors are selected to ensure sensible values."""
    properties = self
    properties["hasPrimaryColour"] = (
        properties.hasPrimaryColour or properties.hasSecondaryColour or properties.hasTernaryColour)
    properties["hasSecondaryColour"] = (properties.hasSecondaryColour or properties.hasTernaryColour)


# Custom properties to reuse for different object types
#######################################################

height = bpy.props.IntProperty(
    name="Height",
    description=(
        "Height of the object, where there are 8 units per height step (for reference, a "
        "\"quarter\" height wall is one step = 8 units high). Therefore this value is generally a "
        "multiple of eight."),
    default=16,
    min=0,
    step=8,  # step is unused by blender, but I wish it was
    update=update_height)

hasPrimaryColour = bpy.props.BoolProperty(
    name="Primary Color",
    description=("True for objects that have at least one remappable color."),
    default=False)

hasSecondaryColour = bpy.props.BoolProperty(
    name="Secondary Color",
    description=("True for objects that have at least two remappable colors."),
    update=update_colors,
    default=False)

hasTernaryColour = bpy.props.BoolProperty(
    name="Tertiary Color",
    description=("True for objects that have three remappable colors."),
    update=update_colors,
    default=False)

price = bpy.props.IntProperty(
    name="Price",
    description=("The in-game cost of building this object."),
    default=15,
    soft_min=0)

removalPrice = bpy.props.IntProperty(
    name="Removal Price",
    description="The cost of removing this object. This value is negative if the object gives a refund.",
    default=-10,
    soft_max=0)

cursor = bpy.props.EnumProperty(
    name="Cursor",
    default="CURSOR_ARROW",
    description="Cursor icon to use when placing this object",
    items=[
        ("CURSOR_BLANK", "BLANK", ""),
        ("CURSOR_UP_ARROW", "UP ARROW", ""),
        ("CURSOR_UP_DOWN_ARROW", "UP DOWN ARROW", ""),
        ("CURSOR_HAND_POINT", "HAND POINT", ""),
        ("CURSOR_ZZZ", "ZZZ", ""),
        ("CURSOR_DIAGONAL_ARROWS", "DIAGONAL ARROWS", ""),
        ("CURSOR_PICKER", "PICKER", ""),
        ("CURSOR_TREE_DOWN", "TREE DOWN", ""),
        ("CURSOR_FOUNTAIN_DOWN", "FOUNTAIN DOWN", ""),
        ("CURSOR_STATUE_DOWN", "STATUE DOWN", ""),
        ("CURSOR_BENCH_DOWN", "BENCH DOWN", ""),
        ("CURSOR_CROSS_HAIR", "CROSS HAIR", ""),
        ("CURSOR_BIN_DOWN", "BIN DOWN", ""),
        ("CURSOR_LAMPPOST_DOWN", "LAMPPOST DOWN", ""),
        ("CURSOR_FENCE_DOWN", "FENCE DOWN", ""),
        ("CURSOR_FLOWER_DOWN", "FLOWER DOWN", ""),
        ("CURSOR_PATH_DOWN", "PATH DOWN", ""),
        ("CURSOR_DIG_DOWN", "DIG DOWN", ""),
        ("CURSOR_WATER_DOWN", "WATER DOWN", ""),
        ("CURSOR_HOUSE_DOWN", "HOUSE DOWN", ""),
        ("CURSOR_VOLCANO_DOWN", "VOLCANO DOWN", ""),
        ("CURSOR_WALK_DOWN", "WALK DOWN", ""),
        ("CURSOR_PAINT_DOWN", "PAINT DOWN", ""),
        ("CURSOR_ENTRANCE_DOWN", "ENTRANCE DOWN", ""),
        ("CURSOR_HAND_OPEN", "HAND OPEN", ""),
        ("CURSOR_HAND_CLOSED", "HAND CLOSED", ""),
        ("CURSOR_ARROW", "ARROW", ""),
    ])

colour_list = [
    ("black", "Black", ""),
    ("grey", "Grey", ""),
    ("white", "White", ""),
    ("dark_purple", "Dark Purple", ""),
    ("light_purple", "Light Purple", ""),
    ("bright_purple", "Bright Purple", ""),
    ("dark_blue", "Dark Blue", ""),
    ("light_blue", "Light Blue", ""),
    ("icy_blue", "Icy Blue", ""),
    ("teal", "Teal", ""),
    ("aquamarine", "Aquamarine", ""),
    ("saturated_green", "Saturated Green", ""),
    ("dark_green", "Dark Green", ""),
    ("moss_green", "Moss Green", ""),
    ("bright_green", "Bright Green", ""),
    ("olive_green", "Olive Green", ""),
    ("dark_olive_green", "Dark Olive Green", ""),
    ("bright_yellow", "Bright Yellow", ""),
    ("yellow", "Yellow", ""),
    ("dark_yellow", "Dark Yellow", ""),
    ("light_orange", "Light Orange", ""),
    ("dark_orange", "Dark Orange", ""),
    ("light_brown", "Light Brown", ""),
    ("saturated_brown", "Saturated Brown", ""),
    ("dark_brown", "Dark Brown", ""),
    ("salmon_pink", "Salmon Pink", ""),
    ("bordeaux_red", "Bordeaux Red", ""),
    ("saturated_red", "Saturated Red", ""),
    ("bright_red", "Bright Red", ""),
    ("dark_pink", "Dark Pink", ""),
    ("bright_pink", "Bright Pink", ""),
    ("light_pink", "Light Pink", "")
]

colour = bpy.props.EnumProperty(
    colour_list,
    name="Color",
    description="Color",
    default="black"
)


# Car Colours
##############

def set_car_colours(context, carColours):
    scene = context.scene  # bpy.types.Scene
    if carColours is not None:
        scene.carColours.clear()
        if len(carColours) == 1:
            for entry in carColours[0]:
                item = scene.carColours.add()  # type: CarColourItem
                item.colour1 = entry[0]
                item.colour2 = entry[1]
                item.colour3 = entry[2]
        elif len(carColours) > 1:
            for entry in carColours:
                item = scene.carColours.add()  # type: CarColourItem
                item.colour1 = entry[0][0]
                item.colour2 = entry[0][1]
                item.colour3 = entry[0][2]


class CarColours_OT_actions(bpy.types.Operator):
    """Buttons to add/remove/move a car colour item."""
    bl_idname = "carcolours.actions"
    bl_label = "List Actions"
    bl_description = "Add/Remove\n\nMove Up/Down"
    bl_options = {'REGISTER'}

    action = bpy.props.StringProperty(name="Action", description="")

    def invoke(self, context: bpy.types.Context, event):
        scene = context.scene
        index = getattr(scene, "car_colours_index")
        carColours = getattr(scene, "carColours")

        try:
            item = carColours[index]
        except IndexError:
            pass
        else:
            if self.action == 'DOWN' and index < len(carColours) - 1:
                carColours.move(index, index+1)
                setattr(scene, "car_colours_index", index + 1)

            elif self.action == 'UP' and index >= 1:
                carColours.move(index, index-1)
                setattr(scene, "car_colours_index", index + 1)

            elif self.action == 'REMOVE':
                if index != 0:
                    setattr(scene, "car_colours_index", index + 1)
                carColours.remove(index)

        if self.action == 'ADD':
            item = carColours.add()
            setattr(scene, "car_colours_index", len(carColours)-1)

        return {"FINISHED"}


class CarColours_UL_List(bpy.types.UIList):
    """Defines the drawing function for each car colour item"""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            row.prop(item, "colour1", text="")
            row.prop(item, "colour2", text="")
            row.prop(item, "colour3", text="")
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="colourEntry")


class CarColourItem(bpy.types.PropertyGroup):
    """Defines one entry in carColours"""
    colour1 = bpy.props.EnumProperty(
        items=colour_list,
        name="Primary Color",
        description="Primary Color",
        default="black"
    )
    colour2 = bpy.props.EnumProperty(
        items=colour_list,
        name="Secondary Color",
        description="Secondary Color",
        default="black"
    )
    colour3 = bpy.props.EnumProperty(
        items=colour_list,
        name="Tertiary Color",
        description="Tertiary Color",
        default="black"
    )


def process_car_colours(context):
    car_colours = []
    raw_car_colours = [group_as_dict(i) for i in context.scene.carColours]  # type: list[CarColourItem]
    if not raw_car_colours:
        return [[["black", "black", "black"]]]
    for entry in raw_car_colours:
        if context.scene.car_colours_single_preset:
            car_colours.append([[entry['colour1'], entry['colour2'], entry['colour3']]])
        else:
            car_colours.append([entry['colour1'], entry['colour2'], entry['colour3']])
    return car_colours


carColours = bpy.props.CollectionProperty(
    type=CarColourItem, name="Preset Colors",
    description="A list of color schemes to use as preset(s) for this object when building a new ride.")
car_colours_index = bpy.props.IntProperty(default=0)
car_colours_single_preset = bpy.props.BoolProperty(
    name="Single Preset",
    description="If true, this list of color schemes is always used for new rides, and each entry is for the next "
    "car/vehicle on the ride. If false, OpenRCT2 will randomly choose *one* of these color schemes when building a "
    "new ride, and apply it to all vehicles.\n\nIn other words, a ride can either have multiple presets with a "
    "single color scheme each (which are randomly chosen from when a ride is built), or it can have a single preset "
    "that has different color schemes for each car/train",
    default=False
)
