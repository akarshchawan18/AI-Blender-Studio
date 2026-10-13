
import bpy
import math
import os
from mathutils import Vector
import json

PROJECT = r"C:\python 311\PyCharm Community Edition 2023.1.3\projects\AI-Blender-Studio"
BLEND_OUT = os.path.join(PROJECT, "projects", "AI_Interior_Realistic.blend")
RENDER_OUT = os.path.join(PROJECT, "renders", "AI_Interior_Realistic.png")

CONFIG_FILE = os.path.join(PROJECT, "projects", "kitchen_prompt.json")

# Default settings if a prompt setting is missing.
CABINET_COLOR = (0.075, 0.19, 0.15)
COUNTER_COLOR = (0.80, 0.77, 0.70)
LIGHTING_TONE = "warm"
KITCHEN_STYLE = "modern"


def load_kitchen_config():
    global CABINET_COLOR, COUNTER_COLOR
    global LIGHTING_TONE, KITCHEN_STYLE

    if not os.path.isfile(CONFIG_FILE):
        print("WARNING: Kitchen config not found:", CONFIG_FILE)
        return

    with open(CONFIG_FILE, "r", encoding="utf-8") as config_file:
        settings = json.load(config_file)

    def read_color(value, fallback):
        if isinstance(value, (list, tuple)) and len(value) >= 3:
            return tuple(
                max(0.0, min(1.0, float(component)))
                for component in value[:3]
            )
        return fallback

    CABINET_COLOR = read_color(
        settings.get("cabinet_color"), CABINET_COLOR
    )
    COUNTER_COLOR = read_color(
        settings.get("counter_color"), COUNTER_COLOR
    )

    tone = str(settings.get("lighting_tone", "warm")).lower()
    LIGHTING_TONE = tone if tone in ("warm", "cool", "neutral") else "warm"

    style = str(settings.get("style", "modern")).lower()
    KITCHEN_STYLE = (
        style
        if style in ("modern", "luxury", "scandinavian", "minimalist")
        else "modern"
    )

    print("Loaded kitchen settings:")
    print("Style:", KITCHEN_STYLE)
    print("Cabinet:", CABINET_COLOR)
    print("Countertop:", COUNTER_COLOR)
    print("Lighting:", LIGHTING_TONE)


load_kitchen_config()
PROJECT = r"C:\python 311\PyCharm Community Edition 2023.1.3\projects\AI-Blender-Studio"
BLEND_OUT = os.path.join(PROJECT, "projects", "AI_Interior_Realistic.blend")
RENDER_OUT = os.path.join(PROJECT, "renders", "AI_Interior_Realistic.png")

# Clear only the new scene being generated
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.samples = 32
scene.cycles.use_denoising = True
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100


def mat(name, color, roughness=0.4, metallic=0.0, texture="plain"):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True

    nodes = m.node_tree.nodes
    links = m.node_tree.links

    p = nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Roughness"].default_value = roughness
    p.inputs["Metallic"].default_value = metallic

    if texture == "wood":
        wave = nodes.new("ShaderNodeTexWave")
        wave.name = "Natural Wood Grain"
        wave.inputs["Scale"].default_value = 3.0
        wave.inputs["Distortion"].default_value = 7.0
        wave.inputs["Detail"].default_value = 3.0

        ramp = nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position = 0.18
        ramp.color_ramp.elements[0].color = (
            0.12, 0.045, 0.018, 1
        )
        ramp.color_ramp.elements[1].position = 0.82
        ramp.color_ramp.elements[1].color = (
            0.48, 0.25, 0.10, 1
        )

        links.new(wave.outputs["Color"], ramp.inputs["Fac"])
        links.new(ramp.outputs["Color"], p.inputs["Base Color"])

    elif texture in ("stone", "floor", "wall"):
        noise = nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = {
            "stone": 22.0,
            "floor": 35.0,
            "wall": 45.0,
        }[texture]
        noise.inputs["Detail"].default_value = 4.0
        noise.inputs["Roughness"].default_value = 0.7

        ramp = nodes.new("ShaderNodeValToRGB")

        if texture == "stone":
            ramp.color_ramp.elements[0].color = (
                0.018, 0.020, 0.022, 1
            )
            ramp.color_ramp.elements[1].color = (
                0.16, 0.17, 0.18, 1
            )

        elif texture == "floor":
            ramp.color_ramp.elements[0].color = (
                0.22, 0.18, 0.14, 1
            )
            ramp.color_ramp.elements[1].color = (
                0.43, 0.37, 0.30, 1
            )

        else:
            ramp.color_ramp.elements[0].color = (
                0.60, 0.55, 0.48, 1
            )
            ramp.color_ramp.elements[1].color = (
                0.76, 0.72, 0.65, 1
            )

        links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
        links.new(ramp.outputs["Color"], p.inputs["Base Color"])

    return m

def box(name, loc, dims, material, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(material)
    if bevel:
        b = o.modifiers.new("Soft edges", "BEVEL")
        b.width = bevel
        b.segments = 3
        o.modifiers.new("Weighted normals", "WEIGHTED_NORMAL")
    return o

def cylinder(name, loc, radius, depth, material, rotation=None):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32, radius=radius, depth=depth, location=loc
    )
    o = bpy.context.object
    o.name = name
    o.data.materials.append(material)
    if rotation:
        o.rotation_euler = rotation
    b = o.modifiers.new("Soft edges", "BEVEL")
    b.width = min(0.01, depth * 0.15)
    b.segments = 2
    return o

def ring(name, loc, radius, thickness, material):
    bpy.ops.mesh.primitive_torus_add(
        major_radius=radius, minor_radius=thickness,
        major_segments=40, minor_segments=10, location=loc
    )
    o = bpy.context.object
    o.name = name
    o.data.materials.append(material)
    return o

def aim(obj, target):
    obj.rotation_euler = (
        Vector(target) - obj.location
    ).to_track_quat("-Z", "Y").to_euler()


# Materials

# Style-dependent colors must be defined before creating materials.
if KITCHEN_STYLE == "scandinavian":
    WOOD_COLOR = (0.48, 0.32, 0.18)
    WALL_COLOR = (0.88, 0.86, 0.80)
    FLOOR_COLOR = (0.58, 0.49, 0.37)

elif KITCHEN_STYLE == "luxury":
    WOOD_COLOR = (0.20, 0.075, 0.025)
    WALL_COLOR = (0.78, 0.74, 0.66)
    FLOOR_COLOR = (0.24, 0.20, 0.16)

elif KITCHEN_STYLE == "minimalist":
    WOOD_COLOR = (0.30, 0.28, 0.25)
    WALL_COLOR = (0.82, 0.82, 0.79)
    FLOOR_COLOR = (0.40, 0.40, 0.38)

else:
    WOOD_COLOR = (0.32, 0.15, 0.06)
    WALL_COLOR = (0.72, 0.68, 0.60)
    FLOOR_COLOR = (0.38, 0.33, 0.27)


ivory = mat(
    "Custom Cabinet Finish",
    CABINET_COLOR,
    0.26,
    texture="plain"
)

wood = mat(
    "Oak Wood",
    WOOD_COLOR,
    0.4,
    texture="wood"
)

stone = mat(
    "Custom Quartz Countertop",
    COUNTER_COLOR,
    0.28,
    texture="plain"
)

wall = mat(
    "Warm Plaster",
    WALL_COLOR,
    0.85,
    texture="wall"
)

floor = mat(
    "Porcelain Floor",
    FLOOR_COLOR,
    0.34,
    texture="floor"
)

steel = mat(
    "Brushed Stainless Steel",
    (0.48, 0.52, 0.55),
    0.24,
    0.7
)

black = mat(
    "Black Appliance Glass",
    (0.012, 0.016, 0.02),
    0.13,
    0.2
)

dark = mat(
    "Sink Interior",
    (0.025, 0.03, 0.032),
    0.35
)

burner = mat(
    "Burner Metal",
    (0.045, 0.05, 0.052),
    0.3,
    0.6
)


# Room shell
W, L, H = 4.572, 3.658, 3.048

box("Floor", (0, 0, -0.12), (W, L, 0.24), floor, 0.02)
box("Back Wall", (0, L/2+0.08, H/2), (W, 0.16, H), wall)
box("Left Wall", (-W/2-0.08, 0, H/2), (0.16, L, H), wall)
box("Right Wall", (W/2+0.08, 0, H/2), (0.16, L, H), wall)


# Lower cabinets and countertop
cx, cy, run_w, depth = -0.10, L/2-0.48, 3.55, 0.62
front_y = cy-depth/2-0.025

box("Toe Kick", (cx, cy-0.10, 0.12),
    (run_w, 0.10, 0.13), wood, 0.015)

box("Lower Cabinet Base", (cx, cy, 0.43),
    (run_w, depth, 0.62), ivory, 0.015)

box("Stone Countertop", (cx, cy-0.02, 0.79),
    (run_w+0.10, depth+0.08, 0.075), stone, 0.025)

box("Wood Backsplash", (cx, L/2-0.18, 1.17),
    (run_w, 0.045, 0.64), wood, 0.01)


# Six separate lower fronts with handles
door_w = 0.57
start_x = cx-run_w/2+door_w/2+0.025

for i in range(6):
    x = start_x+i*door_w

    if i in (2, 3):
        for j, z in enumerate((0.31, 0.55)):
            box(
                f"Drawer {i}-{j}",
                (x, front_y, z),
                (door_w-0.035, 0.035, 0.21),
                ivory,
                0.012
            )

            box(
                f"Drawer Pull {i}-{j}",
                (x, front_y-0.026, z+0.045),
                (0.16, 0.025, 0.018),
                steel,
                0.006
            )
    else:
        box(
            f"Cabinet Door {i}",
            (x, front_y, 0.43),
            (door_w-0.035, 0.035, 0.52),
            ivory,
            0.012
        )

        hx = x+(0.19 if i % 2 == 0 else -0.19)

        box(
            f"Cabinet Handle {i}",
            (hx, front_y-0.03, 0.44),
            (0.018, 0.025, 0.17),
            steel,
            0.006
        )


# Sink and faucet
sx, sy = -0.90, cy-0.02

box("Sink Rim", (sx, sy, 0.834),
    (0.78, 0.43, 0.025), steel, 0.02)

box("Sink Basin", (sx, sy-0.005, 0.849),
    (0.65, 0.31, 0.012), dark, 0.025)

cylinder("Faucet Base", (sx, sy+0.24, 0.86),
         0.045, 0.025, steel)

cylinder("Faucet Stem", (sx, sy+0.24, 1.01),
         0.018, 0.27, steel)

cylinder(
    "Faucet Spout",
    (sx, sy+0.13, 1.14),
    0.018,
    0.22,
    steel,
    rotation=(math.radians(90), 0, 0)
)

cylinder("Faucet Outlet", (sx, sy+0.025, 1.10),
         0.015, 0.07, steel)


# Black cooktop with four burner rings
hx, hy = 0.52, sy-0.01

box("Black Glass Hob", (hx, hy, 0.836),
    (0.82, 0.47, 0.018), black, 0.015)

for x in (hx-0.21, hx+0.21):
    for y in (hy-0.12, hy+0.11):
        ring("Burner Ring", (x, y, 0.85),
             0.078, 0.009, burner)

        ring("Inner Burner Ring", (x, y, 0.852),
             0.044, 0.005, steel)

        cylinder("Burner Cap", (x, y, 0.85),
                 0.025, 0.009, burner)


# Upper cabinets with separate doors
uz, uy, uw = 2.05, L/2-0.42, 3.12

box("Upper Cabinet Base", (cx, uy, uz),
    (uw, 0.48, 0.88), ivory, 0.015)

uy_front = uy-0.25
section = uw/5

for i in range(5):
    x = cx-uw/2+section*(i+0.5)

    box(
        f"Upper Door {i}",
        (x, uy_front-0.015, uz),
        (section-0.025, 0.035, 0.82),
        ivory,
        0.012
    )

    box(
        f"Upper Handle {i}",
        (x+section*0.26, uy_front-0.04, uz-0.28),
        (0.11, 0.022, 0.016),
        steel,
        0.006
    )


# Refrigerator and details
fx, fy = 1.92, cy-0.01

box("Refrigerator Body", (fx, fy, 1.12),
    (0.70, 0.66, 2.18), steel, 0.04)

box("Refrigerator Door", (fx, fy-0.34, 1.12),
    (0.65, 0.035, 2.10), steel, 0.025)

box("Freezer Divider", (fx, fy-0.365, 0.72),
    (0.63, 0.012, 0.018), dark)

box("Water Dispenser", (fx-0.16, fy-0.37, 1.15),
    (0.15, 0.018, 0.34), black, 0.012)

box("Fridge Handle Upper", (fx+0.23, fy-0.39, 1.50),
    (0.022, 0.022, 0.40), black, 0.008)

box("Fridge Handle Lower", (fx+0.23, fy-0.39, 0.87),
    (0.022, 0.022, 0.30), black, 0.008)


# Simple countertop props
box("Oak Chopping Board", (0.0, sy-0.12, 0.852),
    (0.38, 0.23, 0.025), wood, 0.015)

cylinder("Utensil Holder", (1.20, sy-0.10, 0.93),
         0.065, 0.15, steel)

for i, xo in enumerate((-0.025, 0.0, 0.025)):
    cylinder(
        f"Utensil {i}",
        (1.20+xo, sy-0.10, 1.07),
        0.006,
        0.20,
        wood
    )


# Lighting and world
world = (
    bpy.data.worlds.new("Kitchen World")
    if not bpy.data.worlds
    else bpy.data.worlds[0]
)

scene.world = world
world.use_nodes = True

world.node_tree.nodes["Background"].inputs["Color"].default_value = (
    0.34, 0.38, 0.43, 1
)

world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.32

def area(name, loc, power, color, size, target):
    d = bpy.data.lights.new(name, "AREA")
    d.energy, d.color, d.shape, d.size = power, color, "DISK", size
    o = bpy.data.objects.new(name, d)
    scene.collection.objects.link(o)
    o.location = loc
    aim(o, target)


# Select light colors from the API prompt settings.
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


area(
    "Warm Softbox",
    (-3.2, -3.0, 4.6),
    520,
    key_color,
    4.0,
    (0, 0.8, 1.2)
)

area(
    "Cool Fill",
    (3.0, -2.0, 3.2),
    350,
    fill_color,
    3.0,
    (0.5, 0.8, 1.2)
)

area(
    "Ceiling Bounce",
    (0, 1.1, 2.85),
    280,
    bounce_color,
    2.5,
    (0, 0.8, 1.0)
)

# Camera
bpy.ops.object.camera_add(location=(0.0, -6.7, 2.55))
camera = bpy.context.object
camera.name = "Kitchen Camera"
aim(camera, (0.0, 0.75, 1.42))
camera.data.lens = 43
scene.camera = camera

scene.view_settings.view_transform = "AgX"
scene.view_settings.look = "AgX - Medium High Contrast"
scene.render.filepath = RENDER_OUT

os.makedirs(os.path.dirname(BLEND_OUT), exist_ok=True)
os.makedirs(os.path.dirname(RENDER_OUT), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUT)
bpy.ops.render.render(write_still=True)
print("KITCHEN GENERATION COMPLETE")
print("BLEND:", BLEND_OUT)
print("RENDER:", RENDER_OUT)