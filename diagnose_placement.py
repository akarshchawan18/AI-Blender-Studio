import bpy
from mathutils import Vector

blend_path = r"C:\python 311\PyCharm Community Edition 2023.1.3\projects\AI-Blender-Studio\projects\AI_Interior_Final.blend"

bpy.ops.wm.open_mainfile(filepath=blend_path)

print("\n========== ROOM AND FURNITURE DIAGNOSTIC ==========")

for name in ("AI_Floor", "Floor", "Room_Floor"):
    obj = bpy.data.objects.get(name)
    if obj:
        print("Floor found:", name, "location:", tuple(round(v, 2) for v in obj.location))

for parent_name in (
    "ASSET_INSTANCE_Sofa_Modern",
    "ASSET_INSTANCE_TVUnit_Wood",
    "ASSET_INSTANCE_CoffeeTable_Modern",
):
    parent = bpy.data.objects.get(parent_name)

    if not parent:
        print("\nMISSING PARENT:", parent_name)
        continue

    print("\n", parent_name)
    print("Parent location:", tuple(round(v, 2) for v in parent.location))
    print("Parent rotation:", tuple(round(v, 2) for v in parent.rotation_euler))

    children = [
        obj for obj in bpy.data.objects
        if obj.type == "MESH"
        and (
            obj == parent
            or obj.parent == parent
            or obj.name.startswith(parent_name.replace("ASSET_INSTANCE_", ""))
        )
    ]

    if not children:
        print("No matching mesh children found.")
        continue

    for obj in children:
        corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
        mins = [min(v[i] for v in corners) for i in range(3)]
        maxs = [max(v[i] for v in corners) for i in range(3)]

        print(
            obj.name,
            "| world min:", tuple(round(v, 2) for v in mins),
            "| world max:", tuple(round(v, 2) for v in maxs),
        )

camera = bpy.context.scene.camera
print("\nCamera:", camera.name if camera else "NONE")
if camera:
    print("Camera location:", tuple(round(v, 2) for v in camera.location))
    print("Camera rotation:", tuple(round(v, 2) for v in camera.rotation_euler))

print("\n========== END DIAGNOSTIC ==========")
