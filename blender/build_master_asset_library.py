import bpy
import os
import shutil


# =========================================================
# PATHS
# =========================================================

PROJECT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

CURRENT_LIBRARY = os.path.join(
    PROJECT_DIR,
    "assets",
    "interior_assets.blend"
)

DAY11_BACKUP = os.path.join(
    PROJECT_DIR,
    "assets",
    "interior_assets_day11_backup.blend"
)

DAY8_LIBRARY = os.path.join(
    PROJECT_DIR,
    "projects",
    "living_room_furniture.blend"
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
# ASSETS WE WANT
# =========================================================

DAY8_ASSETS = [
    "Sofa_Modern",
    "Sofa_LShape",
    "CoffeeTable_Modern",
    "TVUnit_Wood",
    "Chair_Modern",
]

DAY11_ASSETS = [
    "Bed_Modern",
    "Wardrobe_Modern",
    "Desk_Modern",
    "DiningTable_Modern",
    "Lamp_Modern",
]


# =========================================================
# CLEAR CURRENT BLENDER SCENE
# =========================================================

def clear_scene():

    print()
    print("Clearing temporary Blender scene...")

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)

    for collection in list(bpy.data.collections):
        if collection.name != "Collection":
            bpy.data.collections.remove(
                collection,
                do_unlink=True
            )

    print("Scene cleared.")


# =========================================================
# APPEND COLLECTIONS FROM BLEND FILE
# =========================================================

def append_collections(blend_file, asset_names):

    if not os.path.exists(blend_file):

        print()
        print("ERROR: Source file not found:")
        print(blend_file)

        return []

    print()
    print("Source:")
    print(blend_file)

    appended = []

    with bpy.data.libraries.load(
        blend_file,
        link=False
    ) as (
        data_from,
        data_to
    ):

        available = set(data_from.collections)

        for asset_name in asset_names:

            if asset_name not in available:

                print(
                    f"WARNING: Collection not found: "
                    f"{asset_name}"
                )

                continue

            data_to.collections.append(asset_name)

    for collection in data_to.collections:

        if collection is None:
            continue

        collection_name = collection.name

        print(
            f"  Appended: {collection_name}"
        )

        appended.append(collection_name)

        # Make sure collection is linked to scene
        if collection.name not in bpy.context.scene.collection.children:

            try:
                bpy.context.scene.collection.children.link(
                    collection
                )
            except RuntimeError:
                pass

    return appended


# =========================================================
# FIND DAY 11 ASSETS
# =========================================================

def append_day11_assets():

    print()
    print("==========================================")
    print("ADDING DAY 11 ASSETS")
    print("==========================================")

    # Use the backup we created earlier.
    source = DAY11_BACKUP

    return append_collections(
        source,
        DAY11_ASSETS
    )


# =========================================================
# FIND DAY 8 ASSETS
# =========================================================

def append_day8_assets():

    print()
    print("==========================================")
    print("ADDING DAY 8 ASSETS")
    print("==========================================")

    return append_collections(
        DAY8_LIBRARY,
        DAY8_ASSETS
    )


# =========================================================
# REMOVE EMPTY DEFAULT COLLECTION
# =========================================================

def remove_empty_collection():

    collection = bpy.data.collections.get("Collection")

    if collection is None:
        return

    if len(collection.objects) == 0 and len(collection.children) == 0:

        try:
            bpy.data.collections.remove(
                collection,
                do_unlink=True
            )
        except Exception:
            pass


# =========================================================
# VERIFY MASTER ASSETS
# =========================================================

def verify_assets():

    print()
    print("==========================================")
    print("MASTER ASSET VERIFICATION")
    print("==========================================")

    expected = DAY8_ASSETS + DAY11_ASSETS

    found = []
    missing = []

    for asset_name in expected:

        collection = bpy.data.collections.get(
            asset_name
        )

        if collection:

            found.append(asset_name)

            print(
                f"  FOUND   : {asset_name}"
            )

        else:

            missing.append(asset_name)

            print(
                f"  MISSING : {asset_name}"
            )

    print()
    print(
        f"Found : {len(found)} / {len(expected)}"
    )

    print(
        f"Missing : {len(missing)}"
    )

    return found, missing


# =========================================================
# SAVE MASTER LIBRARY
# =========================================================

def save_master_library():

    print()
    print("Saving master asset library...")

    os.makedirs(
        os.path.dirname(TEMP_LIBRARY),
        exist_ok=True
    )

    bpy.ops.wm.save_as_mainfile(
        filepath=TEMP_LIBRARY
    )

    print()
    print("Temporary master saved:")
    print(TEMP_LIBRARY)

    # Replace existing library
    if os.path.exists(MASTER_LIBRARY):

        os.remove(MASTER_LIBRARY)

    shutil.move(
        TEMP_LIBRARY,
        MASTER_LIBRARY
    )

    print()
    print("MASTER LIBRARY CREATED:")
    print(MASTER_LIBRARY)


# =========================================================
# MAIN
# =========================================================

def main():

    print()
    print("==========================================")
    print("AI INTERIOR DESIGN")
    print("MASTER ASSET LIBRARY BUILDER")
    print("==========================================")

    print()
    print("Day 8 source:")
    print(DAY8_LIBRARY)

    print()
    print("Day 11 backup:")
    print(DAY11_BACKUP)

    print()
    print("Current library:")
    print(CURRENT_LIBRARY)

    # -----------------------------------------------------
    # Safety checks
    # -----------------------------------------------------

    if not os.path.exists(DAY8_LIBRARY):

        raise FileNotFoundError(
            "Day 8 furniture library not found:\n"
            + DAY8_LIBRARY
        )

    if not os.path.exists(DAY11_BACKUP):

        raise FileNotFoundError(
            "Day 11 backup not found:\n"
            + DAY11_BACKUP
        )

    # -----------------------------------------------------
    # Build
    # -----------------------------------------------------

    clear_scene()

    day11_found = append_day11_assets()

    day8_found = append_day8_assets()

    remove_empty_collection()

    found, missing = verify_assets()

    # -----------------------------------------------------
    # Safety
    # -----------------------------------------------------

    if missing:

        print()
        print("==========================================")
        print("ERROR")
        print("MASTER LIBRARY NOT SAVED")
        print("==========================================")

        print()
        print("Missing assets:")

        for asset in missing:
            print(" -", asset)

        raise RuntimeError(
            "Some required assets are missing."
        )

    # -----------------------------------------------------
    # Save
    # -----------------------------------------------------

    save_master_library()

    print()
    print("==========================================")
    print("MASTER LIBRARY BUILD COMPLETE")
    print("==========================================")

    print()
    print("Total assets:")
    print(len(found))

    print()
    print("Assets:")

    for asset in found:
        print(" -", asset)

    print()
    print("Library:")
    print(MASTER_LIBRARY)

    print()
    print("==========================================")
    print("SUCCESS")
    print("==========================================")


if __name__ == "__main__":
    main()