import bpy
import os
import mathutils


# ============================================================
# AI BLENDER STUDIO
# DAY 7
# COMPLETE INTERIOR GENERATOR
# ============================================================

print("==========================================")
print("AI BLENDER STUDIO - DAY 7")
print("COMPLETE INTERIOR GENERATOR")
print("==========================================")


# ============================================================
# 1. PROJECT PATHS
# ============================================================

PROJECT_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
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


# ============================================================
# 2. ROOM SETTINGS
# ============================================================

WIDTH = 4.572
LENGTH = 3.658
HEIGHT = 3.048

WALL_THICKNESS = 0.15


# ============================================================
# 3. CLEAR SCENE
# ============================================================

def clear_scene():

    print("Clearing scene...")

    bpy.ops.object.select_all(action="SELECT")

    bpy.ops.object.delete(
        use_global=False
    )

    # Remove unused collections of objects
    for datablocks in (
        bpy.data.meshes,
        bpy.data.curves,
        bpy.data.materials,
        bpy.data.cameras,
        bpy.data.lights,
    ):

        for datablock in list(datablocks):

            if datablock.users == 0:

                datablocks.remove(
                    datablock
                )

    print("Scene cleared")


# ============================================================
# 4. CREATE BOX
# ============================================================

def create_box(
    name,
    location,
    dimensions,
    material=None
):

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

    if material:

        obj.data.materials.append(
            material
        )

    return obj


# ============================================================
# 5. CREATE MATERIAL
# ============================================================

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

    principled = nodes.get(
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


# ============================================================
# 6. MATERIAL LIBRARY
# ============================================================

def create_materials():

    print("Creating materials...")

    materials = {}

    materials["wall"] = create_material(
        "MAT_Wall_Cream",
        (0.72, 0.62, 0.48),
        0.75
    )

    materials["floor"] = create_material(
        "MAT_Floor_Wood",
        (0.18, 0.07, 0.025),
        0.55
    )

    materials["ceiling"] = create_material(
        "MAT_Ceiling_White",
        (0.8, 0.8, 0.8),
        0.9
    )

    materials["sofa"] = create_material(
        "MAT_Sofa",
        (0.18, 0.20, 0.22),
        0.8
    )

    materials["wood"] = create_material(
        "MAT_Wood",
        (0.15, 0.055, 0.02),
        0.5
    )

    materials["black"] = create_material(
        "MAT_Black",
        (0.015, 0.015, 0.015),
        0.3
    )

    materials["rug"] = create_material(
        "MAT_Rug",
        (0.35, 0.28, 0.20),
        0.95
    )

    materials["door"] = create_material(
        "MAT_Door",
        (0.25, 0.10, 0.035),
        0.55
    )

    materials["frame"] = create_material(
        "MAT_Frame",
        (0.03, 0.03, 0.03),
        0.3
    )

    materials["glass"] = create_material(
        "MAT_Glass",
        (0.12, 0.35, 0.50),
        0.15
    )

    return materials


# ============================================================
# 7. CREATE ROOM
# ============================================================

def create_room(materials):

    print("Creating room...")

    # Floor
    create_box(
        "Floor",
        (0, 0, 0),
        (
            WIDTH,
            LENGTH,
            0.10
        ),
        materials["floor"]
    )

    # Back wall
    create_box(
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
        ),
        materials["wall"]
    )

    # Left wall
    create_box(
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
        ),
        materials["wall"]
    )

    # Right wall
    create_box(
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
        ),
        materials["wall"]
    )

    # Ceiling
    create_box(
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
        ),
        materials["ceiling"]
    )

    print("Room created")


# ============================================================
# 8. CREATE DOOR
# ============================================================

def create_door(materials):

    print("Creating door...")

    door_width = 0.9
    door_height = 2.1

    # Door panel
    create_box(
        "Door",
        (
            -1.3,
            (LENGTH / 2) - 0.09,
            door_height / 2
        ),
        (
            door_width,
            0.08,
            door_height
        ),
        materials["door"]
    )

    # Left frame
    create_box(
        "Door_Frame_Left",
        (
            -1.3 - door_width / 2 - 0.06,
            (LENGTH / 2) - 0.10,
            door_height / 2
        ),
        (
            0.08,
            0.10,
            door_height + 0.15
        ),
        materials["frame"]
    )

    # Right frame
    create_box(
        "Door_Frame_Right",
        (
            -1.3 + door_width / 2 + 0.06,
            (LENGTH / 2) - 0.10,
            door_height / 2
        ),
        (
            0.08,
            0.10,
            door_height + 0.15
        ),
        materials["frame"]
    )

    # Top frame
    create_box(
        "Door_Frame_Top",
        (
            -1.3,
            (LENGTH / 2) - 0.10,
            door_height + 0.075
        ),
        (
            door_width + 0.20,
            0.10,
            0.08
        ),
        materials["frame"]
    )

    print("Door created")


# ============================================================
# 9. CREATE WINDOW
# ============================================================

def create_window(
    name,
    location,
    materials
):

    window_width = 1.3
    window_height = 1.2

    x, y, z = location

    # Glass
    create_box(
        name + "_Glass",
        location,
        (
            window_width,
            0.06,
            window_height
        ),
        materials["glass"]
    )

    # Bottom frame
    create_box(
        name + "_Bottom",
        (
            x,
            y - 0.05,
            z - window_height / 2
        ),
        (
            window_width + 0.12,
            0.10,
            0.08
        ),
        materials["frame"]
    )

    # Top frame
    create_box(
        name + "_Top",
        (
            x,
            y - 0.05,
            z + window_height / 2
        ),
        (
            window_width + 0.12,
            0.10,
            0.08
        ),
        materials["frame"]
    )

    # Left frame
    create_box(
        name + "_Left",
        (
            x - window_width / 2,
            y - 0.05,
            z
        ),
        (
            0.08,
            0.10,
            window_height
        ),
        materials["frame"]
    )

    # Right frame
    create_box(
        name + "_Right",
        (
            x + window_width / 2,
            y - 0.05,
            z
        ),
        (
            0.08,
            0.10,
            window_height
        ),
        materials["frame"]
    )

    print(name + " created")


# ============================================================
# 10. CREATE WINDOWS
# ============================================================

def create_windows(materials):

    print("Creating windows...")

    # Back wall windows
    create_window(
        "Window_Left",
        (-1.5, LENGTH / 2 - 0.08, 1.8),
        materials
    )

    create_window(
        "Window_Right",
        (1.5, LENGTH / 2 - 0.08, 1.8),
        materials
    )

    print("Windows created")


# ============================================================
# 11. CREATE SOFA
# ============================================================

def create_sofa(materials):

    print("Creating sofa...")

    # Seat
    create_box(
        "Sofa_Seat",
        (
            0,
            0.75,
            0.45
        ),
        (
            2.4,
            0.85,
            0.35
        ),
        materials["sofa"]
    )

    # Back
    create_box(
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
        ),
        materials["sofa"]
    )

    # Left arm
    create_box(
        "Sofa_Left_Arm",
        (
            -1.15,
            0.75,
            0.75
        ),
        (
            0.25,
            0.85,
            0.8
        ),
        materials["sofa"]
    )

    # Right arm
    create_box(
        "Sofa_Right_Arm",
        (
            1.15,
            0.75,
            0.75
        ),
        (
            0.25,
            0.85,
            0.8
        ),
        materials["sofa"]
    )

    print("Sofa created")


# ============================================================
# 12. COFFEE TABLE
# ============================================================

def create_coffee_table(materials):

    print("Creating coffee table...")

    create_box(
        "Coffee_Table_Top",
        (
            0,
            -0.45,
            0.5
        ),
        (
            1.5,
            0.8,
            0.12
        ),
        materials["wood"]
    )

    # Legs
    leg_positions = [
        (-0.60, -0.75),
        (0.60, -0.75),
        (-0.60, -0.15),
        (0.60, -0.15)
    ]

    for index, (x, y) in enumerate(
        leg_positions
    ):

        create_box(
            "Coffee_Table_Leg_" + str(index + 1),
            (
                x,
                y,
                0.25
            ),
            (
                0.08,
                0.08,
                0.50
            ),
            materials["wood"]
        )

    print("Coffee table created")


# ============================================================
# 13. TV UNIT
# ============================================================

def create_tv_unit(materials):

    print("Creating TV unit...")

    create_box(
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
        ),
        materials["wood"]
    )

    create_box(
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
        ),
        materials["black"]
    )

    print("TV unit created")


# ============================================================
# 14. RUG
# ============================================================

def create_rug(materials):

    print("Creating rug...")

    create_box(
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
        ),
        materials["rug"]
    )

    print("Rug created")


# ============================================================
# 15. AREA LIGHT
# ============================================================

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


# ============================================================
# 16. LIGHTING
# ============================================================

def create_lighting():

    print("Creating lighting...")

    # Key light
    create_area_light(
        "Key_Light",
        (-1.5, -1.0, 2.8),
        900,
        3.0
    )

    # Fill light
    create_area_light(
        "Fill_Light",
        (2.0, 0.5, 2.2),
        500,
        2.5
    )

    # Ceiling light
    create_area_light(
        "Ceiling_Light",
        (0, 0, 2.9),
        700,
        2.0
    )

    # Warm point light
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

    print("Lighting created")


# ============================================================
# 17. CAMERA
# ============================================================

def create_camera():

    print("Creating camera...")

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


# ============================================================
# 18. WORLD
# ============================================================

def setup_world():

    print("Setting up world...")

    world = bpy.context.scene.world

    if world is None:

        world = bpy.data.worlds.new(
            "World"
        )

        bpy.context.scene.world = world

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

    print("World configured")


# ============================================================
# 19. RENDER SETTINGS
# ============================================================

def setup_render():

    print("Setting up render...")

    scene = bpy.context.scene

    # Blender 5.2 EEVEE
    scene.render.engine = "BLENDER_EEVEE"

    scene.render.resolution_x = 800

    scene.render.resolution_y = 600

    scene.render.resolution_percentage = 100

    scene.render.image_settings.file_format = "PNG"

    print("Render settings configured")


# ============================================================
# 20. RENDER
# ============================================================

def render_scene():

    render_path = os.path.join(
        RENDERS_DIR,
        "AI_Living_Room.png"
    )

    scene = bpy.context.scene

    scene.render.filepath = render_path

    print("==========================================")
    print("STARTING RENDER")
    print("==========================================")

    result = bpy.ops.render.render(
        write_still=True
    )

    print("Render result:")
    print(result)

    print("Render saved:")
    print(render_path)

    return render_path


# ============================================================
# 21. SAVE BLEND
# ============================================================

def save_project():

    blend_path = os.path.join(
        PROJECTS_DIR,
        "AI_Living_Room.blend"
    )

    bpy.ops.wm.save_as_mainfile(
        filepath=blend_path
    )

    print("Blend project saved:")
    print(blend_path)

    return blend_path


# ============================================================
# 22. MAIN GENERATOR
# ============================================================

def generate_interior():

    print("")
    print("==========================================")
    print("STARTING COMPLETE INTERIOR GENERATOR")
    print("==========================================")

    clear_scene()

    materials = create_materials()

    create_room(materials)

    create_door(materials)

    create_windows(materials)

    create_sofa(materials)

    create_coffee_table(materials)

    create_tv_unit(materials)

    create_rug(materials)

    create_lighting()

    create_camera()

    setup_world()

    setup_render()

    render_path = render_scene()

    blend_path = save_project()

    print("")
    print("==========================================")
    print("DAY 7 COMPLETE")
    print("==========================================")

    print("PROJECT:")
    print(blend_path)

    print("RENDER:")
    print(render_path)

    print("==========================================")


# ============================================================
# 23. RUN
# ============================================================

generate_interior()