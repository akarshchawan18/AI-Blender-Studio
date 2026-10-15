import bpy

library = r"C:\python 311\PyCharm Community Edition 2023.1.3\projects\AI-Blender-Studio\assets\interior_assets.blend"

print("\n--- ASSET LIBRARY CHECK ---")

with bpy.data.libraries.load(library, link=False) as (source, target):
    print("Available collections:")
    for name in source.collections:
        print(" ", name)

    print("\nAvailable objects:")
    for name in source.objects:
        print(" ", name)
