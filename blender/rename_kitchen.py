import bpy

scene = bpy.context.scene

renames = {
    "Room": "Kitchen Structure",
    "Kitchen": "Kitchen Furniture & Appliances",
}

for old_name, new_name in renames.items():
    col = bpy.data.collections.get(old_name)
    if col:
        col.name = new_name

for obj_name, new_name in {
    "Room_Floor": "Kitchen_Floor",
    "Room_Back_Wall": "Kitchen_Back_Wall",
    "Room_Left_Wall": "Kitchen_Left_Wall",
    "Room_Right_Wall": "Kitchen_Right_Wall",
}.items():
    obj = bpy.data.objects.get(obj_name)
    if obj:
        obj.name = new_name

bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)

print("Kitchen structure renamed and saved.")
