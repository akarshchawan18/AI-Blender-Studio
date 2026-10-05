import bpy
import os




# ==========================================
# AI BLENDER STUDIO
# MATERIAL SYSTEM
# ==========================================


def create_material(name, color, roughness=0.5, metallic=0.0):

    # Check whether material already exists
    material = bpy.data.materials.get(name)

    if material is None:
        material = bpy.data.materials.new(name=name)

    # Enable nodes
    material.use_nodes = True

    # Get Principled BSDF
    nodes = material.node_tree.nodes

    principled = nodes.get("Principled BSDF")

    if principled:

        # Base Color
        principled.inputs["Base Color"].default_value = (
            color[0],
            color[1],
            color[2],
            1.0
        )

        # Roughness
        principled.inputs["Roughness"].default_value = roughness

        # Metallic
        principled.inputs["Metallic"].default_value = metallic

    return material


def apply_material(object_name, material):

    obj = bpy.data.objects.get(object_name)

    if obj is None:
        print(f"Object not found: {object_name}")
        return

    # Clear existing material slots
    obj.data.materials.clear()

    # Add new material
    obj.data.materials.append(material)

    print(
        f"Material '{material.name}' applied to '{object_name}'"
    )


def setup_room_materials():

    print("Creating materials...")

    # --------------------------------------
    # WALL MATERIAL
    # --------------------------------------

    wall_material = create_material(
        "MAT_Wall_Cream",
        (0.72, 0.62, 0.48),
        roughness=0.75
    )

    # --------------------------------------
    # FLOOR MATERIAL
    # --------------------------------------

    floor_material = create_material(
        "MAT_Floor_Wood",
        (0.18, 0.07, 0.025),
        roughness=0.55
    )

    # --------------------------------------
    # CEILING MATERIAL
    # --------------------------------------

    ceiling_material = create_material(
        "MAT_Ceiling_White",
        (0.8, 0.8, 0.8),
        roughness=0.9
    )

    # --------------------------------------
    # APPLY WALL MATERIAL
    # --------------------------------------

    apply_material("Wall_Back", wall_material)
    apply_material("Wall_Front", wall_material)
    apply_material("Wall_Left", wall_material)
    apply_material("Wall_Right", wall_material)

    # --------------------------------------
    # APPLY FLOOR
    # --------------------------------------

    apply_material("Floor", floor_material)

    # --------------------------------------
    # APPLY CEILING
    # --------------------------------------

    apply_material("Ceiling", ceiling_material)

    print("All materials applied!")


# ------------------------------------------
# RUN
# ------------------------------------------

if __name__ == "__main__":

    setup_room_materials()

    print("================================")
    print("MATERIAL SETUP COMPLETE")
    print("================================")