import bpy

source = r"C:\python 311\PyCharm Community Edition 2023.1.3\projects\AI-Blender-Studio\projects\AI_Interior_Room_View.blend"
output = r"C:\python 311\PyCharm Community Edition 2023.1.3\projects\AI-Blender-Studio\projects\AI_Open_Room_View.blend"

bpy.ops.wm.open_mainfile(filepath=source)

# Make all objects visible first.
for obj in bpy.context.scene.objects:
    obj.hide_set(False)

# Hide the walls in the viewport only.
for name in ["AI_Wall_Back", "AI_Wall_Left", "AI_Wall_Right"]:
    obj = bpy.data.objects.get(name)
    if obj:
        obj.hide_set(True)

# Keep the floor visible.
floor = bpy.data.objects.get("AI_Floor")
if floor:
    floor.hide_set(False)

# Set a useful 3D viewport distance.
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == "VIEW_3D":
            region = area.spaces.active.region_3d
            region.view_perspective = "ORTHO"
            region.view_location = (0, 0, 1)
            region.view_distance = 8

bpy.ops.wm.save_as_mainfile(filepath=output)
print("Created:", output)
