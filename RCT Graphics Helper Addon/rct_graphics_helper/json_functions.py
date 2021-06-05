'''
Copyright (c) 2021 RCT Graphics Helper developers

For a complete list of all authors, please refer to the addon's meta info.
Interested in contributing? Visit https://github.com/oli414/Blender-RCT-Graphics

RCT Graphics Helper is licensed under the GNU General Public License version 3.
'''

import bpy.types
from collections import namedtuple
from . render_task import *
import json
import zipfile
import os


json_data = {}
"""Contains the JSON data for this object."""


def add_general_properties_json(context):
    """Processes the general object data and adds it to the global JSON data"""
    print("Adding general properties")
    general_properties = context.scene.rct_graphics_helper_general_properties
    general_properties_dict = group_as_dict(general_properties)
    general_properties_dict.pop("name_strings_index", None)
    general_properties_dict.pop("description_strings_index", None)
    general_properties_dict.pop("capacity_strings_index", None)
    general_properties_dict.pop("edge_darkening", None)
    general_properties_dict.pop("dither_threshold", None)
    general_properties_dict.pop("cast_shadows", None)
    objectType = general_properties_dict.get("objectType", None)
    if objectType in ("stall", "flat_ride", "vehicle"):
        general_properties_dict["objectType"] = "ride"
    originalId = general_properties_dict.pop("originalId", "")
    if originalId != "":
        general_properties_dict["originalId"] = originalId
    strings = {}
    name_strings = general_properties_dict.pop("name_strings", None)
    if name_strings is not None:
        strings["name"] = process_strings(name_strings)
    description_strings = general_properties_dict.pop("description_strings", None)
    if description_strings is not None:
        strings["description"] = process_strings(description_strings)
    capacity_strings = general_properties_dict.pop("capacity_strings", None)
    if capacity_strings is not None:
        strings["capacity"] = process_strings(capacity_strings)
    if strings:
        general_properties_dict["strings"] = strings
    authors = general_properties_dict.get("authors", None)
    if authors is not None:
        general_properties_dict["authors"] = process_string_to_list(authors)
    sourceGame = general_properties_dict.get("sourceGame", None)
    if sourceGame is not None:
        general_properties_dict["sourceGame"] = process_string_to_list(sourceGame)
    json_data.update(general_properties_dict)


def process_string_to_list(string):
    """Converts a string with comma separated items into a list

    Args:
        string (str): A string with items separated by commas

    Returns:
        list[str]: A list of the items in `string`, with surrounding whitespace
            removed
    """
    string_list = []
    strings = string.split(',')  # type: list[str]
    return [s.strip() for s in strings]


def process_strings(string_entries):
    """Converts a list of string entries into a string dictionary

    Args:
        string_entries (list[dict]): A list of string entry dicts:
            language (str): The language code for this string entry
            value (str): The actual string

    Returns:
        dict: A dictionary of entries for this string type, where each
            key is the language code for the entry.
    """
    strings = {}
    for entry in string_entries:
        if "value" in entry.keys():
            language = entry.get("language", None)
            if language is None:
                language = "en-GB"
            value = entry.get("value", None)
            if value:
                strings[language] = value
    return strings


def write_json_file():
    """Converts the object info to JSON format and writes the JSON file."""
    with open(get_output_path("object.json"), "w") as offset_file:
        offset_file.write(json.dumps(json_data, indent=4, sort_keys=True))


def JsonImage(path="", x=0, y=0, format="", keepPalette=True):
    """Returns a dict of the given JSON image information

    Args:
        path (str, optional): The relative path of the image. Usually
            something like "[index].png".
        x (int, optional): The x-offset of the image. Defaults to 0.
        y (int, optional): The y-offset of the image. Defaults to 0.
        format (str, optional): If set to "raw", image will not be run-length
            encoded when loaded by OpenRCT2. Defaults to "".
        keepPalette (bool, optional): Tells OpenRCT2 that this image is already
            correctly paletted. Defaults to True. There shouldn't be any reason
            to change this.
    """
    image = {
        "path": path,
        "x": int(x),
        "y": int(y),
    }
    if format != "":
        image["format"] = format
    if keepPalette:
        image["palette"] = "keep"
    return image


def make_parkobj(context):
    """Creates a .parkobj file from the created images and json"""
    print("Making parkobj file")
    name = context.scene.rct_graphics_helper_general_properties.id
    write_json_file()
    with zipfile.ZipFile(get_output_path("%s.parkobj" % name), 'w') as parkobj:
        json_file_path = get_output_path("object.json")
        if os.path.exists(json_file_path):
            parkobj.write(json_file_path, "object.json")
        else:
            print("WARNING: object.json file not found when writing .parkobj")
        images_path = get_output_path("images/")
        if os.path.exists(images_path):
            for image_name in os.listdir(images_path):
                image_path = os.path.join(images_path, image_name)
                parkobj.write(image_path, "images/%s" % image_name)
        else:
            print("WARNING: Images not found when writing .parkobj")
        

def group_as_dict(group, includeFalse=False):
    """Get values from a bpy property group as a dict."""

    EXCLUDE = {'rna_type', 'name'}
    prop_dict = {}
    props = group.bl_rna.properties

    for key in props.keys():
        
        # Avoid properties we don't want
        if key in EXCLUDE:
            continue

        prop_type = type(props.get(key))

        # Pointers to other property groups
        if prop_type == bpy.types.PointerProperty:
            prop_dict[key] = getattr(group, key)

        # Store collection properties as lists
        elif prop_type == bpy.types.CollectionProperty:
            prop_dict[key] = [group_as_dict(i) for i in getattr(group, key)]

        # Get everything else as a value
        else:
            prop = getattr(group, key)
            if includeFalse or prop is not False:
                prop_dict[key] = prop

    return prop_dict
