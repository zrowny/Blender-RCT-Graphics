
# Prerequisites

The following programs are necessary:

- [G'MIC CLI](https://gmic.eu/download.html)
  - On Windows, scroll down to "Command-line interface (CLI)", download and extract that somewhere, and add that to your system's [PATH environmental variable](https://superuser.com/a/284351).
- [Blender 2.79](https://download.blender.org/release/Blender2.79/#:~:text=blender-2.79b,115536799)
  - Download one of the 2.79b releases that's appropriate for your system

# Installing

1. [Download](https://nightly.link/zrowny/Blender-RCT-Graphics/workflows/main/master/rct-graphics-helper.zip) the rct_graphics_helper Add-on and put it somewhere useful.
2. [Install and enable](https://docs.blender.org/manual/en/2.79/preferences/addons.html) RCT Graphics Helper in Blender's Add-ons menu. 

The Render tab should now contain new panels (they appear at the bottom by default, but you can drag them to the top if you'd like).

# Usage

1. In a new or existing file, go to the `RCT General` panel and click `Set Up Rendering Rig`.
3. In the `General` panel and the panel for the object type, configure the properties you want for this object. Each property will have a tooltip when you hover over it that will have more information
  - For supported object types (just small scenery for now), click "Import Existing JSON" to use the properties from an existing JSON object.
4. Create your object, give it materials, etc.
5. Make sure to save your .blend file (preferable in its own folder)!
6. Click `Render [TYPE] Object`. Once it's done rendering, the results will be in the output folder next to the .blend file.

Please check the [guidelines](https://github.com/zrowny/Blender-RCT-Graphics/wiki/Guidelines) for the best results.

## Object Types

Initially, the only OpenRCT2 object type that is properly supported is small scenery, but the `Custom` object type allows you to specify the rendering settings to use manually, so you can accomplish other results.

## Output

After rendering, the output folder will contain a `[objectId].parkobj` file that (if everything is finalized) can be used immediately with OpenRCT2. It is a zip archive of the `object.json` file and the `images` folder.

The `images` folder contain the final images that are included in the `.parkobj` file. They store _only_ the palette indices, and not the palette itself, so they appear as weird and greyscale. (Note that only the New Save Format (NSF) branch of OpenRCT2 currently supports these palette-index images. Until this functionality is added to the main development branch, you can replace them with the images in the `preview` folder if you aren't using the NSF branch).

The `preview` folder contains final rendered images that are colored with the RCT2 palette so that they appear as they would inside the game.

The `object.json` file is the JSON file that describes the created object. See the [OpenGraphics wiki](https://github.com/OpenRCT2/OpenGraphics/wiki/OpenRCT2-JSON-Objects) for more information about the JSON format.

# Links

* The textures distributed with the sample models are licensed under public domain and were taken from: https://opengameart.org/
* [OpenGraphics](https://github.com/OpenRCT2/OpenGraphics) A project to create free replacements for the graphics in open source re-implementation of RollerCoaster Tycoon 2.
