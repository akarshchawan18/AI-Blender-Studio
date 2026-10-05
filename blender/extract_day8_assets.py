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

DAY11_BACKUP = os.path.join(
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
    "interior_assets_master_temp.blend"
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

# These are supporting objects from the old scene.
# We keep them available for reference but don't
# create separate assets from them yet.

OTHER_OBJECTS = [
    "Side_Table",
    "Living_Room_Rug",
    "Lamp_Shade",
    "Lamp_Pole",
]


# =========================================================
# CLEAR SCENE
# =========================================================

def clear_scene():

    print()
    print("Clearing temporary scene...")

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)

    for collection in list(bpy.data.collections):

        if collection.name != "Collection":

            try:
                bpy.data.collections.remove(
                    collection,
                    do_unlink=True
                )
            except Exception:
                pass


# =========================================================
# APPEND DAY 8 OBJECTS
# =========================================================

def append_day8_objects():

    print()
    print("==========================================")
    print("APPENDING DAY 8 OBJECTS")
    print("==========================================")

    with bpy.data.libraries.load(
        DAY8_LIBRARY,
        link=False
    ) as (data_from, data_to):

        available = set(data_from.objects)

        requested = (
            SOFA_OBJECTS
            + COFFEE_TABLE_OBJECTS
            + TV_UNIT_OBJECTS
            + OTHER_OBJECTS
        )

        for object_name in requested:

            if object_name in available:

                data_to.objects.append(object_name)

            else:

                print(
                    "WARNING: Object not found:",
                    object_name
                )

    print()

    appended_objects = []

    for obj in data_to.objects:

        if obj is None:
            continue

        appended_objects.append(obj)

        print(
            "Appended:",
            obj.name
        )

        # Link to the temporary scene
        try:

            bpy.context.scene.collection.objects.link(obj)

        except RuntimeError:

            pass

    return appended_objects


# =========================================================
# CREATE ASSET COLLECTION
# =========================================================

def create_asset_collection(name):

    # Remove existing collection with same name
    old_collection = bpy.data.collections.get(name)

    if old_collection:

        try:
            bpy.data.collections.remove(
                old_collection,
                do_unlink=True
            )
        except Exception:
            pass

    collection = bpy.data.collections.new(name)

    bpy.context.scene.collection.children.link(
        collection
    )

    return collection


# =========================================================
# MOVE OBJECTS TO COLLECTION
# =========================================================

def move_objects_to_collection(
    object_names,
    collection
):

    moved = []

    for object_name in object_names:

        obj = bpy.data.objects.get(object_name)

        if obj is None:

            print(
                "WARNING: Object unavailable:",
                object_name
            )

            continue

        # Remove from all existing collections
        for old_collection in list(obj.users_collection):

            try:

                old_collection.objects.unlink(obj)

            except Exception:

                pass

        # Add to new asset collection
        collection.objects.link(obj)

        moved.append(obj)

    return moved


# =========================================================
# BUILD SOFA
# =========================================================

def build_sofa():

    print()
    print("Creating Sofa_Modern...")

    collection = create_asset_collection(
        "Sofa_Modern"
    )

    objects = move_objects_to_collection(
        SOFA_OBJECTS,
        collection
    )

    return collection, objects


# =========================================================
# BUILD COFFEE TABLE
# =========================================================

def build_coffee_table():

    print()
    print("Creating CoffeeTable_Modern...")

    collection = create_asset_collection(
        "CoffeeTable_Modern"
    )

    objects = move_objects_to_collection(
        COFFEE_TABLE_OBJECTS,
        collection
    )

    return collection, objects


# =========================================================
# BUILD TV UNIT
# =========================================================

def build_tv_unit():

    print()
    print("Creating TVUnit_Wood...")

    collection = create_asset_collection(
        "TVUnit_Wood"
    )

    objects = move_objects_to_collection(
        TV_UNIT_OBJECTS,
        collection
    )

    return collection, objects


# =========================================================
# VERIFY
# =========================================================

def verify_assets():

    print()
    print("==========================================")
    print("DAY 8 ASSET VERIFICATION")
    print("==========================================")

    required = [
        "Sofa_Modern",
        "CoffeeTable_Modern",
        "TVUnit_Wood",
    ]

    success = True

    for asset_name in required:

        collection = bpy.data.collections.get(
            asset_name
        )

        if collection is None:

            print(
                "MISSING:",
                asset_name
            )

            success = False

            continue

        object_count = len(
            collection.all_objects
        )

        print(
            "FOUND:",
            asset_name,
            "| Objects:",
            object_count
        )

    return success


# =========================================================
# SAVE
# =========================================================

def save_master():

    print()
    print("==========================================")
    print("SAVING MASTER LIBRARY")
    print("==========================================")

    os.makedirs(
        os.path.dirname(TEMP_LIBRARY),
        exist_ok=True
    )

    bpy.ops.wm.save_as_mainfile(
        filepath=TEMP_LIBRARY
    )

    if os.path.exists(MASTER_LIBRARY):

        os.remove(MASTER_LIBRARY)

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
    print("DAY 8 → MASTER ASSET EXTRACTION")
    print("==========================================")

    if not os.path.exists(DAY8_LIBRARY):

        raise FileNotFoundError(
            "Day 8 library not found:\n"
            + DAY8_LIBRARY
        )

    if not os.path.exists(DAY11_BACKUP):

        raise FileNotFoundError(
            "Day 11 backup not found:\n"
            + DAY11_BACKUP
        )

    clear_scene()

    append_day8_objects()

    build_sofa()

    build_coffee_table()

    build_tv_unit()

    success = verify_assets()

    if not success:

        print()
        print("ERROR: Asset extraction failed.")
        print("Master library will NOT be saved.")

        raise RuntimeError(
            "Day 8 asset extraction failed."
        )

    save_master()

    print()
    print("==========================================")
    print("DAY 8 EXTRACTION COMPLETE")
    print("==========================================")

    print()
    print("Created:")
    print(" - Sofa_Modern")
    print(" - CoffeeTable_Modern")
    print(" - TVUnit_Wood")

    print()
    print("==========================================")
    print("SUCCESS")
    print("==========================================")


if __name__ == "__main__":
    main()