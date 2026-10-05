import bpy
import os


# ============================================================
# AI BLENDER STUDIO
# DAY 8
# REUSABLE FURNITURE ASSET LIBRARY
# ============================================================

print("==========================================")
print("AI BLENDER STUDIO - DAY 8")
print("FURNITURE ASSET LIBRARY")
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

ASSETS_DIR = os.path.join(
    PROJECT_DIR,
    "assets"
)

PROJECTS_DIR = os.path.join(
    PROJECT_DIR,
    "projects"
)

os.makedirs(
    ASSETS_DIR,
    exist_ok=True
)

os.makedirs(
    PROJECTS_DIR,
    exist_ok=True
)


# ============================================================
# 2. CLEAR SCENE
# ============================================================

def clear_scene():

    print("Clearing scene...")

    bpy.ops.object.select_all(
        action="SELECT"
    )

    bpy.ops.object.delete(
        use_global=False
    )

    print("Scene cleared")


# ============================================================
# 3. CREATE MATERIAL
# ============================================================

def create_material(
    name,
    color,
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

    principled = (
        material.node_tree.nodes.get(
            "Principled BSDF"
        )
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


# ============================================================
# 4. MATERIALS
# ============================================================

def create_materials():

    print("Creating materials...")

    return {

        "fabric": create_material(
            "ASSET_Fabric",
            (0.20, 0.22, 0.24),
            0.85
        ),

        "fabric_light": create_material(
            "ASSET_Fabric_Light",
            (0.55, 0.50, 0.43),
            0.85
        ),

        "wood": create_material(
            "ASSET_Wood",
            (0.20, 0.07, 0.025),
            0.55
        ),

        "wood_light": create_material(
            "ASSET_Wood_Light",
            (0.42, 0.20, 0.07),
            0.55
        ),

        "black": create_material(
            "ASSET_Black",
            (0.01, 0.01, 0.01),
            0.3
        ),

        "metal": create_material(
            "ASSET_Metal",
            (0.25, 0.25, 0.25),
            0.25,
            0.8
        ),

    }


# ============================================================
# 5. CREATE BOX
# ============================================================

def create_box(
    name,
    location,
    dimensions,
    material
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
# 6. CREATE COLLECTION
# ============================================================

def create_collection(name):

    collection = bpy.data.collections.get(
        name
    )

    if collection:

        # Remove existing objects
        for obj in list(collection.objects):

            bpy.data.objects.remove(
                obj,
                do_unlink=True
            )

    else:

        collection = bpy.data.collections.new(
            name
        )

        bpy.context.scene.collection.children.link(
            collection
        )

    return collection


# ============================================================
# 7. MOVE OBJECT TO COLLECTION
# ============================================================

def move_to_collection(
    obj,
    collection
):

    # Remove from existing collections
    for old_collection in list(
        obj.users_collection
    ):

        old_collection.objects.unlink(
            obj
        )

    collection.objects.link(
        obj
    )


# ============================================================
# 8. MARK COLLECTION AS ASSET
# ============================================================

def mark_collection_as_asset(
    collection
):

    try:

        collection.asset_mark()

        print(
            "Asset marked:",
            collection.name
        )

    except Exception as error:

        print(
            "Could not mark asset:",
            collection.name
        )

        print(error)


# ============================================================
# 9. MODERN 3-SEATER SOFA
# ============================================================

def create_modern_sofa(materials):

    print("Creating Sofa_Modern...")

    collection = create_collection(
        "Sofa_Modern"
    )

    # Seat
    seat = create_box(
        "Sofa_Modern_Seat",
        (0, 0, 0.45),
        (2.4, 0.85, 0.35),
        materials["fabric"]
    )

    move_to_collection(
        seat,
        collection
    )

    # Back
    back = create_box(
        "Sofa_Modern_Back",
        (0, 0.30, 1.0),
        (2.4, 0.25, 1.1),
        materials["fabric"]
    )

    move_to_collection(
        back,
        collection
    )

    # Left arm
    left_arm = create_box(
        "Sofa_Modern_Left_Arm",
        (-1.15, 0, 0.75),
        (0.25, 0.85, 0.8),
        materials["fabric"]
    )

    move_to_collection(
        left_arm,
        collection
    )

    # Right arm
    right_arm = create_box(
        "Sofa_Modern_Right_Arm",
        (1.15, 0, 0.75),
        (0.25, 0.85, 0.8),
        materials["fabric"]
    )

    move_to_collection(
        right_arm,
        collection
    )

    mark_collection_as_asset(
        collection
    )

    return collection


# ============================================================
# 10. LIGHT L-SHAPED SOFA
# ============================================================

def create_l_shape_sofa(materials):

    print("Creating Sofa_LShape...")

    collection = create_collection(
        "Sofa_LShape"
    )

    # Main seat
    main = create_box(
        "Sofa_LShape_Main",
        (0, 0, 0.45),
        (2.5, 0.8, 0.35),
        materials["fabric_light"]
    )

    move_to_collection(
        main,
        collection
    )

    # Main back
    main_back = create_box(
        "Sofa_LShape_Back",
        (0, 0.30, 1.0),
        (2.5, 0.25, 1.1),
        materials["fabric_light"]
    )

    move_to_collection(
        main_back,
        collection
    )

    # L section
    side = create_box(
        "Sofa_LShape_Side",
        (0.85, 0.75, 0.45),
        (0.8, 1.5, 0.35),
        materials["fabric_light"]
    )

    move_to_collection(
        side,
        collection
    )

    # Side back
    side_back = create_box(
        "Sofa_LShape_Side_Back",
        (0.85, 1.35, 1.0),
        (0.25, 0.8, 1.1),
        materials["fabric_light"]
    )

    move_to_collection(
        side_back,
        collection
    )

    mark_collection_as_asset(
        collection
    )

    return collection


# ============================================================
# 11. COFFEE TABLE
# ============================================================

def create_modern_table(materials):

    print("Creating CoffeeTable_Modern...")

    collection = create_collection(
        "CoffeeTable_Modern"
    )

    top = create_box(
        "CoffeeTable_Top",
        (0, 0, 0.5),
        (1.5, 0.8, 0.12),
        materials["wood_light"]
    )

    move_to_collection(
        top,
        collection
    )

    positions = [
        (-0.6, -0.3),
        (0.6, -0.3),
        (-0.6, 0.3),
        (0.6, 0.3)
    ]

    for index, (x, y) in enumerate(
        positions
    ):

        leg = create_box(
            "CoffeeTable_Leg_" + str(index + 1),
            (x, y, 0.25),
            (0.08, 0.08, 0.5),
            materials["metal"]
        )

        move_to_collection(
            leg,
            collection
        )

    mark_collection_as_asset(
        collection
    )

    return collection


# ============================================================
# 12. WOODEN TV UNIT
# ============================================================

def create_tv_unit(materials):

    print("Creating TVUnit_Wood...")

    collection = create_collection(
        "TVUnit_Wood"
    )

    body = create_box(
        "TVUnit_Body",
        (0, 0, 0.45),
        (2.5, 0.45, 0.7),
        materials["wood"]
    )

    move_to_collection(
        body,
        collection
    )

    top = create_box(
        "TVUnit_Top",
        (0, 0, 0.83),
        (2.7, 0.5, 0.08),
        materials["wood_light"]
    )

    move_to_collection(
        top,
        collection
    )

    mark_collection_as_asset(
        collection
    )

    return collection


# ============================================================
# 13. MODERN CHAIR
# ============================================================

def create_modern_chair(materials):

    print("Creating Chair_Modern...")

    collection = create_collection(
        "Chair_Modern"
    )

    seat = create_box(
        "Chair_Seat",
        (0, 0, 0.5),
        (0.75, 0.75, 0.25),
        materials["fabric"]
    )

    move_to_collection(
        seat,
        collection
    )

    back = create_box(
        "Chair_Back",
        (0, 0.28, 1.05),
        (0.75, 0.18, 1.1),
        materials["fabric"]
    )

    move_to_collection(
        back,
        collection
    )

    leg_positions = [
        (-0.28, -0.28),
        (0.28, -0.28),
        (-0.28, 0.28),
        (0.28, 0.28)
    ]

    for index, (x, y) in enumerate(
        leg_positions
    ):

        leg = create_box(
            "Chair_Leg_" + str(index + 1),
            (x, y, 0.25),
            (0.07, 0.07, 0.5),
            materials["metal"]
        )

        move_to_collection(
            leg,
            collection
        )

    mark_collection_as_asset(
        collection
    )

    return collection


# ============================================================
# 14. SAVE ASSET LIBRARY
# ============================================================

def save_asset_library():

    asset_file = os.path.join(
        ASSETS_DIR,
        "interior_assets.blend"
    )

    print("Saving asset library...")

    bpy.ops.wm.save_as_mainfile(
        filepath=asset_file
    )

    print("Asset library saved:")
    print(asset_file)

    return asset_file


# ============================================================
# 15. MAIN
# ============================================================

def create_asset_library():

    clear_scene()

    materials = create_materials()

    create_modern_sofa(
        materials
    )

    create_l_shape_sofa(
        materials
    )

    create_modern_table(
        materials
    )

    create_tv_unit(
        materials
    )

    create_modern_chair(
        materials
    )

    asset_file = save_asset_library()

    print("")
    print("==========================================")
    print("DAY 8 COMPLETE")
    print("==========================================")

    print("ASSET LIBRARY:")
    print(asset_file)

    print("")
    print("AVAILABLE ASSETS:")
    print("Sofa_Modern")
    print("Sofa_LShape")
    print("CoffeeTable_Modern")
    print("TVUnit_Wood")
    print("Chair_Modern")

    print("==========================================")


# ============================================================
# 16. RUN
# ============================================================

create_asset_library()