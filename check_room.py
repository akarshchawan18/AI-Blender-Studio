import bpy

path = r"C:\python 311\PyCharm Community Edition 2023.1.3\projects\AI-Blender-Studio\projects\AI_Interior_Room_View.blend"
bpy.ops.wm.open_mainfile(filepath=path)

print("\n--- ALL OBJECTS ---")
for obj in bpy.context.scene.objects:
    if obj.name.startswith(("AI_Floor", "AI_Wall_", "AI_Ceiling")):
        print(
            obj.name,
            "type =", obj.type,
            "location =", tuple(round(v, 2) for v in obj.location),
            "hidden =", obj.hide_get(),
            "viewport_hidden =", obj.hide_viewport
        )

print("\n--- TOTAL OBJECTS ---", len(bpy.context.scene.objects))
