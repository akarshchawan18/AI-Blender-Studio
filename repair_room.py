import bpy

room_names = [
    "AI_Floor",
    "AI_Wall_Back",
    "AI_Wall_Left",
    "AI_Wall_Right",
    "AI_Ceiling",
]

scene = bpy.context.scene
root_collection = scene.collection.children.get("Collection")

if root_collection is None:
    root_collection = bpy.data.collections.new("Collection")
    scene.collection.children.link(root_collection)

for name in room_names:
    obj = bpy.data.objects.get(name)
    if obj is None:
        print("MISSING:", name)
        continue

    if obj.name not in scene.objects:
        root_collection.objects.link(obj)

    obj.hide_render = False
    obj.hide_viewport = False

    try:
        obj.hide_set(False)
    except Exception:
        pass

    print("RESTORED:", obj.name, "dimensions:", tuple(round(v, 2) for v in obj.dimensions))

for obj in bpy.context.selected_objects:
    obj.select_set(False)

floor = bpy.data.objects.get("AI_Floor")
if floor:
    floor.select_set(True)
    bpy.context.view_layer.objects.active = floor

output = bpy.path.abspath("//AI_Interior_Repaired.blend")
bpy.ops.wm.save_as_mainfile(filepath=output)
print("REPAIRED COPY:", output)
