import bpy
import os

print("================================")
print("AI BLENDER PROJECT")
print("================================")

# Delete default objects
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

# Create cube
bpy.ops.mesh.primitive_cube_add(
    location=(0, 0, 1)
)

cube = bpy.context.object
cube.name = "AI_Test_Cube"
cube.scale = (2, 2, 1)

print("Cube created!")

# Find project directory
project_dir = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "projects"
    )
)

# Create projects directory if needed
os.makedirs(project_dir, exist_ok=True)

# Save Blender project
blend_path = os.path.join(
    project_dir,
    "test_project.blend"
)

bpy.ops.wm.save_as_mainfile(
    filepath=blend_path
)

print("================================")
print("PROJECT SAVED")
print(blend_path)
print("================================")