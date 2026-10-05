import bpy
import os
import shutil


# =========================================================
# PATHS
# =========================================================

PROJECT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

DAY8_LIBRARY = os.path.join(
    PROJECT_DIR,
    "projects",
    "living_room_furniture.blend"
)

DAY11_LIBRARY = os.path.join(
    PROJECT_DIR,
    "assets",
    "interior_assets_day11_backup.blend"
)

MASTER_LIBRARY = os.path.join(
    PROJECT_DIR,
    "assets",
    "interior_assets.blend"
)

TEMP_LIBRARY = os.path.join(
    PROJECT_DIR,
    "assets",
    "interior_assets_rebuilt_temp.blend"
)


# =========================================================
# DAY 8 OBJECT GROUPS
# =========================================================

SOFA_OBJECTS = [
    "Sofa_Seat",
    "Sofa_Back",
    "Sofa_Arm_Right",
    "Sofa_Arm_Left",
]

COFFEE_TABLE_OBJECTS = [
    "Coffee_Table_Top",
    "Coffee_Table_Leg",
    "Coffee_Table_Leg.001",
    "Coffee_Table_Leg.002",
    "Coffee_Table_Leg.003",
]

TV_UNIT_OBJECTS = [
    "TV_Unit",
    "TV_Stand",
    "TV",
]


# =========================================================
# DAY 11 COLLECTIONS
# =========================================================

DAY11_ASSETS = [
    "Bed_Modern",
    "Wardrobe_Modern",
    "Desk_Modern",
    "DiningTable_Modern",
    "Lamp_Modern",
]


# =========================================================
# CLEAR SCENE
# =========================================================

def clear_scene():

    print()
    print("Clearing temporary Blender scene...")

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)

    for collection in list(bpy.data.collections):

        try:
            bpy.data.collections.remove(
                collection,
                do_unlink=True
            )
        except Exception:
            pass


# =========================================================
# APPEND OBJECTS FROM DAY 8
# =========================================================

def append_day8_objects():

    print()
    print("==========================================")
    print("APPENDING DAY 8 OBJECTS")
    print("==========================================")

    if not os.path.exists(DAY8_LIBRARY):

        raise FileNotFoundError(
            DAY8_LIBRARY
        )

    requested = (
        SOFA_OBJECTS
        + COFFEE_TABLE_OBJECTS
        + TV_UNIT_OBJECTS
    )

    with bpy.data.libraries.load(
        DAY8_LIBRARY,
        link=False
    ) as (data_from, data_to):

        available = set(
            data_from.objects
        )

        for object_name in requested:

            if object_name not in available:

                print(
                    "ERROR: Object not found:",
                    object_name
                )

                raise RuntimeError(
                    "Missing Day 8 object: "
                    + object_name
                )

            data_to.objects.append(
                object_name
            )

    appended = []

    for obj in data_to.objects:

        if obj is None:
            continue

        try:
            bpy.context.scene.collection.objects.link(
                obj
            )
        except RuntimeError:
            pass

        appended.append(obj)

        print(
            "Appended object:",
            obj.name
        )

    return appended


# =========================================================
# CREATE COLLECTION
# =========================================================

def create_collection(name):

    existing = bpy.data.collections.get(
        name
    )

    if existing:

        bpy.data.collections.remove(
            existing,
            do_unlink=True
        )

    collection = bpy.data.collections.new(
        name
    )

    bpy.context.scene.collection.children.link(
        collection
    )

    return collection


# =========================================================
# MOVE OBJECTS TO COLLECTION
# =========================================================

def move_objects(
    object_names,
    collection
):

    moved = []

    for object_name in object_names:

        obj = bpy.data.objects.get(
            object_name
        )

        if obj is None:

            raise RuntimeError(
                "Object not found after append: "
                + object_name
            )

        # Remove from existing collections
        for old_collection in list(
            obj.users_collection
        ):

            try:
                old_collection.objects.unlink(
                    obj
                )
            except Exception:
                pass

        collection.objects.link(
            obj
        )

        moved.append(obj)

    return moved


# =========================================================
# BUILD SOFA
# =========================================================

def build_sofa():

    print()
    print("Creating Sofa_Modern...")

    collection = create_collection(
        "Sofa_Modern"
    )

    move_objects(
        SOFA_OBJECTS,
        collection
    )

    try:
        collection.asset_mark()
    except Exception:
        pass

    print(
        "Sofa_Modern created."
    )


# =========================================================
# BUILD COFFEE TABLE
# =========================================================

def build_coffee_table():

    print()
    print("Creating CoffeeTable_Modern...")

    collection = create_collection(
        "CoffeeTable_Modern"
    )

    move_objects(
        COFFEE_TABLE_OBJECTS,
        collection
    )

    try:
        collection.asset_mark()
    except Exception:
        pass

    print(
        "CoffeeTable_Modern created."
    )


# =========================================================
# BUILD TV UNIT
# =========================================================

def build_tv_unit():

    print()
    print("Creating TVUnit_Wood...")

    collection = create_collection(
        "TVUnit_Wood"
    )

    move_objects(
        TV_UNIT_OBJECTS,
        collection
    )

    try:
        collection.asset_mark()
    except Exception:
        pass

    print(
        "TVUnit_Wood created."
    )


# =========================================================
# APPEND DAY 11
# =========================================================

def append_day11_assets():

    print()
    print("==========================================")
    print("APPENDING DAY 11 ASSETS")
    print("==========================================")

    if not os.path.exists(
        DAY11_LIBRARY
    ):

        raise FileNotFoundError(
            DAY11_LIBRARY
        )

    with bpy.data.libraries.load(
        DAY11_LIBRARY,
        link=False
    ) as (data_from, data_to):

        available = set(
            data_from.collections
        )

        for asset_name in DAY11_ASSETS:

            if asset_name not in available:

                raise RuntimeError(
                    "Missing Day 11 collection: "
                    + asset_name
                )

            data_to.collections.append(
                asset_name
            )

    for collection in data_to.collections:

        if collection is None:
            continue

        try:

            bpy.context.scene.collection.children.link(
                collection
            )

        except RuntimeError:

            pass

        print(
            "Appended collection:",
            collection.name
        )


# =========================================================
# MATERIALS
# =========================================================

def create_material(
    name,
    color
):

    material = bpy.data.materials.get(
        name
    )

    if material is None:

        material = bpy.data.materials.new(
            name
        )

    material.diffuse_color = (
        color[0],
        color[1],
        color[2],
        1.0
    )

    return material


# =========================================================
# CUBE
# =========================================================

def create_cube(
    name,
    location,
    dimensions,
    material,
    collection
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

    for old_collection in list(
        obj.users_collection
    ):

        try:
            old_collection.objects.unlink(
                obj
            )
        except Exception:
            pass

    collection.objects.link(
        obj
    )

    if material:

        obj.data.materials.append(
            material
        )

    return obj


# =========================================================
# CHAIR
# =========================================================

def create_chair():

    print()
    print("Creating Chair_Modern...")

    collection = create_collection(
        "Chair_Modern"
    )

    fabric = create_material(
        "ASSET_Fabric_Modern",
        (0.45, 0.45, 0.45)
    )

    wood = create_material(
        "ASSET_Wood_Modern",
        (0.25, 0.12, 0.05)
    )

    create_cube(
        "Chair_Seat",
        (0, 0, 0.45),
        (0.75, 0.75, 0.18),
        fabric,
        collection
    )

    create_cube(
        "Chair_Back",
        (0, 0.30, 0.95),
        (0.75, 0.15, 1.00),
        fabric,
        collection
    )

    positions = [
        (-0.27, -0.27),
        (0.27, -0.27),
        (-0.27, 0.27),
        (0.27, 0.27)
    ]

    for index, (x, y) in enumerate(
        positions
    ):

        create_cube(
            f"Chair_Leg_{index + 1}",
            (x, y, 0.20),
            (0.08, 0.08, 0.40),
            wood,
            collection
        )

    try:
        collection.asset_mark()
    except Exception:
        pass

    print(
        "Chair_Modern created."
    )


# =========================================================
# L-SHAPE SOFA
# =========================================================

def create_l_shape_sofa():

    print()
    print("Creating Sofa_LShape...")

    collection = create_collection(
        "Sofa_LShape"
    )

    fabric = create_material(
        "ASSET_LShape_Fabric",
        (0.60, 0.58, 0.54)
    )

    dark_fabric = create_material(
        "ASSET_LShape_Fabric_Dark",
        (0.42, 0.42, 0.42)
    )

    wood = create_material(
        "ASSET_LShape_Wood",
        (0.25, 0.12, 0.05)
    )

    create_cube(
        "LShape_Main_Seat",
        (0, 0, 0.45),
        (2.80, 1.00, 0.25),
        fabric,
        collection
    )

    create_cube(
        "LShape_Main_Back",
        (0, 0.40, 0.95),
        (2.80, 0.20, 1.00),
        dark_fabric,
        collection
    )

    create_cube(
        "LShape_Main_Arm",
        (-1.30, 0, 0.75),
        (0.20, 1.00, 0.60),
        dark_fabric,
        collection
    )

    create_cube(
        "LShape_Side_Seat",
        (0.90, -0.50, 0.45),
        (1.00, 1.80, 0.25),
        fabric,
        collection
    )

    create_cube(
        "LShape_Side_Back",
        (1.30, 0.00, 0.95),
        (0.20, 1.00, 1.00),
        dark_fabric,
        collection
    )

    create_cube(
        "LShape_Side_Arm",
        (0.90, -1.30, 0.75),
        (1.00, 0.20, 0.60),
        dark_fabric,
        collection
    )

    positions = [
        (-1.10, -0.30),
        (0.00, -0.30),
        (1.10, -0.30),
        (-1.10, 0.30),
        (0.00, 0.30),
        (1.10, 0.30)
    ]

    for index, (x, y) in enumerate(
        positions
    ):

        create_cube(
            f"LShape_Leg_{index + 1}",
            (x, y, 0.20),
            (0.08, 0.08, 0.40),
            wood,
            collection
        )

    try:
        collection.asset_mark()
    except Exception:
        pass

    print(
        "Sofa_LShape created."
    )


# =========================================================
# VERIFY
# =========================================================

def verify_all_assets():

    print()
    print("==========================================")
    print("FINAL MASTER ASSET VERIFICATION")
    print("==========================================")

    required = [
        "Sofa_Modern",
        "Sofa_LShape",
        "CoffeeTable_Modern",
        "TVUnit_Wood",
        "Chair_Modern",
        "Bed_Modern",
        "Wardrobe_Modern",
        "Desk_Modern",
        "DiningTable_Modern",
        "Lamp_Modern"
    ]

    missing = []

    for asset_name in required:

        collection = bpy.data.collections.get(
            asset_name
        )

        if collection:

            count = len(
                collection.all_objects
            )

            print(
                f"FOUND   : {asset_name}"
                f" | Objects: {count}"
            )

        else:

            print(
                f"MISSING : {asset_name}"
            )

            missing.append(
                asset_name
            )

    print()
    print(
        f"Found : "
        f"{len(required) - len(missing)}"
        f" / {len(required)}"
    )

    print(
        f"Missing : {len(missing)}"
    )

    return missing


# =========================================================
# SAVE
# =========================================================

def save_master():

    print()
    print("==========================================")
    print("SAVING MASTER LIBRARY")
    print("==========================================")

    bpy.ops.wm.save_as_mainfile(
        filepath=TEMP_LIBRARY
    )

    if os.path.exists(
        MASTER_LIBRARY
    ):

        os.remove(
            MASTER_LIBRARY
        )

    shutil.move(
        TEMP_LIBRARY,
        MASTER_LIBRARY
    )

    print()
    print("Master library saved:")
    print(MASTER_LIBRARY)


# =========================================================
# MAIN
# =========================================================

def main():

    print()
    print("==========================================")
    print("REBUILD MASTER ASSET LIBRARY")
    print("==========================================")

    if not os.path.exists(
        DAY8_LIBRARY
    ):

        raise FileNotFoundError(
            DAY8_LIBRARY
        )

    if not os.path.exists(
        DAY11_LIBRARY
    ):

        raise FileNotFoundError(
            DAY11_LIBRARY
        )

    # Start clean.
    clear_scene()

    # -----------------------------------------------------
    # DAY 8
    # -----------------------------------------------------

    append_day8_objects()

    build_sofa()

    build_coffee_table()

    build_tv_unit()

    # -----------------------------------------------------
    # DAY 11
    # -----------------------------------------------------

    append_day11_assets()

    # -----------------------------------------------------
    # NEW ASSETS
    # -----------------------------------------------------

    create_chair()

    create_l_shape_sofa()

    # -----------------------------------------------------
    # VERIFY
    # -----------------------------------------------------

    missing = verify_all_assets()

    if missing:

        print()
        print("==========================================")
        print("ERROR")
        print("MASTER LIBRARY NOT SAVED")
        print("==========================================")

        for asset in missing:

            print(
                "Missing:",
                asset
            )

        raise RuntimeError(
            "Master asset library incomplete."
        )

    # -----------------------------------------------------
    # SAVE
    # -----------------------------------------------------

    save_master()

    print()
    print("==========================================")
    print("MASTER LIBRARY COMPLETE")
    print("==========================================")

    print()
    print("Total assets: 10")

    print()
    print("SUCCESS")


if __name__ == "__main__":

    main()