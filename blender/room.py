import bpy
import os


# ==========================================
# AI BLENDER STUDIO
# ROOM + MATERIAL GENERATOR
# ==========================================

print("================================")
print("AI BLENDER ROOM GENERATOR")
print("================================")


# ==========================================
# 1. DELETE EVERYTHING
# ==========================================

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

print("Old scene cleared")


# ==========================================
# 2. ROOM DIMENSIONS
# ==========================================

WIDTH = 4.572       # 15 feet
LENGTH = 3.658      # 12 feet
HEIGHT = 3.048      # 10 feet

WALL_THICKNESS = 0.15


# ==========================================
# 3. CREATE BOX
# ==========================================

def create_box(name, location, scale):

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

    return obj


# ==========================================
# 4. CREATE MATERIAL
# ==========================================

def create_material(
    name,
    color,
    roughness=0.5,
    metallic=0.0
):

    material = bpy.data.materials.get(name)

    if material is None:

        material = bpy.data.materials.new(
            name=name
        )

    material.use_nodes = True

    nodes = material.node_tree.nodes

    principled = nodes.get("Principled BSDF")

    if principled:

        principled.inputs[
            "Base Color"
        ].default_value = (
            color[0],
            color[1],
            color[2],
            1.0
        )

        principled.inputs[
            "Roughness"
        ].default_value = roughness

        principled.inputs[
            "Metallic"
        ].default_value = metallic

    return material


# ==========================================
# 5. APPLY MATERIAL
# ==========================================

def apply_material(object_name, material):

    obj = bpy.data.objects.get(object_name)

    if obj is None:

        print(
            f"Object not found: {object_name}"
        )

        return

    obj.data.materials.clear()

    obj.data.materials.append(material)

    print(
        f"Material '{material.name}' "
        f"applied to '{object_name}'"
    )


# ==========================================
# 6. ROOM MATERIALS
# ==========================================

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

    apply_material(
        "Wall_Back",
        wall_material
    )

    apply_material(
        "Wall_Front",
        wall_material
    )

    apply_material(
        "Wall_Left",
        wall_material
    )

    apply_material(
        "Wall_Right",
        wall_material
    )


    # --------------------------------------
    # APPLY FLOOR MATERIAL
    # --------------------------------------

    apply_material(
        "Floor",
        floor_material
    )


    # --------------------------------------
    # APPLY CEILING MATERIAL
    # --------------------------------------

    apply_material(
        "Ceiling",
        ceiling_material
    )


    print("All materials applied!")


# ==========================================
# 7. CREATE FLOOR
# ==========================================

create_box(
    "Floor",
    (0, 0, 0),
    (
        WIDTH / 2,
        LENGTH / 2,
        0.05
    )
)

print("Floor created")


# ==========================================
# 8. BACK WALL
# ==========================================

create_box(
    "Wall_Back",
    (
        0,
        LENGTH / 2,
        HEIGHT / 2
    ),
    (
        WIDTH / 2,
        WALL_THICKNESS / 2,
        HEIGHT / 2
    )
)

print("Back wall created")


# ==========================================
# 9. FRONT WALL
# ==========================================

create_box(
    "Wall_Front",
    (
        0,
        -LENGTH / 2,
        HEIGHT / 2
    ),
    (
        WIDTH / 2,
        WALL_THICKNESS / 2,
        HEIGHT / 2
    )
)

print("Front wall created")


# ==========================================
# 10. LEFT WALL
# ==========================================

create_box(
    "Wall_Left",
    (
        -WIDTH / 2,
        0,
        HEIGHT / 2
    ),
    (
        WALL_THICKNESS / 2,
        LENGTH / 2,
        HEIGHT / 2
    )
)

print("Left wall created")


# ==========================================
# 11. RIGHT WALL
# ==========================================

create_box(
    "Wall_Right",
    (
        WIDTH / 2,
        0,
        HEIGHT / 2
    ),
    (
        WALL_THICKNESS / 2,
        LENGTH / 2,
        HEIGHT / 2
    )
)

print("Right wall created")


# ==========================================
# 12. CEILING
# ==========================================

create_box(
    "Ceiling",
    (
        0,
        0,
        HEIGHT
    ),
    (
        WIDTH / 2,
        LENGTH / 2,
        0.05
    )
)

print("Ceiling created")


# ==========================================
# 13. APPLY MATERIALS
# ==========================================

setup_room_materials()


# ==========================================
# 14. SAVE BLENDER PROJECT
# ==========================================

project_dir = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "projects"
    )
)

os.makedirs(
    project_dir,
    exist_ok=True
)


blend_path = os.path.join(
    project_dir,
    "room_materials.blend"
)


bpy.ops.wm.save_as_mainfile(
    filepath=blend_path
)


# ==========================================
# 15. FINISHED
# ==========================================

print("================================")
print("ROOM + MATERIALS COMPLETE")
print("================================")

print("Project saved:")
print(blend_path)

print("================================")