
import bpy
import json
import os
import math
from mathutils import Vector

print("=" * 50)
print("DAY 20 - JSON TO BLENDER SCENE")
print("=" * 50)


# =========================================================
# 1. PROJECT PATHS
# =========================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Support both a script in the project root and one in a
# subfolder such as scripts/.
if os.path.isfile(os.path.join(SCRIPT_DIR, "scene.json")):
    PROJECT_DIR = SCRIPT_DIR
else:
    PROJECT_DIR = os.path.abspath(
        os.path.join(SCRIPT_DIR, "..")
    )


GENERATED_JSON_PATH = os.path.join(PROJECT_DIR, "scene_generated.json")
DEFAULT_JSON_PATH = os.path.join(PROJECT_DIR, "scene.json")

JSON_PATH = (
    GENERATED_JSON_PATH
    if os.path.isfile(GENERATED_JSON_PATH)
    else DEFAULT_JSON_PATH
)

ASSET_LIBRARY = os.path.join(
    PROJECT_DIR, "assets", "interior_assets.blend"
)

OUTPUT_DIR = os.path.join(PROJECT_DIR, "projects")
RENDER_DIR = os.path.join(PROJECT_DIR, "renders")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(RENDER_DIR, exist_ok=True)

BLEND_PATH = os.path.join(
    OUTPUT_DIR, "day20_image_scene.blend"
)

RENDER_PATH = os.path.join(
    RENDER_DIR, "day20_image_scene.png"
)


# =========================================================
# 2. LOAD AND VALIDATE JSON
# =========================================================

print("\nLoading scene.json...")

if not os.path.isfile(JSON_PATH):
    raise FileNotFoundError(
        f"scene.json was not found at: {JSON_PATH}"
    )

with open(JSON_PATH, "r", encoding="utf-8") as file:
    scene_data = json.load(file)

if not isinstance(scene_data, dict):
    raise ValueError("scene.json must contain a JSON object.")

room = scene_data.get("room")
assets = scene_data.get("assets")
camera_config = scene_data.get("camera", {})

if not isinstance(room, dict):
    raise ValueError("Missing or invalid 'room' object.")

for dimension in ("width", "length", "height"):
    value = room.get(dimension)

    if not isinstance(value, (int, float)) or value <= 0:
        raise ValueError(
            f"room.{dimension} must be a positive number."
        )

if not isinstance(assets, list):
    raise ValueError("'assets' must be a list.")

materials_config = scene_data.get("materials", {})
if not isinstance(materials_config, dict):
    raise ValueError("'materials' must be an object.")
# Default furniture colours (hex format)
default_materials = {
    "sofa": "#858585",
    "chair": "#B0A090",
    "wood": "#795548",
    "wood_dark": "#4E342E",
}

for name, color in default_materials.items():
    materials_config.setdefault(name, color)

if not isinstance(materials_config, dict):
    raise ValueError("'materials' must be an object.")

WIDTH = float(room["width"])
LENGTH = float(room["length"])
HEIGHT = float(room["height"])

print("JSON validation passed.")
print(f"Room: {WIDTH} x {LENGTH} x {HEIGHT} metres")
print(f"Furniture assets: {len(assets)}")


# =========================================================
# 3. MATERIAL HELPERS
# =========================================================

def hex_to_rgba(hex_color):
    """Convert #RRGGBB or #RRGGBBAA into RGBA values."""

    if not isinstance(hex_color, str):
        raise ValueError("Material color must be a hex string.")

    color = hex_color.strip().lstrip("#")

    if len(color) not in (6, 8):
        raise ValueError(
            f"Invalid hex color: {hex_color}"
        )

    try:
        values = [
            int(color[i:i + 2], 16) / 255.0
            for i in range(0, len(color), 2)
        ]
    except ValueError as exc:
        raise ValueError(
            f"Invalid hex color: {hex_color}"
        ) from exc

    if len(values) == 3:
        values.append(1.0)

    return tuple(values)


def get_material(material_name, default_color):
    """Create or update a Principled BSDF material."""

    color = materials_config.get(
        material_name, default_color
    )

    rgba = hex_to_rgba(color)
    material = bpy.data.materials.get(
        f"AI_{material_name}"
    )

    if material is None:
        material = bpy.data.materials.new(
            name=f"AI_{material_name}"
        )

    material.diffuse_color = rgba
    material.use_nodes = True

    principled = next(
        (
            node
            for node in material.node_tree.nodes
            if node.type == "BSDF_PRINCIPLED"
        ),
        None
    )

    if principled:
        principled.inputs["Base Color"].default_value = rgba

        if material_name == "floor":
            principled.inputs["Roughness"].default_value = 0.65
        else:
            principled.inputs["Roughness"].default_value = 0.8

    return material


def assign_material(obj, material):
    """Apply one material to every mesh material slot."""

    if obj.type != "MESH":
        return

    obj.data.materials.clear()
    obj.data.materials.append(material)


def apply_material_to_collection(collection, material):
    """Apply a selected material to mesh objects in an asset."""

    for obj in collection.all_objects:
        assign_material(obj, material)


# =========================================================
# 4. CLEAR PREVIOUS SCENE
# =========================================================

print("\nClearing current scene...")

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

# Remove old child-collection links to avoid accumulating
# duplicate collections on repeated runs.
for child in list(bpy.context.scene.collection.children):
    bpy.context.scene.collection.children.unlink(child)


# =========================================================
# 5. CREATE ROOM
# =========================================================

print("\nCreating room geometry...")


# =========================================================
# 5. CREATE ROOM - OPEN FRONT INTERIOR
# =========================================================

print("\nCreating room geometry...")


def create_box(name, location, scale, material=None):
    bpy.ops.mesh.primitive_cube_add(location=location)

    obj = bpy.context.object
    obj.name = name
    obj.dimensions = (
        scale[0] * 2,
        scale[1] * 2,
        scale[2] * 2
    )

    bpy.ops.object.transform_apply(
        location=False,
        rotation=False,
        scale=True
    )

    if material:
        assign_material(obj, material)

    return obj


wall_material = get_material("wall", "#E8DED0")
floor_material = get_material("floor", "#8B5E3C")
ceiling_material = get_material("ceiling", "#F5F5F5")

# Floor: top surface at Z = 0
create_box(
    "Floor",
    (0, 0, -0.075),
    (WIDTH / 2, LENGTH / 2, 0.075),
    floor_material
)

# Back wall
create_box(
    "Wall_Back",
    (0, LENGTH / 2, HEIGHT / 2),
    (WIDTH / 2, 0.075, HEIGHT / 2),
    wall_material
)

# Left wall
create_box(
    "Wall_Left",
    (-WIDTH / 2, 0, HEIGHT / 2),
    (0.075, LENGTH / 2, HEIGHT / 2),
    wall_material
)

# Right wall
create_box(
    "Wall_Right",
    (WIDTH / 2, 0, HEIGHT / 2),
    (0.075, LENGTH / 2, HEIGHT / 2),
    wall_material
)

# Ceiling retained in the scene but hidden in the render
create_box(
    "Ceiling",
    (0, 0, HEIGHT + 0.075),
    (WIDTH / 2, LENGTH / 2, 0.075),
    ceiling_material
)

ceiling_object = bpy.data.objects.get("Ceiling")

if ceiling_object:
    ceiling_object.hide_render = True
    ceiling_object.hide_set(True)

print("Room created: floor, back wall, two side walls.")



# =========================================================
# 6. LOAD FURNITURE COLLECTIONS
# =========================================================

def append_collection(collection_name):
    """
    Load a furniture collection from interior_assets.blend.
    The collection is used as an instance so its objects
    retain their internal hierarchy.
    """

    print(f"\nLoading furniture: {collection_name}")

    if not os.path.isfile(ASSET_LIBRARY):
        raise FileNotFoundError(
            f"Asset library not found: {ASSET_LIBRARY}"
        )

    with bpy.data.libraries.load(
        ASSET_LIBRARY,
        link=False
    ) as (data_from, data_to):

        if collection_name not in data_from.collections:
            available = ", ".join(data_from.collections)

            raise ValueError(
                f"Collection '{collection_name}' was not found. "
                f"Available collections: {available}"
            )

        data_to.collections = [collection_name]

    if not data_to.collections or data_to.collections[0] is None:
        raise RuntimeError(
            f"Failed to load collection: {collection_name}"
        )

    collection = data_to.collections[0]

    print(f"Loaded collection: {collection_name}")

    return collection


def vector3(value, field_name):
    """Validate a three-number vector."""

    if (
        not isinstance(value, (list, tuple))
        or len(value) != 3
        or not all(
            isinstance(n, (int, float)) for n in value
        )
    ):
        raise ValueError(
            f"{field_name} must contain three numbers."
        )

    return [float(n) for n in value]


def add_asset_instance(asset_data):
    """Create a positioned collection instance from JSON."""

    asset_name = asset_data.get("asset")

    if not isinstance(asset_name, str) or not asset_name.strip():
        raise ValueError(
            "Each asset needs a non-empty 'asset' collection name."
        )

    position = vector3(
        asset_data.get("position", [0, 0, 0]),
        f"{asset_name}.position"
    )

    rotation = vector3(
        asset_data.get("rotation", [0, 0, 0]),
        f"{asset_name}.rotation"
    )

    scale = vector3(
        asset_data.get("scale", [1, 1, 1]),
        f"{asset_name}.scale"
    )

    if any(abs(value) < 0.000001 for value in scale):
        raise ValueError(
            f"{asset_name}.scale cannot contain zero."
        )

    collection = append_collection(asset_name)

    # Optional material override, for example "sofa" or "wood".
    material_key = asset_data.get("material")

    if not material_key:
        if "Sofa" in asset_name:
            material_key = "sofa"
        elif "Chair" in asset_name:
            material_key = "chair"
        elif "TVUnit" in asset_name:
            material_key = "wood_dark"
        elif "CoffeeTable" in asset_name:
            material_key = "wood"

    if material_key:
        if material_key not in materials_config:
            raise ValueError(
                f"Material '{material_key}' for {asset_name} "
                "is missing from scene.json materials."
            )

        material = get_material(
            material_key,
            materials_config[material_key]
        )

        apply_material_to_collection(
            collection, material
        )

    # Use an Empty to transform the whole collection together.
    instance = bpy.data.objects.new(
        f"Instance_{asset_name}",
        None
    )

    instance.empty_display_type = "PLAIN_AXES"
    instance.instance_type = "COLLECTION"
    instance.instance_collection = collection

    bpy.context.scene.collection.objects.link(instance)

    instance.location = position

    instance.rotation_euler = (
        math.radians(rotation[0]),
        math.radians(rotation[1]),
        math.radians(rotation[2])
    )

    instance.scale = scale

    print(
        f"Placed {asset_name} at {position}, "
        f"rotation {rotation}, scale {scale}"
    )


print("\nAdding furniture from scene.json...")

for asset_data in assets:
    if not isinstance(asset_data, dict):
        raise ValueError(
            "Every item in 'assets' must be a JSON object."
        )

    add_asset_instance(asset_data)


# =========================================================
# 7. LIGHTING
# =========================================================

print("\nCreating lighting...")


def create_area_light(name, location, energy, size):
    light_data = bpy.data.lights.new(
        name=name,
        type="AREA"
    )

    light_data.energy = energy
    light_data.shape = "DISK"
    light_data.size = size

    light_obj = bpy.data.objects.new(
        name, light_data
    )

    bpy.context.scene.collection.objects.link(light_obj)
    light_obj.location = location

    return light_obj


lighting_config = scene_data.get("lighting", {})
brightness = float(
    lighting_config.get("brightness", 1.0)
)

if brightness < 0:
    raise ValueError(
        "lighting.brightness cannot be negative."
    )

create_area_light(
    "Key_Light",
    (0, -1, HEIGHT - 0.3),
    900 * brightness,
    3
)

create_area_light(
    "Fill_Light",
    (-WIDTH * 0.4, 0, HEIGHT * 0.7),
    500 * brightness,
    2
)

create_area_light(
    "Ceiling_Light",
    (0, 0, HEIGHT - 0.2),
    700 * brightness,
    2
)

# =========================================================
# CAMERA-FRIENDLY FRONT WALL VISIBILITY
# =========================================================

front_wall = bpy.data.objects.get("Wall_Front")

if front_wall is not None:
    front_wall.hide_render = True
    print("Front wall hidden for a clear interior render.")
else:
    print("Wall_Front not found; no wall was hidden.")

# =========================================================
# 8. CAMERA
# =========================================================

print("\nCreating camera...")

camera_position = vector3(
    camera_config.get(
        "position",
        [WIDTH * 1.05, -LENGTH * 1.05, HEIGHT * 0.85]
    ),
    "camera.position"
)

camera_target = vector3(
    camera_config.get(
        "target",
        [0, 0, HEIGHT * 0.35]
    ),
    "camera.target"
)

camera_data = bpy.data.cameras.new("AI_Camera")
camera = bpy.data.objects.new("AI_Camera", camera_data)

bpy.context.scene.collection.objects.link(camera)

camera.location = camera_position

direction = Vector(camera_target) - camera.location

if direction.length < 0.000001:
    raise ValueError(
        "Camera position and target cannot be identical."
    )

camera.rotation_euler = direction.to_track_quat(
    "-Z", "Y"
).to_euler()


camera_data.lens = float(camera_config.get("lens", 28))
camera_data.clip_start = 0.05
camera_data.clip_end = 200.0
bpy.context.scene.camera = camera

# --- Interior camera and render improvements ---
scene = bpy.context.scene

# Hide ceiling from the final render
ceiling = bpy.data.objects.get("Ceiling")
if ceiling:
    ceiling.hide_render = True

# Hide the front wall if it exists
front_wall = bpy.data.objects.get("Wall_Front")
if front_wall:
    front_wall.hide_render = True

# Wider camera view
camera_data.lens = 24

# Render settings
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1200
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.render.filepath = RENDER_PATH

# Save the Blender scene and generate PNG
bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
bpy.ops.render.render(write_still=True)

print("PNG generated:", RENDER_PATH)


# =========================================================
# 9. RENDER SETTINGS
# =========================================================

scene = bpy.context.scene

# Blender 4.2+ and Blender 5.x use EEVEE Next.

# Select a render engine supported by this Blender build.
available_engines = {
    item.identifier
    for item in scene.bl_rna.properties["render"].fixed_type.properties[
        "engine"
    ].enum_items
}

if "BLENDER_EEVEE_NEXT" in available_engines:
    scene.render.engine = "BLENDER_EEVEE_NEXT"
elif "BLENDER_EEVEE" in available_engines:
    scene.render.engine = "BLENDER_EEVEE"
elif "CYCLES" in available_engines:
    scene.render.engine = "CYCLES"
else:
    raise RuntimeError(
        f"No supported render engine found: {available_engines}"
    )

print("Selected render engine:", scene.render.engine)
# Keep the render settings predictable.
scene.render.film_transparent = False
scene.view_settings.exposure = -0.7


scene.render.resolution_x = 800
scene.render.resolution_y = 600
scene.render.resolution_percentage = 100

scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.render.filepath = RENDER_PATH

print("Render output:", scene.render.filepath)
# =========================================================
# 10. WORLD BACKGROUND
# =========================================================

world = scene.world

if world is None:
    world = bpy.data.worlds.new("AI_World")
    scene.world = world

world.use_nodes = True

background = world.node_tree.nodes.get("Background")

if background:
    background.inputs["Color"].default_value = (
        0.08, 0.08, 0.08, 1.0
    )
    background.inputs["Strength"].default_value = 0.3


# =========================================================
# 11. SAVE BLEND FILE
# =========================================================

print("\nSaving Blender project...")

bpy.ops.wm.save_as_mainfile(
    filepath=BLEND_PATH
)

print(f"Saved Blender project: {BLEND_PATH}")


# =========================================================
# 12. RENDER IMAGE
# =========================================================

print("\nRendering interior scene...")

bpy.ops.render.render(write_still=True)

print("\n" + "=" * 50)
print("DAY 20 SCENE GENERATION COMPLETE")
print("=" * 50)
print(f"Blender file: {BLEND_PATH}")
print(f"Rendered image: {RENDER_PATH}")