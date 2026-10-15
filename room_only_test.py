import bpy

source = r"C:\python 311\PyCharm Community Edition 2023.1.3\projects\AI-Blender-Studio\projects\AI_Interior_Room_View.blend"
output = r"C:\python 311\PyCharm Community Edition 2023.1.3\projects\AI-Blender-Studio\projects\AI_Room_Only_Test.blend"

bpy.ops.wm.open_mainfile(filepath=source)

room_names = {"AI_Floor", "AI_Wall_Back", "AI_Wall_Left", "AI_Wall_Right"}
for obj in bpy.context.scene.objects:
    if obj.type == 'MESH' and obj.name not in room_names:
        obj.hide_set(True)

for obj in bpy.context.scene.objects:
    if obj.name in room_names:
        obj.hide_set(False)

bpy.ops.wm.save_as_mainfile(filepath=output)
print("Room-only test saved:", output)
