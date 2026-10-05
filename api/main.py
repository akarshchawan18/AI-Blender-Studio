from fastapi import FastAPI
from pydantic import BaseModel
import json
import os
import subprocess

from api.layout_optimizer import find_best_layout

from api.style_engine import (
    get_style_materials,
    get_style_lighting,
    apply_style_to_assets
)

from api.room_size_engine import (
    detect_room_size,
    get_room_dimensions,
    apply_room_size_to_assets
)

from api.layout_validator import validate_and_fix_layout


# =========================================================
# APP
# =========================================================

app = FastAPI(
    title="AI Interior Design Generator",
    description="Local AI-ready Interior Design Generator",
    version="3.1.0"
)


# =========================================================
# PROJECT PATHS
# =========================================================

PROJECT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

SCENE_FILE = os.path.join(
    PROJECT_DIR,
    "scene_generated.json"
)

BLENDER_EXE = (
    r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
)

BLENDER_SCRIPT = os.path.join(
    PROJECT_DIR,
    "blender",
    "ai_interior_generator.py"
)


# =========================================================
# REQUEST MODEL
# =========================================================

class GenerateRequest(BaseModel):
    prompt: str


# =========================================================
# RESPONSE MODEL
# =========================================================

class GenerateResponse(BaseModel):
    status: str
    message: str
    prompt: str
    planner: str

    # Room information
    room_type: str
    room_size: str
    style: str

    # Layout intelligence
    layout_score: float
    layout_variation: int
    candidates_tested: int
    layout_valid: bool

    # Generated files
    scene_file: str
    blend_file: str
    render_file: str

    # Blender result
    blender_return_code: int


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():

    return {
        "status": "online",
        "message": "AI Interior Design Generator API is running",
        "version": "3.1.0"
    }


# =========================================================
# COLOR DETECTION
# =========================================================

def detect_sofa_color(prompt):

    if "grey sofa" in prompt or "gray sofa" in prompt:
        return "#808080"

    if "white sofa" in prompt:
        return "#F5F5F5"

    if "black sofa" in prompt:
        return "#202020"

    if "beige sofa" in prompt:
        return "#D8C3A5"

    if "brown sofa" in prompt:
        return "#6B4226"

    return "#C8B39A"


def detect_wall_color(prompt):

    if "white wall" in prompt:
        return "#F5F5F5"

    if "grey wall" in prompt or "gray wall" in prompt:
        return "#B8B8B8"

    if "beige wall" in prompt:
        return "#E8DED0"

    if "dark wall" in prompt:
        return "#303030"

    if "green wall" in prompt:
        return "#6F8068"

    return "#E8DED0"


def detect_floor_color(prompt):

    if "light wood" in prompt:
        return "#C69C6D"

    if "dark wood" in prompt:
        return "#5A3825"

    if "white floor" in prompt:
        return "#E8E8E8"

    if "grey floor" in prompt or "gray floor" in prompt:
        return "#858585"

    return "#8B5E3C"


# =========================================================
# STYLE DETECTION
# =========================================================

def detect_style(prompt):

    if "luxury" in prompt:
        return "luxury"

    if "minimal" in prompt:
        return "minimal"

    if "traditional" in prompt:
        return "traditional"

    if "classic" in prompt:
        return "classic"

    if "industrial" in prompt:
        return "industrial"

    return "modern"


# =========================================================
# ROOM TYPE
# =========================================================

def detect_room_type(prompt):

    if "home office" in prompt:
        return "office"

    if "office" in prompt:
        return "office"

    if "bedroom" in prompt:
        return "bedroom"

    if "dining room" in prompt:
        return "dining_room"

    if "dining" in prompt:
        return "dining_room"

    return "living_room"


# =========================================================
# LIGHTING DETECTION
# =========================================================

def detect_lighting(prompt):

    if "daylight" in prompt:
        return {
            "type": "daylight",
            "brightness": 1.5
        }

    if "bright lighting" in prompt:
        return {
            "type": "bright",
            "brightness": 1.5
        }

    if "cool lighting" in prompt:
        return {
            "type": "cool",
            "brightness": 1.0
        }

    if "dark lighting" in prompt:
        return {
            "type": "dark",
            "brightness": 0.5
        }

    if "warm lighting" in prompt:
        return {
            "type": "warm",
            "brightness": 1.0
        }

    return {
        "type": "warm",
        "brightness": 1.0
    }


# =========================================================
# CAMERA
# =========================================================

def detect_camera(prompt):

    if "close up" in prompt or "close-up" in prompt:

        return {
            "position": [3.2, -3.2, 2.0],
            "target": [0, 0, 1.0]
        }

    return {
        "position": [4.2, -4.2, 2.5],
        "target": [0, 0, 1.1]
    }


# =========================================================
# LOCAL SCENE PLANNER
# =========================================================

def create_local_scene(prompt_text):

    prompt = prompt_text.lower().strip()

    # =====================================================
    # DETECT REQUIREMENTS
    # =====================================================

    room_type = detect_room_type(prompt)

    style = detect_style(prompt)

    sofa_color = detect_sofa_color(prompt)

    wall_color = detect_wall_color(prompt)

    floor_color = detect_floor_color(prompt)

    camera = detect_camera(prompt)

    # =====================================================
    # ROOM SIZE
    # =====================================================

    room_size = detect_room_size(prompt)

    room_dimensions = get_room_dimensions(
        room_size
    )

    room_width = room_dimensions["width"]
    room_length = room_dimensions["length"]
    room_height = room_dimensions["height"]

    # =====================================================
    # STYLE MATERIALS
    # =====================================================

    materials = get_style_materials(style)

    # =====================================================
    # USER COLOR OVERRIDES
    # =====================================================

    materials["wall"] = wall_color
    materials["floor"] = floor_color

    materials["sofa"] = sofa_color

    # =====================================================
    # LIGHTING
    # =====================================================

    lighting = get_style_lighting(style)

    # =====================================================
    # USER LIGHTING OVERRIDES
    # =====================================================

    if "daylight" in prompt:

        lighting = {
            "type": "daylight",
            "brightness": 1.5
        }

    elif "bright lighting" in prompt:

        lighting = {
            "type": "bright",
            "brightness": 1.5
        }

    elif "cool lighting" in prompt:

        lighting = {
            "type": "cool",
            "brightness": 1.0
        }

    elif "warm lighting" in prompt:

        lighting = {
            "type": "warm",
            "brightness": 1.0
        }

    elif "dark lighting" in prompt:

        lighting = {
            "type": "dark",
            "brightness": 0.5
        }

    # =====================================================
    # MULTI-LAYOUT OPTIMIZATION
    # =====================================================

    layout_result = find_best_layout(
        room_type,
        room_width,
        room_length,
        candidate_count=5
    )

    best_layout = layout_result["best"]

    assets = best_layout["assets"]

    layout_score = float(
        best_layout["score"]
    )

    layout_variation = int(
        best_layout["variation"]
    )

    layout_valid = bool(
        best_layout["valid"]
    )

    layout_reasons = best_layout.get(
        "reasons",
        []
    )

    # =====================================================
    # APPLY ROOM SIZE
    # =====================================================

    assets = apply_room_size_to_assets(
        assets,
        room_size
    )

    # =====================================================
    # APPLY STYLE
    # =====================================================

    assets = apply_style_to_assets(
        assets,
        style
    )

    # =====================================================
    # OPTIONAL LIVING ROOM CHAIR
    # =====================================================

    if room_type == "living_room" and "chair" in prompt:

        assets.append({

            "asset": "Chair_Modern",

            "position": [
                room_width * 0.30,
                room_length * 0.10,
                0
            ],

            "rotation": [
                0,
                0,
                1.5708
            ],

            "scale": [
                1,
                1,
                1
            ]

        })

    # =====================================================
    # OPTIONAL BEDROOM TV
    # =====================================================

    if room_type == "bedroom" and "tv" in prompt:

        assets.append({

            "asset": "TVUnit_Wood",

            "position": [
                0,
                -room_length * 0.40,
                0
            ],

            "rotation": [
                0,
                0,
                0
            ],

            "scale": [
                1,
                1,
                1
            ]

        })

    # =====================================================
    # FINAL VALIDATION
    # =====================================================

    assets, validation = validate_and_fix_layout(
        assets,
        room_width,
        room_length
    )

    # =====================================================
    # ADD OPTIMIZER INFORMATION
    # =====================================================

    validation["layout_score"] = layout_score

    validation["layout_variation"] = layout_variation

    validation["layout_valid"] = layout_valid

    validation["layout_reasons"] = layout_reasons

    validation["candidates_tested"] = len(
        layout_result["candidates"]
    )

    # =====================================================
    # FINAL SCENE DATA
    # =====================================================

    scene_data = {

        "room": {

            "type": room_type,

            "size": room_size,

            "width": room_width,

            "length": room_length,

            "height": room_height

        },

        "style": style,

        "prompt": prompt_text,

        "materials": materials,

        "assets": assets,

        "lighting": lighting,

        "camera": camera,

        "validation": validation

    }

    return scene_data


# =========================================================
# GENERATE
# =========================================================

@app.post(
    "/generate",
    response_model=GenerateResponse
)
def generate(request: GenerateRequest):

    prompt = request.prompt.strip()

    # =====================================================
    # EMPTY PROMPT
    # =====================================================

    if not prompt:

        return GenerateResponse(

            status="error",

            message="Prompt cannot be empty",

            prompt="",

            planner="local",

            room_type="unknown",

            room_size="unknown",

            style="unknown",

            layout_score=0.0,

            layout_variation=0,

            candidates_tested=0,

            layout_valid=False,

            scene_file="",

            blend_file="",

            render_file="",

            blender_return_code=-1
        )

    # =====================================================
    # CREATE SCENE
    # =====================================================

    scene_data = create_local_scene(
        prompt
    )

    # =====================================================
    # EXTRACT SCENE INFORMATION
    # =====================================================

    room_type = scene_data["room"]["type"]

    room_size = scene_data["room"].get(
        "size",
        "medium"
    )

    style = scene_data["style"]

    validation = scene_data.get(
        "validation",
        {}
    )

    # =====================================================
    # EXTRACT LAYOUT INFORMATION
    # =====================================================

    layout_score = float(
        validation.get(
            "layout_score",
            0.0
        )
    )

    layout_variation = int(
        validation.get(
            "layout_variation",
            0
        )
    )

    candidates_tested = int(
        validation.get(
            "candidates_tested",
            0
        )
    )

    layout_valid = bool(
        validation.get(
            "layout_valid",
            validation.get(
                "valid",
                False
            )
        )
    )

    # =====================================================
    # SAVE SCENE JSON
    # =====================================================

    with open(
        SCENE_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            scene_data,
            file,
            indent=4
        )

    # =====================================================
    # PRINT INFORMATION
    # =====================================================

    print()

    print("==========================================")
    print("LOCAL AI INTERIOR PLANNER")
    print("==========================================")

    print("Prompt:")
    print(prompt)

    print()

    print("Room:")
    print(room_type)

    print("Room Size:")
    print(room_size)

    print("Style:")
    print(style)

    print()

    print("Assets:")

    for item in scene_data["assets"]:

        print(
            " -",
            item["asset"]
        )

    print()

    print("Layout Score:")
    print(layout_score)

    print("Best Layout:")
    print(layout_variation)

    print("Candidates Tested:")
    print(candidates_tested)

    print()

    print("Validation:")
    print(validation)

    print()

    print("Scene JSON created:")
    print(SCENE_FILE)

    # =====================================================
    # CHECK BLENDER
    # =====================================================

    if not os.path.exists(BLENDER_EXE):

        return GenerateResponse(

            status="error",

            message="Blender executable not found",

            prompt=prompt,

            planner="local",

            room_type=room_type,

            room_size=room_size,

            style=style,

            layout_score=layout_score,

            layout_variation=layout_variation,

            candidates_tested=candidates_tested,

            layout_valid=layout_valid,

            scene_file=SCENE_FILE,

            blend_file="",

            render_file="",

            blender_return_code=-1
        )

    # =====================================================
    # CHECK BLENDER SCRIPT
    # =====================================================

    if not os.path.exists(BLENDER_SCRIPT):

        return GenerateResponse(

            status="error",

            message="Blender generator script not found",

            prompt=prompt,

            planner="local",

            room_type=room_type,

            room_size=room_size,

            style=style,

            layout_score=layout_score,

            layout_variation=layout_variation,

            candidates_tested=candidates_tested,

            layout_valid=layout_valid,

            scene_file=SCENE_FILE,

            blend_file="",

            render_file="",

            blender_return_code=-1
        )

    # =====================================================
    # RUN BLENDER
    # =====================================================

    print()

    print("Starting Blender...")

    print()

    try:

        result = subprocess.run(

            [
                BLENDER_EXE,
                "--background",
                "--python",
                BLENDER_SCRIPT
            ],

            cwd=PROJECT_DIR,

            capture_output=True,

            text=True,

            timeout=300
        )

    except subprocess.TimeoutExpired:

        return GenerateResponse(

            status="error",

            message="Blender generation timed out",

            prompt=prompt,

            planner="local",

            room_type=room_type,

            room_size=room_size,

            style=style,

            layout_score=layout_score,

            layout_variation=layout_variation,

            candidates_tested=candidates_tested,

            layout_valid=layout_valid,

            scene_file=SCENE_FILE,

            blend_file="",

            render_file="",

            blender_return_code=-1
        )

    # =====================================================
    # BLENDER ERROR
    # =====================================================

    if result.returncode != 0:

        print(result.stdout)

        print(result.stderr)

        return GenerateResponse(

            status="error",

            message="Blender generation failed",

            prompt=prompt,

            planner="local",

            room_type=room_type,

            room_size=room_size,

            style=style,

            layout_score=layout_score,

            layout_variation=layout_variation,

            candidates_tested=candidates_tested,

            layout_valid=layout_valid,

            scene_file=SCENE_FILE,

            blend_file="",

            render_file="",

            blender_return_code=result.returncode
        )

    # =====================================================
    # OUTPUT FILES
    # =====================================================

    blend_file = os.path.join(

        PROJECT_DIR,

        "projects",

        "AI_Interior_Final.blend"
    )

    render_file = os.path.join(

        PROJECT_DIR,

        "renders",

        "AI_Interior_Final.png"
    )

    # =====================================================
    # VERIFY BLEND
    # =====================================================

    if not os.path.exists(blend_file):

        return GenerateResponse(

            status="error",

            message=(
                "Blender completed but "
                ".blend file was not created"
            ),

            prompt=prompt,

            planner="local",

            room_type=room_type,

            room_size=room_size,

            style=style,

            layout_score=layout_score,

            layout_variation=layout_variation,

            candidates_tested=candidates_tested,

            layout_valid=layout_valid,

            scene_file=SCENE_FILE,

            blend_file=blend_file,

            render_file=render_file,

            blender_return_code=result.returncode
        )

    # =====================================================
    # VERIFY RENDER
    # =====================================================

    if not os.path.exists(render_file):

        return GenerateResponse(

            status="error",

            message=(
                "Blender completed but "
                "render was not created"
            ),

            prompt=prompt,

            planner="local",

            room_type=room_type,

            room_size=room_size,

            style=style,

            layout_score=layout_score,

            layout_variation=layout_variation,

            candidates_tested=candidates_tested,

            layout_valid=layout_valid,

            scene_file=SCENE_FILE,

            blend_file=blend_file,

            render_file=render_file,

            blender_return_code=result.returncode
        )

    # =====================================================
    # SUCCESS
    # =====================================================

    print()

    print("==========================================")
    print("GENERATION SUCCESSFUL")
    print("==========================================")

    print("Room:", room_type)

    print("Room Size:", room_size)

    print("Style:", style)

    print("Layout Score:", layout_score)

    print("Best Layout:", layout_variation)

    print("Candidates Tested:", candidates_tested)

    print("Validation:", validation)

    print("Blend:", blend_file)

    print("Render:", render_file)

    print()

    # =====================================================
    # FINAL API RESPONSE
    # =====================================================

    return GenerateResponse(

        status="success",

        message="AI interior generated successfully.",

        prompt=prompt,

        planner="local",

        room_type=room_type,

        room_size=room_size,

        style=style,

        layout_score=layout_score,

        layout_variation=layout_variation,

        candidates_tested=candidates_tested,

        layout_valid=layout_valid,

        scene_file=SCENE_FILE,

        blend_file=blend_file,

        render_file=render_file,

        blender_return_code=result.returncode
    )