'''
Copyright (c) 2021 RCT Graphics Helper developers

For a complete list of all authors, please refer to the addon's meta info.
Interested in contributing? Visit https://github.com/oli414/Blender-RCT-Graphics

RCT Graphics Helper is licensed under the GNU General Public License version 3.
'''

import bpy
import bpy.utils.previews
import math
import os

from . render_task import *
from . import json_functions as json_functions
from bpy.app import driver_namespace


preview_collections = {}  # type: dict[bpy.utils.previews.ImagePreviewCollection]


def removePreviews():
    """Deletes the preview collect and the previews stored in it"""
    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()


def preview_dir_update(context):
    """Updates the previews in the preview collection"""
    enum_items = []
    directory = get_output_path("preview/")

    # Get the preview collection (defined in register func).
    removePreviews()
    pcoll = preview_collections.setdefault("main", bpy.utils.previews.new())

    if os.path.exists(directory):
        # Scan the directory for png files
        image_paths = []
        for fn in os.listdir(directory):
            if fn.lower().endswith(".png"):
                image_paths.append(fn)

        for i, name in enumerate(image_paths):
            # generates a thumbnail preview for a file.
            filepath = os.path.join(directory, name)
            thumb = pcoll.load(filepath, filepath, 'IMAGE')
            enum_items.append((name, name, "", thumb.icon_id, i))

    pcoll.my_previews = enum_items
    return pcoll.my_previews


class RCTRender(object):
    """The base class for rendering RCT objects"""

    _timer = None
    rendering = False
    stop = False
    renderTask = None  # type: RenderTask

    @classmethod
    def poll(cls, context):
        """Returns true if the RCT Rig exists"""
        return bpy.data.objects.get('RCT_Rig') is not None

    def pre(self, dummy):
        """Runs when a blender render starts."""
        self.rendering = True

    def post(self, dummy):
        """Runs when a blender render stops"""
        self.rendering = False

    def cancel(self, dummy):
        """Runs when a blender render is cancelled by the user."""
        self.stop = True

    def execute(self, context):
        """Initiates an RCT render."""
        reset_rig()

        self.rendering = False
        self.stop = False

        if os.path.exists(get_output_path("TMP/")):
            shutil.rmtree(get_output_path("TMP/"))
        if os.path.exists(get_output_path("images/")):
            shutil.rmtree(get_output_path("images/"))
        if os.path.exists(get_output_path("preview/")):
            shutil.rmtree(get_output_path("preview/"))
        context.scene.render.resolution_x = 256
        context.scene.render.resolution_y = 256
        context.scene.render.resolution_percentage = 100
        context.scene.render.alpha_mode = 'TRANSPARENT'
        
        json_functions.add_general_properties_json(context)
        
        handlers = bpy.app.handlers
        handlers.render_pre.clear()
        handlers.render_post.clear()
        handlers.render_cancel.clear()
        handlers.render_pre.append(self.pre)
        handlers.render_post.append(self.post)
        handlers.render_cancel.append(self.cancel)
        self._timer = context.window_manager.event_timer_add(0.25, context.window)
        context.window_manager.modal_handler_add(self)

        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        """Runs every [x] seconds while rendering to start the next render"""
        if event.type == 'TIMER':

            if self.stop or self.renderTask is None or (self.renderTask.status == "FINISHED" and not self.rendering):
                self.finished(context)

                return {"FINISHED"}

            elif not self.rendering:
                # render next frame
                self.renderTask.step()

        return {"PASS_THROUGH"}

    def finished(self, context):
        """Runs when render is finished to reset things and generate parkobj"""
        bpy.app.handlers.render_pre.remove(self.pre)
        bpy.app.handlers.render_post.remove(self.post)
        bpy.app.handlers.render_cancel.remove(self.cancel)
        context.window_manager.event_timer_remove(self._timer)

        # if os.path.exists(get_output_path("TMP/")):
        #     shutil.rmtree(get_output_path("TMP/"))

        preview_dir_update(context)
        json_functions.make_parkobj(context)

        reset_rig()
