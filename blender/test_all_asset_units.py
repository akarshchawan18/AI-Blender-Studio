import bpy
import os
import math

# ============================================================
# AI INTERIOR DESIGN STUDIO
# DAY 13 - PART 8
# TEST ALL ASSET UNITS
# ============================================================

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ASSET_LIBRARY = os.path.join(
    PROJECT_DIR,
    "assets",
    "interior_assets_units.blend"
)

OUTPUT_FILE = os.path.join(
    PROJECT_DIR,
    "projects",
    "test_all_asset_units.blend"
)

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
    "Lamp_Modern",
]


# ============================================================
# CLEAR SCENE
# ============================================================

def clear_scene():

    print("\nCLEARING TEST SCENE")

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)

    for collection in list(bpy.data.collections):

        if collection.name != "Collection":

            try:
                bpy.data.collections.remove(
                    collection
                )

            except:
                pass


# ============================================================
# APPEND ASSET COLLECTION
# ============================================================

def append_asset_collection(asset_name):

    print(f"\nLoading asset: {asset_name}")

    collection_name = asset_name

    root_name = f"ASSET_ROOT_{asset_name}"

    loaded_collection = None

    with bpy.data.libraries.load(
        ASSET_LIBRARY,
        link=False
    ) as (data_from, data_to):

        if collection_name not in data_from.collections:

            print(
                f"ERROR: Collection not found: {collection_name}"
            )

            return None

        data_to.collections = [collection_name]

    loaded_collection = bpy.data.collections.get(
        collection_name
    )

    if loaded_collection is None:

        print(
            f"ERROR: Failed to load collection: {collection_name}"
        )

        return None

    root = None

    # Search direct collection objects
    for obj in loaded_collection.objects:

        if obj.name == root_name:

            root = obj
            break

    # Fallback: search all objects
    if root is None:

        root = bpy.data.objects.get(root_name)

    if root is None:

        print(
            f"ERROR: Root not found: {root_name}"
        )

        return None

    return {
        "collection": loaded_collection,
        "root": root
    }


# ============================================================
# TEST TRANSFORM
# ============================================================

def test_transform(root, index):

    # Arrange assets in a simple grid.

    column = index % 5
    row = index // 5

    x = (column - 2) * 3.5
    y = (1 - row) * 3.5

    # Different rotation for each asset.
    rotation_z = math.radians(
        index * 15
    )

    # Different scale to verify root scaling.
    scale_value = 1.0 + (index * 0.03)

    root.location = (
        x,
        y,
        0
    )

    root.rotation_euler = (
        0,
        0,
        rotation_z
    )

    root.scale = (
        scale_value,
        scale_value,
        scale_value
    )

    print(
        f"  Position : "
        f"({x:.2f}, {y:.2f}, 0.00)"
    )

    print(
        f"  Rotation : "
        f"{math.degrees(rotation_z):.1f} degrees"
    )

    print(
        f"  Scale    : "
        f"{scale_value:.2f}"
    )


# ============================================================
# VERIFY ROOT
# ============================================================

def verify_root(asset_name, root):

    expected_root = f"ASSET_ROOT_{asset_name}"

    if root.name != expected_root:

        print(
            f"  FAIL: Wrong root name: {root.name}"
        )

        return False

    children = list(root.children)

    if len(children) == 0:

        print(
            "  FAIL: Root has no children"
        )

        return False

    print(
        f"  ROOT OK: {root.name}"
    )

    print(
        f"  Children: {len(children)}"
    )

    return True


# ============================================================
# MAIN TEST
# ============================================================

def main():

    print("\n")
    print("=" * 65)
    print("AI INTERIOR DESIGN STUDIO")
    print("DAY 13 - PART 8")
    print("ALL ASSET UNIT TEST")
    print("=" * 65)

    # --------------------------------------------------------
    # Check library
    # --------------------------------------------------------

    if not os.path.exists(ASSET_LIBRARY):

        print("\nERROR")
        print(
            "Asset-unit library not found:"
        )
        print(ASSET_LIBRARY)

        return

    print("\nAsset library:")
    print(ASSET_LIBRARY)

    # --------------------------------------------------------
    # Clear scene
    # --------------------------------------------------------

    clear_scene()

    # --------------------------------------------------------
    # Load all assets
    # --------------------------------------------------------

    successful = 0
    failed = 0

    loaded_assets = []

    for index, asset_name in enumerate(
        ASSET_NAMES
    ):

        print("\n" + "-" * 55)

        result = append_asset_collection(
            asset_name
        )

        if result is None:

            failed += 1
            continue

        root = result["root"]

        # Verify root
        valid = verify_root(
            asset_name,
            root
        )

        if not valid:

            failed += 1
            continue

        # Test transform
        test_transform(
            root,
            index
        )

        loaded_assets.append(
            asset_name
        )

        successful += 1

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print("\n")
    print("=" * 65)
    print("FINAL TEST RESULTS")
    print("=" * 65)

    print(
        f"\nExpected assets : {len(ASSET_NAMES)}"
    )

    print(
        f"Successful      : {successful}"
    )

    print(
        f"Failed          : {failed}"
    )

    print("\n")

    for asset_name in ASSET_NAMES:

        if asset_name in loaded_assets:

            print(
                f"FOUND   : {asset_name}"
            )

        else:

            print(
                f"MISSING : {asset_name}"
            )

    # --------------------------------------------------------
    # Save test file
    # --------------------------------------------------------

    print("\n")

    if failed == 0:

        print(
            "ALL ASSET UNITS PASSED"
        )

        print(
            "\nSaving test scene..."
        )

        bpy.ops.wm.save_as_mainfile(
            filepath=OUTPUT_FILE
        )

        print(
            f"\nTest file saved:"
        )

        print(OUTPUT_FILE)

        print(
            "\nPART 8 SUCCESS"
        )

    else:

        print(
            "\nPART 8 FAILED"
        )

        print(
            "Fix the missing assets before continuing."
        )


# ============================================================
# RUN
# ============================================================

main()