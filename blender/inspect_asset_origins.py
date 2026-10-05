import bpy
import os
from mathutils import Vector


PROJECT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

ASSET_LIBRARY = os.path.join(
    PROJECT_DIR,
    "assets",
    "interior_assets.blend"
)


ASSETS = [
    "Sofa_Modern",
    "Sofa_LShape",
    "CoffeeTable_Modern",
    "TVUnit_Wood",
    "Chair_Modern",
    "Bed_Modern",
    "Wardrobe_Modern",
    "Desk_Modern",
    "DiningTable_Modern",
    "Lamp_Modern"
]


print("")
print("==========================================")
print("      ASSET ORIGIN INSPECTION")
print("==========================================")


def inspect_asset(asset_name):

    print("")
    print("------------------------------------------")
    print(asset_name)
    print("------------------------------------------")

    # Clear current scene
    bpy.ops.object.select_all(
        action="SELECT"
    )

    bpy.ops.object.delete(
        use_global=False
    )

    # -----------------------------------------------------
    # LOAD COLLECTION
    # -----------------------------------------------------

    with bpy.data.libraries.load(
        ASSET_LIBRARY,
        link=False
    ) as (
        data_from,
        data_to
    ):

        if asset_name not in data_from.collections:

            print(
                "ERROR: Asset not found"
            )

            return

        data_to.collections = [
            asset_name
        ]

    collection = None

    for c in data_to.collections:

        if c is not None:

            collection = c
            break

    if collection is None:

        print(
            "ERROR: Collection failed"
        )

        return

    bpy.context.scene.collection.children.link(
        collection
    )

    # -----------------------------------------------------
    # OBJECTS
    # -----------------------------------------------------

    objects = list(
        collection.all_objects
    )

    mesh_objects = [
        obj
        for obj in objects
        if obj.type == "MESH"
    ]

    print(
        "Objects:",
        len(objects)
    )

    print(
        "Mesh objects:",
        len(mesh_objects)
    )

    # -----------------------------------------------------
    # ORIGINS
    # -----------------------------------------------------

    for obj in mesh_objects:

        print(
            "OBJECT:",
            obj.name
        )

        print(
            "  Location:",
            tuple(
                round(v, 3)
                for v in obj.location
            )
        )

        print(
            "  World:",
            tuple(
                round(v, 3)
                for v in obj.matrix_world.translation
            )
        )

        print(
            "  Dimensions:",
            tuple(
                round(v, 3)
                for v in obj.dimensions
            )
        )

    # -----------------------------------------------------
    # BOUNDS
    # -----------------------------------------------------

    min_x = float("inf")
    min_y = float("inf")
    min_z = float("inf")

    max_x = float("-inf")
    max_y = float("-inf")
    max_z = float("-inf")

    for obj in mesh_objects:

        for corner in obj.bound_box:

            world_corner = (
                obj.matrix_world @
                Vector(corner)
            )

            min_x = min(
                min_x,
                world_corner.x
            )

            min_y = min(
                min_y,
                world_corner.y
            )

            min_z = min(
                min_z,
                world_corner.z
            )

            max_x = max(
                max_x,
                world_corner.x
            )

            max_y = max(
                max_y,
                world_corner.y
            )

            max_z = max(
                max_z,
                world_corner.z
            )

    center = (
        (min_x + max_x) / 2,
        (min_y + max_y) / 2,
        (min_z + max_z) / 2
    )

    floor_center = (
        center[0],
        center[1],
        min_z
    )

    print("")
    print("BOUNDING BOX")

    print(
        "  Min:",
        (
            round(min_x, 3),
            round(min_y, 3),
            round(min_z, 3)
        )
    )

    print(
        "  Max:",
        (
            round(max_x, 3),
            round(max_y, 3),
            round(max_z, 3)
        )
    )

    print("")
    print(
        "  Center:",
        tuple(
            round(v, 3)
            for v in center
        )
    )

    print(
        "  Floor Center:",
        tuple(
            round(v, 3)
            for v in floor_center
        )
    )


for asset in ASSETS:

    inspect_asset(asset)


print("")
print("==========================================")
print("INSPECTION COMPLETE")
print("==========================================")