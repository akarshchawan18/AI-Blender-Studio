import bpy

# Move only the kitchen furniture and appliances forward.
# The room, lighting, and camera remain unchanged.
scene = bpy.context.scene

move_names = [
    "Base_Cabinet_1",
    "Base_Cabinet_2",
    "Base_Cabinet_3",
    "Base_Cabinet_4",
    "Stone_Countertop",
    "Stone_Backsplash",
    "Upper_Cabinet_1",
    "Upper_Cabinet_2",
    "Upper_Cabinet_3",
    "Upper_Cabinet_4",
    "Sink_Rim",
    "Sink_Basin",
    "Faucet_Stem",
    "Faucet_Spout",
    "Faucet_Nozzle",
    "Cooktop",
    "Cooktop_Burner",
    "Burner_Centre",
    "Cooktop_Burner.001",
    "Burner_Centre.001",
    "Cooktop_Burner.002",
    "Burner_Centre.002",
    "Cooktop_Burner.003",
    "Burner_Centre.003",
    "Refrigerator",
    "Fridge_Door_Upper",
    "Fridge_Door_Lower",
    "Fridge_Handle_Upper",
    "Fridge_Handle_Lower",
]

# Include every cabinet door and handle by name.
for obj in list(scene.objects):
    if obj.name.startswith("Cabinet_"):
        if obj.name not in move_names:
            move_names.append(obj.name)
    if obj.name.startswith("Upper_Door_") or obj.name.startswith("Upper_Handle_"):
        if obj.name not in move_names:
            move_names.append(obj.name)

moved = []
for name in move_names:
    obj = bpy.data.objects.get(name)
    if obj is not None:
        obj.location.y -= 0.25
        moved.append(obj.name)

bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)

print(f"\nMoved {len(moved)} furniture objects forward by 0.25 m.")
print("Room walls, floor, lights, and camera were not moved.")
print("Saved:", bpy.data.filepath)
