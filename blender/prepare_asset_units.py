import bpy
import os

from mathutils import Vector
# =========================================================
# PATHS
# =========================================================

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ASSET_LIBRARY = os.path.join(
    PROJECT_DIR,
    "assets",
    "interior_assets.blend"
)

OUTPUT_LIBRARY = os.path.join(
    PROJECT_DIR,
    "assets",
    "interior_assets_units.blend"
)


# =========================================================
# ASSETS
# =========================================================

ASSET_NAMES = [
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


# =========================================================
# CLEAR SCENE
# =========================================================

def clear_scene():

    print("\nClearing temporary scene...")

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)

    for collection in list(bpy.data.collections):

        if collection.name != "Collection":

            bpy.data.collections.remove(
                collection
            )


# =========================================================
# LOAD ASSET COLLECTIONS
# =========================================================

def load_assets():

    print("\nLoading master asset library...")

    with bpy.data.libraries.load(
        ASSET_LIBRARY,
        link=False
    ) as (
        data_from,
        data_to
    ):

        available = set(data_from.collections)

        selected = []

        for asset_name in ASSET_NAMES:

            if asset_name in available:

                selected.append(asset_name)

            else:

                print(
                    f"WARNING: Missing asset: {asset_name}"
                )

        data_to.collections = selected

    print(
        f"Loaded {len(data_to.collections)} asset collections."
    )

    return data_to.collections


# =========================================================
# CREATE ROOT
# =========================================================

def create_root(asset_name):

    root_name = f"ASSET_ROOT_{asset_name}"

    root = bpy.data.objects.get(root_name)

    if root:

        bpy.data.objects.remove(
            root,
            do_unlink=True
        )

    root = bpy.data.objects.new(
        root_name,
        None
    )

    root.empty_display_type = "PLAIN_AXES"

    root.empty_display_size = 0.5

    return root


# =========================================================
# PARENT ASSET OBJECTS
# =========================================================

def prepare_asset(collection):

    asset_name = collection.name

    print("\nPreparing:", asset_name)

    root = create_root(asset_name)

    collection.objects.link(root)

    objects = [
        obj
        for obj in collection.objects
        if obj != root
    ]

    if not objects:

        print(
            "WARNING: No objects found:",
            asset_name
        )

        return False

    # -----------------------------------------------------
    # Calculate center of geometry
    # -----------------------------------------------------

    min_x = float("inf")
    min_y = float("inf")
    min_z = float("inf")

    max_x = float("-inf")
    max_y = float("-inf")
    max_z = float("-inf")

    for obj in objects:

        if obj.type != "MESH":
            continue

        for corner in obj.bound_box:

            world_corner = obj.matrix_world @ Vector(corner)

            min_x = min(
                min_x,
                world_corner.x
            )

            max_x = max(
                max_x,
                world_corner.x
            )

            min_y = min(
                min_y,
                world_corner.y
            )

            max_y = max(
                max_y,
                world_corner.y
            )

            min_z = min(
                min_z,
                world_corner.z
            )

            max_z = max(
                max_z,
                world_corner.z
            )

    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2

    # -----------------------------------------------------
    # Put root at geometry center
    # -----------------------------------------------------

    root.location = (
        center_x,
        center_y,
        min_z
    )

    # -----------------------------------------------------
    # Parent objects while preserving world transform
    # -----------------------------------------------------

    for obj in objects:

        if obj == root:
            continue

        world_matrix = obj.matrix_world.copy()

        obj.parent = root

        obj.matrix_world = world_matrix

    # -----------------------------------------------------
    # Metadata
    # -----------------------------------------------------

    root["asset_name"] = asset_name
    root["asset_type"] = "interior_furniture"
    root["asset_unit"] = True

    print(
        f"  Root created: {root.name}"
    )

    print(
        f"  Objects: {len(objects)}"
    )

    return True


# =========================================================
# VERIFY
# =========================================================

def verify_assets():

    print("\n" + "=" * 50)
    print("VERIFYING ASSET UNITS")
    print("=" * 50)

    success = 0

    for asset_name in ASSET_NAMES:

        root_name = f"ASSET_ROOT_{asset_name}"

        root = bpy.data.objects.get(root_name)

        if root:

            children = len(root.children)

            print(
                f"FOUND : {asset_name}"
                f" | Children: {children}"
            )

            success += 1

        else:

            print(
                f"MISSING: {asset_name}"
            )

    print()

    print(
        f"Prepared: {success} / {len(ASSET_NAMES)}"
    )

    return success == len(ASSET_NAMES)


# =========================================================
# MAIN
# =========================================================

def main():

    print("=" * 50)
    print("AI INTERIOR ASSET UNIT PREPARATION")
    print("=" * 50)

    clear_scene()

    collections = load_assets()

    for collection in collections:

        prepare_asset(collection)

    success = verify_assets()

    if not success:

        print("\nERROR: Asset preparation incomplete.")

        return

    print("\nSaving asset-unit library...")

    bpy.ops.wm.save_as_mainfile(
        filepath=OUTPUT_LIBRARY
    )

    print("\n" + "=" * 50)
    print("ASSET UNIT LIBRARY COMPLETE")
    print("=" * 50)

    print(
        "Output:",
        OUTPUT_LIBRARY
    )

    print("\nSUCCESS")


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    main()