import bpy
from mathutils import Quaternion

source = r"C:\python 311\PyCharm Community Edition 2023.1.3\projects\AI-Blender-Studio\projects\AI_Interior_Final.blend"
output = r"C:\python 311\PyCharm Community Edition 2023.1.3\projects\AI-Blender-Studio\projects\AI_Interior_Room_View.blend"

bpy.ops.wm.open_mainfile(filepath=source)

# Ensure room objects are enabled and visible.
for name in ["AI_Floor", "AI_Wall_Back", "AI_Wall_Left", "AI_Wall_Right"]:
    obj = bpy.data.objects.get(name)
    if obj:
        obj.hide_viewport = False
        obj.hide_render = False
        obj.hide_set(False)

# Set every saved 3D viewport to a useful elevated view.
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == "VIEW_3D":
            space = area.spaces.active
            space.region_3d.view_perspective = 'ORTHO'
            space.region_3d.view_location = (0.0, 0.0, 1.0)
            space.region_3d.view_distance = 9.0
            space.region_3d.view_rotation = Quaternion((0.88, 0.36, 0.20, 0.24)).normalized()

bpy.ops.wm.save_as_mainfile(filepath=output)
print("Saved room-view copy:", output)
