import bpy
import os
import json
from mathutils import Vector


# =========================================================
# PATHS
# =========================================================

PROJECT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

ASSET_LIBRARY = os.path.join(
    PROJECT_DIR,
    "assets",
    "interior_assets.blend"
)

OUTPUT_FILE = os.path.join(
    PROJECT_DIR,
    "projects",
    "asset_geometry.json"
)


# =========================================================
# ASSETS TO INSPECT
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
# GET WORLD BOUNDING BOX
# =========================================================

def get_world_bounds(objects):

    world_corners = []

    for obj in objects:

        if obj.type != "MESH":
            continue

        for corner in obj.bound_box:

            world_corner = obj.matrix_world @ Vector(corner)

            world_corners.append(world_corner)

    if not world_corners:

        return None

    min_x = min(v.x for v in world_corners)
    max_x = max(v.x for v in world_corners)

    min_y = min(v.y for v in world_corners)
    max_y = max(v.y for v in world_corners)

    min_z = min(v.z for v in world_corners)
    max_z = max(v.z for v in world_corners)

    return {
        "min": [
            min_x,
            min_y,
            min_z
        ],

        "max": [
            max_x,
            max_y,
            max_z
        ],

        "width": max_x - min_x,

        "depth": max_y - min_y,

        "height": max_z - min_z
    }


# =========================================================
# LOAD ASSET COLLECTION
# =========================================================

def load_asset(asset_name):

    if not os.path.exists(ASSET_LIBRARY):

        raise FileNotFoundError(
            f"Asset library not found: {ASSET_LIBRARY}"
        )

    with bpy.data.libraries.load(
        ASSET_LIBRARY,
        link=False
    ) as (
        data_from,
        data_to
    ):

        if asset_name not in data_from.collections:

            print(
                f"WARNING: Asset not found: {asset_name}"
            )

            return None

        data_to.collections = [
            asset_name
        ]

    collection = data_to.collections[0]

    bpy.context.scene.collection.children.link(
        collection
    )

    return collection


# =========================================================
# INSPECT COLLECTION
# =========================================================

def inspect_collection(collection):

    objects = list(
        collection.all_objects
    )

    bounds = get_world_bounds(
        objects
    )

    if bounds is None:

        return {
            "asset": collection.name,
            "objects": 0,
            "bounds": None
        }

    return {
        "asset": collection.name,

        "objects": len(objects),

        "bounds": bounds
    }


# =========================================================
# MAIN
# =========================================================

def main():

    print()
    print("==========================================")
    print("REAL BLENDER ASSET GEOMETRY INSPECTOR")
    print("==========================================")
    print()

    results = {}

    # -----------------------------------------------------
    # CLEAR CURRENT SCENE
    # -----------------------------------------------------

    bpy.ops.object.select_all(
        action="SELECT"
    )

    bpy.ops.object.delete(
        use_global=False
    )

    # -----------------------------------------------------
    # LOAD AND INSPECT ASSETS
    # -----------------------------------------------------

    for asset_name in ASSET_NAMES:

        print(
            f"Inspecting: {asset_name}"
        )

        collection = load_asset(
            asset_name
        )

        if collection is None:

            continue

        result = inspect_collection(
            collection
        )

        results[asset_name] = result

        if result["bounds"]:

            bounds = result["bounds"]

            print(
                f"  Width : {bounds['width']:.3f} m"
            )

            print(
                f"  Depth : {bounds['depth']:.3f} m"
            )

            print(
                f"  Height: {bounds['height']:.3f} m"
            )

        else:

            print(
                "  No mesh geometry found"
            )

        print()

    # -----------------------------------------------------
    # SAVE JSON
    # -----------------------------------------------------

    os.makedirs(
        os.path.dirname(OUTPUT_FILE),
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            results,
            file,
            indent=4
        )

    print("==========================================")
    print("GEOMETRY INSPECTION COMPLETE")
    print("==========================================")

    print()
    print("Output:")
    print(OUTPUT_FILE)
    print()


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    main()