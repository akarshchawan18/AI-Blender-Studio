import bpy

scene = bpy.context.scene

# Create or reuse collections
def get_collection(name):
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        scene.collection.children.link(col)
    elif col.name not in [c.name for c in scene.collection.children]:
        scene.collection.children.link(col)
    return col

room = get_collection("Room")
kitchen = get_collection("Kitchen")
lighting = get_collection("Lighting & Camera")

room_names = {
    "Room_Floor",
    "Room_Back_Wall",
    "Room_Left_Wall",
    "Room_Right_Wall",
}

light_names = {
    "Kitchen_Key_Light",
    "Kitchen_Fill_Light",
    "Counter_Light",
    "Kitchen_Camera",
}

# Move objects without deleting them
for obj in list(scene.objects):
    if obj.name in room_names:
        target = room
    elif obj.name in light_names:
        target = lighting
    else:
        target = kitchen

    if target not in obj.users_collection:
        target.objects.link(obj)

    for old_col in list(obj.users_collection):
        if old_col != target:
            old_col.objects.unlink(obj)

# Remove the old empty collection if possible
old = bpy.data.collections.get("Collection")
if old is not None and len(old.objects) == 0:
    bpy.data.collections.remove(old)

# Preserve the existing scene and save
bpy.ops.wm.save_as_mainfile(
    filepath=bpy.data.filepath
)

print("\nCOLLECTION ORGANIZATION COMPLETE")
for col in (room, kitchen, lighting):
    print(f"{col.name}: {len(col.objects)} objects")
