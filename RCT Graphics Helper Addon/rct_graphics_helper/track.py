'''
Copyright (c) 2021 RCT Graphics Helper developers

For a complete list of all authors, please refer to the addon's meta info.
Interested in contributing? Visit https://github.com/oli414/Blender-RCT-Graphics

RCT Graphics Helper is licensed under the GNU General Public License version 3.
'''

from . render_task import AngleSection

track_angle_sections_names = [
    "VEHICLE_SPRITE_FLAG_FLAT",
    "VEHICLE_SPRITE_FLAG_GENTLE_SLOPES",
    "VEHICLE_SPRITE_FLAG_STEEP_SLOPES",
    "VEHICLE_SPRITE_FLAG_VERTICAL_SLOPES",
    "VEHICLE_SPRITE_FLAG_DIAGONAL_SLOPES",
    "VEHICLE_SPRITE_FLAG_FLAT_BANKED",
    "VEHICLE_SPRITE_FLAG_INLINE_TWISTS",
    "VEHICLE_SPRITE_FLAG_FLAT_TO_GENTLE_SLOPE_BANKED_TRANSITIONS",
    "VEHICLE_SPRITE_FLAG_DIAGONAL_GENTLE_SLOPE_BANKED_TRANSITIONS",
    "VEHICLE_SPRITE_FLAG_GENTLE_SLOPE_BANKED_TRANSITIONS",
    "VEHICLE_SPRITE_FLAG_GENTLE_SLOPE_BANKED_TURNS",
    "VEHICLE_SPRITE_FLAG_FLAT_TO_GENTLE_SLOPE_WHILE_BANKED_TRANSITIONS",
    "VEHICLE_SPRITE_FLAG_CORKSCREWS",
    "VEHICLE_SPRITE_FLAG_RESTRAINT_ANIMATION",
    "VEHICLE_SPRITE_FLAG_CURVED_LIFT_HILL"
]

track_angle_sections = {
    "VEHICLE_SPRITE_FLAG_FLAT": [
        AngleSection(False, 32, 0, 0, 0)
    ],
    "VEHICLE_SPRITE_FLAG_GENTLE_SLOPES": [
        AngleSection(False, 4, 11.1026, 0, 0),
        AngleSection(False, 4, -11.1026, 0, 0),
        AngleSection(False, 32, 22.2052, 0, 0),
        AngleSection(False, 32, -22.2052, 0, 0)
    ],
    "VEHICLE_SPRITE_FLAG_STEEP_SLOPES": [
        AngleSection(False, 8, 40.36, 0, 0),
        AngleSection(False, 8, -40.36, 0, 0),
        AngleSection(False, 32, 58.5148, 0, 0),
        AngleSection(False, 32, -58.5148, 0, 0)
    ],
    "VEHICLE_SPRITE_FLAG_VERTICAL_SLOPES": [
        AngleSection(False, 4, 75, 0, 0),
        AngleSection(False, 4, -75, 0, 0),
        AngleSection(False, 32, 90, 0, 0),
        AngleSection(False, 32, -90, 0, 0),
        AngleSection(False, 4, 105, 0, 0),
        AngleSection(False, 4, -105, 0, 0),
        AngleSection(False, 4, 120, 0, 0),
        AngleSection(False, 4, -120, 0, 0),
        AngleSection(False, 4, 135, 0, 0),
        AngleSection(False, 4, -135, 0, 0),
        AngleSection(False, 4, 150, 0, 0),
        AngleSection(False, 4, -150, 0, 0),
        AngleSection(False, 4, 165, 0, 0),
        AngleSection(False, 4, -165, 0, 0),
        AngleSection(False, 4, 180, 0, 0)
    ],
    "VEHICLE_SPRITE_FLAG_DIAGONAL_SLOPES": [
        AngleSection(True, 4, 8.0503, 0, 0),
        AngleSection(True, 4, -8.0503, 0, 0),
        AngleSection(True, 4, 16.1005, 0, 0),
        AngleSection(True, 4, -16.1005, 0, 0),
        AngleSection(True, 4, 49.1035, 0, 0),
        AngleSection(True, 4, -49.1035, 0, 0)
    ],
    "VEHICLE_SPRITE_FLAG_FLAT_BANKED": [
        AngleSection(False, 8, 0, -22.5, 0),
        AngleSection(False, 8, 0, 22.5, 0),
        AngleSection(False, 32, 0, -45, 0),
        AngleSection(False, 32, 0, 45, 0)
    ],
    "VEHICLE_SPRITE_FLAG_INLINE_TWISTS": [
        AngleSection(False, 4, 0, -15, 0),
        AngleSection(False, 4, 0, 15, 0),
        AngleSection(False, 4, 0, -30, 0),
        AngleSection(False, 4, 0, 30, 0),
        AngleSection(False, 4, 0, -45, 0),
        AngleSection(False, 4, 0, 45, 0),
        AngleSection(False, 4, 0, -60, 0),
        AngleSection(False, 4, 0, 60, 0),
        AngleSection(False, 4, 0, -75, 0),
        AngleSection(False, 4, 0, 75, 0)
    ],
    "VEHICLE_SPRITE_FLAG_FLAT_TO_GENTLE_SLOPE_BANKED_TRANSITIONS": [
        AngleSection(False, 32, 11.1026, -22.5, 0),
        AngleSection(False, 32, 11.1026, 22.5, 0),
        AngleSection(False, 32, -11.1026, -22.5, 0),
        AngleSection(False, 32, -11.1026, 22.5, 0)
    ],
    "VEHICLE_SPRITE_FLAG_DIAGONAL_GENTLE_SLOPE_BANKED_TRANSITIONS": [
        AngleSection(True, 4, 8.0503, -22.5, 0),
        AngleSection(True, 4, 8.0503, 22.5, 0),
        AngleSection(True, 4, -8.0503, -22.5, 0),
        AngleSection(True, 4, -8.0503, 22.5, 0)
    ],
    "VEHICLE_SPRITE_FLAG_GENTLE_SLOPE_BANKED_TRANSITIONS": [
        AngleSection(False, 4, 22.2052, -22.5, 0),
        AngleSection(False, 4, 22.2052, 22.5, 0),
        AngleSection(False, 4, -22.2052, -22.5, 0),
        AngleSection(False, 4, -22.2052, 22.5, 0)
    ],
    "VEHICLE_SPRITE_FLAG_GENTLE_SLOPE_BANKED_TURNS": [
        AngleSection(False, 32, 22.2052, -45, 0),
        AngleSection(False, 32, 22.2052, 45, 0),
        AngleSection(False, 32, -22.2052, -45, 0),
        AngleSection(False, 32, -22.2052, 45, 0)
    ],
    "VEHICLE_SPRITE_FLAG_FLAT_TO_GENTLE_SLOPE_WHILE_BANKED_TRANSITIONS": [
        AngleSection(False, 4, 11.1026, -45, 0),
        AngleSection(False, 4, 11.1026, 45, 0),
        AngleSection(False, 4, -11.1026, -45, 0),
        AngleSection(False, 4, -11.1026, 45, 0)
    ],
    "VEHICLE_SPRITE_FLAG_CORKSCREWS": [
        AngleSection(False, 4, 16.4, -15.8, 2.3),
        AngleSection(False, 4, 43.3, -34.4, 14),
        AngleSection(False, 4, 90, -45, 45),
        AngleSection(False, 4, 136.7, -34.4, 76),
        AngleSection(False, 4, 163.6, -15.8, 87.7),
        AngleSection(False, 4, -16.4, 15.8, 2.3),
        AngleSection(False, 4, -43.3, 34.4, 14),
        AngleSection(False, 4, -90, 45, 45),
        AngleSection(False, 4, -136.7, 34.4, 76),
        AngleSection(False, 4, -163.6, 15.8, 87.7),
        AngleSection(False, 4, 16.4, 15.8, -2.3),
        AngleSection(False, 4, 43.3, 34.4, -14),
        AngleSection(False, 4, 90, 45, -45),
        AngleSection(False, 4, 136.7, 34.4, -76),
        AngleSection(False, 4, 163.6, 15.8, -87.7),
        AngleSection(False, 4, -16.4, -15.8, -2.3),
        AngleSection(False, 4, -43.3, -34.4, -14),
        AngleSection(False, 4, -90, -45, -45),
        AngleSection(False, 4, -136.7, -34.4, -76),
        AngleSection(False, 4, -163.6, -15.8, -87.7)
    ],
    "VEHICLE_SPRITE_FLAG_RESTRAINT_ANIMATION": [
        AngleSection(False, 4, 0, 0, 0)
    ],
    "VEHICLE_SPRITE_FLAG_CURVED_LIFT_HILL": [
        AngleSection(False, 32, 9.8287, 0, 0)
    ]
}
