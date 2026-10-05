import bpy
import json
import os
import math
from mathutils import Vector

print("================================")
print("DAY 9 - JSON TO REAL ASSETS")
print("================================")


# =========================================================
# PATHS
# =========================================================

PROJECT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

JSON_PATH = os.path.join(
    PROJECT_DIR,
    "scene.json"
)

ASSET_LIBRARY = os.path.join(
    PROJECT_DIR,
    "assets",
    "interior_assets.blend"
)

OUTPUT_DIR = os.path.join(
    PROJECT_DIR,
    "projects"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)


# =========================================================
# LOAD JSON
# =========================================================

print("Loading scene.json...")

with open(JSON_PATH, "r", encoding="utf-8") as file:
    scene_data = json.load(file)

print("JSON loaded successfully")


# =========================================================
# CLEAR SCENE
# =========================================================

print("Clearing scene...")

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)


# =========================================================
# ROOM
# =========================================================

room = scene_data["room"]

WIDTH = room["width"]
LENGTH = room["length"]
HEIGHT = room["height"]


def create_box(name, location, scale):

    bpy.ops.mesh.primitive_cube_add(
        location=location
    )

    obj = bpy.context.object
    obj.name = name
    obj.scale = scale

    return obj


print("Creating room...")


# Floor
create_box(
    "Floor",
    (0, 0, -0.075),
    (WIDTH / 2, LENGTH / 2, 0.075)
)


# Back wall
create_box(
    "Wall_Back",
    (0, LENGTH / 2, HEIGHT / 2),
    (WIDTH / 2, 0.075, HEIGHT / 2)
)


# Left wall
create_box(
    "Wall_Left",
    (-WIDTH / 2, 0, HEIGHT / 2),
    (0.075, LENGTH / 2, HEIGHT / 2)
)


# Right wall
create_box(
    "Wall_Right",
    (WIDTH / 2, 0, HEIGHT / 2),
    (0.075, LENGTH / 2, HEIGHT / 2)
)


# Ceiling
create_box(
    "Ceiling",
    (0, 0, HEIGHT),
    (WIDTH / 2, LENGTH / 2, 0.075)
)


# =========================================================
# LOAD COLLECTION FROM ASSET LIBRARY
# =========================================================

def append_collection(collection_name):

    print("--------------------------------")
    print("Loading asset:", collection_name)
    print("--------------------------------")

    if not os.path.exists(ASSET_LIBRARY):

        print("ERROR: Asset library not found:")
        print(ASSET_LIBRARY)

        return None


    with bpy.data.libraries.load(
        ASSET_LIBRARY,
        link=False
    ) as (data_from, data_to):

        if collection_name in data_from.collections:

            data_to.collections = [collection_name]

        else:

            print(
                "ERROR: Collection not found:",
                collection_name
            )

            print("Available collections:")

            for name in data_from.collections:
                print(" -", name)

            return None


    if not data_to.collections:

        print(
            "ERROR: Failed to load:",
            collection_name
        )

        return None


    collection = data_to.collections[0]


    # Link collection to current scene
    bpy.context.scene.collection.children.link(
        collection
    )


    print(
        "Asset loaded:",
        collection_name
    )

    return collection


# =========================================================
# MOVE COLLECTION OBJECTS
# =========================================================

def position_collection(
    collection,
    position,
    rotation,
    scale
):

    if collection is None:
        return


    for obj in collection.objects:

        obj.location.x += position[0]
        obj.location.y += position[1]
        obj.location.z += position[2]

        obj.rotation_euler.x += math.radians(
            rotation[0]
        )

        obj.rotation_euler.y += math.radians(
            rotation[1]
        )

        obj.rotation_euler.z += math.radians(
            rotation[2]
        )

        obj.scale.x *= scale[0]
        obj.scale.y *= scale[1]
        obj.scale.z *= scale[2]


# =========================================================
# ADD ASSETS FROM JSON
# =========================================================

print("================================")
print("ADDING JSON ASSETS")
print("================================")


for asset in scene_data["assets"]:

    asset_name = asset["asset"]

    position = asset.get(
        "position",
        [0, 0, 0]
    )

    rotation = asset.get(
        "rotation",
        [0, 0, 0]
    )

    scale = asset.get(
        "scale",
        [1, 1, 1]
    )


    collection = append_collection(
        asset_name
    )


    position_collection(
        collection,
        position,
        rotation,
        scale
    )


# =========================================================
# LIGHTING
# =========================================================

print("Creating lighting...")


def create_area_light(
    name,
    location,
    energy,
    size
):

    data = bpy.data.lights.new(
        name=name,
        type="AREA"
    )

    data.energy = energy
    data.shape = "DISK"
    data.size = size


    obj = bpy.data.objects.new(
        name,
        data
    )

    bpy.context.collection.objects.link(obj)

    obj.location = location

    return obj


create_area_light(
    "Key_Light",
    (0, -1, HEIGHT - 0.3),
    900,
    3
)


create_area_light(
    "Fill_Light",
    (-3, 1, 2.2),
    500,
    2
)


create_area_light(
    "Ceiling_Light",
    (0, 0, HEIGHT - 0.2),
    700,
    2
)


# =========================================================
# CAMERA
# =========================================================

print("Creating camera...")


camera_data = bpy.data.cameras.new(
    "AI_Camera"
)

camera = bpy.data.objects.new(
    "AI_Camera",
    camera_data
)

bpy.context.collection.objects.link(
    camera
)


camera.location = (
    scene_data["camera"]["position"][0],
    scene_data["camera"]["position"][1],
    scene_data["camera"]["position"][2]
)


target = scene_data["camera"]["target"]


direction = (
    Vector(target)
    - camera.location
)


camera.rotation_euler = (
    direction.to_track_quat(
        "-Z",
        "Y"
    ).to_euler()
)


camera_data.lens = 24


bpy.context.scene.camera = camera


# =========================================================
# RENDER SETTINGS
# =========================================================

scene = bpy.context.scene

scene.render.engine = "BLENDER_EEVEE"

scene.render.resolution_x = 800
scene.render.resolution_y = 600
scene.render.resolution_percentage = 100

scene.render.image_settings.file_format = "PNG"


# =========================================================
# WORLD
# =========================================================

world = scene.world

if world is None:

    world = bpy.data.worlds.new(
        "World"
    )

    scene.world = world


world.use_nodes = True


background = world.node_tree.nodes.get(
    "Background"
)


if background:

    background.inputs["Color"].default_value = (
        0.04,
        0.04,
        0.04,
        1
    )

    background.inputs["Strength"].default_value = 0.3


# =========================================================
# SAVE
# =========================================================

blend_path = os.path.join(
    OUTPUT_DIR,
    "day9_real_assets.blend"
)


bpy.ops.wm.save_as_mainfile(
    filepath=blend_path
)


# =========================================================
# RENDER
# =========================================================

render_path = os.path.join(
    PROJECT_DIR,
    "renders",
    "day9_real_assets.png"
)


os.makedirs(
    os.path.dirname(render_path),
    exist_ok=True
)


scene.render.filepath = render_path


print("Rendering...")

bpy.ops.render.render(
    write_still=True
)


print("================================")
print("DAY 9 PART 2 COMPLETE")
print("================================")

print("Blend:")
print(blend_path)

print("Render:")
print(render_path)