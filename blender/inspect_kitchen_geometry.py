import bpy
from mathutils import Vector

names = [
    "Kitchen_Floor",
    "Kitchen_Back_Wall",
    "Kitchen_Left_Wall",
    "Kitchen_Right_Wall",
    "Base_Cabinet_1",
    "Base_Cabinet_2",
    "Base_Cabinet_3",
    "Base_Cabinet_4",
    "Stone_Countertop",
    "Upper_Cabinet_1",
    "Upper_Cabinet_2",
    "Upper_Cabinet_3",
    "Upper_Cabinet_4",
    "Refrigerator",
]

fallback = {
    "Kitchen_Floor": "Room_Floor",
    "Kitchen_Back_Wall": "Room_Back_Wall",
    "Kitchen_Left_Wall": "Room_Left_Wall",
    "Kitchen_Right_Wall": "Room_Right_Wall",
}

print("\n===== KITCHEN GEOMETRY REPORT =====")

for name in names:
    obj = bpy.data.objects.get(name)
    if obj is None:
        obj = bpy.data.objects.get(fallback.get(name, name))

    if obj is None:
        print(f"{name}: NOT FOUND")
        continue

    corners = [
        obj.matrix_world @ Vector(corner)
        for corner in obj.bound_box
    ]

    mins = [
        min(v[i] for v in corners)
        for i in range(3)
    ]
    maxs = [
        max(v[i] for v in corners)
        for i in range(3)
    ]

    print(
        f"{obj.name}: "
        f"X={mins[0]:.2f}..{maxs[0]:.2f}, "
        f"Y={mins[1]:.2f}..{maxs[1]:.2f}, "
        f"Z={mins[2]:.2f}..{maxs[2]:.2f}"
    )

print("\nInspection complete. Scene was not modified.")
