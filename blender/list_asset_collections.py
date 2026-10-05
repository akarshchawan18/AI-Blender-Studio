import bpy
import os

PROJECT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

ASSET_LIBRARY = os.path.join(
    PROJECT_DIR,
    "assets",
    "interior_assets.blend"
)

print()
print("==========================================")
print("ASSET LIBRARY COLLECTION LIST")
print("==========================================")
print()

if not os.path.exists(ASSET_LIBRARY):
    print("ERROR:")
    print("Asset library not found:")
    print(ASSET_LIBRARY)
    raise SystemExit

print("Asset library:")
print(ASSET_LIBRARY)
print()

with bpy.data.libraries.load(
    ASSET_LIBRARY,
    link=False
) as (data_from, data_to):

    print("Collections inside interior_assets.blend:")
    print()

    for collection_name in data_from.collections:
        print(" -", collection_name)

print()
print("==========================================")
print("DONE")
print("==========================================")
print()