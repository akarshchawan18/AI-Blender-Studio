import bpy

path = r"C:\python 311\PyCharm Community Edition 2023.1.3\projects\AI-Blender-Studio\projects\AI_Interior_Room_View.blend"
bpy.ops.wm.open_mainfile(filepath=path)

print("\n--- OBJECT POSITIONS ---")
for obj in bpy.context.scene.objects:
    if obj.type == "MESH":
        print(
            obj.name,
            "location:", tuple(round(v, 2) for v in obj.location),
            "dimensions:", tuple(round(v, 2) for v in obj.dimensions)
        )
