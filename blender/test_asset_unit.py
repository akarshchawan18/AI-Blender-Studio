import bpy
import os
from mathutils import Vector


# =========================================================
# PATHS
# =========================================================

PROJECT_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

ASSET_LIBRARY = os.path.join(
    PROJECT_DIR,
    "assets",
    "interior_assets_units.blend"
)

OUTPUT_FILE = os.path.join(
    PROJECT_DIR,
    "projects",
    "test_sofa_unit.blend"
)


# =========================================================
# CLEAR SCENE
# =========================================================

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

for collection in list(bpy.data.collections):

    if collection.name != "Collection":

        bpy.data.collections.remove(
            collection
        )


# =========================================================
# LOAD SOFA
# =========================================================

print("=" * 50)
print("ASSET UNIT TEST")
print("=" * 50)

print("\nLoading Sofa_Modern...")

with bpy.data.libraries.load(
    ASSET_LIBRARY,
    link=False
) as (
    data_from,
    data_to
):

    if "Sofa_Modern" not in data_from.collections:

        print("ERROR: Sofa_Modern not found")

        raise SystemExit

    data_to.collections = [
        "Sofa_Modern"
    ]


collection = data_to.collections[0]

bpy.context.scene.collection.children.link(
    collection
)


# =========================================================
# FIND ROOT
# =========================================================

root_name = "ASSET_ROOT_Sofa_Modern"

root = bpy.data.objects.get(root_name)

if root is None:

    print("ERROR: Asset root not found")

    raise SystemExit


print(
    "Root found:",
    root.name
)

print(
    "Children:",
    len(root.children)
)


# =========================================================
# TEST TRANSFORM
# =========================================================

print("\nOriginal root location:")

print(
    tuple(round(v, 3) for v in root.location)
)


# Move entire sofa

root.location = (
    0.0,
    0.0,
    0.0
)

root.rotation_euler = (
    0.0,
    0.0,
    0.0
)

root.scale = (
    1.0,
    1.0,
    1.0
)


print("\nMoving sofa to:")

print(
    "X = 0.0"
)

print(
    "Y = 0.0"
)

print(
    "Z = 0.0"
)


# =========================================================
# TEST ROTATION
# =========================================================

root.rotation_euler[2] = 0.35

print(
    "\nApplied rotation:",
    round(root.rotation_euler[2], 3),
    "radians"
)


# =========================================================
# TEST SCALE
# =========================================================

root.scale = (
    1.0,
    1.0,
    1.0
)


# =========================================================
# SAVE
# =========================================================

bpy.ops.wm.save_as_mainfile(
    filepath=OUTPUT_FILE
)


# =========================================================
# RESULT
# =========================================================

print("\n" + "=" * 50)
print("ASSET UNIT TEST COMPLETE")
print("=" * 50)

print(
    "Asset:",
    root_name
)

print(
    "Children:",
    len(root.children)
)

print(
    "Output:",
    OUTPUT_FILE
)

print("\nSUCCESS")