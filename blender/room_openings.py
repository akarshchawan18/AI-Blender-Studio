import bpy
import os


# ==========================================
# AI BLENDER STUDIO
# ROOM + DOOR + WINDOWS
# ==========================================

print("================================")
print("AI BLENDER ROOM + OPENINGS")
print("================================")


# ==========================================
# 1. CLEAR SCENE
# ==========================================

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

print("Old scene cleared")


# ==========================================
# 2. ROOM DIMENSIONS
# ==========================================

WIDTH = 4.572
LENGTH = 3.658
HEIGHT = 3.048

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

    principled = material.node_tree.nodes.get(
        "Principled BSDF"
    )

    if principled:

        principled.inputs[
            "Base Color"
        ].default_value = (
            color[0],
            color[1],
            color[2],
            1
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

    if obj:

        obj.data.materials.clear()

        obj.data.materials.append(material)

        print(
            "Material applied:",
            object_name
        )


# ==========================================
# 6. MATERIALS
# ==========================================

wall_material = create_material(
    "MAT_Wall_Cream",
    (0.72, 0.62, 0.48),
    0.75
)

floor_material = create_material(
    "MAT_Floor_Wood",
    (0.18, 0.07, 0.025),
    0.55
)

ceiling_material = create_material(
    "MAT_Ceiling_White",
    (0.8, 0.8, 0.8),
    0.9
)

door_material = create_material(
    "MAT_Door_Wood",
    (0.12, 0.045, 0.015),
    0.4
)

frame_material = create_material(
    "MAT_Frame_White",
    (0.85, 0.85, 0.82),
    0.45
)

glass_material = create_material(
    "MAT_Glass",
    (0.25, 0.55, 0.8),
    0.1
)


# ==========================================
# 7. FLOOR
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
    (0, 0, HEIGHT),
    (
        WIDTH / 2,
        LENGTH / 2,
        0.05
    )
)

print("Ceiling created")


# ==========================================
# 13. DOOR
# ==========================================

DOOR_WIDTH = 0.9
DOOR_HEIGHT = 2.1
DOOR_THICKNESS = 0.08


door = create_box(
    "Door",
    (
        -1.0,
        -LENGTH / 2 - 0.01,
        DOOR_HEIGHT / 2
    ),
    (
        DOOR_WIDTH / 2,
        DOOR_THICKNESS / 2,
        DOOR_HEIGHT / 2
    )
)

print("Door created")


# ==========================================
# 14. DOOR FRAME
# ==========================================

FRAME = 0.08


# Left frame

create_box(
    "Door_Frame_Left",
    (
        -1.0 - DOOR_WIDTH / 2 - FRAME / 2,
        -LENGTH / 2 - 0.06,
        DOOR_HEIGHT / 2
    ),
    (
        FRAME / 2,
        0.06,
        DOOR_HEIGHT / 2 + FRAME
    )
)


# Right frame

create_box(
    "Door_Frame_Right",
    (
        -1.0 + DOOR_WIDTH / 2 + FRAME / 2,
        -LENGTH / 2 - 0.06,
        DOOR_HEIGHT / 2
    ),
    (
        FRAME / 2,
        0.06,
        DOOR_HEIGHT / 2 + FRAME
    )
)


# Top frame

create_box(
    "Door_Frame_Top",
    (
        -1.0,
        -LENGTH / 2 - 0.06,
        DOOR_HEIGHT + FRAME / 2
    ),
    (
        DOOR_WIDTH / 2 + FRAME,
        0.06,
        FRAME / 2
    )
)

print("Door frame created")


# ==========================================
# 15. WINDOW FUNCTION
# ==========================================

def create_window(name, x_position):

    WINDOW_WIDTH = 1.2
    WINDOW_HEIGHT = 1.1

    window_z = 1.7

    # Glass

    create_box(
        name + "_Glass",
        (
            x_position,
            -LENGTH / 2 - 0.02,
            window_z
        ),
        (
            WINDOW_WIDTH / 2,
            0.025,
            WINDOW_HEIGHT / 2
        )
    )

    # Left frame

    create_box(
        name + "_Left",
        (
            x_position - WINDOW_WIDTH / 2,
            -LENGTH / 2 - 0.06,
            window_z
        ),
        (
            0.04,
            0.06,
            WINDOW_HEIGHT / 2 + 0.04
        )
    )

    # Right frame

    create_box(
        name + "_Right",
        (
            x_position + WINDOW_WIDTH / 2,
            -LENGTH / 2 - 0.06,
            window_z
        ),
        (
            0.04,
            0.06,
            WINDOW_HEIGHT / 2 + 0.04
        )
    )

    # Top frame

    create_box(
        name + "_Top",
        (
            x_position,
            -LENGTH / 2 - 0.06,
            window_z + WINDOW_HEIGHT / 2
        ),
        (
            WINDOW_WIDTH / 2,
            0.06,
            0.04
        )
    )

    # Bottom frame

    create_box(
        name + "_Bottom",
        (
            x_position,
            -LENGTH / 2 - 0.06,
            window_z - WINDOW_HEIGHT / 2
        ),
        (
            WINDOW_WIDTH / 2,
            0.06,
            0.04
        )

    )

    print("Window created:", name)


# ==========================================
# 16. WINDOWS
# ==========================================

create_window(
    "Window_01",
    0.8
)

create_window(
    "Window_02",
    2.0
)


# ==========================================
# 17. APPLY MATERIALS
# ==========================================

apply_material(
    "Floor",
    floor_material
)

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

apply_material(
    "Ceiling",
    ceiling_material
)

apply_material(
    "Door",
    door_material
)

apply_material(
    "Door_Frame_Left",
    frame_material
)

apply_material(
    "Door_Frame_Right",
    frame_material
)

apply_material(
    "Door_Frame_Top",
    frame_material
)


# ==========================================
# WINDOW MATERIALS
# ==========================================

for obj in bpy.data.objects:

    if obj.name.startswith("Window_"):

        if "Glass" in obj.name:

            apply_material(
                obj.name,
                glass_material
            )

        else:

            apply_material(
                obj.name,
                frame_material
            )


# ==========================================
# 18. SAVE
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
    "room_openings.blend"
)

bpy.ops.wm.save_as_mainfile(
    filepath=blend_path
)


# ==========================================
# 19. COMPLETE
# ==========================================

print("================================")
print("ROOM + DOOR + WINDOWS COMPLETE")
print("================================")

print("Project saved:")
print(blend_path)

print("================================")