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

JSON_PATH = os.path.join(
    PROJECT_DIR,
    "scene_generated.json"
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

    material = bpy.data.materials.get(
        name
    )

    if material is None:

        material = bpy.data.materials.new(
            name=name
        )

    material.use_nodes = True

    nodes = material.node_tree.nodes

    principled = nodes.get(
        "Principled BSDF"
    )

    if principled:

        principled.inputs[
            "Base Color"
        ].default_value = hex_to_rgba(
            hex_color
        )

        principled.inputs[
            "Roughness"
        ].default_value = roughness

        principled.inputs[
            "Metallic"
        ].default_value = metallic

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
        "#C8B39A"
    ),
    0.9
)


wood_material = create_material(
    "AI_Wood",
    materials_data.get(
        "wood",
        "#6B4226"
    ),
    0.45
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

    bpy.ops.mesh.primitive_cube_add(
        location=location
    )

    obj = bpy.context.object

    obj.name = name

    obj.scale = scale

    if material:

        assign_material(
            obj,
            material
        )

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
print("Applying JSON materials...")


for obj in bpy.context.scene.objects:

    name = obj.name.lower()

    if "sofa" in name:

        assign_material(
            obj,
            sofa_material
        )

    elif (
        "table" in name
        or "tvunit" in name
        or "wood" in name
        or "desk" in name
        or "wardrobe" in name
        or "bed" in name
    ):

        assign_material(
            obj,
            wood_material
        )

    elif (
        "tv" in name
        or "black" in name
    ):

        assign_material(
            obj,
            black_material
        )


# =========================================================
# LIGHTING
# =========================================================

print("")
print("[6/9] Creating lighting...")


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

    return obj


# Key light

create_area_light(
    "AI_Key_Light",
    (
        0,
        -0.5,
        HEIGHT - 0.3
    ),
    900,
    3
)


# Fill light

create_area_light(
    "AI_Fill_Light",
    (
        -3,
        1,
        2.2
    ),
    500,
    2
)


# Ceiling light

create_area_light(
    "AI_Ceiling_Light",
    (
        0,
        0,
        HEIGHT - 0.2
    ),
    700,
    2
)


# Warm / daylight point light

warm_data = bpy.data.lights.new(
    "AI_Warm_Light",
    type="POINT"
)

warm_data.energy = (
    150 * brightness
)


if lighting_type == "warm":

    warm_data.color = (
        1.0,
        0.55,
        0.3
    )

else:

    warm_data.color = (
        1.0,
        1.0,
        1.0
    )


warm_light = bpy.data.objects.new(
    "AI_Warm_Light",
    warm_data
)

bpy.context.scene.collection.objects.link(
    warm_light
)

warm_light.location = (
    1.5,
    0.5,
    2.2
)


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

camera_data.lens = 24

bpy.context.scene.camera = camera


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
        0.04,
        0.04,
        0.04,
        1
    )

    background.inputs[
        "Strength"
    ].default_value = 0.3


# =========================================================
# RENDER SETTINGS
# =========================================================

print("")
print("[8/9] Configuring render...")


scene = bpy.context.scene

scene.render.engine = "BLENDER_EEVEE"

scene.render.resolution_x = 800

scene.render.resolution_y = 600

scene.render.resolution_percentage = 100

scene.render.image_settings.file_format = "PNG"


# =========================================================
# OUTPUT PATHS
# =========================================================

blend_path = os.path.join(
    PROJECTS_DIR,
    "AI_Interior_Final.blend"
)

render_path = os.path.join(
    RENDERS_DIR,
    "AI_Interior_Final.png"
)


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