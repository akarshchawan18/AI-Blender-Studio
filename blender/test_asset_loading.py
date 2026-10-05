import bpy
import os

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ASSET_LIBRARY = os.path.join(
    PROJECT_DIR,
    "assets",
    "interior_assets.blend"
)

print("=" * 70)
print("ASSET LOADING TEST")
print("=" * 70)

print("\nAsset library:")
print(ASSET_LIBRARY)

print("\nExists:", os.path.exists(ASSET_LIBRARY))

# ---------------------------------------------------------
# CLEAR SCENE
# ---------------------------------------------------------

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

for collection in list(bpy.data.collections):
    if collection.name != "Collection":
        bpy.data.collections.remove(collection)

# ---------------------------------------------------------
# LOAD COLLECTIONS
# ---------------------------------------------------------

required_assets = [
    "Sofa_Modern",
    "TVUnit_Wood",
    "CoffeeTable_Modern"
]

print("\nRequested assets:")

for asset in required_assets:
    print(" -", asset)

with bpy.data.libraries.load(
    ASSET_LIBRARY,
    link=False
) as (data_from, data_to):

    available_collections = list(data_from.collections)

    print("\nAvailable collections in library:")

    for collection_name in available_collections:
        print(" -", collection_name)

    data_to.collections = [
        name
        for name in required_assets
        if name in available_collections
    ]

# ---------------------------------------------------------
# LINK LOADED COLLECTIONS INTO SCENE
# ---------------------------------------------------------

print("\nLoaded collections:")

for collection in data_to.collections:

    if collection is None:
        continue

    print("LOADED:", collection.name)

    if collection.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(collection)

# ---------------------------------------------------------
# CHECK OBJECTS
# ---------------------------------------------------------

print("\nSCENE OBJECTS:")

for obj in bpy.context.scene.objects:

    print(
        f"{obj.name:30} "
        f"Type={obj.type:10} "
        f"Location={tuple(round(v, 2) for v in obj.location)}"
    )

# ---------------------------------------------------------
# COUNT
# ---------------------------------------------------------

mesh_objects = [
    obj
    for obj in bpy.context.scene.objects
    if obj.type == "MESH"
]

print("\nTotal mesh objects:", len(mesh_objects))

# ---------------------------------------------------------
# SAVE TEST BLEND
# ---------------------------------------------------------

output = os.path.join(
    PROJECT_DIR,
    "projects",
    "asset_loading_test.blend"
)

bpy.ops.wm.save_as_mainfile(filepath=output)

print("\nSaved:")
print(output)

print("\n" + "=" * 70)
print("ASSET LOADING TEST COMPLETE")
print("=" * 70)