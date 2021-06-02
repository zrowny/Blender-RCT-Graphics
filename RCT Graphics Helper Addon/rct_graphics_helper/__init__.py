'''
Copyright (c) 2021 RCT Graphics Helper developers

For a complete list of all authors, please refer to the addon's meta info.
Interested in contributing? Visit https://github.com/oli414/Blender-RCT-Graphics

RCT Graphics Helper is licensed under the GNU General Public License version 3.
'''

bl_info = {
    "name": "RCT Graphics Helper",
    "description": "Render tools to replicate RCT graphics",
    "author": "Olivier Wervers, Zrowny",
    "version": (0, 0, 2),
    "blender": (2, 79, 0),
    "location": "Render",
    "support": "COMMUNITY",
    "category": "Render"}


import bpy


# load and reload submodules
##################################

import importlib
from . import developer_utils
importlib.reload(developer_utils)
modules = developer_utils.setup_addon_modules(__path__, __name__, "bpy" in locals())


# register
##################################

from . general_panel import register_general_panel, unregister_general_panel
from . custom_panel import register_custom_panel, unregister_custom_panel
from . small_scenery_panel import register_small_scenery_panel, unregister_small_scenery_panel
from . vehicles_panel import register_vehicles_panel, unregister_vehicles_panel

import traceback


def register():
    try:
        bpy.utils.register_module(__name__)
    except:
        traceback.print_exc()

    register_general_panel()
    register_custom_panel()
    register_small_scenery_panel()
    register_vehicles_panel()

    print("Registered {} with {} modules".format(bl_info["name"], len(modules)))


def unregister():
    try:
        bpy.utils.unregister_module(__name__)
    except:
        traceback.print_exc()

    unregister_general_panel()
    unregister_custom_panel()
    unregister_small_scenery_panel()
    unregister_vehicles_panel()

    print("Unregistered {}".format(bl_info["name"]))
