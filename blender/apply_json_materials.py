import bpy
import json
import os


print("================================")
print("DAY 9 - JSON MATERIAL SYSTEM")
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


# =========================================================
# LOAD JSON
# =========================================================

with open(
    JSON_PATH,
    "r",
    encoding="utf-8"
) as file:

    scene_data = json.load(file)


materials_data = scene_data["materials"]


print("Materials loaded from JSON")


# =========================================================
# HEX → RGB
# =========================================================

def hex_to_rgba(hex_color):

    hex_color = hex_color.replace("#", "")

    if len(hex_color) != 6:

        raise ValueError(
            "Invalid HEX color: " + hex_color
        )

    r = int(
        hex_color[0:2],
        16
    ) / 255

    g = int(
        hex_color[2:4],
        16
    ) / 255

    b = int(
        hex_color[4:6],
        16
    ) / 255

    return (
        r,
        g,
        b,
        1.0
    )


# =========================================================
# CREATE MATERIAL
# =========================================================

def create_material(
    name,
    hex_color,
    roughness=0.5,
    metallic=0.0
):

    color = hex_to_rgba(
        hex_color
    )


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
        ].default_value = color


        principled.inputs[
            "Roughness"
        ].default_value = roughness


        principled.inputs[
            "Metallic"
        ].default_value = metallic


    print(
        "Created material:",
        name,
        hex_color
    )


    return material


# =========================================================
# CREATE MATERIALS
# =========================================================

wall_material = create_material(
    "JSON_Wall",
    materials_data["wall"],
    roughness=0.8
)


floor_material = create_material(
    "JSON_Floor",
    materials_data["floor"],
    roughness=0.65
)


ceiling_material = create_material(
    "JSON_Ceiling",
    materials_data["ceiling"],
    roughness=0.9
)


sofa_material = create_material(
    "JSON_Sofa",
    materials_data["sofa"],
    roughness=0.9
)


wood_material = create_material(
    "JSON_Wood",
    materials_data["wood"],
    roughness=0.45
)


black_material = create_material(
    "JSON_Black",
    materials_data["black"],
    roughness=0.3
)


# =========================================================
# ASSIGN MATERIAL TO OBJECT
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
# APPLY MATERIALS TO ROOM
# =========================================================

for obj in bpy.context.scene.objects:

    if obj.name == "Floor":

        assign_material(
            obj,
            floor_material
        )


    elif obj.name.startswith("Wall_"):

        assign_material(
            obj,
            wall_material
        )


    elif obj.name == "Ceiling":

        assign_material(
            obj,
            ceiling_material
        )


# =========================================================
# APPLY MATERIALS TO FURNITURE
# =========================================================

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


print("================================")
print("MATERIAL APPLICATION COMPLETE")
print("================================")