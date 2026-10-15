import bpy

path = r"C:\python 311\PyCharm Community Edition 2023.1.3\projects\AI-Blender-Studio\projects\AI_Interior_Final.blend"
bpy.ops.wm.open_mainfile(filepath=path)

print("\n--- SAVED SCENE OBJECTS ---")

for obj in bpy.context.scene.objects:
    if any(word in obj.name.lower() for word in ("sofa", "coffee", "table", "tv", "camera")):
        print(
            obj.name,
            "| type:", obj.type,
            "| location:", tuple(round(v, 2) for v in obj.location),
            "| hidden render:", obj.hide_render,
            "| dimensions:", tuple(round(v, 2) for v in obj.dimensions)
        )

print("\nActive camera:", bpy.context.scene.camera.name if bpy.context.scene.camera else "NONE")
