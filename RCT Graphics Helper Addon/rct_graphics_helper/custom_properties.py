'''
Copyright (c) 2021 RCT Graphics Helper developers

For a complete list of all authors, please refer to the addon's meta info.
Interested in contributing? Visit https://github.com/oli414/Blender-RCT-Graphics

RCT Graphics Helper is licensed under the GNU General Public License version 3.
'''

import bpy
from bpy.types import EnumProperty, Property, bpy_struct


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

    rct_box_mesh = bpy.data.meshes.get("RCT_preview_cube")
    if rct_box_mesh is None:
        vertices = [(-0.5, -0.5, -0.5), (-0.5, -0.5, 0.5), (-0.5, 0.5, -0.5), (-0.5, 0.5, 0.5),
                    (0.5, -0.5, -0.5), (0.5, -0.5, 0.5), (0.5, 0.5, -0.5), (0.5, 0.5, 0.5)]
        edges = [(0, 1), (1, 3), (3, 2), (2, 0), (4, 5), (5, 7), (7, 6), (6, 4), (0, 4), (1, 5), (2, 6), (3, 7)]
        rct_box_mesh = bpy.data.meshes.new("RCT_preview_cube")
        rct_box_mesh.from_pydata(vertices, edges, [])
        rct_box_mesh.update()
    rct_box = objects.get("RCT_Full_Tile")
    if rct_box is None:
        rct_box = objects.new("RCT_Full_Tile", rct_box_mesh)
        scene.objects.link(rct_box)
    rct_box.hide_select = True
    rct_box.empty_draw_size = 0.50
    rct_box.empty_draw_type = 'CUBE'
    rct_box.scale = (1.0, 1.0, 0.025516)
    rct_box.location = (0, 0, 0.012758)
    rct_box.parent = rct_size_preview

    rct_box = objects.get("RCT_Half_Tile")
    if rct_box is None:
        rct_box = objects.new("RCT_Half_Tile", rct_box_mesh)
        scene.objects.link(rct_box)
    rct_box.hide_select = True
    rct_box.empty_draw_size = 0.50
    rct_box.empty_draw_type = 'CUBE'
    rct_box.scale = (0.5, 1, 0.025516)
    rct_box.location = (0.25, 0, 0.012758)
    rct_box.parent = rct_size_preview

    rct_box = objects.get("RCT_One_Quarter")
    if rct_box is None:
        rct_box = objects.new("RCT_One_Quarter", rct_box_mesh)
        scene.objects.link(rct_box)
    rct_box.hide_select = True
    rct_box.empty_draw_size = 0.50
    rct_box.empty_draw_type = 'CUBE'
    rct_box.scale = (0.5, 0.5, 0.025516)
    rct_box.location = (0, 0, 0.012758)
    rct_box.parent = rct_size_preview

    rct_box = objects.get("RCT_Diagonal_1")
    if rct_box is None:
        rct_box = objects.new("RCT_Diagonal_1", rct_box_mesh)
        scene.objects.link(rct_box)
    rct_box.hide_select = True
    rct_box.empty_draw_size = 0.50
    rct_box.empty_draw_type = 'CUBE'
    rct_box.scale = (0.5, 0.5, 0.025516)
    rct_box.location = (-0.25, 0.25, 0.012758)
    rct_box.parent = rct_size_preview

    rct_box = objects.get("RCT_Diagonal_2")
    if rct_box is None:
        rct_box = objects.new("RCT_Diagonal_2", rct_box_mesh)
        scene.objects.link(rct_box)
    rct_box.hide_select = True
    rct_box.empty_draw_size = 0.50
    rct_box.empty_draw_type = 'CUBE'
    rct_box.scale = (0.5, 0.5, 0.025516)
    rct_box.location = (0.25, -0.25, 0.012758)
    rct_box.parent = rct_size_preview

    rct_box = objects.get("RCT_Three_Quarter")
    if rct_box is None:
        vertices = [(0.0, 0.0, -0.5), (0.0, 0.0, 0.5), (0.5, 0.5, -0.5), (0.5, 0.5, 0.5),
                    (0.0, -0.5, -0.5), (0.0, -0.5, 0.5), (0.5, -0.5, -0.5), (0.5, -0.5, 0.5),
                    (-0.5, 0.0, -0.5), (-0.5, 0.0, 0.5), (-0.5, 0.5, -0.5), (-0.5, 0.5, 0.5)]
        edges = [(0, 1), (3, 2), (4, 5), (6, 7), (5, 7), (3, 7), (1, 5), (8, 9), (9, 11), (11, 10),
                 (3, 11), (1, 9), (2, 10), (8, 10), (0, 8), (2, 6), (0, 4), (4, 6)]
        rct_box_mesh = bpy.data.meshes.new("RCT_preview_three_quarters")
        rct_box_mesh.from_pydata(vertices, edges, [])
        rct_box_mesh.update()
        rct_box = objects.new("RCT_Three_Quarter", rct_box_mesh)
        scene.objects.link(rct_box)
    rct_box.hide_select = True
    rct_box.empty_draw_size = 0.50
    rct_box.empty_draw_type = 'CUBE'
    rct_box.scale = (1, 1, 0.025516)
    rct_box.location = (0, 0, 0.012758)
    rct_box.parent = rct_size_preview

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
