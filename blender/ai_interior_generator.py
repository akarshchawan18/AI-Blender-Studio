import bpy
import json
import os
import math

from mathutils import Vector, Matrix


print("==========================================")
print("      AI INTERIOR DESIGN GENERATOR")
print("==========================================")


# =========================================================
# PATHS
# =========================================================

PROJECT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

JSON_PATH = os.path.abspath(
    os.environ.get(
        "AI_STUDIO_SCENE_FILE",
        os.path.join(PROJECT_DIR, "scene_generated.json")
    )
)

# Known-good master asset library
ASSET_LIBRARY = os.path.join(
    PROJECT_DIR,
    "assets",
    "interior_assets.blend"
)

PROJECTS_DIR = os.path.join(
    PROJECT_DIR,
    "projects"
)

RENDERS_DIR = os.path.join(
    PROJECT_DIR,
    "renders"
)

os.makedirs(PROJECTS_DIR, exist_ok=True)
os.makedirs(RENDERS_DIR, exist_ok=True)


# =========================================================
# CHECK REQUIRED FILES
# =========================================================

print("")
print("[1/9] Checking input files...")

if not os.path.exists(JSON_PATH):
    raise FileNotFoundError(
        "scene_generated.json not found:\n"
        + JSON_PATH
    )

if not os.path.exists(ASSET_LIBRARY):
    raise FileNotFoundError(
        "Asset library not found:\n"
        + ASSET_LIBRARY
    )

print("Scene JSON found:")
print(JSON_PATH)

print("Master asset library found:")
print(ASSET_LIBRARY)


# =========================================================
# LOAD JSON
# =========================================================

print("")
print("[2/9] Loading scene_generated.json...")

with open(
    JSON_PATH,
    "r",
    encoding="utf-8"
) as file:

    scene_data = json.load(file)

print("JSON loaded successfully.")
# =========================================================
# DOMINANT COLOR PALETTE DIAGNOSTIC (READ-ONLY)
# =========================================================

materials_data = scene_data.get("materials", {})
dominant_colors = materials_data.get("dominant_colors", [])

print("\n[IMAGE COLOR PALETTE]")
if dominant_colors:
    for color in dominant_colors:
        print(
            "Name:", color.get("name", "unknown"),
            "| Percentage:", color.get("percentage", "unknown"),
            "| HEX:", color.get("hex", "missing")
        )
else:
    print("No dominant color palette found in scene JSON.")

# =========================================================
# VALIDATE JSON
# =========================================================

print("")
print("[3/9] Validating scene...")

required_sections = [
    "room",
    "assets",
    "lighting",
    "camera"
]

for section in required_sections:

    if section not in scene_data:

        raise ValueError(
            "Missing JSON section: "
            + section
        )


room = scene_data["room"]

WIDTH = float(room["width"])
LENGTH = float(room["length"])
HEIGHT = float(room["height"])


print("Room:")
print(" Width :", WIDTH)
print(" Length:", LENGTH)
print(" Height:", HEIGHT)

print("Prompt:")
print(
    scene_data.get(
        "prompt",
        "No prompt supplied"
    )
)


# =========================================================
# CLEAR OLD SCENE
# =========================================================

print("")
print("[4/9] Clearing old scene...")

bpy.ops.object.select_all(
    action="SELECT"
)

bpy.ops.object.delete(
    use_global=False
)


# Remove old collections except main collection
for collection in list(bpy.data.collections):

    if collection.name != "Collection":

        try:

            bpy.data.collections.remove(
                collection,
                do_unlink=True
            )

        except Exception:

            pass


print("Scene cleared.")


# =========================================================
# MATERIAL SYSTEM
# =========================================================

print("")
print("[5/9] Creating materials...")


def hex_to_rgba(hex_color):

    hex_color = str(
        hex_color
    ).replace(
        "#",
        ""
    )

    if len(hex_color) != 6:

        raise ValueError(
            "Invalid HEX color: "
            + hex_color
        )

    r = int(
        hex_color[0:2],
        16
    ) / 255.0

    g = int(
        hex_color[2:4],
        16
    ) / 255.0

    b = int(
        hex_color[4:6],
        16
    ) / 255.0

    return (
        r,
        g,
        b,
        1.0
    )


def create_material(
    name,
    hex_color,
    roughness=0.5,
    metallic=0.0
):
    material = bpy.data.materials.get(name)

    if material is None:
        material = bpy.data.materials.new(name=name)

    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    principled = nodes.get("Principled BSDF")

    if principled:
        principled.inputs["Base Color"].default_value = hex_to_rgba(hex_color)
        principled.inputs["Roughness"].default_value = roughness
        principled.inputs["Metallic"].default_value = metallic

        # Add procedural surface detail only to wood and countertop.
        if name in (
                "AI_Floor",
                "AI_Coffee_Table_Oak",
                "Kitchen_Wood_Accent",
                "Kitchen_Black_Countertop",
                "AI_Sofa",
                "AI_Chair",
                "AI_Chair",
                "AI_Wall",
        ):
            texcoord = nodes.new("ShaderNodeTexCoord")
            texcoord.location = (-700, 100)

            mapping = nodes.new("ShaderNodeMapping")
            mapping.location = (-500, 100)
            links.new(texcoord.outputs["Generated"], mapping.inputs["Vector"])

            noise = nodes.new("ShaderNodeTexNoise")
            noise.location = (-280, 100)
            noise.inputs["Detail"].default_value = 3.0
            noise.inputs["Roughness"].default_value = 0.7

            ramp = nodes.new("ShaderNodeValToRGB")
            ramp.location = (-40, 160)

            bump = nodes.new("ShaderNodeBump")
            bump.location = (180, -100)

            if name == "AI_Floor":

                # Warm oak floor grain
                mapping.inputs["Scale"].default_value = (1.5, 1.5, 24.0)
                noise.inputs["Scale"].default_value = 5.0
                ramp.color_ramp.elements[0].position = 0.25
                ramp.color_ramp.elements[0].color = (0.20, 0.09, 0.035, 1.0)
                ramp.color_ramp.elements[1].position = 0.78
                ramp.color_ramp.elements[1].color = (0.58, 0.34, 0.15, 1.0)
                bump.inputs["Strength"].default_value = 0.10
                bump.inputs["Distance"].default_value = 0.015
            elif name == "AI_Coffee_Table_Oak":
                # Natural oak wood grain
                mapping.inputs["Scale"].default_value = (2.0, 2.0, 18.0)
                noise.inputs["Scale"].default_value = 3.0
                noise.inputs["Detail"].default_value = 3.0
                noise.inputs["Roughness"].default_value = 0.7

                ramp.color_ramp.elements[0].position = 0.22
                ramp.color_ramp.elements[0].color = (
                    0.28, 0.16, 0.07, 1.0
                )

                ramp.color_ramp.elements[1].position = 0.78
                ramp.color_ramp.elements[1].color = (
                    0.62, 0.40, 0.22, 1.0
                )

                bump.inputs["Strength"].default_value = 0.08
                bump.inputs["Distance"].default_value = 0.012

                principled.inputs["Roughness"].default_value = 0.65
            elif name == "Kitchen_Wood_Accent":
                # Elongated kitchen wood grain
                mapping.inputs["Scale"].default_value = (2.0, 2.0, 18.0)
                noise.inputs["Scale"].default_value = 3.0
                ramp.color_ramp.elements[0].position = 0.22
                ramp.color_ramp.elements[0].color = (0.16, 0.055, 0.022, 1.0)
                ramp.color_ramp.elements[1].position = 0.78
                ramp.color_ramp.elements[1].color = (0.48, 0.24, 0.10, 1.0)
                bump.inputs["Strength"].default_value = 0.12
                bump.inputs["Distance"].default_value = 0.025

            elif name == "Kitchen_Black_Countertop":
                # Subtle dark stone variation
                mapping.inputs["Scale"].default_value = (1.0, 1.0, 1.0)
                noise.inputs["Scale"].default_value = 28.0
                ramp.color_ramp.elements[0].position = 0.25
                ramp.color_ramp.elements[0].color = (0.012, 0.012, 0.012, 1.0)
                ramp.color_ramp.elements[1].position = 0.78
                ramp.color_ramp.elements[1].color = (0.055, 0.055, 0.055, 1.0)
                bump.inputs["Strength"].default_value = 0.07
                bump.inputs["Distance"].default_value = 0.008
                # Fine, low-contrast variation for a dark stone-like surface.
                mapping.inputs["Scale"].default_value = (1.0, 1.0, 1.0)
                noise.inputs["Scale"].default_value = 28.0
                ramp.color_ramp.elements[0].position = 0.25
                ramp.color_ramp.elements[0].color = (0.012, 0.012, 0.012, 1.0)
                ramp.color_ramp.elements[1].position = 0.78
                ramp.color_ramp.elements[1].color = (0.055, 0.055, 0.055, 1.0)
                bump.inputs["Strength"].default_value = 0.07
                bump.inputs["Distance"].default_value = 0.008
            elif name == "AI_Wall":
                # Very subtle painted-plaster surface texture
                mapping.inputs["Scale"].default_value = (1.0, 1.0, 1.0)
                noise.inputs["Scale"].default_value = 220.0
                noise.inputs["Detail"].default_value = 2.0
                noise.inputs["Roughness"].default_value = 0.7

                bump.inputs["Strength"].default_value = 0.07
                bump.inputs["Distance"].default_value = 0.001
            elif name == "AI_Chair":
                # Subtle fine surface texture for the dark-grey chair
                mapping.inputs["Scale"].default_value = (1.0, 1.0, 1.0)
                noise.inputs["Scale"].default_value = 160.0
                noise.inputs["Detail"].default_value = 2.0
                noise.inputs["Roughness"].default_value = 0.7

                bump.inputs["Strength"].default_value = 0.10
                bump.inputs["Distance"].default_value = 0.002
            elif name == "AI_Sofa":
                # Subtle woven fabric texture for the red sofa
                mapping.inputs["Scale"].default_value = (1.0, 1.0, 1.0)
                noise.inputs["Scale"].default_value = 180.0
                noise.inputs["Detail"].default_value = 2.0
                noise.inputs["Roughness"].default_value = 0.7

                ramp.color_ramp.elements[0].position = 0.25
                ramp.color_ramp.elements[0].color = (
                    0.65, 0.65, 0.65, 1.0
                )

                ramp.color_ramp.elements[1].position = 0.75
                ramp.color_ramp.elements[1].color = (
                    1.0, 1.0, 1.0, 1.0
                )

                bump.inputs["Strength"].default_value = 0.16
                bump.inputs["Distance"].default_value = 0.005

                principled.inputs["Roughness"].default_value = 0.82

            links.new(mapping.outputs["Vector"], noise.inputs["Vector"])
            links.new(noise.outputs["Fac"], ramp.inputs["Fac"])

            if name not in ("AI_Sofa", "AI_Floor","AI_Chair","AI_Wall"):
                links.new(ramp.outputs["Color"], principled.inputs["Base Color"])

            links.new(noise.outputs["Fac"], bump.inputs["Height"])
            links.new(bump.outputs["Normal"], principled.inputs["Normal"])



    return material

materials_data = scene_data.get(
    "materials",
    {}
)


wall_material = create_material(
    "AI_Wall",
    materials_data.get(
        "wall",
        "#E8DED0"
    ),
    0.85
)


floor_material = create_material(
    "AI_Floor",
    materials_data.get(
        "floor",
        "#8B5E3C"
    ),
    0.65
)


ceiling_material = create_material(
    "AI_Ceiling",
    materials_data.get(
        "ceiling",
        "#F5F5F5"
    ),
    0.9
)


sofa_material = create_material(
    "AI_Sofa",
    materials_data.get(
        "sofa",
        "#B8202F"
    ),
    0.9
)
chair_material = create_material(
    "AI_Chair",

    materials_data.get(
        "chair",
      "#C62828"
    ),
    1.0
)


wood_material = create_material(
    "AI_Wood",
    materials_data.get(
        "wood",
        "#6B4226"
    ),
    0.45
)
coffee_table_material = create_material(
    "AI_Coffee_Table_Oak",
    "#A98255",
    0.65
)


black_material = create_material(
    "AI_Black",
    materials_data.get(
        "black",
        "#111111"
    ),
    0.3
)


# =========================================================
# MATERIAL ASSIGNMENT
# =========================================================

def assign_material(
    obj,
    material
):

    if obj.type != "MESH":
        return

    obj.data.materials.clear()

    obj.data.materials.append(
        material
    )


# =========================================================
# BOX CREATOR
# =========================================================

def create_box(
    name,
    location,
    scale,
    material=None
):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale

    if material:
        assign_material(
            obj,
            material
        )

    # Add subtle bevels to the main kitchen furniture.
    bevel_targets = (
        "Kitchen_Lower_Cabinets",
        "Kitchen_Black_Countertop",
        "Kitchen_Wood_Backsplash",
        "Kitchen_Upper_Cabinets",
        "Kitchen_Refrigerator",
    )

    if (
        name in bevel_targets
        or name.startswith("Kitchen_Cabinet_Door_")
    ):
        bevel = obj.modifiers.new(
            name="Subtle_Edge_Bevel",
            type="BEVEL"
        )
        bevel.width = 0.015
        bevel.segments = 3
        bevel.limit_method = "ANGLE"

    return obj


# =========================================================
# ROOM CREATION
# =========================================================

print("")
print("Creating room...")


# ---------------------------------------------------------
# Floor
# ---------------------------------------------------------

create_box(
    "AI_Floor",
    (
        0,
        0,
        -0.075
    ),
    (
        WIDTH / 2,
        LENGTH / 2,
        0.075
    ),
    floor_material
)


# ---------------------------------------------------------
# Back wall
# ---------------------------------------------------------

create_box(
    "AI_Wall_Back",
    (
        0,
        LENGTH / 2,
        HEIGHT / 2
    ),
    (
        WIDTH / 2,
        0.075,
        HEIGHT / 2
    ),
    wall_material
)


# ---------------------------------------------------------
# Left wall
# ---------------------------------------------------------

create_box(
    "AI_Wall_Left",
    (
        -WIDTH / 2,
        0,
        HEIGHT / 2
    ),
    (
        0.075,
        LENGTH / 2,
        HEIGHT / 2
    ),
    wall_material
)


# ---------------------------------------------------------
# Right wall
# ---------------------------------------------------------

create_box(
    "AI_Wall_Right",
    (
        WIDTH / 2,
        0,
        HEIGHT / 2
    ),
    (
        0.075,
        LENGTH / 2,
        HEIGHT / 2
    ),
    wall_material
)


# ---------------------------------------------------------
# Ceiling
# ---------------------------------------------------------

create_box(
    "AI_Ceiling",
    (
        0,
        0,
        HEIGHT
    ),
    (
        WIDTH / 2,
        LENGTH / 2,
        0.075
    ),
    ceiling_material
)


print("Room created.")

# =========================================================
# OPEN ROOM VIEW â€” KEEP FLOOR AND THREE WALLS
# =========================================================
# =========================================================
# OPEN ROOM VIEW â€” CAMERA-FRIENDLY RENDER
# =========================================================

# Remove the ceiling for an open interior view.
ceiling = bpy.data.objects.get("AI_Ceiling")
if ceiling:
    bpy.data.objects.remove(ceiling, do_unlink=True)


print("Open room created for interior viewing.")
print("Side walls visible in viewport and final render.")

# =========================================================
# PROCEDURAL KITCHEN FURNITURE
# =========================================================

room_type = str(
    scene_data.get("room_type", room.get("type", "living_room"))
).lower()

if room_type == "kitchen":
    print("Creating procedural kitchen...")


    # Matte white cabinet finish
    white_mat = create_material(
        "Kitchen_White_Cabinets",
        "#F5F5F2",
        roughness=0.42
    )

    # Natural medium-brown wood
    wood_mat = create_material(
        "Kitchen_Wood_Accent",
        "#8B5E3C",
        roughness=0.58
    )

    # Dark countertop with a subtle sheen
    black_mat = create_material(
        "Kitchen_Black_Countertop",
        "#202020",
        roughness=0.32
    )

    # Brushed-metal appearance
    metal_mat = create_material(
        "Kitchen_Metal",
        "#A8ADB2",
        roughness=0.38,
        metallic=0.55
    )

    # Kitchen runs along the back wall.
    counter_x = -0.05
    counter_y = LENGTH / 2 - 0.42
    counter_depth = min(0.62, LENGTH * 0.22)
    counter_height = min(0.90, HEIGHT * 0.32)
    cabinet_width = WIDTH * 0.68
    top_thickness = 0.055

    # Lower cabinets
    create_box(
        "Kitchen_Lower_Cabinets",
        (counter_x, counter_y, counter_height / 2),
        (cabinet_width / 2, counter_depth / 2, counter_height / 2),
        white_mat
    )

    # Black countertop
    create_box(
        "Kitchen_Black_Countertop",
        (counter_x, counter_y, counter_height + top_thickness / 2),
        (cabinet_width / 2 + 0.04, counter_depth / 2 + 0.04,
         top_thickness / 2),
        black_mat
    )

    # Individual cabinet fronts
    door_count = 4
    door_width = cabinet_width / door_count

    for i in range(door_count):
        door_x = counter_x - cabinet_width / 2 + door_width * (i + 0.5)
        create_box(
            f"Kitchen_Cabinet_Door_{i + 1}",
            (door_x, counter_y - counter_depth / 2 - 0.015,
             counter_height * 0.52),
            (door_width * 0.44, 0.018, counter_height * 0.40),
            white_mat
        )

    # Wooden backsplash
    backsplash_height = min(0.42, HEIGHT * 0.16)
    create_box(
        "Kitchen_Wood_Backsplash",
        (counter_x, counter_y + counter_depth / 2 + 0.015,
         counter_height + backsplash_height / 2),
        (cabinet_width / 2, 0.025, backsplash_height / 2),
        wood_mat
    )

    # Upper cabinets
    upper_height = min(0.68, HEIGHT * 0.23)
    upper_z = min(HEIGHT * 0.70, counter_height + backsplash_height + upper_height / 2 + 0.12)

    create_box(
        "Kitchen_Upper_Cabinets",
        (counter_x, counter_y + 0.10, upper_z),
        (cabinet_width * 0.40, 0.20, upper_height / 2),
        white_mat
    )

    # Sink
    sink_x = counter_x - cabinet_width * 0.22
    create_box(
        "Kitchen_Sink",
        (sink_x, counter_y - 0.04,
         counter_height + top_thickness + 0.012),
        (0.22, 0.15, 0.018),
        metal_mat
    )

    # Cooktop
    cooktop_x = counter_x + cabinet_width * 0.22
    create_box(
        "Kitchen_Cooktop",
        (cooktop_x, counter_y - 0.03,
         counter_height + top_thickness + 0.014),
        (0.23, 0.18, 0.014),
        black_mat
    )

    # Refrigerator at the right side
    fridge_width = min(0.62, WIDTH * 0.16)
    fridge_depth = min(0.65, LENGTH * 0.20)
    fridge_height = min(1.95, HEIGHT * 0.68)
    fridge_x = WIDTH / 2 - fridge_width / 2 - 0.12
    fridge_y = counter_y

    create_box(
        "Kitchen_Refrigerator",
        (fridge_x, fridge_y, fridge_height / 2),
        (fridge_width / 2, fridge_depth / 2, fridge_height / 2),
        white_mat
    )

    create_box(
        "Kitchen_Refrigerator_Handle",
        (fridge_x - fridge_width * 0.30,
         fridge_y - fridge_depth / 2 - 0.015,
         fridge_height * 0.55),
        (0.018, 0.018, fridge_height * 0.18),
        metal_mat
    )

    # Visible under-cabinet light strip
    create_box(
        "Kitchen_Under_Cabinet_Light_Strip",
        (counter_x, counter_y - 0.08, upper_z - upper_height / 2 - 0.015),
        (cabinet_width * 0.38, 0.025, 0.012),
        create_material("Kitchen_Light_Strip", "#FFE5A3", roughness=0.25)
    )

    print("Procedural kitchen created.")



# =========================================================
# LOAD MASTER ASSETS
# =========================================================

print("")
print("==========================================")
print("LOADING MASTER FURNITURE ASSETS")
print("==========================================")


def append_asset(asset_name):

    print("")
    print("------------------------------------------")
    print("Loading asset:", asset_name)
    print("------------------------------------------")

    loaded_collection = None

    # =====================================================
    # APPEND COLLECTION
    # =====================================================

    with bpy.data.libraries.load(
        ASSET_LIBRARY,
        link=False
    ) as (
        data_from,
        data_to
    ):

        available = list(
            data_from.collections
        )

        print(
            "Available collections:",
            available
        )

        if asset_name not in available:

            raise RuntimeError(
                f"Asset collection '{asset_name}' "
                f"was not found in:\n{ASSET_LIBRARY}"
            )

        data_to.collections = [
            asset_name
        ]

    # =====================================================
    # FIND LOADED COLLECTION
    # =====================================================

    for collection in data_to.collections:

        if collection is not None:

            loaded_collection = collection

            break

    if loaded_collection is None:

        raise RuntimeError(
            f"Could not load collection: {asset_name}"
        )

    # =====================================================
    # LINK COLLECTION
    # =====================================================

    scene_children = [
        collection.name
        for collection
        in bpy.context.scene.collection.children
    ]

    if loaded_collection.name not in scene_children:

        bpy.context.scene.collection.children.link(
            loaded_collection
        )

    # IMPORTANT:
    # Force Blender to evaluate transforms.
    bpy.context.view_layer.update()

    # =====================================================
    # GET OBJECTS
    # =====================================================

    objects = list(
        loaded_collection.all_objects
    )

    mesh_objects = [
        obj
        for obj in objects
        if obj.type == "MESH"
    ]

    print(
        "Total objects:",
        len(objects)
    )

    print(
        "Mesh objects:",
        len(mesh_objects)
    )

    if not mesh_objects:

        raise RuntimeError(
            f"Asset '{asset_name}' "
            f"contains no mesh objects."
        )

    # =====================================================
    # IMPORTANT:
    # CAPTURE ORIGINAL LOCAL TRANSFORMS
    # =====================================================

    #
    # We deliberately use matrix_basis.
    #
    # matrix_basis contains the object's own transform
    # before parenting.
    #
    # This preserves things such as:
    #
    # Sofa_Seat      Y = 0.80
    # Sofa_Back      Y = 1.15
    # Sofa_Arm_Left  X = -1.15
    # Sofa_Arm_Right X = 1.15
    #
    # Blender documents matrix_basis as the transform
    # before parenting is applied.
    #

    original_local_transforms = {}

    for obj in objects:

        original_local_transforms[
            obj.name
        ] = obj.matrix_basis.copy()

    # =====================================================
    # CREATE CONTROLLER
    # =====================================================

    root_name = (
        f"ASSET_INSTANCE_{asset_name}"
    )

    old_root = bpy.data.objects.get(
        root_name
    )

    if old_root is not None:

        bpy.data.objects.remove(
            old_root,
            do_unlink=True
        )

    root = bpy.data.objects.new(
        root_name,
        None
    )

    root.empty_display_type = "PLAIN_AXES"
    root.empty_display_size = 0.5

    bpy.context.scene.collection.objects.link(
        root
    )

    # =====================================================
    # RESET ROOT
    # =====================================================

    root.location = (
        0,
        0,
        0
    )

    root.rotation_euler = (
        0,
        0,
        0
    )

    root.scale = (
        1,
        1,
        1
    )

    # =====================================================
    # PARENT USING LOCAL TRANSFORMS
    # =====================================================

    for obj in objects:

        if obj == root:
            continue

        local_matrix = (
            original_local_transforms[
                obj.name
            ]
        )

        # Remove previous parent.
        obj.parent = None

        # Parent to controller.
        obj.parent = root

        # No parent inverse.
        #
        # This means the child's local transform is
        # interpreted directly relative to the root.
        #
        obj.matrix_parent_inverse = (
            Matrix.Identity(4)
        )

        # Restore original local transform.
        obj.matrix_basis = local_matrix

    # =====================================================
    # UPDATE BLENDER
    # =====================================================

    bpy.context.view_layer.update()

    # =====================================================
    # NORMALIZE USING ACTUAL LOCAL GEOMETRY
    # =====================================================

    #
    # At this point all objects are children of root.
    #
    # Their local transforms are preserved.
    #
    # We calculate bounds in the asset's local coordinate
    # system rather than relying on the potentially confusing
    # world matrix from the source library.
    #

    min_x = float("inf")
    min_y = float("inf")
    min_z = float("inf")

    max_x = float("-inf")
    max_y = float("-inf")
    max_z = float("-inf")

    for obj in mesh_objects:

        local_matrix = obj.matrix_basis

        for corner in obj.bound_box:

            local_corner = (
                local_matrix @
                Vector(corner)
            )

            min_x = min(
                min_x,
                local_corner.x
            )

            min_y = min(
                min_y,
                local_corner.y
            )

            min_z = min(
                min_z,
                local_corner.z
            )

            max_x = max(
                max_x,
                local_corner.x
            )

            max_y = max(
                max_y,
                local_corner.y
            )

            max_z = max(
                max_z,
                local_corner.z
            )

    center_x = (
        min_x + max_x
    ) / 2.0

    center_y = (
        min_y + max_y
    ) / 2.0

    floor_z = min_z

    print("")
    print("Asset local bounds:")

    print(
        " X:",
        round(min_x, 3),
        "to",
        round(max_x, 3)
    )

    print(
        " Y:",
        round(min_y, 3),
        "to",
        round(max_y, 3)
    )

    print(
        " Z:",
        round(min_z, 3),
        "to",
        round(max_z, 3)
    )

    print(
        "Local center:",
        (
            round(center_x, 3),
            round(center_y, 3)
        )
    )

    print(
        "Local floor:",
        round(floor_z, 3)
    )

    # =====================================================
    # NORMALIZE CHILDREN
    # =====================================================

    #
    # Shift each child locally so that:
    #
    # center X = 0
    # center Y = 0
    # floor Z  = 0
    #
    # Because the root remains at zero, this makes the
    # controller's location the actual furniture placement.
    #

    normalization = Vector(
        (
            -center_x,
            -center_y,
            -floor_z
        )
    )

    for obj in mesh_objects:

        local_matrix = obj.matrix_basis.copy()

        local_matrix.translation += normalization

        obj.matrix_basis = local_matrix

    bpy.context.view_layer.update()

    # =====================================================
    # VERIFY NORMALIZATION
    # =====================================================

    verify_min_x = float("inf")
    verify_min_y = float("inf")
    verify_min_z = float("inf")

    verify_max_x = float("-inf")
    verify_max_y = float("-inf")
    verify_max_z = float("-inf")

    for obj in mesh_objects:

        local_matrix = obj.matrix_basis

        for corner in obj.bound_box:

            local_corner = (
                local_matrix @
                Vector(corner)
            )

            verify_min_x = min(
                verify_min_x,
                local_corner.x
            )

            verify_min_y = min(
                verify_min_y,
                local_corner.y
            )

            verify_min_z = min(
                verify_min_z,
                local_corner.z
            )

            verify_max_x = max(
                verify_max_x,
                local_corner.x
            )

            verify_max_y = max(
                verify_max_y,
                local_corner.y
            )

            verify_max_z = max(
                verify_max_z,
                local_corner.z
            )

    verified_center_x = (
        verify_min_x +
        verify_max_x
    ) / 2.0

    verified_center_y = (
        verify_min_y +
        verify_max_y
    ) / 2.0

    print("")
    print("Normalized asset:")

    print(
        " Center X:",
        round(
            verified_center_x,
            3
        )
    )

    print(
        " Center Y:",
        round(
            verified_center_y,
            3
        )
    )

    print(
        " Floor Z:",
        round(
            verify_min_z,
            3
        )
    )

    # =====================================================
    # CONTROLLER METADATA
    # =====================================================

    root["asset_name"] = asset_name
    root["asset_controller"] = True
    root["normalized"] = True

    print(
        "Asset controller:",
        root.name
    )

    print(
        "Children:",
        len(root.children)
    )

    print(
        "Asset normalization complete:",
        asset_name
    )

    return root


# =========================================================
# POSITION ASSET
# =========================================================

def position_asset(
    root,
    asset_name,
    position,
    rotation,
    scale
):

    if root is None:
        return

    # -----------------------------------------------------
    # IMPORTANT
    #
    # After normalization:
    #
    # JSON position X/Y = furniture center
    # JSON position Z   = floor
    #
    # Therefore the controller sits directly on the
    # requested X/Y/Z coordinate.
    #
    # -----------------------------------------------------

    x = float(position[0])
    y = float(position[1])
    z = float(position[2])

    root.location = (
        x,
        y,
        z
    )

    # -----------------------------------------------------
    # ROTATION
    # -----------------------------------------------------

    root.rotation_mode = "XYZ"

    root.rotation_euler = (
        math.radians(
            float(rotation[0])
        ),
        math.radians(
            float(rotation[1])
        ),
        math.radians(
            float(rotation[2])
        )
    )

    # -----------------------------------------------------
    # SCALE
    # -----------------------------------------------------

    root.scale = (
        float(scale[0]),
        float(scale[1]),
        float(scale[2])
    )

    bpy.context.view_layer.update()

    print(
        "PLACED:",
        asset_name,
        "| X=",
        round(x, 3),
        "Y=",
        round(y, 3),
        "Z=",
        round(z, 3),
        "| ROT=",
        rotation,
        "| SCALE=",
        scale
    )


# =========================================================
# LOAD JSON ASSETS
# =========================================================

loaded_assets = []

asset_roots = []
asset_roots_names = []

expected_assets = []


for asset_data in scene_data["assets"]:

    asset_name = asset_data["asset"]

    expected_assets.append(
        asset_name
    )

    position = asset_data.get(
        "position",
        [0, 0, 0]
    )

    rotation = asset_data.get(
        "rotation",
        [0, 0, 0]
    )

    scale = asset_data.get(
        "scale",
        [1, 1, 1]
    )

    root = append_asset(
        asset_name
    )

    position_asset(
        root,
        asset_name,
        position,
        rotation,
        scale
    )

    loaded_assets.append(
        asset_name
    )

    asset_roots.append(
        root
    )
    asset_roots_names.append(asset_name)


# =========================================================
# HARD ASSET VERIFICATION
# =========================================================

print("")
print("==========================================")
print("ASSET VERIFICATION")
print("==========================================")


missing_assets = [
    asset
    for asset in expected_assets
    if asset not in loaded_assets
]


if missing_assets:

    raise RuntimeError(
        "Furniture assets missing: "
        + ", ".join(missing_assets)
    )


scene_mesh_objects = [
    obj
    for obj in bpy.context.scene.objects
    if obj.type == "MESH"
]


print(
    "Expected furniture assets:",
    expected_assets
)

print(
    "Loaded furniture assets:",
    loaded_assets
)

print(
    "Total scene mesh objects:",
    len(scene_mesh_objects)
)


if len(scene_mesh_objects) <= 5:

    raise RuntimeError(
        "Furniture verification failed. "
        "Only room geometry exists."
    )


print("")
print("Furniture verification PASSED.")


# =========================================================
# APPLY JSON MATERIALS
# =========================================================

print("")
print("Applying JSON materials by asset identity...")


for root in asset_roots:

    # Read the asset name from the saved Python-side
    # list, not from a potentially deleted Blender object.
    asset_name = asset_roots_names[asset_roots.index(root)].lower()

    if root.name not in bpy.data.objects:
        print(f"Skipping removed controller: {asset_name}")
        continue

    if "sofa" in asset_name:
        material = sofa_material

    elif "chair" in asset_name:
        material = chair_material

    elif "coffee" in asset_name and "table" in asset_name:
        material = coffee_table_material

    elif any(
        keyword in asset_name
        for keyword in (
            "table",
            "tvunit",
            "wood",
            "desk",
            "wardrobe",
            "bed",
        )
    ):
        material = wood_material



    elif "tv" in asset_name or "black" in asset_name:
        material = black_material

    else:
        continue


    assigned_count = 0

    for obj in root.children_recursive:

        if obj.type != "MESH":
            continue

        object_name = obj.name.lower().split(".")[0]

        # Keep the television screen black.
        if object_name == "tv":
            object_material = black_material

        # Keep the TV stand black.
        elif object_name == "tv_stand":
            object_material = black_material

        # Keep the wooden TV cabinet and other furniture wood.
        else:
            object_material = material

        assign_material(obj, object_material)
        assigned_count += 1
        if object_name == "coffee_table_top":
            print(
                "ACTUAL TABLETOP MATERIAL:",
                obj.data.materials[0].name
            )
            print(
                "ACTUAL TABLETOP COLOR:",
                tuple(
                    round(v, 3)
                    for v in obj.data.materials[0]
                    .node_tree.nodes["Principled BSDF"]
                    .inputs["Base Color"].default_value[:3]
                )
            )


    print(
        f"Asset: {root.name} | "
        f"Material: {material.name} | "
        f"Meshes updated: {assigned_count}"
    )
    if "sofa" in asset_name:
        print(
            "SOFA MATERIAL COLOR:",
            tuple(
                round(v, 3)
                for v in sofa_material.node_tree.nodes["Principled BSDF"]
                         .inputs["Base Color"].default_value[:3]
            )
        )

    elif "chair" in asset_name:
        print(
            "CHAIR ROUGHNESS:",
            chair_material.node_tree.nodes["Principled BSDF"]
            .inputs["Roughness"].default_value
        )
        print(
            "CHAIR MATERIAL COLOR:",
            tuple(
                round(v, 3)
                for v in chair_material.node_tree.nodes["Principled BSDF"]
                .inputs["Base Color"].default_value[:3]
            )
        )

    elif "coffee" in asset_name and "table" in asset_name:
        print(
            "COFFEE TABLE MATERIAL COLOR:",
            tuple(
                round(v, 3)
                for v in coffee_table_material.node_tree
                .nodes["Principled BSDF"]
                .inputs["Base Color"].default_value[:3]
            )
        )
# =========================================================
# CREATE TV SCREEN PANEL - FIXED GEOMETRY
# =========================================================

tv_root = bpy.data.objects.get("ASSET_INSTANCE_TVUnit_Wood")

if tv_root:
    tv_obj = next(
        (
            obj for obj in tv_root.children_recursive
            if obj.name.lower().split(".")[0] == "tv"
            and obj.type == "MESH"
        ),
        None
    )

    if tv_obj:
        # Remove the previous incorrect screen panel.
        old_screen = bpy.data.objects.get("AI_TV_Screen_Panel")
        if old_screen:
            bpy.data.objects.remove(old_screen, do_unlink=True)

        tv_screen_material = create_material(
            "AI_TV_Screen",
            "#05070A",
            roughness=0.12
        )

        # Build a thin rectangular screen directly in TV-local space.
        x = 1.05
        z = 0.575
        y_front = -0.043
        y_back = -0.041

        vertices = [
            (-x, y_front, -z),
            ( x, y_front, -z),
            ( x, y_back, -z),
            (-x, y_back, -z),
            (-x, y_front,  z),
            ( x, y_front,  z),
            ( x, y_back,  z),
            (-x, y_back,  z),
        ]

        faces = [
            (0, 1, 5, 4),
            (1, 2, 6, 5),
            (2, 3, 7, 6),
            (3, 0, 4, 7),
            (4, 5, 6, 7),
            (3, 2, 1, 0),
        ]

        mesh = bpy.data.meshes.new("AI_TV_Screen_Mesh")
        mesh.from_pydata(vertices, [], faces)
        mesh.materials.append(tv_screen_material)
        mesh.update()

        screen = bpy.data.objects.new(
            "AI_TV_Screen_Panel",
            mesh
        )

        bpy.context.collection.objects.link(screen)

        # Parent directly to the TV mesh.
        screen.parent = tv_obj
        screen.location = (0, 0, 0)
        screen.rotation_euler = (0, 0, 0)
        screen.scale = (1, 1, 1)

        print("TV SCREEN CREATED WITH FIXED RECTANGULAR GEOMETRY")
        print("TV SCREEN DIMENSIONS:", tuple(round(v, 3) for v in screen.dimensions))

    else:
        print("WARNING: TV mesh not found")
else:
    print("WARNING: TV controller not found")

print("")


lighting_data = scene_data.get(
    "lighting",
    {}
)

brightness = float(
    lighting_data.get(
        "brightness",
        1.0
    )
)

lighting_type = lighting_data.get(
    "type",
    "warm"
)


def create_area_light(
    name,
    location,
    energy,
    size
):

    light_data = bpy.data.lights.new(
        name=name,
        type="AREA"
    )

    light_data.energy = (
            energy * brightness
    )

    light_data.shape = "DISK"

    light_data.size = size

    obj = bpy.data.objects.new(
        name,
        light_data
    )

    bpy.context.scene.collection.objects.link(
        obj
    )

    obj.location = location

    # Aim the area light towards the centre of the room
    target = Vector((0.0, 0.0, 1.0))
    direction = target - obj.location
    obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

    return obj



# =========================================================
# BRIGHT NEUTRAL-WHITE KITCHEN LIGHTING
# =========================================================


# Key light â€” soft white illumination
create_area_light(
    "AI_Key_Light",
    (0, -2.0, HEIGHT - 0.2),
    500,
    4
)

# Fill light â€” gentle illumination on the left
create_area_light(
    "AI_Fill_Light",
    (-2.0, -0.2, 2.2),
    150,
    3
)

# Ceiling light â€” balanced illumination
create_area_light(
    "AI_Ceiling_Light",
    (0, 0.5, HEIGHT - 0.15),
    300,
    3
)

# Neutral-white point light
warm_data = bpy.data.lights.new(
    "AI_Warm_Light",
    type="POINT"
)

warm_data.energy = 40 * brightness
warm_data.color = (1.0, 1.0, 1.0)

warm_light = bpy.data.objects.new(
    "AI_Warm_Light",
    warm_data
)

bpy.context.scene.collection.objects.link(warm_light)

warm_light.location = (1.5, 0.5, 2.2)
# =========================================================
# CAMERA
# =========================================================

print("")
print("[7/9] Creating camera...")


camera_data = bpy.data.cameras.new(
    "AI_Camera"
)

camera = bpy.data.objects.new(
    "AI_Camera",
    camera_data
)

bpy.context.scene.collection.objects.link(
    camera
)


camera_position = scene_data[
    "camera"
]["position"]

camera_target = scene_data[
    "camera"
]["target"]


camera.location = (
    float(camera_position[0]),
    float(camera_position[1]),
    float(camera_position[2])
)


direction = (
    Vector(camera_target)
    - camera.location
)


camera.rotation_euler = (
    direction.to_track_quat(
        "-Z",
        "Y"
    ).to_euler()
)

# Camera settings for interior photography
camera_data.lens = float(
    scene_data.get("camera", {}).get("lens", 28)
)

camera_data.sensor_width = 36
camera_data.clip_start = 0.05
camera_data.clip_end = 100

# Keep the camera settings predictable
camera_data.type = "PERSP"


# =========================================================
# =========================================================
# CAMERA FRAMING
# =========================================================


# =========================================================
# CAMERA FRAMING
# =========================================================

print("[7/9] Configuring camera framing...")

from mathutils import Vector

# Read the camera settings from scene_generated.json
camera_position = scene_data["camera"]["position"]
camera_target = scene_data["camera"]["target"]

# Apply the requested camera position
camera.location = Vector(
    tuple(float(v) for v in camera_position)
)

# Aim the camera at the requested target
target = Vector(
    tuple(float(v) for v in camera_target)
)

direction = target - camera.location

camera.rotation_euler = direction.to_track_quat(
    "-Z", "Y"
).to_euler()

# Apply camera settings
camera_data.lens = float(
    scene_data.get("camera", {}).get("lens", 28)
)
camera_data.sensor_width = 36
camera_data.sensor_fit = "AUTO"
camera_data.clip_start = 0.1
camera_data.clip_end = 200

# Activate the camera
bpy.context.scene.camera = camera

print(
    "Camera position:",
    tuple(round(v, 2) for v in camera.location)
)
print(
    "Camera target:",
    tuple(round(v, 2) for v in target)
)
print("Camera lens:", camera_data.lens, "mm")

# =========================================================
# WORLD
# =========================================================
# =========================================================
# WORLD
# =========================================================

world = bpy.context.scene.world

if world is None:

    world = bpy.data.worlds.new(
        "AI_World"
    )

    bpy.context.scene.world = world


world.use_nodes = True

background = (
    world.node_tree.nodes.get(
        "Background"
    )
)


if background:

    background.inputs[
        "Color"
    ].default_value = (
        0.15,
        0.15,
        0.15,
        1
    )

    background.inputs[
        "Strength"
    ].default_value = 0.5


# =========================================================
# RENDER SETTINGS
# =========================================================

print("")
print("[8/9] Configuring render...")



scene = bpy.context.scene

# Render engine
scene.render.engine = "BLENDER_EEVEE"

# Higher-quality widescreen image
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100

# Blender 5.2 compatible render settings
# Keep default Eevee lighting; do not use the removed GTAO properties.
# Color management for a more balanced architectural render
scene.view_settings.view_transform = "AgX"
scene.view_settings.look = "AgX - Medium High Contrast"
scene.view_settings.exposure = 0.0
scene.view_settings.gamma = 1.0

# Save as PNG
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.render.film_transparent = False


# =========================================================
# OUTPUT PATHS
# =========================================================

blend_path = os.path.abspath(
    os.environ.get(
        "AI_STUDIO_BLEND_FILE",
        os.path.join(PROJECTS_DIR, "AI_Interior_Final.blend")
    )
)

render_path = os.path.abspath(
    os.environ.get(
        "AI_STUDIO_RENDER_FILE",
        os.path.join(RENDERS_DIR, "AI_Interior_Final.png")
    )
)

os.makedirs(os.path.dirname(blend_path), exist_ok=True)
os.makedirs(os.path.dirname(render_path), exist_ok=True)

# =========================================================
# FINAL TRANSFORM VERIFICATION
# =========================================================

print("")
print("==========================================")
print("FINAL FURNITURE POSITIONS")
print("==========================================")


for root in asset_roots:

    print(
        root.name,
        "|",
        "Location:",
        tuple(
            round(value, 3)
            for value in root.location
        ),
        "|",
        "Rotation:",
        tuple(
            round(
                math.degrees(value),
                1
            )
            for value in root.rotation_euler
        ),
        "|",
        "Scale:",
        tuple(
            round(value, 3)
            for value in root.scale
        )
    )


# =========================================================
# SAVE BLEND
# =========================================================

print("")
print("[9/9] Saving Blender project...")


bpy.ops.wm.save_as_mainfile(
    filepath=blend_path
)


print("Blend file saved:")
print(blend_path)


# =========================================================
# RENDER
# =========================================================

print("")
print("Rendering final interior...")


scene.render.filepath = render_path


bpy.ops.render.render(
    write_still=True
)


# =========================================================
# VERIFY RENDER
# =========================================================

if not os.path.exists(
    render_path
):

    raise RuntimeError(
        "Blender finished but render file "
        "was not created:\n"
        + render_path
    )


# =========================================================
# FINAL OUTPUT
# =========================================================

print("")
print("==========================================")
print("       AI GENERATION COMPLETE")
print("==========================================")


print("")
print("Prompt:")

print(
    scene_data.get(
        "prompt",
        "No prompt"
    )
)


print("")
print("Expected furniture assets:")

for asset in expected_assets:

    print(
        " -",
        asset
    )


print("")
print("Loaded furniture assets:")

for asset in loaded_assets:

    print(
        " -",
        asset
    )


print("")
print("Asset controllers:")

for root in asset_roots:

    print(
        " -",
        root.name,
        "| Children:",
        len(root.children)
    )


print("")
print("Scene mesh objects:")

for obj in scene_mesh_objects:

    print(
        " -",
        obj.name
    )


print("")
print("BLEND FILE:")
print(blend_path)


print("")
print("RENDER:")
print(render_path)


print("")
print("==========================================")
print("SUCCESS")
print("==========================================")
