import bpy

source = r"C:\python 311\PyCharm Community Edition 2023.1.3\projects\AI-Blender-Studio\projects\AI_Interior_Room_View.blend"
output = r"C:\python 311\PyCharm Community Edition 2023.1.3\projects\AI-Blender-Studio\projects\AI_Full_Scene_Test.blend"

bpy.ops.wm.open_mainfile(filepath=source)

# Unhide every object in the scene.
for obj in bpy.context.scene.objects:
    obj.hide_set(False)
    obj.hide_viewport = False

# Keep the room visible and set a useful viewing distance.
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == "VIEW_3D":
            space = area.spaces.active
            space.region_3d.view_perspective = "ORTHO"
            space.region_3d.view_location = (0, 0, 1)
            space.region_3d.view_distance = 10

bpy.ops.wm.save_as_mainfile(filepath=output)
print("Saved:", output)
