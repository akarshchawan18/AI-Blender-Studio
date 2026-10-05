import bpy
import os
import shutil

# =========================================================
# PATHS
# =========================================================

PROJECT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

MASTER_LIBRARY = os.path.join(
    PROJECT_DIR,
    "assets",
    "interior_assets.blend"
)

TEMP_LIBRARY = os.path.join(
    PROJECT_DIR,
    "assets",
    "interior_assets_temp.blend"
)


# =========================================================
# MATERIALS
# =========================================================

def get_or_create_material(name, color):
    material = bpy.data.materials.get(name)

    if material is None:
        material = bpy.data.materials.new(name)

    material.diffuse_color = (
        color[0],
        color[1],
        color[2],
        1.0
    )

    return material


FABRIC = get_or_create_material(
    "ASSET_Fabric_Modern",
    (0.45, 0.45, 0.45)
)

FABRIC_LIGHT = get_or_create_material(
    "ASSET_Fabric_Light",
    (0.70, 0.68, 0.64)
)

WOOD = get_or_create_material(
    "ASSET_Wood_Modern",
    (0.25, 0.12, 0.05)
)

BLACK = get_or_create_material(
    "ASSET_Black_Modern",
    (0.03, 0.03, 0.03)
)

METAL = get_or_create_material(
    "ASSET_Metal_Modern",
    (0.35, 0.35, 0.35)
)


# =========================================================
# CREATE COLLECTION
# =========================================================

def create_collection(name):
    existing = bpy.data.collections.get(name)

    if existing:
        print("Collection already exists:", name)

        return existing

    collection = bpy.data.collections.new(name)

    bpy.context.scene.collection.children.link(
        collection
    )

    return collection


# =========================================================
# CREATE CUBE
# =========================================================

def create_cube(
        name,
        location,
        dimensions,
        material,
        collection
):
    bpy.ops.mesh.primitive_cube_add(
        location=location
    )

    obj = bpy.context.object

    obj.name = name

    obj.dimensions = dimensions

    bpy.ops.object.transform_apply(
        location=False,
        rotation=False,
        scale=True
    )

    # Remove from current collections
    for old_collection in list(
            obj.users_collection
    ):
        old_collection.objects.unlink(obj)

    # Add to target collection
    collection.objects.link(obj)

    if material:
        obj.data.materials.append(
            material
        )

    return obj


# =========================================================
# CREATE CYLINDER
# =========================================================

def create_cylinder(
        name,
        location,
        radius,
        depth,
        material,
        collection
):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=radius,
        depth=depth,
        location=location
    )

    obj = bpy.context.object

    obj.name = name

    for old_collection in list(
            obj.users_collection
    ):
        old_collection.objects.unlink(obj)

    collection.objects.link(obj)

    if material:
        obj.data.materials.append(
            material
        )

    return obj


# =========================================================
# CHAIR
# =========================================================

def create_chair():
    print()
    print("Creating Chair_Modern...")

    collection = create_collection(
        "Chair_Modern"
    )

    # -----------------------------------------------------
    # Seat
    # -----------------------------------------------------

    create_cube(
        "Chair_Seat",
        (0, 0, 0.45),
        (0.75, 0.75, 0.18),
        FABRIC,
        collection
    )

    # -----------------------------------------------------
    # Back
    # -----------------------------------------------------

    create_cube(
        "Chair_Back",
        (0, 0.30, 0.95),
        (0.75, 0.15, 1.00),
        FABRIC,
        collection
    )

    # -----------------------------------------------------
    # Legs
    # -----------------------------------------------------

    leg_positions = [
        (-0.27, -0.27),
        (0.27, -0.27),
        (-0.27, 0.27),
        (0.27, 0.27)
    ]

    for index, (x, y) in enumerate(
            leg_positions
    ):
        create_cube(
            f"Chair_Leg_{index + 1}",
            (x, y, 0.20),
            (0.08, 0.08, 0.40),
            WOOD,
            collection
        )

    # -----------------------------------------------------
    # Mark collection as asset
    # -----------------------------------------------------

    try:
        collection.asset_mark()
    except Exception:
        pass

    return collection


# =========================================================
# L-SHAPE SOFA
# =========================================================

def create_l_shape_sofa():
    print()
    print("Creating Sofa_LShape...")

    collection = create_collection(
        "Sofa_LShape"
    )

    # -----------------------------------------------------
    # Main seat
    # -----------------------------------------------------

    create_cube(
        "LShape_Main_Seat",
        (0, 0, 0.45),
        (2.80, 1.00, 0.25),
        FABRIC_LIGHT,
        collection
    )

    # -----------------------------------------------------
    # Main back
    # -----------------------------------------------------

    create_cube(
        "LShape_Main_Back",
        (0, 0.40, 0.95),
        (2.80, 0.20, 1.00),
        FABRIC,
        collection
    )

    # -----------------------------------------------------
    # Main arm
    # -----------------------------------------------------

    create_cube(
        "LShape_Main_Arm",
        (-1.30, 0, 0.75),
        (0.20, 1.00, 0.60),
        FABRIC,
        collection
    )

    # -----------------------------------------------------
    # L section seat
    # -----------------------------------------------------

    create_cube(
        "LShape_Side_Seat",
        (0.90, -0.50, 0.45),
        (1.00, 1.80, 0.25),
        FABRIC_LIGHT,
        collection
    )

    # -----------------------------------------------------
    # L section back
    # -----------------------------------------------------

    create_cube(
        "LShape_Side_Back",
        (1.30, 0.00, 0.95),
        (0.20, 1.00, 1.00),
        FABRIC,
        collection
    )

    # -----------------------------------------------------
    # Side arm
    # -----------------------------------------------------

    create_cube(
        "LShape_Side_Arm",
        (0.90, -1.30, 0.75),
        (1.00, 0.20, 0.60),
        FABRIC,
        collection
    )

    # -----------------------------------------------------
    # Legs
    # -----------------------------------------------------

    leg_positions = [
        (-1.10, -0.30),
        (0.00, -0.30),
        (1.10, -0.30),
        (-1.10, 0.30),
        (0.00, 0.30),
        (1.10, 0.30)
    ]

    for index, (x, y) in enumerate(
            leg_positions
    ):
        create_cube(
            f"LShape_Leg_{index + 1}",
            (x, y, 0.20),
            (0.08, 0.08, 0.40),
            WOOD,
            collection
        )

    # -----------------------------------------------------
    # Mark collection as asset
    # -----------------------------------------------------

    try:
        collection.asset_mark()
    except Exception:
        pass

    return collection


# =========================================================
# VERIFY EXISTING MASTER
# =========================================================

def verify_existing_assets():
    print()
    print("==========================================")
    print("CHECKING EXISTING MASTER ASSETS")
    print("==========================================")

    expected = [
        "Sofa_Modern",
        "CoffeeTable_Modern",
        "TVUnit_Wood",
        "Bed_Modern",
        "Wardrobe_Modern",
        "Desk_Modern",
        "DiningTable_Modern",
        "Lamp_Modern"
    ]

    missing = []

    for name in expected:

        if bpy.data.collections.get(name):

            print("FOUND:", name)

        else:

            print("MISSING:", name)

            missing.append(name)

    if missing:
        raise RuntimeError(
            "Existing master library is missing assets: "
            + ", ".join(missing)
        )


# =========================================================
# VERIFY NEW ASSETS
# =========================================================

def verify_new_assets():
    print()
    print("==========================================")
    print("VERIFYING NEW ASSETS")
    print("==========================================")

    required = [
        "Chair_Modern",
        "Sofa_LShape"
    ]

    for name in required:

        collection = bpy.data.collections.get(
            name
        )

        if collection is None:
            raise RuntimeError(
                f"Missing new asset: {name}"
            )

        object_count = len(
            collection.all_objects
        )

        print(
            f"FOUND: {name} | Objects: {object_count}"
        )


# =========================================================
# SAVE
# =========================================================

def save_master():
    print()
    print("==========================================")
    print("SAVING MASTER ASSET LIBRARY")
    print("==========================================")

    bpy.ops.wm.save_as_mainfile(
        filepath=TEMP_LIBRARY
    )

    if os.path.exists(MASTER_LIBRARY):
        os.remove(MASTER_LIBRARY)

    shutil.move(
        TEMP_LIBRARY,
        MASTER_LIBRARY
    )

    print()
    print("Master library saved:")
    print(MASTER_LIBRARY)


# =========================================================
# MAIN
# =========================================================

def main():
    print()
    print("==========================================")
    print("CREATE MISSING INTERIOR ASSETS")
    print("==========================================")

    if not os.path.exists(MASTER_LIBRARY):
        raise FileNotFoundError(
            "Master asset library not found:\n"
            + MASTER_LIBRARY
        )

    # -----------------------------------------------------
    # IMPORTANT:
    # Open the existing master library.
    # -----------------------------------------------------

    print()
    print("Opening existing master library...")

    bpy.ops.wm.open_mainfile(
        filepath=MASTER_LIBRARY
    )

    print("Master library opened.")

    # -----------------------------------------------------
    # Verify existing assets BEFORE modifying
    # -----------------------------------------------------

    verify_existing_assets()

    # -----------------------------------------------------
    # Create missing assets
    # -----------------------------------------------------

    create_chair()

    create_l_shape_sofa()

    # -----------------------------------------------------
    # Verify
    # -----------------------------------------------------

    verify_new_assets()

    # -----------------------------------------------------
    # Count all target assets
    # -----------------------------------------------------

    all_assets = [
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

    print()
    print("==========================================")
    print("FINAL ASSET COUNT")
    print("==========================================")

    found = 0

    for name in all_assets:

        if bpy.data.collections.get(name):

            print("FOUND:", name)

            found += 1

        else:

            print("MISSING:", name)

    print()
    print(
        f"Assets found: {found} / {len(all_assets)}"
    )

    if found != len(all_assets):
        raise RuntimeError(
            "Not all required assets exist."
        )

    # -----------------------------------------------------
    # Save
    # -----------------------------------------------------

    save_master()

    print()
    print("==========================================")
    print("SUCCESS")
    print("==========================================")

    print()
    print("Master library now contains:")

    for name in all_assets:
        print(" -", name)


if __name__ == "__main__":
    main()