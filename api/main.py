
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import json
import os
import subprocess
import uuid
import math

from api.image_analyzer import analyze_room_image
from api.image_design_adapter import create_image_design_intent
from api.image_layout_adapter import create_layout_request
from api.layout_optimizer import find_best_design_layout
from api.style_engine import (
    get_style_materials,
    get_style_lighting,
    apply_style_to_assets,
)
from api.room_size_engine import (
    detect_room_size,
    get_room_dimensions,
    apply_room_size_to_assets,
)
from api.layout_validator import validate_and_fix_layout
from api.architecture_adapter import adapt_architecture


# =========================================================
# APP
# =========================================================

app = FastAPI(
    title="AI Interior Design Generator",
    description="Local AI-ready Interior Design Generator",
    version="3.2.0",
)


# =========================================================
# PROJECT PATHS
# =========================================================

PROJECT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

IMAGE_UPLOAD_DIR = os.path.join(
    PROJECT_DIR, "projects", "uploaded_images"
)

SCENE_FILE = os.path.join(PROJECT_DIR, "scene_generated.json")

BLENDER_EXE = (
    r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
)

BLENDER_SCRIPT = os.path.join(
    PROJECT_DIR, "blender", "ai_interior_generator.py"
)

os.makedirs(IMAGE_UPLOAD_DIR, exist_ok=True)


# =========================================================
# REQUEST / RESPONSE MODELS
# =========================================================

class GenerateRequest(BaseModel):
    prompt: str


class GenerateResponse(BaseModel):
    status: str
    message: str
    prompt: str
    planner: str
    room_type: str
    room_size: str
    style: str
    layout_score: float
    layout_variation: int
    candidates_tested: int
    layout_valid: bool
    scene_file: str
    blend_file: str
    render_file: str
    blender_return_code: int


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():
    return {
        "status": "online",
        "message": "AI Interior Design Generator API is running",
        "version": "3.2.0",
    }


# =========================================================
# COLOR DETECTION
# =========================================================

def detect_sofa_color(prompt):
    prompt = prompt.lower()

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
    prompt = prompt.lower()

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
    prompt = prompt.lower()

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
# STYLE / ROOM / LIGHTING / CAMERA DETECTION
# =========================================================

def detect_style(prompt):
    prompt = prompt.lower()

    for keyword, style in (
        ("luxury", "luxury"),
        ("minimal", "minimal"),
        ("traditional", "traditional"),
        ("classic", "classic"),
        ("industrial", "industrial"),
    ):
        if keyword in prompt:
            return style

    return "modern"


def detect_room_type(prompt):
    prompt = prompt.lower()

    if "kitchen" in prompt:
        return "kitchen"
    if "home office" in prompt or "office" in prompt:
        return "office"
    if "bedroom" in prompt:
        return "bedroom"
    if "dining room" in prompt or "dining" in prompt:
        return "dining_room"
    if "living room" in prompt or "livingroom" in prompt:
        return "living_room"

    return "living_room"


def detect_lighting(prompt):
    prompt = prompt.lower()

    if "daylight" in prompt:
        return {"type": "daylight", "brightness": 1.5}
    if "bright lighting" in prompt:
        return {"type": "bright", "brightness": 1.5}
    if "cool lighting" in prompt:
        return {"type": "cool", "brightness": 1.0}
    if "dark lighting" in prompt:
        return {"type": "dark", "brightness": 0.5}

    return {"type": "warm", "brightness": 1.0}


def detect_camera(prompt):
    prompt = prompt.lower()

    if "close up" in prompt or "close-up" in prompt:
        return {
            "position": [3.2, -3.2, 2.0],
            "target": [0.0, 0.0, 1.0],
        }

    return {
        "position": [4.2, -4.2, 2.5],
        "target": [0.0, 0.0, 1.1],
    }


# =========================================================
# SCENE PREPARATION AND VALIDATION
# =========================================================

def prepare_blender_scene_data(scene_data, room_height=3.0):
    """Normalize a scene into the JSON structure expected by Blender."""

    if not isinstance(scene_data, dict):
        raise ValueError("Scene data must be a JSON object.")

    room_width = float(
        scene_data.get(
            "room_width",
            scene_data.get("room", {}).get("width", 4.0),
        )
    )

    room_length = float(
        scene_data.get(
            "room_length",
            scene_data.get("room", {}).get("length", 5.0),
        )
    )

    room_height = float(
        scene_data.get(
            "room", {}
        ).get("height", room_height)
    )

    for name, value in (
        ("width", room_width),
        ("length", room_length),
        ("height", room_height),
    ):
        if not 0 < value <= 30:
            raise ValueError(
                f"Room {name} must be greater than 0 and at most 30 metres."
            )

    assets = scene_data.get("assets", [])

    if not isinstance(assets, list):
        raise ValueError("'assets' must be a list.")

    prepared_assets = []

    for index, item in enumerate(assets):
        if not isinstance(item, dict):
            raise ValueError(f"Furniture item {index} must be an object.")

        asset_name = item.get("asset")

        if not isinstance(asset_name, str) or not asset_name.strip():
            raise ValueError(
                f"Furniture item {index} needs a valid asset name."
            )

        prepared_item = dict(item)

        for key in ("position", "rotation", "scale"):
            values = item.get(key)

            if not isinstance(values, (list, tuple)) or len(values) != 3:
                raise ValueError(
                    f"Furniture '{asset_name}' needs three values for '{key}'."
                )

            try:
                values = [float(v) for v in values]
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"Furniture '{asset_name}' has non-numeric '{key}' values."
                ) from exc

            if not all(__import__("math").isfinite(v) for v in values):
                raise ValueError(
                    f"Furniture '{asset_name}' has invalid '{key}' values."
                )

            if key == "scale" and any(v <= 0 for v in values):
                raise ValueError(
                    f"Furniture '{asset_name}' scale values must be positive."
                )

            prepared_item[key] = values

        prepared_assets.append(prepared_item)

    lighting = scene_data.get("lighting", {})
    if not isinstance(lighting, dict):
        lighting = {}

    camera = scene_data.get("camera", {})
    if not isinstance(camera, dict):
        camera = {}

    camera_position = camera.get(
        "position",
        [
            room_width * 1.25,
            -room_length * 1.25,
            room_height * 1,
        ],
    )

    camera_target = camera.get(
        "target",
        [0.0, 0.0, room_height * 0.35],
    )

    for name, values in (
        ("position", camera_position),
        ("target", camera_target),
    ):
        if not isinstance(values, (list, tuple)) or len(values) != 3:
            raise ValueError(f"Camera '{name}' must contain three numbers.")

        try:
            values = [float(v) for v in values]
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"Camera '{name}' must contain numeric values."
            ) from exc

        if not all(__import__("math").isfinite(v) for v in values):
            raise ValueError(f"Camera '{name}' contains invalid values.")

        if name == "position":
            camera_position = values
        else:
            camera_target = values

    prepared = dict(scene_data)

    prepared["room"] = {
        "type": scene_data.get(
            "room_type",
            scene_data.get("room", {}).get("type", "living_room"),
        ),
        "size": scene_data.get(
            "room_size",
            scene_data.get("room", {}).get("size", "medium"),
        ),
        "width": room_width,
        "length": room_length,
        "height": room_height,
    }

    prepared["assets"] = prepared_assets

    prepared["lighting"] = {
        "type": lighting.get(
            "type",
            scene_data.get("design_intent", {}).get("lighting", "warm")
            if isinstance(scene_data.get("design_intent"), dict)
            else "warm",
        ),
        "brightness": float(lighting.get("brightness", 1.0)),
    }

    prepared["camera"] = {
        "position": camera_position,
        "target": camera_target,
    }

    prepared.setdefault("materials", {})
    prepared.setdefault("style", "modern")

    validate_blender_scene(prepared)

    return prepared


def validate_blender_scene(scene_data):
    """Validate the final scene, including the exact Blender JSON sections."""

    required = ("room", "assets", "lighting", "camera")
    missing = [key for key in required if key not in scene_data]

    if missing:
        raise ValueError(f"Missing required scene sections: {missing}")

    room = scene_data["room"]

    for dimension in ("width", "length", "height"):
        value = float(room[dimension])

        if not 0 < value <= 30:
            raise ValueError(f"Invalid room dimension: {dimension}")

    if not isinstance(scene_data["assets"], list):
        raise ValueError("'assets' must be a list.")

    if not isinstance(scene_data["lighting"], dict):
        raise ValueError("'lighting' must be an object.")

    if not isinstance(scene_data["camera"], dict):
        raise ValueError("'camera' must be an object.")

    return True


def save_and_verify_scene(scene_data):
    """Write the JSON and validate the file Blender will actually read."""

    os.makedirs(os.path.dirname(SCENE_FILE), exist_ok=True)

    with open(SCENE_FILE, "w", encoding="utf-8") as file:
        json.dump(scene_data, file, indent=4, allow_nan=False)

    with open(SCENE_FILE, "r", encoding="utf-8") as file:
        saved_scene = json.load(file)

    validate_blender_scene(saved_scene)

    print("Validated scene:", SCENE_FILE)
    print("Room:", saved_scene["room"])
    print("Furniture count:", len(saved_scene["assets"]))

    return saved_scene


# =========================================================
# BLENDER EXECUTION
# =========================================================

def run_blender():
    if not os.path.isfile(BLENDER_EXE):
        raise HTTPException(
            status_code=500,
            detail=f"Blender executable not found: {BLENDER_EXE}",
        )

    if not os.path.isfile(BLENDER_SCRIPT):
        raise HTTPException(
            status_code=500,
            detail=f"Blender script not found: {BLENDER_SCRIPT}",
        )

    try:
        result = subprocess.run(
            [
                BLENDER_EXE,
                "--background",
                "--python",
                BLENDER_SCRIPT,
            ],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
            timeout=300,
        )
    except subprocess.TimeoutExpired as exc:
        raise HTTPException(
            status_code=500,
            detail="Blender generation timed out after 300 seconds.",
        ) from exc
    except OSError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Could not start Blender: {exc}",
        ) from exc

    if result.returncode != 0:
        print("BLENDER STDOUT:")
        print(result.stdout[-6000:])
        print("BLENDER STDERR:")
        print(result.stderr[-6000:])

        raise HTTPException(
            status_code=500,
            detail={
                "message": "Blender generation failed.",
                "return_code": result.returncode,
                "stdout": result.stdout[-4000:],
                "stderr": result.stderr[-4000:],
            },
        )

    blend_file = os.path.join(
        PROJECT_DIR, "projects", "AI_Interior_Final.blend"
    )
    render_file = os.path.join(
        PROJECT_DIR, "renders", "AI_Interior_Final.png"
    )

    if not os.path.isfile(blend_file):
        raise HTTPException(
            status_code=500,
            detail="Blender completed but the .blend file was not created.",
        )

    if not os.path.isfile(render_file):
        raise HTTPException(
            status_code=500,
            detail="Blender completed but the render was not created.",
        )

    return result, blend_file, render_file


# =========================================================
# LOCAL SCENE PLANNER
# =========================================================

def create_local_scene(prompt_text):
    prompt = prompt_text.lower().strip()

    room_type = detect_room_type(prompt)
    style = detect_style(prompt)
    room_size = detect_room_size(prompt)

    room_dimensions = get_room_dimensions(room_size)

    room_width = float(room_dimensions["width"])
    room_length = float(room_dimensions["length"])
    room_height = float(room_dimensions["height"])

    materials = get_style_materials(style)
    materials["wall"] = detect_wall_color(prompt)
    materials["floor"] = detect_floor_color(prompt)
    materials["sofa"] = detect_sofa_color(prompt)

    lighting = detect_lighting(prompt)
    camera = detect_camera(prompt)

    try:
        layout_result = find_best_design_layout(
            prompt=prompt,
            room_type=room_type,
            room_width=room_width,
            room_length=room_length,
            candidate_count=5,
        )

        best_layout = layout_result["best"]
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Local layout optimization failed: {exc}",
        ) from exc

    assets = best_layout.get("assets", [])

    assets = apply_room_size_to_assets(assets, room_size)
    assets = apply_style_to_assets(assets, style)

    if room_type == "living_room" and "chair" in prompt:
        assets.append({
            "asset": "Chair_Modern",
            "position": [room_width * 0.30, room_length * 0.10, 0.0],
            "rotation": [0.0, 0.0, 90.0],
            "scale": [1.0, 1.0, 1.0],
        })

    if room_type == "bedroom" and "tv" in prompt:
        assets.append({
            "asset": "TVUnit_Wood",
            "position": [0.0, -room_length * 0.40, 0.0],
            "rotation": [0.0, 0.0, 0.0],
            "scale": [1.0, 1.0, 1.0],
        })

    assets, validation = validate_and_fix_layout(
        assets,
        room_width,
        room_length,
    )

    validation["layout_score"] = float(best_layout.get("score", 0))
    validation["layout_variation"] = int(best_layout.get("variation", 0))

    # Final room-boundary and collision validation
    validation["valid"] = bool(validation.get("valid", False))

    # Preserve the optimizer's original validation results
    validation["layout_valid"] = bool(
        best_layout.get("layout_valid", False)
    )
    validation["optimizer_valid"] = bool(
        best_layout.get("valid", False)
    )
    validation["architecture_valid"] = bool(
        best_layout.get("architecture_valid", False)
    )

    validation["candidates_tested"] = len(
        layout_result.get("candidates", [])
    )

    scene_data = {
        "prompt": prompt_text,
        "room": {
            "type": room_type,
            "size": room_size,
            "width": room_width,
            "length": room_length,
            "height": room_height,
        },
        "room_type": room_type,
        "room_size": room_size,
        "style": style,
        "materials": materials,
        "lighting": lighting,
        "camera": camera,
        "assets": assets,
        "validation": validation,
    }

    return prepare_blender_scene_data(scene_data)


# =========================================================
# GENERATE FROM TEXT PROMPT
# =========================================================

@app.post("/generate", response_model=GenerateResponse)
def generate(request: GenerateRequest):
    prompt = request.prompt.strip()

    if not prompt:
        raise HTTPException(
            status_code=400,
            detail="Prompt cannot be empty.",
        )

    scene_data = create_local_scene(prompt)
    scene_data = save_and_verify_scene(scene_data)

    validation = scene_data.get("validation", {})

    result, blend_file, render_file = run_blender()

    return GenerateResponse(
        status="success",
        message="AI interior generated successfully.",
        prompt=prompt,
        planner="local",
        room_type=scene_data["room"]["type"],
        room_size=scene_data["room"]["size"],
        style=scene_data.get("style", "modern"),
        layout_score=float(validation.get("layout_score", 0)),
        layout_variation=int(validation.get("layout_variation", 0)),
        candidates_tested=int(validation.get("candidates_tested", 0)),
        layout_valid=bool(validation.get("layout_valid", False)),
        scene_file=SCENE_FILE,
        blend_file=blend_file,
        render_file=render_file,
        blender_return_code=result.returncode,
    )


# =========================================================
# ANALYZE IMAGE ONLY
# =========================================================

@app.post("/analyze-image")
async def analyze_image(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Image file is required.",
        )

    extension = os.path.splitext(file.filename)[1].lower()
    allowed_extensions = {".jpg", ".jpeg", ".png", ".webp"}

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Use JPG, JPEG, PNG, or WEBP.",
        )

    image_path = os.path.join(
        IMAGE_UPLOAD_DIR,
        f"{uuid.uuid4().hex}{extension}",
    )

    try:
        total_bytes = 0
        max_file_size = 15 * 1024 * 1024

        with open(image_path, "wb") as output_file:
            while True:
                chunk = await file.read(1024 * 1024)

                if not chunk:
                    break

                total_bytes += len(chunk)

                if total_bytes > max_file_size:
                    raise HTTPException(
                        status_code=413,
                        detail="Maximum image size is 15 MB.",
                    )

                output_file.write(chunk)

        if total_bytes == 0:
            raise HTTPException(
                status_code=400,
                detail="The uploaded image is empty.",
            )

        analysis = analyze_room_image(image_path)
        design_intent = create_image_design_intent(analysis)

        return {
            "status": "success",
            "original_filename": os.path.basename(file.filename),
            "analysis": analysis,
            "design_intent": design_intent,
        }

    except HTTPException:
        if os.path.exists(image_path):
            os.remove(image_path)
        raise

    except Exception as exc:
        if os.path.exists(image_path):
            os.remove(image_path)

        raise HTTPException(
            status_code=500,
            detail=f"Image analysis failed: {exc}",
        ) from exc

    finally:
        await file.close()


# =========================================================
# GENERATE FROM UPLOADED IMAGE
# =========================================================




@app.post("/generate-from-image")
async def generate_from_image(file: UploadFile = File(...)):
    # 1. Validate the uploaded file
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Image file is required."
        )

    allowed_extensions = {".jpg", ".jpeg", ".png", ".webp"}
    original_name = os.path.basename(file.filename)
    extension = os.path.splitext(original_name)[1].lower()

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Unsupported image type. Use JPG, JPEG, PNG or WEBP."
        )

    # 2. Save the uploaded image
    os.makedirs(IMAGE_UPLOAD_DIR, exist_ok=True)

    image_id = uuid.uuid4().hex
    image_filename = f"{image_id}{extension}"
    image_path = os.path.join(IMAGE_UPLOAD_DIR, image_filename)

    total_bytes = 0
    max_file_size = 15 * 1024 * 1024

    try:
        with open(image_path, "wb") as image_file:
            while True:
                chunk = await file.read(1024 * 1024)

                if not chunk:
                    break

                total_bytes += len(chunk)

                if total_bytes > max_file_size:
                    raise HTTPException(
                        status_code=413,
                        detail="Image is too large. Maximum size is 15 MB."
                    )

                image_file.write(chunk)

    except HTTPException:
        if os.path.exists(image_path):
            os.remove(image_path)
        raise

    except Exception as exc:
        if os.path.exists(image_path):
            os.remove(image_path)

        raise HTTPException(
            status_code=500,
            detail=f"Image upload failed: {exc}"
        ) from exc

    finally:
        await file.close()

    if total_bytes == 0:
        if os.path.exists(image_path):
            os.remove(image_path)

        raise HTTPException(
            status_code=400,
            detail="The uploaded image is empty."
        )

    # 3. Analyze the image
    try:
        analysis = analyze_room_image(image_path)

        mapped_architecture = (
            analysis.get("architecture", {}).get("mapped_room", {})
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Image analysis failed: {exc}"
        ) from exc

    # 4. Create the design intent
    try:
        design_intent = create_image_design_intent(analysis)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Image design intent failed: {exc}"
        ) from exc

    # 5. Validate the detected room type
    room_type = design_intent.get("room_type", "unknown")

    if room_type == "unknown":
        raise HTTPException(
            status_code=422,
            detail={
                "message": "The room type could not be identified confidently.",
                "candidates": design_intent.get("room_candidates", [])
            }
        )

    # 6. Determine room dimensions
    room_size = "medium"

    try:
        room_width, room_length = get_room_dimensions(
            room_type,
            room_size
        )
    except Exception:
        room_width, room_length = 4.0, 5.0

    room_height = 3.0

    # 7. Adapt the detected architecture
    try:
        architecture_for_layout = adapt_architecture(
            mapped_architecture=mapped_architecture,
            room_width=room_width,
            room_length=room_length,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Architecture adaptation failed: {exc}"
        ) from exc

    # 8. Create the layout request
    try:
        layout_request = create_layout_request(
            design_intent=design_intent,
            room_width=room_width,
            room_length=room_length,
        )

        prompt = layout_request["prompt"]

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Layout request creation failed: {exc}"
        ) from exc

    # 9. Optimize furniture placement
    try:
        layout_result = find_best_design_layout(
            prompt=prompt,
            room_type=room_type,
            room_width=room_width,
            room_length=room_length,
            candidate_count=5,
            architecture=architecture_for_layout,
        )

        best_layout = layout_result["best"]

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Layout optimization failed: {exc}"
        ) from exc

    # 10. Extract the selected layout
    assets = best_layout.get("assets", [])
    layout_score = best_layout.get("score", 0)
    layout_valid = best_layout.get("valid", False)
    layout_variation = best_layout.get("variation", 0)
    candidates_tested = len(layout_result.get("candidates", []))

    if not isinstance(assets, list) or not assets:
        raise HTTPException(
            status_code=422,
            detail="Layout optimizer returned no furniture assets."
        )
    # Fix living-room chair placement
    if room_type == "living_room":
        chair = next(
            (a for a in assets if a.get("asset") == "Chair_Modern"),
            None
        )

        coffee_table = next(
            (a for a in assets if a.get("asset") == "CoffeeTable_Modern"),
            None
        )

        if chair and coffee_table:
            chair["position"] = [
                room_width * 0.34,
                0.0,
                0.0
            ]


    # 11. Build scene data in Blender-compatible format
    room_height = 3.0

    scene_data = {
        "prompt": prompt,
        "room": {
            "type": room_type,
            "size": room_size,
            "width": float(room_width),
            "length": float(room_length),
            "height": room_height,
        },
        "room_type": room_type,
        "room_size": room_size,
        "style": design_intent.get("style", "modern"),
        "materials": {
            "style": design_intent.get("style", "modern"),
            "colors": design_intent.get("colors", []),
        },
        "lighting": {
            "type": design_intent.get("lighting", "warm"),
            "brightness": 0.40,
        },

        "camera": {
            "position": [
                0.0,
                -7.0,
                3.8,
            ],
            "target": [
                0.0,
                0.0,
                1.0,
            ],
            "lens": 28,
        },

        "assets": assets,
        "layout_score": layout_score,
        "layout_variation": layout_variation,
        "layout_valid": layout_valid,
        "candidates_tested": candidates_tested,
        "source": "image",
        "image": {
            "filename": original_name,
            "saved_path": image_path,
            "confidence": design_intent.get("room_confidence", 0.0),
            "confidence_level": design_intent.get(
                "room_confidence_level", "unknown"
            ),
            "fallback_used": design_intent.get("fallback_used", False),
        },
        "design_intent": design_intent,
        "architecture": architecture_for_layout,
    }

    # 11A. Prepare and validate the Blender scene ONCE
    try:
        scene_data = prepare_blender_scene_data(
            scene_data,
            room_height=3.0,
        )
    except (TypeError, ValueError, KeyError) as exc:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid generated scene: {exc}",
        ) from exc

    # Confirm required sections
    required_sections = ("room", "assets", "lighting", "camera")
    missing_sections = [
        section for section in required_sections
        if section not in scene_data
    ]

    if missing_sections:
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Missing Blender scene sections.",
                "missing_sections": missing_sections,
            },
        )

    # Validate dimensions
    try:
        room = scene_data["room"]
        for dimension in ("width", "length", "height"):
            value = float(room[dimension])
            if value <= 0:
                raise ValueError(
                    f"Room dimension '{dimension}' must be positive."
                )
            room[dimension] = value
    except (TypeError, ValueError, KeyError) as exc:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid room dimensions: {exc}",
        ) from exc

    # Validate camera
    camera = scene_data["camera"]
    for key in ("position", "target"):
        value = camera.get(key)
        if not isinstance(value, (list, tuple)) or len(value) != 3:
            raise HTTPException(
                status_code=422,
                detail=f"Camera '{key}' must contain three values.",
            )

    # Validate furniture
    assets = scene_data["assets"]
    if not isinstance(assets, list) or not assets:
        raise HTTPException(
            status_code=422,
            detail="The scene must contain at least one furniture asset.",
        )

    for index, asset in enumerate(assets):
        if not isinstance(asset, dict) or not asset.get("asset"):
            raise HTTPException(
                status_code=422,
                detail=f"Invalid furniture entry at index {index}.",
            )

        for key in ("position", "rotation", "scale"):
            value = asset.get(key)
            if not isinstance(value, (list, tuple)) or len(value) != 3:
                raise HTTPException(
                    status_code=422,
                    detail=(
                        f"Furniture entry {index}: "
                        f"'{key}' must contain three values."
                    ),
                )

    # 12. Write the validated scene JSON
    try:
        os.makedirs(os.path.dirname(SCENE_FILE), exist_ok=True)

        with open(SCENE_FILE, "w", encoding="utf-8") as scene_file:
            json.dump(scene_data, scene_file, indent=4)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Could not write scene JSON: {exc}",
        ) from exc

    # Confirm the saved JSON is readable and Blender-compatible
    try:
        with open(SCENE_FILE, "r", encoding="utf-8") as scene_file:
            saved_scene = json.load(scene_file)

        missing_saved = [
            key for key in required_sections if key not in saved_scene
        ]

        if missing_saved:
            raise ValueError(
                f"Saved scene is missing sections: {missing_saved}"
            )

    except (OSError, json.JSONDecodeError, ValueError) as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Saved scene validation failed: {exc}",
        ) from exc

    print("\n==========================================")
    print("IMAGE -> BLENDER GENERATION")
    print("==========================================")
    print("Image:", original_name)
    print("Room:", room_type)
    print("Room dimensions:", room)
    print("Furniture count:", len(scene_data["assets"]))
    print("Layout score:", layout_score)
    print("Layout valid:", layout_valid)
    print("Scene:", SCENE_FILE)

    # 13. Check Blender paths
    if not os.path.exists(BLENDER_EXE):
        raise HTTPException(
            status_code=500,
            detail=f"Blender executable not found: {BLENDER_EXE}",
        )

    if not os.path.exists(BLENDER_SCRIPT):
        raise HTTPException(
            status_code=500,
            detail=f"Blender generator script not found: {BLENDER_SCRIPT}",
        )

    # 14. Run Blender
    try:
        result = subprocess.run(
            [
                BLENDER_EXE,
                "--background",
                "--python",
                BLENDER_SCRIPT,
            ],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
            timeout=300,
        )

    except subprocess.TimeoutExpired as exc:
        raise HTTPException(
            status_code=500,
            detail="Blender generation timed out after 300 seconds.",
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Could not start Blender: {exc}",
        ) from exc

    # 15. Check Blender result
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)

        raise HTTPException(
            status_code=500,
            detail={
                "message": "Blender generation failed.",
                "return_code": result.returncode,
                "stdout": result.stdout[-4000:],
                "stderr": result.stderr[-4000:],
            },
        )

    # 16. Verify output files
    blend_file = os.path.join(
        PROJECT_DIR, "projects", "AI_Interior_Final.blend"
    )
    render_file = os.path.join(
        PROJECT_DIR, "renders", "AI_Interior_Final.png"
    )

    if not os.path.isfile(blend_file):
        raise HTTPException(
            status_code=500,
            detail="Blender completed but the .blend file was not created.",
        )

    if not os.path.isfile(render_file):
        raise HTTPException(
            status_code=500,
            detail="Blender completed but the render was not created.",
        )

    print("\n==========================================")
    print("IMAGE GENERATION SUCCESSFUL")
    print("==========================================")
    print("Blend:", blend_file)
    print("Render:", render_file)
    print("Blender return code:", result.returncode)

    # 17. Return result
    return {
        "status": "success",
        "message": "Interior generated successfully from image.",
        "source": "image",
        "original_filename": original_name,
        "room_type": room_type,
        "room_confidence": design_intent.get("room_confidence", 0.0),
        "room_confidence_level": design_intent.get(
            "room_confidence_level", "unknown"
        ),
        "fallback_used": design_intent.get("fallback_used", False),
        "room_size": room_size,
        "style": design_intent.get("style", "modern"),
        "layout_score": layout_score,
        "layout_variation": layout_variation,
        "candidates_tested": candidates_tested,
        "layout_valid": layout_valid,
        "scene_file": SCENE_FILE,
        "blend_file": blend_file,
        "render_file": render_file,
        "blender_return_code": result.returncode,
        "architecture_summary": {
            "source": architecture_for_layout.get("source", "unknown"),
            "confidence": architecture_for_layout.get("confidence", 0.0),
            "door_count": len(
                architecture_for_layout.get("doors", [])
            ),
            "window_count": len(
                architecture_for_layout.get("windows", [])
            ),
            "dimensions_are_estimates": architecture_for_layout.get(
                "dimensions_are_estimates", True
            ),
        },
        "design_intent": design_intent,

    }

# =========================================================
# GENERATE REALISTIC KITCHEN
# =========================================================



@app.post("/generate-kitchen")
def generate_kitchen(request: GenerateRequest):
    prompt = request.prompt.strip().lower()

    # Choose cabinet finish.
    cabinet_finish = "matte"

    if "glossy" in prompt or "high gloss" in prompt:
        cabinet_finish = "glossy"
    elif "wood grain" in prompt or "wood-grain" in prompt:
        cabinet_finish = "wood"
    elif "matte" in prompt:
        cabinet_finish = "matte"

    if not prompt:
        raise HTTPException(
            status_code=400,
            detail="Prompt cannot be empty.",
        )


    # Choose cabinet color.
    cabinet_color = [0.86, 0.84, 0.78]

    cabinet_colors = {
        "black": [0.045, 0.045, 0.05],
        "white": [0.92, 0.92, 0.88],
        "green": [0.20, 0.32, 0.22],
        "blue": [0.10, 0.22, 0.38],
        "beige": [0.72, 0.60, 0.43],
        "grey": [0.32, 0.33, 0.34],
        "gray": [0.32, 0.33, 0.34],
        "navy": [0.035, 0.075, 0.16],
        "brown": [0.22, 0.10, 0.045],
        "cream": [0.86, 0.79, 0.65],
        "red": [0.40, 0.045, 0.035],
        "yellow": [0.75, 0.55, 0.12],
    }



    import re

    for color_name, color_value in cabinet_colors.items():
        pattern = rf"\b{re.escape(color_name)}\b\s+(?:(?:glossy|matte|high-gloss|wood-grain)\s+)*cabinets?\b"
        if re.search(pattern, prompt):
            cabinet_color = color_value
            break

    # Choose kitchen style.
    kitchen_style = "modern"

    if "luxury" in prompt:
        kitchen_style = "luxury"
    elif "scandinavian" in prompt:
        kitchen_style = "scandinavian"
    elif "minimalist" in prompt:
        kitchen_style = "minimalist"



     # Choose countertop color.
    counter_color = [0.055, 0.06, 0.065]

    countertop_colors = {
        "white": [0.82, 0.80, 0.75],
        "black": [0.025, 0.028, 0.032],
        "grey": [0.25, 0.26, 0.27],
        "gray": [0.25, 0.26, 0.27],
        "beige": [0.72, 0.62, 0.48],
        "cream": [0.86, 0.82, 0.72],
        "brown": [0.24, 0.13, 0.07],
        "green": [0.12, 0.28, 0.18],
        "blue": [0.10, 0.20, 0.32],
        "gold": [0.55, 0.36, 0.10],
        "marble": [0.82, 0.80, 0.75],
        "quartz": [0.78, 0.78, 0.75],
    }

    countertop_keywords = (
        "countertop",
        "counter",
        "quartz",
        "marble countertop",
    )

    for color_name, color_value in countertop_colors.items():
        if any(
            f"{color_name} {keyword}" in prompt
            for keyword in countertop_keywords
        ):
            counter_color = color_value
            break




    # Choose lighting preference.
    lighting_tone = "warm"

    lighting_options = {
        "warm": ["warm lighting", "warm light", "warm lights"],
        "cool": ["cool lighting", "cool light", "cool lights"],
        "neutral": ["neutral lighting", "neutral light", "neutral lights"],
        "natural": ["natural lighting", "natural light", "daylight"],
        "bright": ["bright lighting", "bright light", "bright lights"],
        "dim": ["dim lighting", "dim light", "soft lighting"],
    }

    for tone, keywords in lighting_options.items():
        if any(keyword in prompt for keyword in keywords):
            lighting_tone = tone
            break

    # Save settings for Blender.
    config_file = os.path.join(
        PROJECT_DIR,
        "projects",
        "kitchen_prompt.json",
    )

    os.makedirs(os.path.dirname(config_file), exist_ok=True)

    with open(config_file, "w", encoding="utf-8") as file:
        json.dump(
            {
                "prompt": prompt,
                "cabinet_color": cabinet_color,
                "counter_color": counter_color,
                "lighting_tone": lighting_tone,
                "style": kitchen_style,
                "cabinet_finish": cabinet_finish,
            },
            file,
            indent=4,
        )

    # Define generator and output paths.
    kitchen_script = os.path.join(
        PROJECT_DIR,
        "blender",
        "generate_realistic_kitchen.py",
    )

    blend_file = os.path.join(
        PROJECT_DIR,
        "projects",
        "AI_Interior_Realistic.blend",
    )

    render_file = os.path.join(
        PROJECT_DIR,
        "renders",
        "AI_Interior_Realistic.png",
    )

    if not os.path.isfile(BLENDER_EXE):
        raise HTTPException(
            status_code=500,
            detail="Blender executable was not found.",
        )

    if not os.path.isfile(kitchen_script):
        raise HTTPException(
            status_code=500,
            detail="Realistic kitchen generator script was not found.",
        )

    try:
        result = subprocess.run(
            [
                BLENDER_EXE,
                "--background",
                "--python",
                kitchen_script,
            ],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
            timeout=300,
        )

    except subprocess.TimeoutExpired as exc:
        raise HTTPException(
            status_code=500,
            detail="Kitchen generation timed out after 300 seconds.",
        ) from exc

    except OSError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Could not start Blender: {exc}",
        ) from exc

    if result.returncode != 0:
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Kitchen generation failed.",
                "return_code": result.returncode,
                "stdout": result.stdout[-4000:],
                "stderr": result.stderr[-4000:],
            },
        )

    if not os.path.isfile(blend_file):
        raise HTTPException(
            status_code=500,
            detail="Kitchen .blend file was not created.",
        )

    if not os.path.isfile(render_file):
        raise HTTPException(
            status_code=500,
            detail="Kitchen render was not created.",
        )

    return {
        "status": "success",
        "message": "Realistic kitchen generated successfully.",
        "prompt": prompt,
        "settings": {
            "cabinet_color": cabinet_color,
            "counter_color": counter_color,
            "lighting_tone": lighting_tone,
        },
        "blend_file": blend_file,
        "render_file": render_file,
        "blender_return_code": result.returncode,
    }