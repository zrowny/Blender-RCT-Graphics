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


def add_general_properties_json(context):
    print("Adding general properties")
    general_properties = context.scene.rct_graphics_helper_general_properties
    general_properties_dict = group_as_dict(general_properties)
    general_properties_dict.pop("name_strings_index", None)
    general_properties_dict.pop("description_strings_index", None)
    general_properties_dict.pop("capacity_strings_index", None)
    general_properties_dict.pop("edge_darkening", None)
    general_properties_dict.pop("dither_threshold", None)
    general_properties_dict.pop("cast_shadows", None)
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
    string_list = []
    strings = string.split(',')  # type: list[str]
    return [s.strip() for s in strings]


def process_strings(string_entries):
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
    with open(get_output_path("object.json"), "w") as offset_file:
        offset_file.write(json.dumps(json_data, indent=4, sort_keys=True))


def JsonImage(path="", x=0, y=0, format="", keepPalette=True):
    image = {
        "path": path,
        "x": x,
        "y": y,
    }
    if format != "":
        image["format"] = format
    if keepPalette:
        image["keepPalette"] = True
    return image


def make_parkobj(context):
    print("Making parkobj file")
    name = context.scene.rct_graphics_helper_general_properties.id
    write_json_file()
    with zipfile.ZipFile(get_output_path("%s.parkobj" % name), 'w') as parkobj:
        json_file_path = get_output_path("object.json")
        if os.path.exists(json_file_path):
            parkobj.write(json_file_path, "object.json")
        else:
            print("WARNING: object.json file not found")
        for image_name in os.listdir(get_output_path("images/")):
            image_path = os.path.join(get_output_path("images/"), image_name)
            parkobj.write(image_path, "images/%s" % image_name)
        

def group_as_dict(group, includeFalse=False):
    """Get values from a property group as a dict."""

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
