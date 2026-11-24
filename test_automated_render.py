
import subprocess
from pathlib import Path

blender = Path(
    r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
)

scene = Path(
    r"C:\python 311\PyCharm Community Edition 2023.1.3"
    r"\projects\AI-Blender-Studio\projects\AI_Interior_Layout_Test.blend"
)

output = scene.parent / "AI_Interior_Automated_Test.png"

if not blender.exists():
    raise FileNotFoundError(f"Blender not found: {blender}")

if not scene.exists():
    raise FileNotFoundError(f"Scene not found: {scene}")

expression = (
    "import bpy; "
    "bpy.context.scene.render.image_settings.file_format='PNG'; "
    f"bpy.context.scene.render.filepath={str(output)!r}; "
    "bpy.context.scene.render.resolution_percentage=100; "
    "bpy.context.scene.render.use_file_extension=True; "
    "bpy.ops.render.render(write_still=True)"
)

subprocess.run(
    [
        str(blender),
        "--background",
        str(scene),
        "--python-expr",
        expression,
    ],
    check=True,
)

if output.exists():
    print(f"SUCCESS: Render saved to {output}")
else:
    print("Render finished, but the expected output file was not found.")
