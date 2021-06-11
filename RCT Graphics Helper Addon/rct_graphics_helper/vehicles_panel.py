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
    objects.get("RCT_One_Quarter").hide = True
    objects.get("RCT_Diagonal_1").hide = True
    objects.get("RCT_Diagonal_2").hide = True
    objects.get("RCT_Three_Quarter").hide = True
    objects.get("RCT_Half_Tile").hide = True
    size_preview = objects.get("RCT_Size_Preview")
    if len(properties.cars) == 0:
        objects.get("RCT_Full_Tile").hide = True
        objects.get("RCT_Vehicle_Arrow").hide = True
    else:
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
            car = properties.cars[properties.cars_index]  # type: CarProperties
            length = car.spacing / 262144
            size_preview.scale = (length, 1, clearance)
        size_preview.location = (0, 0, z_offset)
    size_preview.hide = True


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
    flat = bpy.props.BoolProperty(name="Flat", default=False)
    gentleSlopes = bpy.props.BoolProperty(name="Gentle Slope", default=False)
    steepSlopes = bpy.props.BoolProperty(name="Steep Slope", default=False)
    verticalSlopes = bpy.props.BoolProperty(name="Vertical Slope", default=False)
    diagonalSlopes = bpy.props.BoolProperty(name="Diagonal Slope", default=False)
    flatBanked = bpy.props.BoolProperty(name="Banked", default=False)
    inlineTwists = bpy.props.BoolProperty(name="Inline Twist", default=False)
    flatToGentleSlopeBankedTransitions = bpy.props.BoolProperty(name="Bank Transition", default=False)
    diagonalGentleSlopeBankedTransitions = bpy.props.BoolProperty(name="Diagonal Bank Transition", default=False)
    gentleSlopeBankedTransitions = bpy.props.BoolProperty(name="Gentle Bank Transition", default=False)
    gentleSlopeBankedTurns = bpy.props.BoolProperty(name="Gentle Banked Turn", default=False)
    flatToGentleSlopeWhileBankedTransitions = bpy.props.BoolProperty(
        name="Gentle Transition While Banked", default=False)
    corkscrews = bpy.props.BoolProperty(name="Corkscrew", default=False)
    restraintAnimation = bpy.props.BoolProperty(name="Restraints", default=False)
    curvedLiftHill = bpy.props.BoolProperty(name="Curved Lift", default=False)
    VEHICLE_SPRITE_FLAG_15 = bpy.props.BoolProperty(name="4 Rotation Frames", default=False)


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
        default=0, min=0, max=255
    )
    seatsInPairs = bpy.props.BoolProperty(
        name="Paired Seats",
        description="If set, indicates that guests sit in this car in pairs. Any car that seats more than one rider "
        "(and has riders visible) has to have this set if it uses the default visual mode (i.e. most of them).",
        default=True
    )
    numSeatRows = bpy.props.IntProperty(
        name="Rider Sets",
        description="The number of separate sets of rider images for this car. For the default visual mode, this is "
        "equal to half the number of seats (or 1, if this car only holds one rider, or the default of 0, if riders "
        "are not visible).",
        default=0, min=0, max=255
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
        description="Indicates a special animation mode to use for this car."
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
        default=0, min=0, max=255
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
             "Don't draw this car.\n\nFor flat rides, this means they won't be drawn as a \"vehicle\" on a track, and "
             "drawing will depend on the ride type, as part of the structure of the ride.\n\nFor car rides and "
             "similar rides, they may have an extra car at the front and back that shouldn't be drawn, so those "
             "cars have this visual mode."),
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
        default="0",
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
        default="1",
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
        default=0, min=0, max=255
    )
    use_waypoints = bpy.props.BoolProperty(
        name="Use Waypoints",
        description="If true, use loading waypoints instead of loading positions."
    )
    loadingWaypoints = custom_properties.loadingWaypoints
    loading_waypoints_index = custom_properties.loading_waypoints_index
    loadingPositions = custom_properties.loadingPositions
    loading_positions_index = custom_properties.loading_positions_index

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
        description=("")
    )
    isReverserBogie = bpy.props.BoolProperty(
        name="isReverserBogie",
        description=("")
    )
    isReverserPassengerCar = bpy.props.BoolProperty(
        name="isReverserPassengerCar",
        description=("")
    )
    hasInvertedSpriteSet = bpy.props.BoolProperty(
        name="hasInvertedSpriteSet",
        description=("")
    )
    hasDodgemInUseLights = bpy.props.BoolProperty(
        name="hasDodgemInUseLights",
        description=("")
    )
    hasAdditionalColour2 = bpy.props.BoolProperty(
        name="hasAdditionalColour2",
        description=("")
    )
    recalculateSpriteBounds = bpy.props.BoolProperty(
        name="recalculateSpriteBounds",
        description=("")
    )
    VEHICLE_ENTRY_FLAG_11 = bpy.props.BoolProperty(
        name="VEHICLE_ENTRY_FLAG_11",
        description=("")
    )
    overrideNumberOfVerticalFrames = bpy.props.BoolProperty(
        name="overrideNumberOfVerticalFrames",
        description=("")
    )
    spriteBoundsIncludeInvertedSet = bpy.props.BoolProperty(
        name="spriteBoundsIncludeInvertedSet",
        description=("")
    )
    hasAdditionalSpinningFrames = bpy.props.BoolProperty(
        name="hasAdditionalSpinningFrames",
        description=("")
    )
    isLift = bpy.props.BoolProperty(
        name="isLift",
        description=("")
    )
    hasAdditionalColour1 = bpy.props.BoolProperty(
        name="hasAdditionalColour1",
        description=("")
    )
    hasSwinging = bpy.props.BoolProperty(
        name="hasSwinging",
        description=("")
    )
    hasSpinning = bpy.props.BoolProperty(
        name="hasSpinning",
        description=("")
    )
    isPowered = bpy.props.BoolProperty(
        name="isPowered",
        description=("")
    )
    hasScreamingRiders = bpy.props.BoolProperty(
        name="hasScreamingRiders",
        description=("")
    )
    useSuspendedSwing = bpy.props.BoolProperty(
        name="useSuspendedSwing",
        description=("")
    )
    useBoatHireCollisionDetection = bpy.props.BoolProperty(
        name="useBoatHireCollisionDetection",
        description=("")
    )
    hasVehicleAnimation = bpy.props.BoolProperty(
        name="hasVehicleAnimation",
        description=("")
    )
    hasRiderAnimation = bpy.props.BoolProperty(
        name="hasRiderAnimation",
        description=("")
    )
    useWoodenWildMouseSwing = bpy.props.BoolProperty(
        name="useWoodenWildMouseSwing",
        description=("")
    )
    useSlideSwing = bpy.props.BoolProperty(
        name="useSlideSwing",
        description=("")
    )
    isChairlift = bpy.props.BoolProperty(
        name="isChairlift",
        description=("")
    )
    isWaterRide = bpy.props.BoolProperty(
        name="isWaterRide",
        description=("")
    )
    isGoKart = bpy.props.BoolProperty(
        name="isGoKart",
        description=("")
    )
    useDodgemCarPlacement = bpy.props.BoolProperty(
        name="useDodgemCarPlacement",
        description=("")
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
    ("dodgems", "Dodgems", "dodgems"),
    ("flying_saucers", "Flying Saucers", "flying_saucers"),
    ("go_karts", "Go-Karts", "go_karts"),
    ("log_flume", "Log Flume", "log_flume"),
    ("river_rapids", "River Rapids", "river_rapids"),
    ("reverse_freefall_rc", "Reverse Freefall Coaster", "reverse_freefall_rc"),
    ("lift", "Lift", "lift"),
    ("vertical_drop_rc", "Vertical Drop Roller Coaster", "vertical_drop_rc"),
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
    ("monorail_cycles", "Monorail Cycles", "monorail_cycles"),
    ("compact_inverted_rc", "Compact Inverted Coaster", "compact_inverted_rc"),
    ("water_coaster", "Water Coaster", "water_coaster"),
    ("air_powered_vertical_rc", "Air Powered Vertical Coaster", "air_powered_vertical_rc"),
    ("inverted_hairpin_rc", "Inverted Hairpin Coaster", "inverted_hairpin_rc"),
    ("submarine_ride", "Submarine Ride", "submarine_ride"),
    ("river_rafts", "River Rafts", "river_rafts"),
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


class VehiclesProperties(bpy.types.PropertyGroup):
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

    buildMenuPriority = custom_properties.buildMenuPriority
    maxHeight = custom_properties.maxHeight
    ratingMultiplier = bpy.props.PointerProperty(type=custom_properties.RatingMultiplier)
    minCarsPerTrain = bpy.props.IntProperty(
        name="Min Cars Per Train",
        description="Minimum number of cars that can be in a train.",
        min=0
    )
    maxCarsPerTrain = bpy.props.IntProperty(
        name="Max Cars Per Train",
        description="Maximum number of cars that can be in a train.",
        min=0
    )
    numEmptyCars = bpy.props.IntProperty(
        name="Empty Cars",
        description="The number of \"zero\" cars in the train. That is, cars that do not hold any guests.",
        min=0
    )
    defaultCar = bpy.props.IntProperty(
        name="Default Car",
        description="Index of the car that should be used as the default car for this ride. In other words, this is "
        "the normal car that appears throughout the train wherever there isn't a special (i.e. front or rear) car.",
        min=0
    )
    headCars = bpy.props.StringProperty(
        name="Head Cars",
        description="The index(es) of up to three cars that should be used to fill the front of a train. Separate "
        "multiple indexes with a comma."
    )
    tailCars = bpy.props.StringProperty(
        name="Tail Car",
        description="Index of the car that should be used as the tail car, if any (you can list multiple cars, "
        "separated by commas, but currently only the first index listed is used by OpenRCT2)."
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
        description="Flagged if the ride does not support banking"
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
        description="Flagged if the ride does not support recolouring"
    )
    cars = bpy.props.CollectionProperty(type=CarProperties, name="Cars")
    cars_index = bpy.props.IntProperty()

    restraint_animation = bpy.props.BoolProperty(
        name="Restraint Animation",
        description="Render with restraint animation. The restrain animation is 3 frames long and starts at frame 1",
        default=False)

    inverted_set = bpy.props.BoolProperty(
        name="Inverted Set",
        description=("Used for rides which can invert for an extended amount of time like the flying and"
                     "lay-down rollercoasters"),
        default=False)


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
            head = col.row()
            head.label("Loading:")
            head.prop(car, "use_waypoints")
            if car.use_waypoints:
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
