import bpy

print("\n========== COLLECTIONS ==========")
for collection in bpy.data.collections:
    print(f"\nCollection: {collection.name}")
    for obj in collection.objects:
        print(f"  - {obj.name} ({obj.type})")

print("\n========== ALL SCENE OBJECTS ==========")
for obj in bpy.context.scene.objects:
    print(f"{obj.name} | {obj.type} | {obj.users_collection[0].name if obj.users_collection else 'No Collection'}")
