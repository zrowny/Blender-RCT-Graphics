'''
Copyright (c) 2021 RCT Graphics Helper developers

For a complete list of all authors, please refer to the addon's meta info.
Interested in contributing? Visit https://github.com/oli414/Blender-RCT-Graphics

RCT Graphics Helper is licensed under the GNU General Public License version 3.
'''

import math
import bpy
from bpy.types import Action, EnumProperty, Property, bpy_struct
from . json_functions import group_as_dict


# Processing Ride type
#######################

ride_types = [
    ("spiral_rc", "Spiral Roller Coaster", "spiral_rc"),
    ("stand_up_rc", "Stand-up Roller Coaster", "stand_up_rc"),
    ("suspended_swinging_rc", "Suspended Swinging Coaster", "suspended_swinging_rc"),
    ("inverted_rc", "Inverted Roller Coaster", "inverted_rc"),
    ("junior_rc", "Junior Roller Coaster", "junior_rc"),
    ("miniature_railway", "Miniature Railway", "miniature_railway"),
    ("monorail", "Monorail", "monorail"),
    ("mini_suspended_rc", "Mini Suspended Coaster", "mini_suspended_rc"),
    ("boat_hire", "Boat Hire", "boat_hire"),
    ("wooden_wild_mouse", "Wooden Wild Mouse", "wooden_wild_mouse"),
    ("steeplechase", "Steeplechase", "steeplechase"),
    ("car_ride", "Car Ride", "car_ride"),
    ("launched_freefall", "Launched Freefall", "launched_freefall"),
    ("bobsleigh_rc", "Bobsleigh Coaster", "bobsleigh_rc"),
    ("observation_tower", "Observation Tower", "observation_tower"),
    ("looping_rc", "Looping Roller Coaster", "looping_rc"),
    ("dinghy_slide", "Dinghy Slide", "dinghy_slide"),
    ("mine_train_rc", "Mine Train Coaster", "mine_train_rc"),
    ("chairlift", "Chairlift", "chairlift"),
    ("corkscrew_rc", "Corkscrew Roller Coaster", "corkscrew_rc"),
    ("maze", "Maze", "maze"),
    ("spiral_slide", "Spiral Slide", "spiral_slide"),
    ("go_karts", "Go-Karts", "go_karts"),
    ("log_flume", "Log Flume", "log_flume"),
    ("river_rapids", "River Rapids", "river_rapids"),
    ("dodgems", "Dodgems", "dodgems"),
    ("swinging_ship", "Swinging Ship", "swinging_ship"),
    ("swinging_inverter_ship", "Swinging Inverter Ship", "swinging_inverter_ship"),
    ("merry_go_round", "Merry-Go-Round", "merry_go_round"),
    ("ferris_wheel", "Ferris Wheel", "ferris_wheel"),
    ("motion_simulator", "Motion Simulator", "motion_simulator"),
    ("3d_cinema", "3D Cinema", "3d_cinema"),
    ("top_spin", "Top Spin", "top_spin"),
    ("space_rings", "Space Rings", "space_rings"),
    ("reverse_freefall_rc", "Reverse Freefall Coaster", "reverse_freefall_rc"),
    ("lift", "Lift", "lift"),
    ("vertical_drop_rc", "Vertical Drop Roller Coaster", "vertical_drop_rc"),
    ("cash_machine", "Cash Machine", "cash_machine"),
    ("twist", "Twist", "twist"),
    ("haunted_house", "Haunted House", "haunted_house"),
    ("circus", "Circus", "circus"),
    ("ghost_train", "Ghost Train", "ghost_train"),
    ("twister_rc", "Twister Roller Coaster", "twister_rc"),
    ("wooden_rc", "Wooden Roller Coaster", "wooden_rc"),
    ("side_friction_rc", "Side-Friction Roller Coaster", "side_friction_rc"),
    ("steel_wild_mouse", "Steel Wild Mouse", "steel_wild_mouse"),
    ("multi_dimension_rc", "Multi-Dimension Roller Coaster", "multi_dimension_rc"),
    ("flying_rc", "Flying Roller Coaster", "flying_rc"),
    ("virginia_reel", "Virginia Reel", "virginia_reel"),
    ("splash_boats", "Splash Boats", "splash_boats"),
    ("mini_helicopters", "Mini Helicopters", "mini_helicopters"),
    ("lay_down_rc", "Lay-down Roller Coaster", "lay_down_rc"),
    ("suspended_monorail", "Suspended Monorail", "suspended_monorail"),
    ("reverser_rc", "Reverser Roller Coaster", "reverser_rc"),
    ("heartline_twister_rc", "Heartline Twister Coaster", "heartline_twister_rc"),
    ("mini_golf", "Mini Golf", "mini_golf"),
    ("giga_rc", "Giga Coaster", "giga_rc"),
    ("roto_drop", "Roto-Drop", "roto_drop"),
    ("flying_saucers", "Flying Saucers", "flying_saucers"),
    ("crooked_house", "Crooked House", "crooked_house"),
    ("monorail_cycles", "Monorail Cycles", "monorail_cycles"),
    ("compact_inverted_rc", "Compact Inverted Coaster", "compact_inverted_rc"),
    ("water_coaster", "Water Coaster", "water_coaster"),
    ("air_powered_vertical_rc", "Air Powered Vertical Coaster", "air_powered_vertical_rc"),
    ("inverted_hairpin_rc", "Inverted Hairpin Coaster", "inverted_hairpin_rc"),
    ("magic_carpet", "Magic Carpet", "magic_carpet"),
    ("submarine_ride", "Submarine Ride", "submarine_ride"),
    ("river_rafts", "River Rafts", "river_rafts"),
    ("enterprise", "Enterprise", "enterprise"),
    ("inverted_impulse_rc", "Inverted Impulse Coaster", "inverted_impulse_rc"),
    ("mini_rc", "Mini Roller Coaster", "mini_rc"),
    ("mine_ride", "Mine Ride", "mine_ride"),
    ("lim_launched_rc", "LIM Launched Roller Coaster", "lim_launched_rc"),
    ("hypercoaster", "Hypercoaster", "hypercoaster"),
    ("hyper_twister", "Hyper-Twister", "hyper_twister"),
    ("monster_trucks", "Monster Trucks", "monster_trucks"),
    ("spinning_wild_mouse", "Spinning Wild Mouse", "spinning_wild_mouse"),
    ("classic_mini_rc", "Classic Mini Roller Coaster", "classic_mini_rc"),
    ("hybrid_rc", "Hybrid Coaster", "hybrid_rc"),
    ("single_rail_rc", "Single Rail Roller Coaster", "single_rail_rc")]
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
    "circus", "crooked_house", "ferris_wheel", "haunted_house", "merry_go_round",
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

    rct_empty = objects.get("RCT_Vehicle_Arrow")
    if rct_empty is None:
        rct_empty = objects.new("RCT_Vehicle_Arrow", None)
        scene.objects.link(rct_empty)
    rct_empty.hide = True
    rct_empty.hide_select = True
    rct_empty.empty_draw_type = 'SINGLE_ARROW'
    rct_empty.scale = (0.0, 1.0, 1.0)
    rct_empty.rotation_euler = [0, -math.pi/2, 0]
    rct_empty.location = (0.5, 0, 0)
    # rct_empty.parent = rct_size_preview
    rct_empty.layers = [i == 10 for i in range(20)]

    rct_box = objects.get("RCT_Plaform")
    if rct_box is None:
        vertices = [(-0.5, 0.25, 0.0), (-0.5, 0.25, 0.025516), (-0.5, 0.5, 0.0), (-0.5, 0.5, 0.025516),
                    (0.5, 0.25, 0.0), (0.5, 0.25, 0.025516), (0.5, 0.5, 0.0), (0.5, 0.5, 0.025516), (-0.5, -0.5, 0.0),
                    (-0.5, -0.5, 0.025516), (-0.5, -0.25, 0.0), (-0.5, -0.25, 0.025516), (0.5, -0.5, 0.0),
                    (0.5, -0.5, 0.025516), (0.5, -0.25, 0.0), (0.5, -0.25, 0.025516)]
        edges = [(2, 0), (0, 1), (1, 3), (3, 2), (6, 2), (3, 7), (7, 6), (4, 6), (7, 5), (5, 4), (0, 4), (5, 1),
                 (10, 8), (8, 9), (9, 11), (11, 10), (14, 10), (11, 15), (15, 14), (12, 14), (15, 13), (13, 12),
                 (8, 12), (13, 9)]
        rct_box_mesh = bpy.data.meshes.new("RCT_platform_mesh")
        rct_box_mesh.from_pydata(vertices, edges, [])
        rct_box_mesh.update()
        rct_box = objects.new("RCT_Plaform", rct_box_mesh)
        scene.objects.link(rct_box)
    rct_box.hide = True
    rct_box.hide_select = True
    rct_box.scale = (1.0, 1.0, 1.0)
    rct_box.location = (0, 0, 0)
    rct_box.parent = rct_size_preview
    rct_box.layers = [i == 10 for i in range(20)]

    rct_box = objects.get("RCT_Plaform_Narrow")
    if rct_box is None:
        vertices = [(-0.5, 0.375, 0.0), (-0.5, 0.375, 0.025516), (-0.5, 0.5, 0.0), (-0.5, 0.5, 0.025516),
                    (0.5, 0.375, 0.0), (0.5, 0.375, 0.025516), (0.5, 0.5, 0.0), (0.5, 0.5, 0.025516),
                    (-0.5, -0.5, 0.0), (-0.5, -0.5, 0.025516), (-0.5, -0.375, 0.0), (-0.5, -0.375, 0.025516),
                    (0.5, -0.5, 0.0), (0.5, -0.5, 0.025516), (0.5, -0.375, 0.0), (0.5, -0.375, 0.025516)]
        edges = [(2, 0), (0, 1), (1, 3), (3, 2), (6, 2), (3, 7), (7, 6), (4, 6), (7, 5), (5, 4), (0, 4), (5, 1),
                 (10, 8), (8, 9), (9, 11), (11, 10), (14, 10), (11, 15), (15, 14), (12, 14), (15, 13), (13, 12),
                 (8, 12), (13, 9)]
        rct_box_mesh = bpy.data.meshes.new("RCT_platform_narrow_mesh")
        rct_box_mesh.from_pydata(vertices, edges, [])
        rct_box_mesh.update()
        rct_box = objects.new("RCT_Plaform_Narrow", rct_box_mesh)
        scene.objects.link(rct_box)
    rct_box.hide = True
    rct_box.hide_select = True
    rct_box.scale = (1.0, 1.0, 1.0)
    rct_box.location = (0, 0, 0)
    rct_box.parent = rct_size_preview
    rct_box.layers = [i == 10 for i in range(20)]

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
buildMenuPriority = bpy.props.IntProperty(
    name="Menu Priority",
    description="Except for rides that list their subtypes/vehicles separately in the build menu, this number "
    "describes the priority order for which subtype should show for the generic ride type in the build menu. Of all "
    "the subtypes that are available and researched, whichever has the highest buildMenuPriority will show as "
    "representative of the generic ride type.",
    default=0, soft_min=0
)
maxHeight = bpy.props.IntProperty(
    name="Max Height",
    description="Maximum height of the ride (if set to 0, uses the hardcoded value for the ridetype)",
    default=0, soft_min=0
)


class RatingMultiplier(bpy.types.PropertyGroup):
    excitement = bpy.props.IntProperty(
        name="Excitement Factor",
        description="Additional excitement percentage for this specific ride subtype.\n\nWhile these values are "
        "displayed in-game as if they were a percentage, they're really divided by 128, not 100. I.e., a value of "
        "`10` here would display as `\"10%\"` when selecting a vehicle, but internally it only gives a boost of "
        "10/128 or about 7.8%.",
        default=0, soft_min=0, soft_max=100, subtype='PERCENTAGE'
    )
    intensity = bpy.props.IntProperty(
        name="Intensity Factor",
        description="Additional intensity percentage for this specific ride subtype.\n\nWhile these values are "
        "displayed in-game as if they were a percentage, they're really divided by 128, not 100. I.e., a value of "
        "`10` here would display as `\"10%\"` when selecting a vehicle, but internally it only gives a boost of "
        "10/128 or about 7.8%.",
        default=0, soft_min=0, soft_max=100, subtype='PERCENTAGE'
    )
    nausea = bpy.props.IntProperty(
        name="Nausea Factor",
        description="Additional nausea percentage for this specific ride subtype.\n\nWhile these values are "
        "displayed in-game as if they were a percentage, they're really divided by 128, not 100. I.e., a value of "
        "`10` here would display as `\"10%\"` when selecting a vehicle, but internally it only gives a boost of "
        "10/128 or about 7.8%.",
        default=0, soft_min=0, soft_max=100, subtype='PERCENTAGE'
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


# (track_clearance, vehicle_z_offset, platform_height,
#  is_suspended, list_separately, flat_platform, narrow_platform, unused)
ride_data = {
    "air_powered_vertical_rc": (24, 5, 7, False, False, False, True, False),
    "boat_hire": (16, 0, 3, False, False, False, False, False),
    "bobsleigh_rc": (24, 5, 7, False, False, False, False, False),
    "car_ride": (24, 4, 7, False, False, False, False, False),
    "chairlift": (32, 28, 2, True, False, False, False, False),
    "classic_mini_rc": (24, 5, 7, False, False, False, False, False),
    "compact_inverted_rc": (40, 29, 8, True, False, False, False, False),
    "corkscrew_rc": (24, 8, 11, False, False, False, False, False),
    "dinghy_slide": (24, 5, 7, False, False, False, False, False),
    "dodgems": (48, 2, 2, False, False, True, False, False),
    "flying_rc": (24, 8, 11, False, False, False, False, False),
    "flying_saucers": (48, 2, 2, False, False, True, False, False),
    "ghost_train": (24, 6, 7, False, False, False, False, False),
    "giga_rc": (24, 9, 11, False, False, False, False, False),
    "go_karts": (24, 2, 1, False, False, False, False, False),
    "heartline_twister_rc": (24, 15, 9, False, False, False, False, False),
    "hybrid_rc": (24, 13, 13, False, False, False, True, False),
    "hyper_twister": (24, 8, 9, False, False, False, True, False),
    "hypercoaster": (24, 8, 11, False, False, False, False, False),
    "inverted_hairpin_rc": (24, 24, 7, True, False, False, False, False),
    "inverted_impulse_rc": (40, 29, 8, True, False, False, False, False),
    "inverted_rc": (40, 29, 8, True, False, False, False, False),
    "junior_rc": (24, 4, 7, False, False, False, False, False),
    "launched_freefall": (32, 3, 2, False, False, True, False, False),
    "lay_down_rc": (24, 8, 11, False, False, False, False, False),
    "lift": (32, 3, 2, False, False, True, False, False),
    "lim_launched_rc": (24, 5, 7, False, False, False, False, False),
    "log_flume": (24, 7, 9, False, False, False, False, False),
    "looping_rc": (24, 5, 7, False, False, False, False, False),
    "maze": (24, 0, 1, False, False, False, False, False),
    "mine_ride": (24, 9, 11, False, False, False, False, False),
    "mine_train_rc": (24, 4, 7, False, False, False, False, False),
    "mini_golf": (32, 2, 2, False, False, False, False, False),
    "mini_helicopters": (24, 4, 7, False, False, False, False, False),
    "mini_rc": (24, 9, 11, False, False, False, False, False),
    "mini_suspended_rc": (24, 24, 8, True, False, False, False, False),
    "miniature_railway": (32, 5, 9, False, False, False, False, False),
    "monorail": (32, 8, 9, False, False, False, False, False),
    "monorail_cycles": (24, 8, 7, False, False, False, False, False),
    "monster_trucks": (24, 4, 7, False, False, False, False, False),
    "multi_dimension_rc": (24, 8, 11, False, False, False, False, False),
    "observation_tower": (32, 3, 2, False, False, True, False, False),
    "reverse_freefall_rc": (32, 4, 7, False, False, False, True, False),
    "reverser_rc": (24, 8, 11, False, False, False, False, False),
    "river_rafts": (24, 7, 11, False, False, False, False, False),
    "river_rapids": (32, 14, 15, False, False, False, True, False),
    "roto_drop": (32, 3, 2, False, False, True, False, False),
    "side_friction_rc": (24, 4, 11, False, False, False, False, False),
    "single_rail_rc": (24, 5, 7, False, False, False, False, False),
    "spinning_wild_mouse": (24, 4, 7, False, False, False, False, False),
    "spiral_rc": (24, 9, 11, False, False, False, False, False),
    "splash_boats": (24, 7, 11, False, False, False, True, False),
    "stand_up_rc": (24, 9, 11, False, False, False, False, False),
    "steel_wild_mouse": (24, 4, 7, False, False, False, False, False),
    "steeplechase": (24, 7, 7, False, False, False, False, False),
    "submarine_ride": (32, 16, 19, False, False, False, False, False),  # Added 16 to account for underwater
    "suspended_monorail": (40, 32, 8, True, False, False, False, False),
    "suspended_swinging_rc": (40, 29, 8, True, False, False, False, False),
    "twister_rc": (24, 8, 9, False, False, False, True, False),
    "vertical_drop_rc": (24, 8, 11, False, False, False, True, False),
    "virginia_reel": (24, 6, 7, False, False, False, False, False),
    "water_coaster": (24, 4, 7, False, False, False, False, False),
    "wooden_rc": (24, 8, 11, False, False, False, False, False),
    "wooden_wild_mouse": (24, 4, 7, False, False, False, False, False)}


def update_load_preview(dummyself, context):
    scene = context.scene
    properties = scene.rct_graphics_helper_vehicles_properties
    objects = bpy.data.objects
    objects.get("RCT_One_Quarter").hide = True
    objects.get("RCT_Diagonal_1").hide = True
    objects.get("RCT_Diagonal_2").hide = True
    objects.get("RCT_Three_Quarter").hide = True
    objects.get("RCT_Half_Tile").hide = True
    size_preview = objects.get("RCT_Size_Preview")
    size_preview.hide = True
    if len(properties.cars) == 0:
        objects.get("RCT_Full_Tile").hide = True
        objects.get("RCT_Vehicle_Arrow").hide = True
        objects.get("RCT_Vehicle_Arrow").hide = True
        objects.get("RCT_Plaform").hide = True
    else:
        car = properties.cars[properties.cars_index]
        objects.get("RCT_Full_Tile").hide = False
        clearance = ride_data[properties.type][0]
        z_offset = -ride_data[properties.type][1] * 0.025516
        platform_height = ride_data[properties.type][2]
        objects.get("RCT_Plaform").scale = (1, 1, platform_height / clearance)
        objects.get("RCT_Plaform_Narrow").scale = (1, 1, platform_height / clearance)
        is_narrow = ride_data[properties.type][6]
        if ride_data[properties.type][5]:  # Flat platform
            objects.get("RCT_Vehicle_Arrow").hide = True
            objects.get("RCT_Plaform").hide = True
            objects.get("RCT_Plaform_Narrow").hide = True
        else:
            objects.get("RCT_Vehicle_Arrow").hide = False
            if is_narrow:
                objects.get("RCT_Plaform").hide = True
                objects.get("RCT_Plaform_Narrow").hide = False
            else:
                objects.get("RCT_Plaform").hide = False
                objects.get("RCT_Plaform_Narrow").hide = True
            length = car.spacing / 262144
            size_preview.scale = (length, 1, clearance)
        size_preview.location = (0, 0, z_offset)
        rct_load_preview = objects.get("RCT_Load_Preview", None)
        if rct_load_preview is None:
            rct_load_preview = objects.new("RCT_Load_Preview", None)
            scene.objects.link(rct_load_preview)
        else:
            for o in rct_load_preview.children:
                objects.remove(o)
        rct_load_preview.hide_select = True
        rct_load_preview.hide = True
        rct_load_preview.location = (0, 0, 0)
        if car.use_waypoints:
            pass
        else:
            for i in range(len(car.loadingPositions)):
                x = -car.loadingPositions[i].position / 32
                rct_empty = objects.new("Position %s" % i, None)
                scene.objects.link(rct_empty)
                rct_empty.hide_select = True
                rct_empty.show_name = True
                rct_empty.empty_draw_type = 'SINGLE_ARROW'
                rct_empty.scale = (0.5, 0.5, 0.2)
                rct_empty.rotation_euler = [-math.pi/2, 0, 0]
                rct_empty.location = (x, -0.6, 0)
                rct_empty.parent = rct_load_preview


# Loading Waypoints
###################

class LoadingPositions_OT_actions(bpy.types.Operator):
    """Buttons to add/remove/move a car position item."""
    bl_idname = "loadingpositions.actions"
    bl_label = "List Actions"
    bl_description = "Add/Remove\n\nMove Up/Down"
    bl_options = {'REGISTER'}

    action = bpy.props.StringProperty()
    car_index = bpy.props.IntProperty()
    is_flat = bpy.props.BoolProperty(default=False)

    def invoke(self, context: bpy.types.Context, event):
        if self.is_flat:
            car = context.scene.rct_graphics_helper_flatride_properties.car
        else:
            car = context.scene.rct_graphics_helper_vehicles_properties.cars[self.car_index]
        index = getattr(car, "loading_positions_index")
        loadingPositions = getattr(car, "loadingPositions")

        try:
            item = loadingPositions[index]
        except IndexError:
            pass
        else:
            if self.action == 'DOWN' and index < len(loadingPositions) - 1:
                loadingPositions.move(index, index+1)
                setattr(car, "loading_positions_index", index + 1)

            elif self.action == 'UP' and index >= 1:
                loadingPositions.move(index, index-1)
                setattr(car, "loading_positions_index", index - 1)

            elif self.action == 'REMOVE':
                if index == len(loadingPositions) - 1:
                    setattr(car, "loading_positions_index", index - 1)
                loadingPositions.remove(index)

        if self.action == 'ADD':
            item = loadingPositions.add()
            setattr(car, "loading_positions_index", len(loadingPositions)-1)

        update_load_preview(None, context)
        return {"FINISHED"}


class LoadingPositions_UL_List(bpy.types.UIList):
    """Defines the drawing function for each car position item"""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row().split(0.3)
            row.label("Position %s:" % index)
            row.prop(item, "position", text="")
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="positionEntry")


class LoadingPositionItem(bpy.types.PropertyGroup):
    """Defines one entry (a route) in loadingPositions"""
    position = bpy.props.IntProperty(
        name="Position",
        description="Position",
        default=0,
        update=update_load_preview
    )


loadingPositions = bpy.props.CollectionProperty(
    type=LoadingPositionItem, name="Loading Positions",
    description="A list of loading positions to use for this car.")
loading_positions_index = bpy.props.IntProperty(default=0, update=update_load_preview)


# Loading Waypoints
###################

def set_loading_waypoints(context, loadingWaypoints):
    scene = context.scene  # bpy.types.Scene


class LoadingWaypoints_OT_actions(bpy.types.Operator):
    """Buttons to add/remove/move a car position item."""
    bl_idname = "loadingwaypoints.actions"
    bl_label = "List Actions"
    bl_description = "Add/Remove\n\nMove Up/Down"
    bl_options = {'REGISTER'}

    action = bpy.props.StringProperty()
    car_index = bpy.props.IntProperty()
    is_flat = bpy.props.BoolProperty(default=False)

    def invoke(self, context: bpy.types.Context, event):
        if self.is_flat:
            car = context.scene.rct_graphics_helper_flatride_properties.car
        else:
            car = context.scene.rct_graphics_helper_vehicles_properties.cars[self.car_index]
        index = getattr(car, "loading_waypoints_index")
        loadingWaypoints = getattr(car, "loadingWaypoints")

        try:
            item = loadingWaypoints[index]
        except IndexError:
            pass
        else:
            if self.action == 'DOWN' and index < len(loadingWaypoints) - 1:
                loadingWaypoints.move(index, index+1)
                setattr(car, "loading_waypoints_index", index + 1)

            elif self.action == 'UP' and index >= 1:
                loadingWaypoints.move(index, index-1)
                setattr(car, "loading_waypoints_index", index - 1)

            elif self.action == 'REMOVE':
                if index == len(loadingWaypoints) - 1:
                    setattr(car, "loading_waypoints_index", index - 1)
                loadingWaypoints.remove(index)

        if self.action == 'ADD':
            item = loadingWaypoints.add()
            setattr(car, "loading_waypoints_index", len(loadingWaypoints)-1)

        update_load_preview(None, context)
        return {"FINISHED"}


class LoadingWaypoints_UL_List(bpy.types.UIList):
    """Defines the drawing function for each car position item"""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            maincol = layout.column()  # type: bpy.types.UILayout
            row = maincol.row().split(0.07)
            row.label("[%s]" % index)
            row.label("SW")
            row.label("NW")
            row.label("NE")
            row.label("SE")
            row = maincol.row().split(0.07)
            col = row.column()
            col.label("  0:")
            col.label("  1:")
            col.label("  2:")

            col = row.column(align=True)
            route = item.SW
            subrow = col.row(align=True)
            subrow.prop(route, "position1", text="")
            subrow = col.row(align=True)
            subrow.prop(route, "position2", text="")
            subrow = col.row(align=True)
            subrow.prop(route, "position3", text="")

            col = row.column(align=True)
            route = item.NW
            subrow = col.row(align=True)
            subrow.prop(route, "position1", text="")
            subrow = col.row(align=True)
            subrow.prop(route, "position2", text="")
            subrow = col.row(align=True)
            subrow.prop(route, "position3", text="")

            col = row.column(align=True)
            route = item.NE
            subrow = col.row(align=True)
            subrow.prop(route, "position1", text="")
            subrow = col.row(align=True)
            subrow.prop(route, "position2", text="")
            subrow = col.row(align=True)
            subrow.prop(route, "position3", text="")

            col = row.column(align=True)
            route = item.SE
            subrow = col.row(align=True)
            subrow.prop(route, "position1", text="")
            subrow = col.row(align=True)
            subrow.prop(route, "position2", text="")
            subrow = col.row(align=True)
            subrow.prop(route, "position3", text="")
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="positionEntry")


class LoadingWaypointItem(bpy.types.PropertyGroup):
    """Defines one entry (a route) in loadingWaypoints"""
    position1 = bpy.props.IntVectorProperty(
        name="First Position",
        description="First Position",
        size=2,
        default=(0, 0),
        subtype='XYZ',
        update=update_load_preview
    )
    position2 = bpy.props.IntVectorProperty(
        name="Second Position",
        description="Second Position",
        size=2,
        default=(0, 0),
        subtype='XYZ',
        update=update_load_preview
    )
    position3 = bpy.props.IntVectorProperty(
        name="Third Position",
        description="Third Position",
        size=2,
        default=(0, 0),
        subtype='XYZ',
        update=update_load_preview
    )


class LoadingWaypointSet(bpy.types.PropertyGroup):
    
    SW = bpy.props.PointerProperty(type=LoadingWaypointItem, name="SW",
                                   description="Route when building is on south-west side")
    NW = bpy.props.PointerProperty(type=LoadingWaypointItem, name="NW",
                                   description="Route when building is on north-west side")
    NE = bpy.props.PointerProperty(type=LoadingWaypointItem, name="NE",
                                   description="Route when building is on north-east side")
    SE = bpy.props.PointerProperty(type=LoadingWaypointItem, name="SE",
                                   description="Route when building is on south-east side")


def process_loading_waypoints(context):
    loading_waypoints = []
    raw_waypoints = [group_as_dict(i) for i in context.scene.loadingWaypoints]  # type: list[LoadingWaypointItem]
    if not raw_waypoints:
        return None
    for entry in raw_waypoints:
        loading_waypoints.append([entry['position1'], entry['position2'], entry['position3']])
    return loading_waypoints


loadingWaypoints = bpy.props.CollectionProperty(
    type=LoadingWaypointSet, name="Loading Waypoints",
    description="A list of loading waypoints to use for this car.")
loading_waypoints_index = bpy.props.IntProperty(default=0, update=update_load_preview)
