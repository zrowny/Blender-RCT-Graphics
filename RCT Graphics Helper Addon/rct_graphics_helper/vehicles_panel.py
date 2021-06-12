'''
Copyright (c) 2021 RCT Graphics Helper developers

For a complete list of all authors, please refer to the addon's meta info.
Interested in contributing? Visit https://github.com/oli414/Blender-RCT-Graphics

RCT Graphics Helper is licensed under the GNU General Public License version 3.
'''

import bpy
import math
import os

from . render_operator import RCTRender
from . track import track_angle_sections, track_angle_sections_names
from . render_task import *
from . import custom_properties as custom_properties


def set_vehicles_properties(context, properties):
    pass


def update_vehicles(dummyself, context):
    scene = context.scene
    properties = scene.rct_graphics_helper_vehicles_properties  # type: VehiclesProperties
    objects = bpy.data.objects
    data = ride_data[properties.type]
    if properties.from_json:
        return
    if len(properties.cars) == 0:
        properties.cars.add()
    if data.tiles is not None:
        if data.no_platform:
            properties.use_waypoints = True
        else:
            properties.use_waypoints = False
        if len(properties.cars) > 1:
            for i in range(1, len(properties.cars)):
                properties.cars.remove(i)
        if not data.flat_ride_has_track:
            properties.cars[0]['carVisual'] = 1
        elif properties.type == 'launched_freefall':
            properties.cars[0]['carVisual'] = 2
        elif properties.type == 'observation_tower':
            properties.cars[0]['carVisual'] = 3
        elif properties.type == 'roto_drop':
            properties.cars[0]['carVisual'] = 9
    else:
        if properties.type in ('maze', 'spiral_slide'):
            for i in range(0, len(properties.cars)):
                properties.cars.remove(i)
        elif properties.type == 'mini_golf':
            if len(properties.cars) != 2:
                if len(properties) == 1:
                    properties.cars.add()
                else:
                    for i in range(2, len(properties.cars)):
                        properties.cars.remove(i)
            properties.cars[0]['carVisual'] = 6
            properties.cars[0]['isMiniGolf'] = True
            properties.cars[0]['numSeats'] = 0
            properties.cars[1]['carVisual'] = 5
            properties.cars[1]['isMiniGolf'] = True
            properties.cars[0]['numSeats'] = 1
        properties.use_waypoints = False
    update_load_preview(None, context)


class CompileVehicle(RCTRender, bpy.types.Operator):
    """Operator to compile vehicle object. All cars must be rendered first."""
    bl_idname = "render.rct_vehicle"
    bl_label = "Compile RCT Vehicle"

    scene = None
    props = None

    # Rendering not yet supported
    @classmethod
    def poll(cls, context):
        all_rendered = True
        cars = context.scene.rct_graphics_helper_vehicles_properties.cars
        for car in cars:
            if not car.car_rendered:
                all_rendered = False
        return all_rendered


class RenderCar(RCTRender, bpy.types.Operator):
    """Operator to render vehicle car."""
    bl_idname = "render.rct_car"
    bl_label = "Render RCT Car"

    scene = None
    props = None

    # Rendering not yet supported
    @classmethod
    def poll(cls, context):
        return False

    def key_is_property(self, key):
        for sprite_track_flagset in self.props.sprite_track_flags_list:
            if sprite_track_flagset.section_id == key:
                return True

    def property_value(self, key):
        i = 0
        for sprite_track_flagset in self.props.sprite_track_flags_list:
            if sprite_track_flagset.section_id == key:
                return self.props.sprite_track_flags[i]
            i += 1

    def append_angles_to_rendertask(self, render_layer, inverted):
        start_anim = 0
        if self.scene.rct_graphics_helper_general_properties.number_of_animation_frames != 1:
            start_anim = 4
        anim_count = self.scene.rct_graphics_helper_general_properties.number_of_animation_frames
        for i in range(len(track_angle_sections_names)):
            key = track_angle_sections_names[i]
            track_section = track_angle_sections[key]
            if self.key_is_property(key):
                if self.property_value(key):
                    self.renderTask.add(
                        track_section, render_layer, inverted, start_anim, anim_count)
            elif (key == "VEHICLE_SPRITE_FLAG_GENTLE_SLOPE_BANKED_TURNS"
                    or key == "VEHICLE_SPRITE_FLAG_GENTLE_SLOPE_BANKED_TRANSITIONS"):
                if self.property_value("SLOPED_TURNS"):
                    self.renderTask.add(
                        track_section, render_layer, inverted, start_anim, anim_count)
            elif key == "VEHICLE_SPRITE_FLAG_FLAT_TO_GENTLE_SLOPE_WHILE_BANKED_TRANSITIONS":
                if self.property_value("SLOPED_TURNS") and self.property_value("VEHICLE_SPRITE_FLAG_FLAT_BANKED"):
                    self.renderTask.add(
                        track_section, render_layer, inverted, start_anim, anim_count)
            elif key == "VEHICLE_SPRITE_FLAG_DIAGONAL_GENTLE_SLOPE_BANKED_TRANSITIONS":
                if self.property_value("SLOPED_TURNS") and self.property_value("VEHICLE_SPRITE_FLAG_DIAGONAL_SLOPES"):
                    self.renderTask.add(
                        track_section, render_layer, inverted, start_anim, anim_count)
            elif key == "VEHICLE_SPRITE_FLAG_FLAT_TO_GENTLE_SLOPE_BANKED_TRANSITIONS":
                if (self.property_value("VEHICLE_SPRITE_FLAG_FLAT_BANKED")
                        and self.property_value("VEHICLE_SPRITE_FLAG_GENTLE_SLOPES")):
                    self.renderTask.add(
                        track_section, render_layer, inverted, start_anim, anim_count)
            elif key == "VEHICLE_SPRITE_FLAG_RESTRAINT_ANIMATION" and inverted is False:
                if self.props.restraint_animation:
                    self.renderTask.add(
                        track_section, render_layer, inverted, 1, 3)

    def execute(self, context):
        self.scene = context.scene
        self.props = self.scene.rct_graphics_helper_vehicles_properties

        self.renderTask = RenderTask(
            context.scene.rct_graphics_helper_general_properties.out_start_index, context)

        for i in range(context.scene.rct_graphics_helper_general_properties.number_of_rider_sets + 1):
            self.append_angles_to_rendertask(i, False)

            if self.props.inverted_set:
                self.append_angles_to_rendertask(i, True)

        return super(RenderCar, self).execute(context)

    def finished(self, context):
        super(RenderCar, self).finished(context)
        self.report({'INFO'}, 'RCT Car render finished.')


RideData = namedtuple(
    "RideData",
    "track_clearance vehicle_z_offset platform_height "
    "is_suspended list_separately no_platform narrow_platform "
    "tiles flat_ride_has_track")
RideData.__new__.__defaults__ = (24, 4, 7, False, False, False, False, None, False)

ride_data = {
    "air_powered_vertical_rc": RideData(24, 5, 7, narrow_platform=True),
    "boat_hire": RideData(16, 0, 3),
    "bobsleigh_rc": RideData(24, 5, 7),
    "car_ride": RideData(24, 4, 7),
    "chairlift": RideData(32, 28, 2, is_suspended=True),
    "circus": RideData(128, 3, 2, no_platform=True, tiles=(3, 3)),
    "crooked_house": RideData(96, 3, 2, no_platform=True, tiles=(3, 3)),
    "ferris_wheel": RideData(176, 3, 2, no_platform=True, tiles=(1, 4)),
    "haunted_house": RideData(160, 3, 2, no_platform=True, tiles=(3, 3)),
    "merry_go_round": RideData(128, 3, 2, no_platform=True, tiles=(3, 3)),
    "space_rings": RideData(48, 3, 2, no_platform=True),
    "spiral_slide": RideData(128, 0, 2, no_platform=True, tiles=(2, 2)),
    "3d_cinema": RideData(128, 3, 2, no_platform=True, tiles=(3, 3)),
    "enterprise": RideData(160, 3, 2, no_platform=True, tiles=(4, 4)),
    "magic_carpet": RideData(176, 7, 11, tiles=(1, 4)),
    "motion_simulator": RideData(64, 3, 2, no_platform=True, tiles=(2, 2)),
    "swinging_ship": RideData(112, 7, 11, tiles=(1, 5)),
    "swinging_inverter_ship": RideData(176, 7, 11, tiles=(1, 4)),
    "top_spin": RideData(112, 3, 2, no_platform=True, tiles=(3, 3)),
    "twist": RideData(64, 3, 2, no_platform=True, tiles=(3, 3)),
    "classic_mini_rc": RideData(24, 5, 7),
    "compact_inverted_rc": RideData(40, 29, 8, is_suspended=True),
    "corkscrew_rc": RideData(24, 8, 11),
    "dinghy_slide": RideData(24, 5, 7),
    "dodgems": RideData(48, 2, 2, no_platform=True),
    "flying_rc": RideData(24, 8, 11),
    "flying_saucers": RideData(48, 2, 2, no_platform=True),
    "ghost_train": RideData(24, 6, 7),
    "giga_rc": RideData(24, 9, 11),
    "go_karts": RideData(24, 2, 1, no_platform=True),
    "heartline_twister_rc": RideData(24, 15, 9),
    "hybrid_rc": RideData(24, 13, 13, narrow_platform=True),
    "hyper_twister": RideData(24, 8, 9, narrow_platform=True),
    "hypercoaster": RideData(24, 8, 11),
    "inverted_hairpin_rc": RideData(24, 24, 7, is_suspended=True),
    "inverted_impulse_rc": RideData(40, 29, 8, is_suspended=True),
    "inverted_rc": RideData(40, 29, 8, is_suspended=True),
    "junior_rc": RideData(24, 4, 7),
    "launched_freefall": RideData(32, 3, 2, no_platform=True, tiles=(3, 3), flat_ride_has_track=True),
    "lay_down_rc": RideData(24, 8, 11),
    "lift": RideData(32, 3, 2, no_platform=True, tiles=(3, 3), flat_ride_has_track=True),
    "lim_launched_rc": RideData(24, 5, 7),
    "log_flume": RideData(24, 7, 9),
    "looping_rc": RideData(24, 5, 7),
    "maze": RideData(24, 0, 1),
    "mine_ride": RideData(24, 9, 11),
    "mine_train_rc": RideData(24, 4, 7),
    "mini_golf": RideData(32, 2, 2),
    "mini_helicopters": RideData(24, 4, 7),
    "mini_rc": RideData(24, 9, 11),
    "mini_suspended_rc": RideData(24, 24, 8, is_suspended=True),
    "miniature_railway": RideData(32, 5, 9),
    "monorail": RideData(32, 8, 9),
    "monorail_cycles": RideData(24, 8, 7),
    "monster_trucks": RideData(24, 4, 7),
    "multi_dimension_rc": RideData(24, 8, 11),
    "observation_tower": RideData(32, 3, 2, no_platform=True, tiles=(3, 3), flat_ride_has_track=True),
    "reverse_freefall_rc": RideData(32, 4, 7, narrow_platform=True),
    "reverser_rc": RideData(24, 8, 11),
    "river_rafts": RideData(24, 7, 11),
    "river_rapids": RideData(32, 14, 15, narrow_platform=True),
    "roto_drop": RideData(32, 3, 2, no_platform=True, tiles=(3, 3), flat_ride_has_track=True),
    "side_friction_rc": RideData(24, 4, 11),
    "single_rail_rc": RideData(24, 5, 7),
    "spinning_wild_mouse": RideData(24, 4, 7),
    "spiral_rc": RideData(24, 9, 11),
    "splash_boats": RideData(24, 7, 11, narrow_platform=True),
    "stand_up_rc": RideData(24, 9, 11),
    "steel_wild_mouse": RideData(24, 4, 7),
    "steeplechase": RideData(24, 7, 7),
    "submarine_ride": RideData(32, 16, 19),  # Added 16 to account for underwater
    "suspended_monorail": RideData(40, 32, 8, is_suspended=True),
    "suspended_swinging_rc": RideData(40, 29, 8, is_suspended=True),
    "twister_rc": RideData(24, 8, 9, narrow_platform=True),
    "vertical_drop_rc": RideData(24, 8, 11, narrow_platform=True),
    "virginia_reel": RideData(24, 6, 7),
    "water_coaster": RideData(24, 4, 7),
    "wooden_rc": RideData(24, 8, 11),
    "wooden_wild_mouse": RideData(24, 4, 7)}


def update_load_preview(dummyself, context):
    scene = context.scene
    properties = scene.rct_graphics_helper_vehicles_properties  # type: VehiclesProperties
    objects = bpy.data.objects
    objects.get("RCT_One_Quarter").hide = True
    objects.get("RCT_Diagonal_1").hide = True
    objects.get("RCT_Diagonal_2").hide = True
    objects.get("RCT_Three_Quarter").hide = True
    objects.get("RCT_Half_Tile").hide = True
    size_preview = objects.get("RCT_Size_Preview")
    size_preview.hide = True
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
    rct_waypoint = objects.get("RCT_Waypoint")
    if rct_waypoint is not None:
        bpy.data.objects.remove(rct_waypoint)
    objects.get("RCT_Full_Tile").hide = True
    objects.get("RCT_Vehicle_Arrow").hide = True
    objects.get("RCT_Vehicle_Arrow").hide = True
    objects.get("RCT_Plaform").hide = True
    if len(properties.cars) > 0:
        car = properties.cars[properties.cars_index]  # type: CarProperties
        if not car.loading_preview:
            return
        data = ride_data[properties.type]
        objects.get("RCT_Full_Tile").hide = False
        objects.get("RCT_Plaform").scale = (1, 1, data.platform_height / data.track_clearance)
        objects.get("RCT_Plaform_Narrow").scale = (1, 1, data.platform_height / data.track_clearance)
        size_preview.location = (0, 0, -data.vehicle_z_offset * 0.025516)
        if not properties.use_waypoints:
            objects.get("RCT_Vehicle_Arrow").hide = False
            if data.no_platform:
                objects.get("RCT_Plaform").hide = True
                objects.get("RCT_Plaform_Narrow").hide = True
            else:
                if data.narrow_platform:
                    objects.get("RCT_Plaform").hide = True
                    objects.get("RCT_Plaform_Narrow").hide = False
                else:
                    objects.get("RCT_Plaform").hide = False
                    objects.get("RCT_Plaform_Narrow").hide = True
            if data.tiles is not None:
                width = data.tiles[0]
                length = data.tiles[1]
            else:
                length = car.spacing / 262144
                width = 1
                if properties.type in ('dodgems', 'space_rings'):
                    width = length
                elif properties.type == 'go_karts':
                    width = 0.5
            size_preview.scale = (length, width, data.track_clearance)
            for i in range(len(car.loadingPositions)):
                x = car.loadingPositions[i].position / 32
                rct_empty = objects.new("Position %s" % i, None)
                scene.objects.link(rct_empty)
                rct_empty.hide_select = True
                rct_empty.show_name = True
                rct_empty.empty_draw_type = 'SINGLE_ARROW'
                rct_empty.scale = (0.5, 0.5, 0.2)
                rct_empty.rotation_euler = [-math.pi/2, 0, 0]
                rct_empty.location = (x, -0.6, 0)
                rct_empty.parent = rct_load_preview
        else:
            x_tiles = data.tiles[0]
            y_tiles = data.tiles[1]
            size_preview.scale = (x_tiles, y_tiles, data.track_clearance)
            objects.get("RCT_Vehicle_Arrow").hide = True
            objects.get("RCT_Plaform").hide = True
            objects.get("RCT_Plaform_Narrow").hide = True
            if len(car.loadingWaypoints) > 0:
                waypoint_set = car.loadingWaypoints[car.loading_waypoints_index]  # type: LoadingWaypointSet
                side = car.loading_waypoints_preview
                waypoint = getattr(waypoint_set, side)  # type: LoadingWaypointItem
                rct_box_mesh = bpy.data.meshes.get("RCT_Waypoint_Mesh")
                if rct_box_mesh is not None:
                    bpy.data.meshes.remove(rct_box_mesh)
                rct_box_mesh = bpy.data.meshes.new("RCT_Waypoint_Mesh")
                vertices = []
                edges = [(0, 1), (1, 2), (0, 2), (2, 3), (3, 4)]
                if side == 'SW':
                    vertices = [((x_tiles/2 - 0.25), (y_tiles/2 - 0.25), 0),
                                ((x_tiles/2 - 0.25), -(y_tiles/2 - 0.25), 0)]
                elif side == 'NW':
                    vertices = [((x_tiles/2 - 0.25), -(y_tiles/2 - 0.25), 0),
                                (-(x_tiles/2 - 0.25), -(y_tiles/2 - 0.25), 0)]
                elif side == 'NE':
                    vertices = [(-(x_tiles/2 - 0.25), (y_tiles/2 - 0.25), 0),
                                (-(x_tiles/2 - 0.25), -(y_tiles/2 - 0.25), 0)]
                elif side == 'SE':
                    vertices = [((x_tiles/2 - 0.25), (y_tiles/2 - 0.25), 0),
                                (-(x_tiles/2 - 0.25), (y_tiles/2 - 0.25), 0)]
                vertices.extend([
                    (waypoint.position1[0]/32, waypoint.position1[1]/32, 0),
                    (waypoint.position2[0]/32, waypoint.position2[1]/32, 0),
                    (waypoint.position3[0]/32, waypoint.position3[1]/32, 0)])
                rct_box_mesh.from_pydata(vertices, edges, [])
                rct_box_mesh.update()
                rct_waypoint = objects.new("RCT_Waypoint", rct_box_mesh)
                scene.objects.link(rct_waypoint)
                rct_waypoint.hide_select = True
                rct_waypoint.location = (0, 0, 0)
                rct_waypoint.layers = [i == 10 for i in range(20)]


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

    def invoke(self, context: bpy.types.Context, event):
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
            side = active_data.loading_waypoints_preview
            col = layout.column()
            col.label("[%s]" % index)
            col.label("  0:")
            col.label("  1:")
            col.label("  2:")

            col = layout.column(align=True)
            route = getattr(item, side)
            col.label(side)
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


class Cars_UL_List(bpy.types.UIList):
    """Defines the drawing function for each car position item"""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label("Car %s:" % index)
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            icon = 'ERROR'
            if item.car_rendered:
                icon = 'FILE_TICK'
            layout.label(text="%s" % index, icon=icon)


class Frames(bpy.types.PropertyGroup):
    flat = bpy.props.BoolProperty(name="Flat", default=False, update=update_vehicles)
    gentleSlopes = bpy.props.BoolProperty(name="Gentle Slope", default=False, update=update_vehicles)
    steepSlopes = bpy.props.BoolProperty(name="Steep Slope", default=False, update=update_vehicles)
    verticalSlopes = bpy.props.BoolProperty(name="Vertical Slope", default=False, update=update_vehicles)
    diagonalSlopes = bpy.props.BoolProperty(name="Diagonal Slope", default=False, update=update_vehicles)
    flatBanked = bpy.props.BoolProperty(name="Banked", default=False, update=update_vehicles)
    inlineTwists = bpy.props.BoolProperty(name="Inline Twist", default=False, update=update_vehicles)
    flatToGentleSlopeBankedTransitions = bpy.props.BoolProperty(
        name="Bank Transition", default=False, update=update_vehicles)
    diagonalGentleSlopeBankedTransitions = bpy.props.BoolProperty(
        name="Diagonal Bank Transition", default=False, update=update_vehicles)
    gentleSlopeBankedTransitions = bpy.props.BoolProperty(
        name="Gentle Bank Transition", default=False, update=update_vehicles)
    gentleSlopeBankedTurns = bpy.props.BoolProperty(name="Gentle Banked Turn", default=False, update=update_vehicles)
    flatToGentleSlopeWhileBankedTransitions = bpy.props.BoolProperty(
        name="Gentle Transition While Banked", default=False, update=update_vehicles)
    corkscrews = bpy.props.BoolProperty(name="Corkscrew", default=False, update=update_vehicles)
    restraintAnimation = bpy.props.BoolProperty(name="Restraints", default=False, update=update_vehicles)
    curvedLiftHill = bpy.props.BoolProperty(name="Curved Lift", default=False, update=update_vehicles)
    VEHICLE_SPRITE_FLAG_15 = bpy.props.BoolProperty(name="4 Rotation Frames", default=False, update=update_vehicles)


class CarProperties(bpy.types.PropertyGroup):
    car_expanded = bpy.props.BoolProperty(default=True)
    car_rendered = bpy.props.BoolProperty(default=False)
    rotationFrameMask = bpy.props.IntProperty(
        name="Rotation Mask",
        description="A bitmask indicating how many rotation frames this car has\n\nFor rendering the spinning car "
        "in the UI?",
        default=31, min=0, max=65535
    )
    spacing = bpy.props.IntProperty(
        name="Spacing",
        description="The space taken up by this car. One tile is 262144 (2^18)",
        default=262144, min=0, soft_max=262144*2,
        update=update_vehicles
    )
    mass = bpy.props.IntProperty(
        name="Mass",
        description="The mass of this car",
        default=1000, min=0, max=65535
    )
    tabOffset = bpy.props.IntProperty(
        name="Tab Offset",
        description="If used, adds a vertical offset to this car when rendered in the UI",
        default=0, min=-128, max=127
    )
    numSeats = bpy.props.IntProperty(
        name="Number Of Seats",
        description="Number of riders that this car holds",
        default=0, min=0, max=255, update=update_vehicles
    )
    seatsInPairs = bpy.props.BoolProperty(
        name="Paired Seats",
        description="If set, indicates that guests sit in this car in pairs. Any car that seats more than one rider "
        "(and has riders visible) has to have this set if it uses the default visual mode (i.e. most of them).",
        default=True, update=update_vehicles
    )
    numSeatRows = bpy.props.IntProperty(
        name="Rider Sets",
        description="The number of separate sets of rider images for this car. For the default visual mode, this is "
        "equal to half the number of seats (or 1, if this car only holds one rider, or the default of 0, if riders "
        "are not visible).",
        default=0, min=0, max=255, update=update_vehicles
    )
    animation = bpy.props.EnumProperty(
        items=[
            ("0", "None", ""),
            ("1", "Miniature Railway", ""),
            ("2", "Swan Boats", ""),
            ("3", "Canoes", ""),
            ("4", "Row Boats", ""),
            ("5", "Water Tricycles", ""),
            ("6", "Observation Tower", ""),
            ("7", "Helicars", ""),
            ("8", "Monorail Cycles", ""),
            ("9", "Multidimensional Coaster", "")],
        name="Animation Mode",
        description="Indicates a special animation mode to use for this car.", update=update_vehicles
    )
    spinningInertia = bpy.props.IntProperty(
        name="Spin Inertia",
        description="For spinning vehicles, this is their inertia for spinning (higher numbers mean the spin is more "
        "stable, and changes speed less).",
        default=0, min=0, max=255
    )
    spinningFriction = bpy.props.IntProperty(
        name="Spin Friction",
        description="For spinning vehicles, this is friction that should slow down their spin over time.\n\n"
        "Technically, because of simplistic code, this is only true for leftward spinning, and rightward spins will "
        "actually speed up over time.",
        default=0, max=255
    )
    frictionSoundId = bpy.props.EnumProperty(
        items=[
            ("0", "Lift", ""),
            ("1", "Wood Classic Friction", ""),
            ("2", "Classic Friction", ""),
            ("21", "Go Kart Engine", ""),
            ("31", "Train Friction", ""),
            ("32", "Water", ""),
            ("54", "Wood Friction", ""),
            ("57", "BM Friction", ""),
            ("255", "None", "")
        ],
        name="Friction Sound",
        description="Selects the \"friction\" sound that's played for this car.",
        default="255"
    )
    logFlumeReverserVehicleType = bpy.props.IntProperty(
        name="Reverser Type",
        description="For rides with reverser elements, this is the index of the car to turn into after going through "
        "a reverser element.",
        default=0, min=0, max=255, update=update_vehicles
    )
    soundRange = bpy.props.EnumProperty(
        items=[
            ("0", "Screams 0", ""),
            ("1", "Screams 1", ""),
            ("2", "Screams 2", ""),
            ("3", "Whistle", ""),
            ("4", "Bell", ""),
            ("255", "None", "")
        ],
        name="Sound Range",
        description="Selects the type of sound that's regularly played for this car.",
        default="255"
    )
    doubleSoundFrequency = bpy.props.IntProperty(
        name="Double Frequency",
        description="If set to 1, sound frequency is doubled (relative to velocity). Used for go-karts.",
        default=0, min=0, max=1
    )
    poweredAcceleration = bpy.props.IntProperty(
        name="Powered Acceleration",
        description="For powered rides, the amount of powered acceleration",
        default=0, min=0, max=255
    )
    poweredMaxSpeed = bpy.props.IntProperty(
        name="Powered Max Speed",
        description="For powered rides, the maximum powered speed",
        default=0, min=0, max=255
    )
    carVisual = bpy.props.EnumProperty(
        items=[
            ("0", "Default", "Draws this car by choosing a sprite based on the car angle."),
            ("1", "Flat or Car Ride",
             "Don't draw this car.\n\nFor flat rides, this is set when this car is part of the flat ride's structure, "
             "and isn't a car on a track (i.e. the flat ride code will draw this car as part of drawing the "
             "structure).\n\nFor car rides and similar rides, they may have an extra car at the front and back that "
             "shouldn't be drawn, so those cars have this visual mode."),
            ("2", "Launched Freefall",
             "First sprite is the full car, then sprites are split into front and back, for a 4-frame animation of "
             "restraints opening. Followed are the rider pairs, nominally from right to left, for a *three* "
             "frame restraint opening animation."),
            ("3", "Observation Tower",
             "An eight frame animation rotating clockwise 45 degrees. Then the same, with each frame split into "
             "back and then front. Then three frames of the doors opening, each split the same way, and then repeated "
             "with the doors facing right. No peep images."),
            ("4", "River Rapids",
             "8-frames of the boat spinning 90 degrees. The same for a half-gentle slope, tilted SW, NW, NE, SE, and "
             "then those 4 again at a full gentle slope. The rider images are the same sequence, repeated separately "
             "for each seat pair in the boat (nominally in the order NW, NE, SE, SW)"),
            ("5", "Mini Golf (Player)",
             "Each frame is four angles, facing NE and then clockwise. 0-5 are a walk cycle. 6-8 are a right-handed "
             "swing animation. 9-11 are a right-handed \"backswing\". 12-15 are an animation of bending down (to pick "
             "up, put down, etc. This will be played in both directions). 16-30 are a \"jumping for joy\" animation. "
             "31-36 are mirrored versions of 6-11 (literally mirrored, meaning left-handed and facing SW too)."),
            ("6", "Mini Golf (Ball)", "Just a single sprite of the ball."),
            ("7", "Reverser",
             "Same as default, but internally its position is calculated as the midpoint of the front and rear cars "
             "(these are the separate wheel bogies for the reverser coaster car)."),
            ("8", "Splash Boats/Water Coaster",
             "The actual splash for the Splash Boats/Water Coaster is a separate car? The splash graphics are "
             "hardcoded in G1.dat so this car has no separate images in the object. Not sure I fully understand this "
             "one."),
            ("9", "Roto-Drop",
             "4 frames of rotation (clockwise by one seat, or 22.5deg). Then repeated for the back and then for the "
             "front. Then \"4\" frames of restraints opening (it's really only 3 frames, and then a blank image), for "
             "the back, and then for the front. Peep images are a 64-frame rotation (clockwise) of a single peep, "
             "then restraint opening animation for every seat (it's a blank image and *then* 3 animation frames this "
             "time. (Peep images start from the NE-most seat and continue clockwise. The game doesn't actually render "
             "the last/rear 16 positions (or 4 seats), so maybe images can actually be blank?"),
            ("15", "Virginia Reel", "Same as River Rapids, except each seat image has only one rider."),
            ("16", "Submarine",
             "Each frame is split into \"above the water\" and \"below the water \". A 32-frame rotation starting NE "
             "and going 360deg clockwise, then 3 frames of it coming out of the water (split into 4 angles--NE,SE,"
             "SW,NW--and then split into above and below). No rider images.")
        ],
        name="Visual Mode",
        description="Specifies the visual drawing mode of the car",
        default="0", update=update_vehicles
    )
    effectVisual = bpy.props.EnumProperty(
        items=[
            ("1", "None", ""),
            ("10", "Splash 1", ""),
            ("11", "Splash 2", ""),
            ("12", "Splash 3", ""),
            ("13", "Splash 4", ""),
            ("14", "Splash 5", "")
        ],
        name="Effect Visual",
        description="If not set to \"None\", selects the type of splash effect to use for this car. (Splash images "
        "are in G1.DAT). Car Visual must be default/reverser or river rapids.",
        default="1", update=update_vehicles
    )
    drawOrder = bpy.props.IntProperty(
        name="Draw Order",
        description="? Only used with default/reverser and submarine visual modes.",
        default=0, min=0, max=15
    )
    numVerticalFramesOverride = bpy.props.IntProperty(
        name="Base Frames Override",
        description="Overrides the calculated number of \"base\" vertical frames. This is used for some cars that "
        "use multiple base frames, but don't have a special spinning or animation flag that sets the correct number.",
        default=0, min=0, max=255, update=update_vehicles
    )

    loading_preview = bpy.props.BoolProperty(name="Loading Preview", default=True, update=update_load_preview)
    loadingPositions = bpy.props.CollectionProperty(
        type=LoadingPositionItem, name="Loading Positions",
        description="A list of loading positions to use for this car.")
    loading_positions_index = bpy.props.IntProperty(default=0, update=update_load_preview)
    loadingWaypoints = bpy.props.CollectionProperty(
        type=LoadingWaypointSet, name="Loading Waypoints",
        description="A list of loading waypoints to use for this car.")
    loading_waypoints_preview = bpy.props.EnumProperty(
        items=[
            ("SW", "SW", ""),
            ("NW", "NW", ""),
            ("NE", "NE", ""),
            ("SE", "SE", "")
        ],
        name="Preview Side",
        description="Chooses which building side to use for previewing waypoints.",
        update=update_load_preview
    )
    loading_waypoints_index = bpy.props.IntProperty(default=0, update=update_load_preview)

    frames = bpy.props.PointerProperty(type=Frames)

    isPoweredRideWithUnrestrictedGravity = bpy.props.BoolProperty(
        name="isPoweredRideWithUnrestrictedGravity",
        description=("")
    )
    hasNoUpstopWheels = bpy.props.BoolProperty(
        name="hasNoUpstopWheels",
        description=("")
    )
    hasNoUpstopWheelsBobsleigh = bpy.props.BoolProperty(
        name="hasNoUpstopWheelsBobsleigh",
        description=("")
    )
    isMiniGolf = bpy.props.BoolProperty(
        name="isMiniGolf",
        description=(""), update=update_vehicles
    )
    isReverserBogie = bpy.props.BoolProperty(
        name="isReverserBogie",
        description=(""), update=update_vehicles
    )
    isReverserPassengerCar = bpy.props.BoolProperty(
        name="isReverserPassengerCar",
        description=(""), update=update_vehicles
    )
    hasInvertedSpriteSet = bpy.props.BoolProperty(
        name="hasInvertedSpriteSet",
        description=(""), update=update_vehicles
    )
    hasDodgemInUseLights = bpy.props.BoolProperty(
        name="hasDodgemInUseLights",
        description=(""), update=update_vehicles
    )
    hasAdditionalColour2 = bpy.props.BoolProperty(
        name="hasAdditionalColour2",
        description=(""), update=update_vehicles
    )
    recalculateSpriteBounds = bpy.props.BoolProperty(
        name="recalculateSpriteBounds",
        description=(""), update=update_vehicles
    )
    VEHICLE_ENTRY_FLAG_11 = bpy.props.BoolProperty(
        name="VEHICLE_ENTRY_FLAG_11",
        description=(""), update=update_vehicles
    )
    overrideNumberOfVerticalFrames = bpy.props.BoolProperty(
        name="overrideNumberOfVerticalFrames",
        description=(""), update=update_vehicles
    )
    spriteBoundsIncludeInvertedSet = bpy.props.BoolProperty(
        name="spriteBoundsIncludeInvertedSet",
        description=(""), update=update_vehicles
    )
    hasAdditionalSpinningFrames = bpy.props.BoolProperty(
        name="hasAdditionalSpinningFrames",
        description=(""), update=update_vehicles
    )
    isLift = bpy.props.BoolProperty(
        name="isLift",
        description=(""), update=update_vehicles
    )
    hasAdditionalColour1 = bpy.props.BoolProperty(
        name="hasAdditionalColour1",
        description=(""), update=update_vehicles
    )
    hasSwinging = bpy.props.BoolProperty(
        name="hasSwinging",
        description=(""), update=update_vehicles
    )
    hasSpinning = bpy.props.BoolProperty(
        name="hasSpinning",
        description=(""), update=update_vehicles
    )
    isPowered = bpy.props.BoolProperty(
        name="isPowered",
        description=(""), update=update_vehicles
    )
    hasScreamingRiders = bpy.props.BoolProperty(
        name="hasScreamingRiders",
        description=("")
    )
    useSuspendedSwing = bpy.props.BoolProperty(
        name="useSuspendedSwing",
        description=(""), update=update_vehicles
    )
    useBoatHireCollisionDetection = bpy.props.BoolProperty(
        name="useBoatHireCollisionDetection",
        description=(""), update=update_vehicles
    )
    hasVehicleAnimation = bpy.props.BoolProperty(
        name="hasVehicleAnimation",
        description=(""), update=update_vehicles
    )
    hasRiderAnimation = bpy.props.BoolProperty(
        name="hasRiderAnimation",
        description=(""), update=update_vehicles
    )
    useWoodenWildMouseSwing = bpy.props.BoolProperty(
        name="useWoodenWildMouseSwing",
        description=(""), update=update_vehicles
    )
    useSlideSwing = bpy.props.BoolProperty(
        name="useSlideSwing",
        description=(""), update=update_vehicles
    )
    isChairlift = bpy.props.BoolProperty(
        name="isChairlift",
        description=(""), update=update_vehicles
    )
    isWaterRide = bpy.props.BoolProperty(
        name="isWaterRide",
        description=(""), update=update_vehicles
    )
    isGoKart = bpy.props.BoolProperty(
        name="isGoKart",
        description=(""), update=update_vehicles
    )
    useDodgemCarPlacement = bpy.props.BoolProperty(
        name="useDodgemCarPlacement",
        description=(""), update=update_vehicles
    )


ride_types = [
    ("chairlift", "Chairlift", "chairlift"),
    ("lift", "Lift", "lift"),
    ("miniature_railway", "Miniature Railway", "miniature_railway"),
    ("monorail", "Monorail", "monorail"),
    ("suspended_monorail", "Suspended Monorail", "suspended_monorail"),
    
    ("car_ride", "Car Ride", "car_ride"),
    ("circus", "Circus", "circus"),
    ("crooked_house", "Crooked House", "crooked_house"),
    ("dodgems", "Dodgems", "dodgems"),
    ("ferris_wheel", "Ferris Wheel", "ferris_wheel"),
    ("flying_saucers", "Flying Saucers", "flying_saucers"),
    ("ghost_train", "Ghost Train", "ghost_train"),
    ("haunted_house", "Haunted House", "haunted_house"),
    ("maze", "Maze", "maze"),
    ("merry_go_round", "Merry-Go-Round", "merry_go_round"),
    ("mini_golf", "Mini Golf", "mini_golf"),
    ("mini_helicopters", "Mini Helicopters", "mini_helicopters"),
    ("monorail_cycles", "Monorail Cycles", "monorail_cycles"),
    ("monster_trucks", "Monster Trucks", "monster_trucks"),
    ("observation_tower", "Observation Tower", "observation_tower"),
    ("space_rings", "Space Rings", "space_rings"),
    ("spiral_slide", "Spiral Slide", "spiral_slide"),

    ("air_powered_vertical_rc", "Air Powered Vertical Coaster", "air_powered_vertical_rc"),
    ("bobsleigh_rc", "Bobsleigh Coaster", "bobsleigh_rc"),
    ("classic_mini_rc", "Classic Mini Roller Coaster", "classic_mini_rc"),
    ("compact_inverted_rc", "Compact Inverted Coaster", "compact_inverted_rc"),
    ("corkscrew_rc", "Corkscrew Roller Coaster", "corkscrew_rc"),
    ("flying_rc", "Flying Roller Coaster", "flying_rc"),
    ("giga_rc", "Giga Coaster", "giga_rc"),
    ("heartline_twister_rc", "Heartline Twister Coaster", "heartline_twister_rc"),
    ("hybrid_rc", "Hybrid Coaster", "hybrid_rc"),
    ("hyper_twister", "Hyper-Twister", "hyper_twister"),
    ("hypercoaster", "Hypercoaster", "hypercoaster"),
    ("inverted_hairpin_rc", "Inverted Hairpin Coaster", "inverted_hairpin_rc"),
    ("inverted_impulse_rc", "Inverted Impulse Coaster", "inverted_impulse_rc"),
    ("inverted_rc", "Inverted Roller Coaster", "inverted_rc"),
    ("junior_rc", "Junior Roller Coaster", "junior_rc"),
    ("lay_down_rc", "Lay-down Roller Coaster", "lay_down_rc"),
    ("lim_launched_rc", "LIM Launched Roller Coaster", "lim_launched_rc"),
    ("looping_rc", "Looping Roller Coaster", "looping_rc"),
    ("mine_ride", "Mine Ride", "mine_ride"),
    ("mine_train_rc", "Mine Train Coaster", "mine_train_rc"),
    ("mini_rc", "Mini Roller Coaster", "mini_rc"),
    ("mini_suspended_rc", "Mini Suspended Coaster", "mini_suspended_rc"),
    ("multi_dimension_rc", "Multi-Dimension Roller Coaster", "multi_dimension_rc"),
    ("reverse_freefall_rc", "Reverse Freefall Coaster", "reverse_freefall_rc"),
    ("reverser_rc", "Reverser Roller Coaster", "reverser_rc"),
    ("side_friction_rc", "Side-Friction Roller Coaster", "side_friction_rc"),
    ("single_rail_rc", "Single Rail Roller Coaster", "single_rail_rc"),
    ("spinning_wild_mouse", "Spinning Wild Mouse", "spinning_wild_mouse"),
    ("spiral_rc", "Spiral Roller Coaster", "spiral_rc"),
    ("stand_up_rc", "Stand-up Roller Coaster", "stand_up_rc"),
    ("steel_wild_mouse", "Steel Wild Mouse", "steel_wild_mouse"),
    ("steeplechase", "Steeplechase", "steeplechase"),
    ("suspended_swinging_rc", "Suspended Swinging Coaster", "suspended_swinging_rc"),
    ("twister_rc", "Twister Roller Coaster", "twister_rc"),
    ("vertical_drop_rc", "Vertical Drop Roller Coaster", "vertical_drop_rc"),
    ("virginia_reel", "Virginia Reel", "virginia_reel"),
    ("water_coaster", "Water Coaster", "water_coaster"),
    ("wooden_rc", "Wooden Roller Coaster", "wooden_rc"),
    ("wooden_wild_mouse", "Wooden Wild Mouse", "wooden_wild_mouse"),

    ("3d_cinema", "3D Cinema", "3d_cinema"),
    ("enterprise", "Enterprise", "enterprise"),
    ("go_karts", "", "go_karts"),
    ("launched_freefall", "Launched Freefall", "launched_freefall"),
    ("magic_carpet", "Magic Carpet", "magic_carpet"),
    ("motion_simulator", "Motion Simulator", "motion_simulator"),
    ("roto_drop", "Roto-Drop", "roto_drop"),
    ("swinging_ship", "Swinging Ship", "swinging_ship"),
    ("swinging_inverter_ship", "Swinging Inverter Ship", "swinging_inverter_ship"),
    ("top_spin", "Top Spin", "top_spin"),
    ("twist", "Twist", "twist"),

    
    ("boat_hire", "Boat Hire", "boat_hire"),
    ("dinghy_slide", "Dinghy Slide", "dinghy_slide"),
    ("log_flume", "Log Flume", "log_flume"),
    ("river_rafts", "River Rafts", "river_rafts"),
    ("river_rapids", "River Rapids", "river_rapids"),
    ("splash_boats", "Splash Boats", "splash_boats"),
    ("submarine_ride", "Submarine Ride", "submarine_ride")]


class VehiclesProperties(bpy.types.PropertyGroup):
    from_json = bpy.props.BoolProperty()
    type = bpy.props.EnumProperty(
        items=ride_types,
        name="Track Type",
        description="One of the track types supported by this vehicle",
        update=update_vehicles
    )
    type2 = bpy.props.EnumProperty(
        items=ride_types + [("none", "No Extra Type", "")],
        name="Track Type 2",
        description="One of the track types supported by this vehicle",
        default='none'
    )
    type3 = bpy.props.EnumProperty(
        items=ride_types + [("none", "No Extra Type", "")],
        name="Track Type 3",
        description="One of the track types supported by this vehicle",
        default='none'
    )
    use_waypoints = bpy.props.BoolProperty()
    force_visual_mode = bpy.props.BoolProperty()
    buildMenuPriority = custom_properties.buildMenuPriority
    maxHeight = custom_properties.maxHeight
    ratingMultiplier = bpy.props.PointerProperty(type=custom_properties.RatingMultiplier)
    minCarsPerTrain = bpy.props.IntProperty(
        name="Min Cars Per Train",
        description="Minimum number of cars that can be in a train.",
        min=0, update=update_vehicles
    )
    maxCarsPerTrain = bpy.props.IntProperty(
        name="Max Cars Per Train",
        description="Maximum number of cars that can be in a train.",
        min=0, update=update_vehicles
    )
    numEmptyCars = bpy.props.IntProperty(
        name="Empty Cars",
        description="The number of \"zero\" cars in the train. That is, cars that do not hold any guests.",
        min=0, update=update_vehicles
    )
    defaultCar = bpy.props.IntProperty(
        name="Default Car",
        description="Index of the car that should be used as the default car for this ride. In other words, this is "
        "the normal car that appears throughout the train wherever there isn't a special (i.e. front or rear) car.",
        min=0, update=update_vehicles
    )
    headCars = bpy.props.StringProperty(
        name="Head Cars",
        description="The index(es) of up to three cars that should be used to fill the front of a train. Separate "
        "multiple indexes with a comma.",
        update=update_vehicles
    )
    tailCars = bpy.props.StringProperty(
        name="Tail Car",
        description="Index of the car that should be used as the tail car, if any (you can list multiple cars, "
        "separated by commas, but currently only the first index listed is used by OpenRCT2).",
        update=update_vehicles
    )
    tabCar = bpy.props.IntProperty(
        name="Tab Car",
        description="The index of the car that should show on the vehicle tab for this ride (0 if not specified)",
        min=0
    )
    tabHalfScale = bpy.props.BoolProperty(
        name="Tab Scale",
        description="If true, this will scale the size of the tab preview in half"
    )

    noInversions = bpy.props.BoolProperty(
        name="No Inversions",
        description="Flagged if the ride does not support inversions"
    )
    noBanking = bpy.props.BoolProperty(
        name="No Banking",
        description="Flagged if the ride does not support banking",
        update=update_vehicles
    )
    playDepartSound = bpy.props.BoolProperty(
        name="Depart Sound",
        description="Flagged if the ride plays a departure sound when departing the station. depending on sound_range "
        "setting, plays Tram or Train departing sound."
    )
    playSplashSound = bpy.props.BoolProperty(
        name="Splash Sound",
        description="Flagged if the ride should play a splashing sound on down to flat elements"
    )
    playSplashSoundSlide = bpy.props.BoolProperty(
        name="Splash Sound (WC)",
        description="Flagged if the ride should play a splashing sound when entering a water channel, for water "
        "coasters. Has no effect if playSplashSound is enabled.\n\nNote: Internally, water channel track is coded as "
        "\"covered\" track, so if this flag is set for a ride running on a track that supports covered pieces, it "
        "will play a splash sound when entering a covered section of track."
    )
    hasShelter = bpy.props.BoolProperty(
        name="Has Shelter",
        description="Flagged if the ride is covered (for example, monorail cars are covered).\n\nNote that there are "
        "some ride types in vanilla RCT2 that seem to have this bit set illogically. Pickup-trucks did not have this "
        "set, and the uncovered ski lift cars did have these set. These have been changed in OpenRCT2 to make more "
        "sense."
    )
    limitAirTimeBonus = bpy.props.BoolProperty(
        name="Limit Airtime Bonus",
        description="Flagged if the ride should have a hard cap on how much bonus it gets from airtime. This is only "
        "set for heartline-twister coasters, and makes it so that a max of ~2 seconds of airtime can give an "
        "excitement bonus."
    )
    disableBreakdown = bpy.props.BoolProperty(
        name="Disable Breakdown",
        description="Flagged if the ride does not break down"
    )
    noCollisionCrashes = bpy.props.BoolProperty(
        name="No Collision",
        description="Flagged if the ride does not crash when vehicles collide"
    )
    disablePainting = bpy.props.BoolProperty(
        name="Disable Painting",
        description="Flagged if the ride does not support recolouring",
        update=update_vehicles
    )
    cars = bpy.props.CollectionProperty(type=CarProperties, name="Cars")
    cars_index = bpy.props.IntProperty(update=update_vehicles)


class Cars_OT_actions(bpy.types.Operator):
    """Buttons to add/remove/move a car position item."""
    bl_idname = "cars.actions"
    bl_label = "List Actions"
    bl_description = "Add/Remove\n\nMove Up/Down"
    bl_options = {'REGISTER'}

    action = bpy.props.StringProperty()
    car_index = bpy.props.IntProperty()

    def invoke(self, context: bpy.types.Context, event):
        properties = context.scene.rct_graphics_helper_vehicles_properties
        cars = properties.cars
        index = self.car_index

        try:
            item = cars[index]
        except IndexError:
            pass
        else:
            if self.action == 'DOWN' and index < len(cars) - 1:
                cars.move(index, index+1)
                setattr(properties, "cars_index", index + 1)

            elif self.action == 'UP' and index >= 1:
                cars.move(index, index-1)
                setattr(properties, "cars_index", index - 1)

            elif self.action == 'REMOVE':
                if index == len(cars) - 1:
                    setattr(properties, "cars_index", index - 1)
                cars.remove(index)

        if self.action == 'ADD':
            item = cars.add()
            setattr(properties, "cars_index", len(cars)-1)
        
        update_vehicles(None, context)
        return {"FINISHED"}


class VehiclesPanel(bpy.types.Panel):
    bl_label = "RCT Vehicles"
    bl_idname = "RENDER_PT_rct_vehicles"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    @classmethod
    def poll(cls, context: bpy.types.Context):
        general_properties = context.scene.rct_graphics_helper_general_properties
        return general_properties.objectType == "vehicle"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        properties = scene.rct_graphics_helper_vehicles_properties
        data = ride_data[properties.type]

        row = layout.row()
        row.operator("render.rct_vehicle", text="Build Vehicle")
        col = layout.column()
        row = col.row()
        row.prop(properties, 'type')
        row = col.row(align=True)
        row.prop(properties, 'type2', "")
        row.prop(properties, 'type3', "")
        row = layout.row()
        row.prop(properties, "buildMenuPriority")
        row.prop(properties, "maxHeight")
        col = layout.column()
        row = col.row(align=True)
        row.alignment = 'CENTER'
        row.label("Excitement:")
        row.label("Intensity:")
        row.label("Nausea:")
        row = col.row(align=True)
        row.prop(properties.ratingMultiplier, "excitement", text="")
        row.prop(properties.ratingMultiplier, "intensity", text="")
        row.prop(properties.ratingMultiplier, "nausea", text="")
        col = layout.column(align=True)
        row = col.row()
        row.alignment = 'CENTER'
        row.label("Cars Per Train:")
        row = col.row(align=True)
        row.prop(properties, "minCarsPerTrain", text="Min")
        row.prop(properties, "maxCarsPerTrain", text="Max")
        row = layout.row().split(0.8, align=True)
        row.label("Number of Empty Cars:")
        row.prop(properties, "numEmptyCars", text="")
        row = layout.row().split(0.8, align=True)
        row.label("Default Car:")
        row.prop(properties, "defaultCar", text="")
        row = layout.row()
        row.prop(properties, "headCars")
        row = layout.row()
        row.prop(properties, "tailCars")
        row = layout.row()
        row.prop(properties, "tabCar")
        row.prop(properties, "tabHalfScale", text="Half Scale", toggle=True)

        col = layout.column(align=True)
        row = col.row(align=True)
        row.alignment = 'CENTER'
        row.label("Flags:")
        row = col.row(align=True)
        row.prop(properties, "noInversions", toggle=True)
        row.prop(properties, "noBanking", toggle=True)
        row = col.row(align=True)
        row.prop(properties, "playDepartSound", toggle=True)
        row.prop(properties, "hasShelter", toggle=True)
        row = col.row(align=True)
        row.prop(properties, "playSplashSound", toggle=True)
        row.prop(properties, "playSplashSoundSlide", toggle=True)
        row = col.row(align=True)
        row.prop(properties, "limitAirTimeBonus", toggle=True)
        row.prop(properties, "disableBreakdown", toggle=True)
        row = col.row(align=True)
        row.prop(properties, "noCollisionCrashes", toggle=True)
        row.prop(properties, "disablePainting", toggle=True)

        row = layout.row()
        row.alignment = 'CENTER'
        row.label("Cars:")
        carscol = layout.column()

        i = 0
        if len(properties.cars) == 0:
            op = carscol.operator("cars.actions", icon='ZOOMIN', text="Add Car")
            op.action = 'ADD'
        else:
            row = carscol.row()
            row.template_list("Cars_UL_List", "", properties, "cars",
                              properties, "cars_index", rows=1, type='GRID')
            i = properties.cars_index
            car = properties.cars[i]
            box = carscol.box()
            row = box.row(align=True)
            row.label("Car %s" % i)
            if car.car_rendered:
                row.label(text="(Rendered)", icon='FILE_TICK')
            else:
                row.label(text="(Not Yet Rendered)", icon='ERROR')
            row.separator()
            op = row.operator("cars.actions", icon='ZOOMIN', text="")
            op.action = 'ADD'
            op.car_index = i
            op = row.operator("cars.actions", icon='ZOOMOUT', text="")
            op.action = 'REMOVE'
            op.car_index = i
            row.separator()
            op = row.operator("cars.actions", icon='TRIA_UP', text="")
            op.action = 'UP'
            op.car_index = i
            op = row.operator("cars.actions", icon='TRIA_DOWN', text="")
            
            row = box.row()
            row.operator("render.rct_car", text="Render Car")
            row = box.row()
            row.prop(car, "rotationFrameMask")
            row = box.row()
            row.prop(car, "spacing")
            row.prop(car, "mass")
            row = box.row()
            row.prop(car, "tabOffset")
            row = box.row()
            row.prop(car, "numSeats")
            row.prop(car, "numSeatRows")
            row = box.row()
            row.prop(car, "seatsInPairs")
            row = box.row()
            row.prop(car, "carVisual")
            row = box.row()
            row.prop(car, "effectVisual")
            row = box.row()
            row.prop(car, "drawOrder")
            row = box.row()
            row.prop(car, "numVerticalFramesOverride")
            row = box.row()
            row.prop(car, "animation")
            row = box.row()
            row.prop(car, "spinningInertia")
            row.prop(car, "spinningFriction")
            row = box.row()
            row.prop(car, "logFlumeReverserVehicleType")
            row = box.row()
            row.prop(car, "frictionSoundId")
            row = box.row()
            row.prop(car, "soundRange")
            row = box.row()
            row.prop(car, "doubleSoundFrequency")
            row = box.row()
            row.prop(car, "poweredAcceleration")
            row.prop(car, "poweredMaxSpeed")
            
            frames = car.frames
            col = box.column(align=True)
            row = col.row(align=True)
            row.prop(frames, "flat", toggle=True)
            row.prop(frames, "gentleSlopes", toggle=True)
            row.prop(frames, "steepSlopes", toggle=True)
            row = col.row(align=True)
            row.prop(frames, "verticalSlopes", toggle=True)
            row.prop(frames, "diagonalSlopes", toggle=True)
            row.prop(frames, "flatBanked", toggle=True)
            row = col.row(align=True)
            row.prop(frames, "flatToGentleSlopeBankedTransitions", toggle=True)
            row.prop(frames, "diagonalGentleSlopeBankedTransitions", toggle=True)
            row.prop(frames, "gentleSlopeBankedTransitions", toggle=True)
            row = col.row(align=True)
            row.prop(frames, "gentleSlopeBankedTurns", toggle=True)
            row.prop(frames, "flatToGentleSlopeWhileBankedTransitions", toggle=True)
            row = col.row(align=True)
            row.prop(frames, "inlineTwists", toggle=True)
            row.prop(frames, "corkscrews", toggle=True)
            row.prop(frames, "restraintAnimation", toggle=True)
            row = col.row(align=True)
            row.prop(frames, "curvedLiftHill", toggle=True)
            row.prop(frames, "VEHICLE_SPRITE_FLAG_15", toggle=True)
            
            col = box.column()
            row = col.row()
            row.label("Loading %s:" % ("Waypoints" if properties.use_waypoints else "Positions"))
            row = col.row(align=True).split(0.33, True)
            row.prop(car, "loading_preview", text="Show Preview")
            if properties.use_waypoints:
                row.prop_enum(car, "loading_waypoints_preview", 'SW')
                row.prop_enum(car, "loading_waypoints_preview", 'NW')
                row.prop_enum(car, "loading_waypoints_preview", 'NE')
                row.prop_enum(car, "loading_waypoints_preview", 'SE')
                sub = col.row()
                subcol = sub.column(align=True)
                subcol.template_list("LoadingWaypoints_UL_List", "", car, "loadingWaypoints",
                                     car, "loading_waypoints_index", rows=3)
                subcol = sub.column(align=True)
                op = subcol.operator("loadingwaypoints.actions", icon='ZOOMIN', text="")
                op.action = 'ADD'
                op.car_index = i
                op = subcol.operator("loadingwaypoints.actions", icon='ZOOMOUT', text="")
                op.action = 'REMOVE'
                op.car_index = i
                subcol.separator()
                op = subcol.operator("loadingwaypoints.actions", icon='TRIA_UP', text="")
                op.action = 'UP'
                op.car_index = i
                op = subcol.operator("loadingwaypoints.actions", icon='TRIA_DOWN', text="")
                op.action = 'DOWN'
                op.car_index = i
            else:
                sub = col.row()
                subcol = sub.column(align=True)
                subcol.template_list("LoadingPositions_UL_List", "", car, "loadingPositions",
                                     car, "loading_positions_index", rows=3)
                subcol = sub.column(align=True)
                op = subcol.operator("loadingpositions.actions", icon='ZOOMIN', text="")
                op.action = 'ADD'
                op.car_index = i
                op = subcol.operator("loadingpositions.actions", icon='ZOOMOUT', text="")
                op.action = 'REMOVE'
                op.car_index = i
                subcol.separator()
                op = subcol.operator("loadingpositions.actions", icon='TRIA_UP', text="")
                op.action = 'UP'
                op.car_index = i
                op = subcol.operator("loadingpositions.actions", icon='TRIA_DOWN', text="")
                op.action = 'DOWN'
                op.car_index = i

            i += 1

        row = layout.row()
        row.label("Color Presets:")
        row = layout.row()
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


def register_vehicles_panel():
    bpy.types.Scene.rct_graphics_helper_vehicles_properties = bpy.props.PointerProperty(
        type=VehiclesProperties)


def unregister_vehicles_panel():
    del bpy.types.Scene.rct_graphics_helper_vehicles_properties
