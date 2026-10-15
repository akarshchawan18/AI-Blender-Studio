
import bpy
import math
import os
import json
from mathutils import Vector

# ============================================================
# PATHS
# ============================================================

ROOT = os.path.abspath(".")
OUT = os.path.join(ROOT, "projects")
RENDERS = os.path.join(ROOT, "renders")
CONFIG_FILE = os.path.join(OUT, "kitchen_prompt.json")

os.makedirs(OUT, exist_ok=True)
os.makedirs(RENDERS, exist_ok=True)

BLEND = os.path.join(OUT, "modern_kitchen.blend")
PNG = os.path.join(RENDERS, "modern_kitchen.png")

# ============================================================
# CONFIGURATION DEFAULTS
# ============================================================

KITCHEN_STYLE = "modern"
LIGHTING_TONE = "warm"

CABINET_COLOR = (0.075, 0.19, 0.15)
COUNTER_COLOR = (0.80, 0.77, 0.70)

WOOD_COLOR = (0.48, 0.29, 0.15)
WALL_COLOR = (0.78, 0.72, 0.62)
FLOOR_COLOR = (0.38, 0.22, 0.12)

# ============================================================
# READ API CONFIGURATION
# ============================================================

def load_kitchen_config():
    global KITCHEN_STYLE
    global LIGHTING_TONE
    global CABINET_COLOR
    global COUNTER_COLOR

    if not os.path.exists(CONFIG_FILE):
        print("No kitchen_prompt.json found. Using defaults.")
        return

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as file:
            settings = json.load(file)

        style = str(settings.get("style", "modern")).lower()
        tone = str(settings.get("lighting_tone", "warm")).lower()

        if style in (
            "modern",
            "luxury",
            "scandinavian",
            "minimalist",
        ):
            KITCHEN_STYLE = style

        if tone in ("warm", "cool", "neutral"):
            LIGHTING_TONE = tone

        # Accept hex colors, such as #123456.
        def parse_color(value, fallback):
            if isinstance(value, str):
                value = value.strip().lstrip("#")

                if len(value) == 6:
                    try:
                        rgb = tuple(
                            int(value[i:i + 2], 16) / 255.0
                            for i in (0, 2, 4)
                        )
                        return rgb
                    except ValueError:
                        return fallback

            # Also accept RGB lists or tuples.
            if isinstance(value, (list, tuple)) and len(value) >= 3:
                try:
                    rgb = tuple(float(value[i]) for i in range(3))

                    if all(0.0 <= component <= 1.0 for component in rgb):
                        return rgb
                except (ValueError, TypeError):
                    pass

            return fallback

        CABINET_COLOR = parse_color(
            settings.get("cabinet_color"),
            CABINET_COLOR,
        )

        COUNTER_COLOR = parse_color(
            settings.get("counter_color"),
            COUNTER_COLOR,
        )

        print("Kitchen configuration loaded:")
        print("Style:", KITCHEN_STYLE)
        print("Lighting:", LIGHTING_TONE)
        print("Cabinet color:", CABINET_COLOR)
        print("Counter color:", COUNTER_COLOR)

    except (OSError, json.JSONDecodeError, TypeError) as error:
        print("Could not read kitchen configuration:", error)
        print("Using default kitchen settings.")


load_kitchen_config()

# ============================================================
# STYLE-DEPENDENT MATERIAL COLORS
# ============================================================

if KITCHEN_STYLE == "luxury":
    WOOD_COLOR = (0.20, 0.075, 0.025)
    WALL_COLOR = (0.78, 0.74, 0.66)
    FLOOR_COLOR = (0.24, 0.20, 0.16)

elif KITCHEN_STYLE == "scandinavian":
    WOOD_COLOR = (0.48, 0.29, 0.13)
    WALL_COLOR = (0.88, 0.86, 0.80)
    FLOOR_COLOR = (0.58, 0.49, 0.37)

elif KITCHEN_STYLE == "minimalist":
    WOOD_COLOR = (0.30, 0.28, 0.25)
    WALL_COLOR = (0.82, 0.82, 0.79)
    FLOOR_COLOR = (0.40, 0.40, 0.38)

else:
    WOOD_COLOR = (0.32, 0.15, 0.06)
    WALL_COLOR = (0.72, 0.68, 0.60)
    FLOOR_COLOR = (0.38, 0.33, 0.27)

# ============================================================
# CLEAR SCENE
# ============================================================

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

for collection in list(bpy.data.collections):
    if collection.users == 0:
        bpy.data.collections.remove(collection)

# ============================================================
# MATERIALS
# ============================================================

def material(name, color, roughness=0.65, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True

    shader = mat.node_tree.nodes.get("Principled BSDF")

    if shader:
        shader.inputs["Base Color"].default_value = (*color, 1.0)
        shader.inputs["Roughness"].default_value = roughness
        shader.inputs["Metallic"].default_value = metallic

    return mat


floor_mat = material("Style Floor", FLOOR_COLOR, 0.55)
wall_mat = material("Style Wall", WALL_COLOR, 0.85)
cabinet_mat = material("Custom Cabinet Color", CABINET_COLOR, 0.32)
wood_mat = material("Style Natural Oak", WOOD_COLOR, 0.42)
counter_mat = material("Custom Stone Countertop", COUNTER_COLOR, 0.28)
dark_mat = material("Black Appliances", (0.025, 0.03, 0.035), 0.28)
metal_mat = material("Brushed Steel", (0.48, 0.52, 0.54), 0.28, 0.65)
glass_mat = material("Cooktop Glass", (0.015, 0.018, 0.02), 0.18)
white_mat = material("Refrigerator White", (0.72, 0.75, 0.75), 0.3)
gold_mat = material("Brass Handles", (0.65, 0.40, 0.12), 0.3, 0.65)

# ============================================================
# GEOMETRY HELPERS
# ============================================================

def cube(name, loc, dims, mat, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dims

    bpy.ops.object.transform_apply(
        location=False,
        rotation=False,
        scale=True,
    )

    if mat:
        obj.data.materials.append(mat)

    if bevel:
        mod = obj.modifiers.new("Soft Edges", "BEVEL")
        mod.width = bevel
        mod.segments = 3

        obj.modifiers.new("Weighted Corner Normals", "WEIGHTED_NORMAL")

    return obj


def cylinder(name, loc, radius, depth, mat, vertices=32):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices,
        radius=radius,
        depth=depth,
        location=loc,
    )

    obj = bpy.context.object
    obj.name = name

    if mat:
        obj.data.materials.append(mat)

    return obj


# ============================================================
# ROOM DIMENSIONS
# ============================================================

W, L, H = 4.572, 3.658, 3.048
T = 0.12

# Floor and three walls; open-front presentation.

cube("Room_Floor", (0, 0, -0.08), (W, L, 0.16), floor_mat)

cube(
    "Room_Back_Wall",
    (0, L / 2, H / 2),
    (W, T, H),
    wall_mat,
)

cube(
    "Room_Left_Wall",
    (-W / 2, 0, H / 2),
    (T, L, H),
    wall_mat,
)

cube(
    "Room_Right_Wall",
    (W / 2, 0, H / 2),
    (T, L, H),
    wall_mat,
)

# ============================================================
# BASE CABINETS
# ============================================================

BACK_Y = 1.30
BASE_FRONT_Y = 0.82
BASE_Z = 0.45
BASE_H = 0.82
COUNTER_Z = 0.88

cabinet_xs = [-0.65, 0.05, 0.75, 1.45]

for i, x in enumerate(cabinet_xs, 1):
    cube(
        f"Base_Cabinet_{i}",
        (x, BASE_FRONT_Y, BASE_Z),
        (0.68, 0.88, BASE_H),
        cabinet_mat,
        0.025,
    )

    for side in [-1, 1]:
        dx = x + side * 0.16

        cube(
            f"Cabinet_{i}_Door_{side}",
            (dx, BASE_FRONT_Y - 0.447, BASE_Z),
            (0.31, 0.025, 0.72),
            cabinet_mat,
            0.012,
        )

        cube(
            f"Cabinet_{i}_Handle_{side}",
            (dx, BASE_FRONT_Y - 0.47, BASE_Z + 0.05),
            (0.035, 0.025, 0.15),
            gold_mat,
            0.012,
        )

# ============================================================
# COUNTERTOP AND BACKSPLASH
# ============================================================

cube(
    "Stone_Countertop",
    (0.40, 0.80, COUNTER_Z),
    (3.15, 1.02, 0.12),
    counter_mat,
    0.035,
)

cube(
    "Stone_Backsplash",
    (0.40, 1.32, 1.15),
    (3.15, 0.045, 0.45),
    counter_mat,
    0.015,
)

# ============================================================
# UPPER CABINETS
# ============================================================

upper_xs = [-0.65, 0.05, 0.75, 1.45]

for i, x in enumerate(upper_xs, 1):
    cube(
        f"Upper_Cabinet_{i}",
        (x, 1.43, 2.02),
        (0.66, 0.60, 0.76),
        cabinet_mat,
        0.025,
    )

    cube(
        f"Upper_Door_{i}",
        (x, 1.115, 2.02),
        (0.59, 0.025, 0.68),
        cabinet_mat,
        0.012,
    )

    cube(
        f"Upper_Handle_{i}",
        (x + 0.20, 1.085, 1.98),
        (0.025, 0.025, 0.15),
        gold_mat,
        0.01,
    )

# ============================================================
# SINK
# ============================================================

cube(
    "Sink_Rim",
    (-0.62, 0.78, 0.953),
    (0.58, 0.43, 0.025),
    metal_mat,
    0.025,
)

cube(
    "Sink_Basin",
    (-0.62, 0.78, 0.965),
    (0.46, 0.32, 0.018),
    dark_mat,
    0.025,
)

# Faucet stem and spout.

cylinder(
    "Faucet_Stem",
    (-0.62, 1.00, 1.08),
    0.025,
    0.24,
    metal_mat,
)

cylinder(
    "Faucet_Spout",
    (-0.62, 0.91, 1.19),
    0.022,
    0.18,
    metal_mat,
)

cylinder(
    "Faucet_Nozzle",
    (-0.62, 0.83, 1.15),
    0.018,
    0.09,
    metal_mat,
)

# ============================================================
# COOKTOP AND BURNERS
# ============================================================

cube(
    "Cooktop",
    (0.92, 0.78, 0.957),
    (0.72, 0.53, 0.035),
    glass_mat,
    0.018,
)

for x in [0.73, 1.11]:
    for y in [0.65, 0.90]:
        cylinder(
            "Cooktop_Burner",
            (x, y, 0.98),
            0.085,
            0.012,
            metal_mat,
        )

        cylinder(
            "Burner_Centre",
            (x, y, 0.989),
            0.045,
            0.01,
            dark_mat,
        )

# ============================================================
# REFRIGERATOR
# ============================================================

cube(
    "Refrigerator",
    (-1.63, 1.12, 1.05),
    (0.72, 0.72, 2.10),
    white_mat,
    0.035,
)

cube(
    "Fridge_Door_Upper",
    (-1.63, 0.747, 1.43),
    (0.67, 0.025, 1.28),
    white_mat,
    0.025,
)

cube(
    "Fridge_Door_Lower",
    (-1.63, 0.747, 0.53),
    (0.67, 0.025, 0.48),
    white_mat,
    0.025,
)

cube(
    "Fridge_Handle_Upper",
    (-1.39, 0.715, 1.43),
    (0.025, 0.025, 0.48),
    metal_mat,
    0.01,
)

cube(
    "Fridge_Handle_Lower",
    (-1.39, 0.715, 0.53),
    (0.025, 0.025, 0.24),
    metal_mat,
    0.01,
)

# ============================================================
# STYLE-DEPENDENT LIGHTING
# ============================================================

if LIGHTING_TONE == "cool":
    key_color = (0.72, 0.84, 1.0)
    fill_color = (0.65, 0.78, 1.0)
    bounce_color = (0.82, 0.90, 1.0)

elif LIGHTING_TONE == "neutral":
    key_color = (1.0, 0.97, 0.92)
    fill_color = (0.90, 0.94, 1.0)
    bounce_color = (1.0, 0.98, 0.95)

else:
    key_color = (1.0, 0.83, 0.68)
    fill_color = (0.74, 0.83, 1.0)
    bounce_color = (1.0, 0.90, 0.78)


def area_light(name, loc, power, size, color, target):
    data = bpy.data.lights.new(name, "AREA")
    data.energy = power
    data.shape = "DISK"
    data.size = size
    data.color = color

    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = loc

    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()

    return obj


area_light(
    "Kitchen_Key_Light",
    (0, -1.0, 2.8),
    500,
    4.0,
    key_color,
    (0, 0.8, 1.2),
)

area_light(
    "Kitchen_Fill_Light",
    (-2, 0.0, 2.4),
    300,
    3.0,
    fill_color,
    (0.5, 0.8, 1.2),
)

area_light(
    "Counter_Light",
    (0.5, 0.75, 2.65),
    180,
    2.0,
    bounce_color,
    (0, 0.8, 1.0),
)

# ============================================================
# CAMERA
# ============================================================

camera_data = bpy.data.cameras.new("Kitchen_Camera")
camera = bpy.data.objects.new("Kitchen_Camera", camera_data)
bpy.context.scene.collection.objects.link(camera)

camera.location = (4.4, -7.5, 4.1)

target = Vector((0, 0.75, 1.25))
direction = target - camera.location

camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
camera_data.lens = 32
camera_data.clip_end = 200

bpy.context.scene.camera = camera

# ============================================================
# RENDER SETTINGS - BLENDER 5.x
# ============================================================

scene = bpy.context.scene

scene.render.engine = "BLENDER_EEVEE"

scene.render.resolution_x = 1200
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100

scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.render.image_settings.color_depth = "8"

scene.render.filepath = PNG
scene.render.film_transparent = False

scene.world.color = (0.12, 0.12, 0.12)

scene.camera.data.dof.use_dof = False

scene.view_settings.view_transform = "AgX"

# ============================================================
# SAVE AND RENDER
# ============================================================

print("\n------------------------------------")
print("AI KITCHEN GENERATOR")
print("------------------------------------")
print("Style:", KITCHEN_STYLE)
print("Lighting:", LIGHTING_TONE)
print("Cabinet color:", CABINET_COLOR)
print("Counter color:", COUNTER_COLOR)
print("Blend output:", BLEND)
print("PNG output:", PNG)

bpy.ops.wm.save_as_mainfile(filepath=BLEND)
bpy.ops.render.render(write_still=True)

print("\nKITCHEN GENERATION COMPLETE")
print("Blend:", BLEND)
print("Render:", PNG)