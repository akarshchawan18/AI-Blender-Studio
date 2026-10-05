import bpy
import os
import mathutils


# ==========================================
# AI BLENDER STUDIO
# LIGHTING + CAMERA + RENDER
# ==========================================

print("================================")
print("AI BLENDER LIGHTING + CAMERA")
print("================================")


# ==========================================
# 1. CLEAR SCENE
# ==========================================

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

print("Scene cleared")


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

def create_box(name, location, dimensions):

    bpy.ops.mesh.primitive_cube_add(
        location=location
    )

    obj = bpy.context.object

    obj.name = name

    obj.dimensions = dimensions

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

def apply_material(obj, material):

    if obj is None:
        return

    obj.data.materials.clear()

    obj.data.materials.append(
        material
    )


# ==========================================
# 6. CREATE MATERIALS
# ==========================================

wall_material = create_material(
    "MAT_Wall",
    (0.72, 0.62, 0.48),
    0.75
)


floor_material = create_material(
    "MAT_Floor",
    (0.18, 0.07, 0.025),
    0.55
)


ceiling_material = create_material(
    "MAT_Ceiling",
    (0.8, 0.8, 0.8),
    0.9
)


sofa_material = create_material(
    "MAT_Sofa",
    (0.18, 0.20, 0.22),
    0.8
)


wood_material = create_material(
    "MAT_Wood",
    (0.15, 0.055, 0.02),
    0.5
)


black_material = create_material(
    "MAT_Black",
    (0.015, 0.015, 0.015),
    0.3
)


rug_material = create_material(
    "MAT_Rug",
    (0.35, 0.28, 0.20),
    0.95
)


print("Materials created")


# ==========================================
# 7. CREATE ROOM
# ==========================================

floor = create_box(
    "Floor",
    (0, 0, 0),
    (
        WIDTH,
        LENGTH,
        0.10
    )
)

apply_material(
    floor,
    floor_material
)


# ------------------------------------------
# BACK WALL
# ------------------------------------------

back = create_box(
    "Wall_Back",
    (
        0,
        LENGTH / 2,
        HEIGHT / 2
    ),
    (
        WIDTH,
        WALL_THICKNESS,
        HEIGHT
    )
)

apply_material(
    back,
    wall_material
)


# ------------------------------------------
# LEFT WALL
# ------------------------------------------

left = create_box(
    "Wall_Left",
    (
        -WIDTH / 2,
        0,
        HEIGHT / 2
    ),
    (
        WALL_THICKNESS,
        LENGTH,
        HEIGHT
    )
)

apply_material(
    left,
    wall_material
)


# ------------------------------------------
# RIGHT WALL
# ------------------------------------------

right = create_box(
    "Wall_Right",
    (
        WIDTH / 2,
        0,
        HEIGHT / 2
    ),
    (
        WALL_THICKNESS,
        LENGTH,
        HEIGHT
    )
)

apply_material(
    right,
    wall_material
)


# ------------------------------------------
# CEILING
# ------------------------------------------

ceiling = create_box(
    "Ceiling",
    (
        0,
        0,
        HEIGHT
    ),
    (
        WIDTH,
        LENGTH,
        0.10
    )
)

apply_material(
    ceiling,
    ceiling_material
)


print("Room created")


# ==========================================
# 8. SOFA
# ==========================================

# Sofa seat

seat = create_box(
    "Sofa_Seat",
    (
        0,
        0.7,
        0.45
    ),
    (
        2.4,
        0.85,
        0.35
    )
)

apply_material(
    seat,
    sofa_material
)


# Sofa back

back_sofa = create_box(
    "Sofa_Back",
    (
        0,
        1.05,
        1.0
    ),
    (
        2.4,
        0.25,
        1.1
    )
)

apply_material(
    back_sofa,
    sofa_material
)


# Sofa left arm

left_arm = create_box(
    "Sofa_Left_Arm",
    (
        -1.15,
        0.7,
        0.75
    ),
    (
        0.25,
        0.85,
        0.8
    )
)

apply_material(
    left_arm,
    sofa_material
)


# Sofa right arm

right_arm = create_box(
    "Sofa_Right_Arm",
    (
        1.15,
        0.7,
        0.75
    ),
    (
        0.25,
        0.85,
        0.8
    )
)

apply_material(
    right_arm,
    sofa_material
)


print("Sofa created")


# ==========================================
# 9. COFFEE TABLE
# ==========================================

table = create_box(
    "Coffee_Table",
    (
        0,
        -0.45,
        0.5
    ),
    (
        1.5,
        0.8,
        0.12
    )
)

apply_material(
    table,
    wood_material
)


# ==========================================
# 10. TV UNIT
# ==========================================

tv_unit = create_box(
    "TV_Unit",
    (
        0,
        -1.35,
        0.45
    ),
    (
        2.5,
        0.4,
        0.7
    )
)

apply_material(
    tv_unit,
    wood_material
)


# ==========================================
# 11. TV
# ==========================================

tv = create_box(
    "TV",
    (
        0,
        -1.58,
        1.55
    ),
    (
        2.2,
        0.08,
        1.25
    )
)

apply_material(
    tv,
    black_material
)


print("TV created")


# ==========================================
# 12. RUG
# ==========================================

rug = create_box(
    "Rug",
    (
        0,
        0,
        0.08
    ),
    (
        3.0,
        2.0,
        0.05
    )
)

apply_material(
    rug,
    rug_material
)


print("Rug created")


# ==========================================
# 13. LIGHT FUNCTION
# ==========================================

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

    light_data.energy = energy

    light_data.shape = "DISK"

    light_data.size = size

    light_object = bpy.data.objects.new(
        name,
        light_data
    )

    bpy.context.collection.objects.link(
        light_object
    )

    light_object.location = location

    return light_object


# ==========================================
# 14. KEY LIGHT
# ==========================================

key_light = create_area_light(
    "Key_Light",
    (-1.5, -1.0, 2.8),
    900,
    3.0
)


# ==========================================
# 15. FILL LIGHT
# ==========================================

fill_light = create_area_light(
    "Fill_Light",
    (2.0, 0.5, 2.2),
    500,
    2.5
)


# ==========================================
# 16. CEILING LIGHT
# ==========================================

ceiling_light = create_area_light(
    "Ceiling_Light",
    (0, 0, 2.9),
    700,
    2.0
)


print("Area lights created")


# ==========================================
# 17. WARM POINT LIGHT
# ==========================================

point_data = bpy.data.lights.new(
    name="Warm_Light",
    type="POINT"
)

point_data.energy = 150

point_data.color = (
    1.0,
    0.65,
    0.35
)


point = bpy.data.objects.new(
    "Warm_Light",
    point_data
)

bpy.context.collection.objects.link(
    point
)

point.location = (
    1.8,
    1.0,
    1.8
)


print("Warm light created")


# ==========================================
# 18. CAMERA
# ==========================================

camera_data = bpy.data.cameras.new(
    "AI_Camera"
)


camera = bpy.data.objects.new(
    "AI_Camera",
    camera_data
)


bpy.context.collection.objects.link(
    camera
)


camera.location = (
    4.2,
    -4.2,
    2.5
)


camera.data.lens = 24


# ==========================================
# 19. CAMERA LOOK AT
# ==========================================

target = (
    0,
    0,
    1.1
)


direction = (
    mathutils.Vector(target)
    - camera.location
)


camera.rotation_euler = (
    direction.to_track_quat(
        "-Z",
        "Y"
    ).to_euler()
)


bpy.context.scene.camera = camera


print("Camera created")


# ==========================================
# 20. WORLD LIGHT
# ==========================================

world = bpy.context.scene.world


# Make sure the world has a node tree.
# Blender 5.2 may already have one.

if world.node_tree is None:

    world.use_nodes = True


background = None

if world.node_tree:

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
    ].default_value = 0.25


print("World lighting configured")


# ==========================================
# 21. RENDER SETTINGS
# ==========================================

scene = bpy.context.scene


# Blender 5.2 EEVEE

scene.render.engine = "BLENDER_EEVEE"


# Resolution

scene.render.resolution_x = 800

scene.render.resolution_y = 600

scene.render.resolution_percentage = 100


# Image format

scene.render.image_settings.file_format = "PNG"


print("Render settings configured")


# ==========================================
# 22. PROJECT DIRECTORIES
# ==========================================

project_dir = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
)


render_dir = os.path.join(
    project_dir,
    "renders"
)


projects_dir = os.path.join(
    project_dir,
    "projects"
)


os.makedirs(
    render_dir,
    exist_ok=True
)


os.makedirs(
    projects_dir,
    exist_ok=True
)


# ==========================================
# 23. RENDER PATH
# ==========================================

render_path = os.path.join(
    render_dir,
    "living_room_test.png"
)


scene.render.filepath = render_path


print("Render output:")
print(render_path)


# ==========================================
# 24. RENDER
# ==========================================

print("================================")
print("STARTING RENDER")
print("================================")


result = bpy.ops.render.render(
    write_still=True
)


print("Render operation:")
print(result)


# ==========================================
# 25. SAVE BLEND FILE
# ==========================================

blend_path = os.path.join(
    projects_dir,
    "living_room_complete.blend"
)


bpy.ops.wm.save_as_mainfile(
    filepath=blend_path
)


# ==========================================
# 26. COMPLETE
# ==========================================

print("================================")
print("RENDER COMPLETE")
print("================================")


print("Blend file:")
print(blend_path)


print("Render:")
print(render_path)


print("================================")
print("AI BLENDER STUDIO TEST COMPLETE")
print("================================")