import bpy
import os
import math


# =========================================================
# AI BLENDER STUDIO — DAY 11
# REUSABLE INTERIOR FURNITURE ASSET LIBRARY
#
# Creates:
#   1. Bed_Modern
#   2. Wardrobe_Modern
#   3. Desk_Modern
#   4. DiningTable_Modern
#   5. Lamp_Modern
#
# Saves to:
#   assets/interior_assets.blend
# =========================================================


print("")
print("==============================================")
print(" AI BLENDER STUDIO — DAY 11 ASSET LIBRARY")
print("==============================================")
print("")


# =========================================================
# PATHS
# =========================================================

PROJECT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

ASSET_DIR = os.path.join(
    PROJECT_DIR,
    "assets"
)

ASSET_FILE = os.path.join(
    ASSET_DIR,
    "interior_assets.blend"
)

os.makedirs(ASSET_DIR, exist_ok=True)


# =========================================================
# CLEAN CURRENT SCENE
# =========================================================

print("[1/8] Cleaning Blender scene...")

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

# Remove old collections created by this script
COLLECTION_NAMES = [
    "Bed_Modern",
    "Wardrobe_Modern",
    "Desk_Modern",
    "DiningTable_Modern",
    "Lamp_Modern"
]

for collection_name in COLLECTION_NAMES:

    collection = bpy.data.collections.get(collection_name)

    if collection:

        bpy.data.collections.remove(
            collection,
            do_unlink=True
        )


# =========================================================
# MATERIAL SYSTEM
# =========================================================

print("[2/8] Creating materials...")


def create_material(name, color, metallic=0.0, roughness=0.5):

    material = bpy.data.materials.get(name)

    if material is None:

        material = bpy.data.materials.new(name)

        material.use_nodes = True

    nodes = material.node_tree.nodes

    principled = nodes.get("Principled BSDF")

    if principled:

        principled.inputs["Base Color"].default_value = (
            color[0],
            color[1],
            color[2],
            color[3]
        )

        principled.inputs["Roughness"].default_value = roughness

        principled.inputs["Metallic"].default_value = metallic

    return material


# Main materials

MAT_WOOD = create_material(
    "ASSET11_Wood",
    (0.30, 0.14, 0.055, 1.0),
    metallic=0.0,
    roughness=0.42
)

MAT_WOOD_LIGHT = create_material(
    "ASSET11_Wood_Light",
    (0.58, 0.34, 0.15, 1.0),
    metallic=0.0,
    roughness=0.45
)

MAT_FABRIC = create_material(
    "ASSET11_Fabric",
    (0.48, 0.43, 0.36, 1.0),
    metallic=0.0,
    roughness=0.85
)

MAT_FABRIC_LIGHT = create_material(
    "ASSET11_Fabric_Light",
    (0.72, 0.66, 0.56, 1.0),
    metallic=0.0,
    roughness=0.9
)

MAT_WHITE = create_material(
    "ASSET11_White",
    (0.88, 0.88, 0.84, 1.0),
    metallic=0.0,
    roughness=0.65
)

MAT_BLACK = create_material(
    "ASSET11_Black",
    (0.015, 0.015, 0.015, 1.0),
    metallic=0.0,
    roughness=0.3
)

MAT_METAL = create_material(
    "ASSET11_Metal",
    (0.35, 0.37, 0.39, 1.0),
    metallic=0.8,
    roughness=0.25
)

MAT_GLASS = create_material(
    "ASSET11_Glass",
    (0.18, 0.28, 0.34, 1.0),
    metallic=0.0,
    roughness=0.12
)

MAT_LAMP = create_material(
    "ASSET11_Lamp_Shade",
    (0.82, 0.68, 0.42, 1.0),
    metallic=0.0,
    roughness=0.65
)


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def apply_material(obj, material):

    if obj.data and hasattr(obj.data, "materials"):

        obj.data.materials.clear()

        obj.data.materials.append(material)


def create_cube(
    name,
    location,
    scale,
    material,
    collection
):

    bpy.ops.mesh.primitive_cube_add(
        location=location
    )

    obj = bpy.context.object

    obj.name = name

    obj.scale = scale

    bpy.ops.object.transform_apply(
        location=False,
        rotation=False,
        scale=True
    )

    apply_material(
        obj,
        material
    )

    # Move object to asset collection
    for old_collection in list(obj.users_collection):

        old_collection.objects.unlink(obj)

    collection.objects.link(obj)

    return obj


def create_cylinder(
    name,
    location,
    radius,
    depth,
    material,
    collection,
    vertices=32
):

    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices,
        radius=radius,
        depth=depth,
        location=location
    )

    obj = bpy.context.object

    obj.name = name

    apply_material(
        obj,
        material
    )

    for old_collection in list(obj.users_collection):

        old_collection.objects.unlink(obj)

    collection.objects.link(obj)

    return obj


def create_uv_sphere(
    name,
    location,
    scale,
    material,
    collection
):

    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=32,
        ring_count=16,
        location=location
    )

    obj = bpy.context.object

    obj.name = name

    obj.scale = scale

    bpy.ops.object.transform_apply(
        location=False,
        rotation=False,
        scale=True
    )

    apply_material(
        obj,
        material
    )

    for old_collection in list(obj.users_collection):

        old_collection.objects.unlink(obj)

    collection.objects.link(obj)

    return obj


def create_collection(name):

    collection = bpy.data.collections.new(name)

    bpy.context.scene.collection.children.link(
        collection
    )

    return collection


def hide_collection_from_scene(collection):

    # Keep collection available in the blend file
    # but don't display it in the current scene.

    collection.hide_viewport = False
    collection.hide_render = False


def mark_collection_as_asset(
    collection,
    description
):

    try:

        collection.asset_mark()

        if collection.asset_data:

            collection.asset_data.description = description

            collection.asset_data.author = "AI Blender Studio"

            collection.asset_data.copyright = (
                "AI Blender Studio"
            )

    except Exception as error:

        print(
            "Asset marking warning:",
            error
        )


# =========================================================
# 1. BED
# =========================================================

print("[3/8] Creating Bed_Modern...")


def create_bed():

    collection = create_collection(
        "Bed_Modern"
    )

    # Mattress base
    create_cube(
        "Bed_Mattress_Base",
        (0, 0, 0.48),
        (1.35, 1.05, 0.18),
        MAT_FABRIC,
        collection
    )

    # Mattress top
    create_cube(
        "Bed_Mattress_Top",
        (0, 0, 0.70),
        (1.32, 1.02, 0.12),
        MAT_FABRIC_LIGHT,
        collection
    )

    # Headboard
    create_cube(
        "Bed_Headboard",
        (0, 1.00, 1.25),
        (1.45, 0.10, 0.75),
        MAT_WOOD,
        collection
    )

    # Headboard padding
    create_cube(
        "Bed_Headboard_Padding",
        (0, 0.89, 1.30),
        (1.20, 0.06, 0.50),
        MAT_FABRIC,
        collection
    )

    # Left side frame
    create_cube(
        "Bed_Frame_Left",
        (-1.38, 0, 0.35),
        (0.08, 1.10, 0.25),
        MAT_WOOD,
        collection
    )

    # Right side frame
    create_cube(
        "Bed_Frame_Right",
        (1.38, 0, 0.35),
        (0.08, 1.10, 0.25),
        MAT_WOOD,
        collection
    )

    # Front frame
    create_cube(
        "Bed_Frame_Front",
        (0, -1.05, 0.35),
        (1.38, 0.08, 0.25),
        MAT_WOOD,
        collection
    )

    # Pillow 1
    create_cube(
        "Bed_Pillow_Left",
        (-0.62, 0.62, 0.92),
        (0.48, 0.25, 0.10),
        MAT_WHITE,
        collection
    )

    # Pillow 2
    create_cube(
        "Bed_Pillow_Right",
        (0.62, 0.62, 0.92),
        (0.48, 0.25, 0.10),
        MAT_WHITE,
        collection
    )

    mark_collection_as_asset(
        collection,
        "Modern double bed for AI-generated bedroom interiors."
    )

    return collection


bed = create_bed()


# =========================================================
# 2. WARDROBE
# =========================================================

print("[4/8] Creating Wardrobe_Modern...")


def create_wardrobe():

    collection = create_collection(
        "Wardrobe_Modern"
    )

    # Main cabinet
    create_cube(
        "Wardrobe_Main",
        (0, 0, 1.35),
        (1.20, 0.38, 1.35),
        MAT_WOOD,
        collection
    )

    # Left door
    create_cube(
        "Wardrobe_Door_Left",
        (-0.58, -0.41, 1.35),
        (0.56, 0.025, 1.25),
        MAT_WOOD_LIGHT,
        collection
    )

    # Right door
    create_cube(
        "Wardrobe_Door_Right",
        (0.58, -0.41, 1.35),
        (0.56, 0.025, 1.25),
        MAT_WOOD_LIGHT,
        collection
    )

    # Handles
    create_cylinder(
        "Wardrobe_Handle_Left",
        (-0.12, -0.47, 1.35),
        0.025,
        0.25,
        MAT_METAL,
        collection
    )

    handle_left = bpy.context.object
    handle_left.rotation_euler = (
        math.radians(90),
        0,
        0
    )

    create_cylinder(
        "Wardrobe_Handle_Right",
        (0.12, -0.47, 1.35),
        0.025,
        0.25,
        MAT_METAL,
        collection
    )

    handle_right = bpy.context.object
    handle_right.rotation_euler = (
        math.radians(90),
        0,
        0
    )

    # Top trim
    create_cube(
        "Wardrobe_Top_Trim",
        (0, -0.02, 2.75),
        (1.28, 0.43, 0.08),
        MAT_BLACK,
        collection
    )

    mark_collection_as_asset(
        collection,
        "Modern two-door wardrobe for AI-generated bedrooms."
    )

    return collection


wardrobe = create_wardrobe()


# =========================================================
# 3. DESK
# =========================================================

print("[5/8] Creating Desk_Modern...")


def create_desk():

    collection = create_collection(
        "Desk_Modern"
    )

    # Desktop
    create_cube(
        "Desk_Top",
        (0, 0, 1.15),
        (1.25, 0.45, 0.10),
        MAT_WOOD,
        collection
    )

    # Left leg
    create_cube(
        "Desk_Leg_Left",
        (-1.05, 0, 0.55),
        (0.10, 0.38, 0.55),
        MAT_BLACK,
        collection
    )

    # Right leg
    create_cube(
        "Desk_Leg_Right",
        (1.05, 0, 0.55),
        (0.10, 0.38, 0.55),
        MAT_BLACK,
        collection
    )

    # Back support
    create_cube(
        "Desk_Back_Support",
        (0, 0.35, 0.75),
        (1.05, 0.06, 0.12),
        MAT_BLACK,
        collection
    )

    # Drawer cabinet
    create_cube(
        "Desk_Drawer_Cabinet",
        (-0.72, -0.02, 0.62),
        (0.30, 0.35, 0.48),
        MAT_WOOD_LIGHT,
        collection
    )

    # Drawer 1
    create_cube(
        "Desk_Drawer_1",
        (-0.72, -0.39, 0.82),
        (0.23, 0.025, 0.12),
        MAT_BLACK,
        collection
    )

    # Drawer 2
    create_cube(
        "Desk_Drawer_2",
        (-0.72, -0.39, 0.52),
        (0.23, 0.025, 0.12),
        MAT_BLACK,
        collection
    )

    # Monitor stand
    create_cube(
        "Desk_Monitor_Stand",
        (0.30, 0, 1.38),
        (0.08, 0.08, 0.20),
        MAT_BLACK,
        collection
    )

    # Monitor
    create_cube(
        "Desk_Monitor",
        (0.30, 0, 1.72),
        (0.58, 0.035, 0.35),
        MAT_BLACK,
        collection
    )

    # Monitor screen
    create_cube(
        "Desk_Monitor_Screen",
        (0.30, -0.04, 1.72),
        (0.48, 0.015, 0.27),
        MAT_GLASS,
        collection
    )

    mark_collection_as_asset(
        collection,
        "Modern work desk with monitor and drawer storage."
    )

    return collection


desk = create_desk()


# =========================================================
# 4. DINING TABLE
# =========================================================

print("[6/8] Creating DiningTable_Modern...")


def create_dining_table():

    collection = create_collection(
        "DiningTable_Modern"
    )

    # Table top
    create_cube(
        "DiningTable_Top",
        (0, 0, 1.00),
        (1.35, 0.75, 0.10),
        MAT_WOOD,
        collection
    )

    # Legs
    create_cube(
        "DiningTable_Leg_1",
        (-1.05, -0.50, 0.50),
        (0.10, 0.10, 0.50),
        MAT_BLACK,
        collection
    )

    create_cube(
        "DiningTable_Leg_2",
        (1.05, -0.50, 0.50),
        (0.10, 0.10, 0.50),
        MAT_BLACK,
        collection
    )

    create_cube(
        "DiningTable_Leg_3",
        (-1.05, 0.50, 0.50),
        (0.10, 0.10, 0.50),
        MAT_BLACK,
        collection
    )

    create_cube(
        "DiningTable_Leg_4",
        (1.05, 0.50, 0.50),
        (0.10, 0.10, 0.50),
        MAT_BLACK,
        collection
    )

    # Center decorative support
    create_cube(
        "DiningTable_Center_Support",
        (0, 0, 0.48),
        (0.08, 0.08, 0.48),
        MAT_BLACK,
        collection
    )

    mark_collection_as_asset(
        collection,
        "Modern dining table for AI-generated dining rooms."
    )

    return collection


dining_table = create_dining_table()


# =========================================================
# 5. LAMP
# =========================================================

print("[7/8] Creating Lamp_Modern...")


def create_lamp():

    collection = create_collection(
        "Lamp_Modern"
    )

    # Base
    create_cylinder(
        "Lamp_Base",
        (0, 0, 0.08),
        0.25,
        0.16,
        MAT_BLACK,
        collection
    )

    # Pole
    create_cylinder(
        "Lamp_Pole",
        (0, 0, 1.05),
        0.045,
        1.90,
        MAT_METAL,
        collection
    )

    # Shade
    create_cylinder(
        "Lamp_Shade",
        (0, 0, 2.05),
        0.35,
        0.40,
        MAT_LAMP,
        collection
    )

    # Bulb
    create_uv_sphere(
        "Lamp_Bulb",
        (0, 0, 1.88),
        (0.12, 0.12, 0.12),
        MAT_WHITE,
        collection
    )

    # Small decorative ring
    create_cylinder(
        "Lamp_Ring",
        (0, 0, 1.80),
        0.15,
        0.04,
        MAT_METAL,
        collection
    )

    mark_collection_as_asset(
        collection,
        "Modern floor lamp for AI-generated interior scenes."
    )

    return collection


lamp = create_lamp()


# =========================================================
# PREPARE ASSET COLLECTIONS
# =========================================================

print("[8/8] Preparing asset library...")


all_assets = [
    bed,
    wardrobe,
    desk,
    dining_table,
    lamp
]


for collection in all_assets:

    print(
        "Asset:",
        collection.name
    )

    # Ensure collection remains linked
    # to the scene collection.
    if collection.name not in bpy.context.scene.collection.children:

        try:

            bpy.context.scene.collection.children.link(
                collection
            )

        except Exception:
            pass


# =========================================================
# SAVE ASSET LIBRARY
# =========================================================

print("")
print("Saving asset library...")

bpy.ops.wm.save_as_mainfile(
    filepath=ASSET_FILE
)


# =========================================================
# FINAL REPORT
# =========================================================

print("")
print("==============================================")
print("       DAY 11 ASSET LIBRARY COMPLETE")
print("==============================================")

print("")
print("Created assets:")

for collection in all_assets:

    print(
        " -",
        collection.name
    )

print("")
print("Asset library saved:")
print(ASSET_FILE)

print("")
print("==============================================")
print("         READY FOR AI GENERATOR")
print("==============================================")
print("")