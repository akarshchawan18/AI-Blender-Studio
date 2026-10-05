import bpy
import os


# ==========================================
# AI BLENDER STUDIO
# FURNITURE GENERATOR
# ==========================================

print("================================")
print("AI BLENDER FURNITURE GENERATOR")
print("================================")


# ==========================================
# 1. CLEAR SCENE
# ==========================================

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

print("Scene cleared")


# ==========================================
# 2. CREATE BOX
# ==========================================

def create_box(name, location, dimensions):

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

    return obj


# ==========================================
# 3. CREATE MATERIAL
# ==========================================

def create_material(name, color, roughness=0.5):

    material = bpy.data.materials.get(name)

    if material is None:
        material = bpy.data.materials.new(name)

    material.use_nodes = True

    principled = material.node_tree.nodes.get(
        "Principled BSDF"
    )

    if principled:

        principled.inputs[
            "Base Color"
        ].default_value = (
            color[0],
            color[1],
            color[2],
            1
        )

        principled.inputs[
            "Roughness"
        ].default_value = roughness

    return material


# ==========================================
# 4. APPLY MATERIAL
# ==========================================

def apply_material(obj, material):

    obj.data.materials.clear()

    obj.data.materials.append(material)


# ==========================================
# 5. MATERIALS
# ==========================================

fabric = create_material(
    "MAT_Sofa_Fabric",
    (0.18, 0.20, 0.22),
    0.8
)

wood = create_material(
    "MAT_Wood",
    (0.15, 0.055, 0.02),
    0.5
)

black = create_material(
    "MAT_Black",
    (0.015, 0.015, 0.015),
    0.3
)

white = create_material(
    "MAT_White",
    (0.8, 0.8, 0.78),
    0.6
)

rug_material = create_material(
    "MAT_Rug",
    (0.35, 0.28, 0.20),
    0.95
)


# ==========================================
# 6. SOFA
# ==========================================

# Seat

sofa_seat = create_box(
    "Sofa_Seat",
    (0, 0.8, 0.45),
    (2.4, 0.85, 0.35)
)

apply_material(
    sofa_seat,
    fabric
)


# Back

sofa_back = create_box(
    "Sofa_Back",
    (0, 1.15, 1.0),
    (2.4, 0.25, 1.1)
)

apply_material(
    sofa_back,
    fabric
)


# Left arm

sofa_left = create_box(
    "Sofa_Arm_Left",
    (-1.15, 0.8, 0.75),
    (0.25, 0.85, 0.8)
)

apply_material(
    sofa_left,
    fabric
)


# Right arm

sofa_right = create_box(
    "Sofa_Arm_Right",
    (1.15, 0.8, 0.75),
    (0.25, 0.85, 0.8)
)

apply_material(
    sofa_right,
    fabric
)


print("Sofa created")


# ==========================================
# 7. COFFEE TABLE
# ==========================================

table_top = create_box(
    "Coffee_Table_Top",
    (0, -0.45, 0.55),
    (1.5, 0.8, 0.12)
)

apply_material(
    table_top,
    wood
)


# Table legs

for x in (-0.6, 0.6):

    for y in (-0.25, 0.25):

        leg = create_box(
            "Coffee_Table_Leg",
            (x, -0.45 + y, 0.27),
            (0.1, 0.1, 0.55)
        )

        apply_material(
            leg,
            wood
        )


print("Coffee table created")


# ==========================================
# 8. TV UNIT
# ==========================================

tv_unit = create_box(
    "TV_Unit",
    (0, -1.45, 0.45),
    (2.6, 0.4, 0.7)
)

apply_material(
    tv_unit,
    wood
)


# ==========================================
# 9. TV
# ==========================================

tv = create_box(
    "TV",
    (0, -1.68, 1.5),
    (2.2, 0.08, 1.25)
)

apply_material(
    tv,
    black
)


# TV stand

tv_stand = create_box(
    "TV_Stand",
    (0, -1.55, 0.85),
    (0.8, 0.2, 0.12)
)

apply_material(
    tv_stand,
    black
)


print("TV unit created")


# ==========================================
# 10. RUG
# ==========================================

rug = create_box(
    "Living_Room_Rug",
    (0, 0, 0.08),
    (3.0, 2.0, 0.05)
)

apply_material(
    rug,
    rug_material
)

print("Rug created")


# ==========================================
# 11. SIDE TABLE
# ==========================================

side_table = create_box(
    "Side_Table",
    (1.7, 0.8, 0.45),
    (0.5, 0.5, 0.7)
)

apply_material(
    side_table,
    wood
)

print("Side table created")


# ==========================================
# 12. FLOOR LAMP
# ==========================================

# Pole

lamp_pole = create_box(
    "Lamp_Pole",
    (2.0, 0.8, 1.4),
    (0.06, 0.06, 1.4)
)

apply_material(
    lamp_pole,
    black
)


# Lamp shade

bpy.ops.mesh.primitive_cone_add(
    vertices=32,
    radius1=0.35,
    radius2=0.2,
    depth=0.45,
    location=(2.0, 0.8, 2.75)
)

lamp_shade = bpy.context.object

lamp_shade.name = "Lamp_Shade"

apply_material(
    lamp_shade,
    white
)


print("Floor lamp created")


# ==========================================
# 13. SAVE
# ==========================================

project_dir = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "projects"
    )
)

os.makedirs(
    project_dir,
    exist_ok=True
)

blend_path = os.path.join(
    project_dir,
    "living_room_furniture.blend"
)

bpy.ops.wm.save_as_mainfile(
    filepath=blend_path
)


# ==========================================
# 14. COMPLETE
# ==========================================

print("================================")
print("FURNITURE GENERATION COMPLETE")
print("================================")

print("Project saved:")
print(blend_path)

print("================================")