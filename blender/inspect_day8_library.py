import bpy
import os


PROJECT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

DAY8_LIBRARY = os.path.join(
    PROJECT_DIR,
    "projects",
    "living_room_furniture.blend"
)


print()
print("==========================================")
print("DAY 8 FURNITURE LIBRARY INSPECTOR")
print("==========================================")
print()

print("Library:")
print(DAY8_LIBRARY)
print()


if not os.path.exists(DAY8_LIBRARY):

    print("ERROR:")
    print("Day 8 library not found.")

    raise SystemExit


with bpy.data.libraries.load(
    DAY8_LIBRARY,
    link=False
) as (data_from, data_to):

    print("==========================================")
    print("COLLECTIONS")
    print("==========================================")
    print()

    if data_from.collections:

        for name in data_from.collections:
            print("COLLECTION:", name)

    else:

        print("No collections found.")

    print()
    print("==========================================")
    print("OBJECTS")
    print("==========================================")
    print()

    if data_from.objects:

        for name in data_from.objects:
            print("OBJECT:", name)

    else:

        print("No objects found.")

    print()
    print("==========================================")
    print("MATERIALS")
    print("==========================================")
    print()

    if data_from.materials:

        for name in data_from.materials:
            print("MATERIAL:", name)

    else:

        print("No materials found.")


print()
print("==========================================")
print("INSPECTION COMPLETE")
print("==========================================")
print()