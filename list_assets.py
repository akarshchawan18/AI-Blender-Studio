import bpy
import os

path = os.path.abspath("assets/interior_assets.blend")

print("\n=== ASSET LIBRARY CHECK ===")
print("Path:", path)
print("Exists:", os.path.isfile(path))

if os.path.isfile(path):
    with bpy.data.libraries.load(path, link=False) as (src, dst):
        print("\n=== AVAILABLE COLLECTIONS ===")
        for name in src.collections:
            print(name)
else:
    print("Asset library file not found.")
