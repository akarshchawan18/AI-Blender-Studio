
from pathlib import Path
import re

main_path = Path("api/main.py")
source = main_path.read_text(encoding="utf-8")

# Locate the existing image-generation endpoint.
start_match = re.search(
    r'(?m)^@app\.post\("/generate-from-image"\)\s*\n'
    r'async def generate_from_image\(',
    source,
)

if not start_match:
    raise SystemExit(
        "Could not find /generate-from-image. "
        "No changes were made."
    )

start = start_match.start()

# Find the next top-level route decorator, if any.
next_route = re.search(
    r'(?m)^@app\.(?:get|post|put|delete|patch|api_route)\(',
    source[start_match.end():],
)

if next_route:
    end = start_match.end() + next_route.start()
else:
    end = len(source)

# Preserve any trailing whitespace before the next route.
old_endpoint = source[start:end]

new_endpoint = r'''
@app.post("/generate-from-image")
async def generate_from_image(file: UploadFile = File(...)):
    """Analyze an uploaded room image, prepare a scene, and render it."""

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

    # 1. Analyze image.
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

    # 2. Create design intent.
    try:
        design_intent = create_image_design_intent(analysis)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Image design intent failed: {exc}"
        ) from exc

    room_type = design_intent.get("room_type", "unknown")

    if room_type == "unknown":
        raise HTTPException(
            status_code=422,
            detail={
                "message": "The room type could not be identified confidently.",
                "candidates": design_intent.get("room_candidates", [])
            }
        )

    # 3. Determine estimated room dimensions.
    room_size = "medium"

    try:
        room_width, room_length = get_room_dimensions(
            room_type, room_size
        )
    except Exception:
        room_width, room_length = 4.0, 5.0

    room_height = 3.0

    if (
        not all(
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            and math.isfinite(value)
            and value > 0
            for value in (room_width, room_length, room_height)
        )
    ):
        raise HTTPException(
            status_code=422,
            detail="Room dimensions must be positive finite numbers."
        )

    # 4. Adapt detected architecture.
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

    # 5. Create the layout request.
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

    # 6. Optimize furniture placement.
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

    try:
        assets = best_layout["assets"]
        layout_score = best_layout["score"]
        layout_valid = best_layout["valid"]
        layout_variation = best_layout["variation"]
        candidates_tested = len(layout_result.get("candidates", []))
    except (KeyError, TypeError) as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Layout optimizer returned incomplete data: {exc}"
        ) from exc

    # 7. Build the scene in the format Blender expects.
    camera = {
        "position": [
            room_width * 1.05,
            -room_length * 1.05,
            room_height * 0.85,
        ],
        "target": [
            0.0,
            0.0,
            room_height * 0.35,
        ],
    }

    lighting = {
        "type": design_intent.get("lighting", "warm"),
        "brightness": 1.0,
    }

    materials = {
        "style": design_intent.get("style", "modern"),
        "colors": design_intent.get("colors", []),
    }

    scene_data = {
        "prompt": prompt,
        "room": {
            "type": room_type,
            "size": room_size,
            "width": float(room_width),
            "length": float(room_length),
            "height": float(room_height),
        },
        "room_type": room_type,
        "room_size": room_size,
        "style": design_intent.get("style", "modern"),
        "materials": materials,
        "lighting": lighting,
        "camera": camera,
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

    # 8. Prepare the scene exactly once.
    try:
        scene_data = prepare_blender_scene_data(
            scene_data,
            room_height=room_height,
        )
    except (TypeError, ValueError, KeyError) as exc:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid generated scene: {exc}"
        ) from exc

    # 9. Validate the final structure and furniture transforms.
    required_sections = ("room", "assets", "lighting", "camera")
    missing_sections = [
        key for key in required_sections if key not in scene_data
    ]

    if missing_sections:
        raise HTTPException(
            status_code=500,
            detail=f"Missing Blender scene sections: {missing_sections}"
        )

    room = scene_data["room"]

    for dimension in ("width", "length", "height"):
        try:
            value = float(room[dimension])
        except (KeyError, TypeError, ValueError) as exc:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid room dimension: {dimension}"
            ) from exc

        if not math.isfinite(value) or value <= 0:
            raise HTTPException(
                status_code=422,
                detail=f"Room dimension '{dimension}' must be positive."
            )

    if not isinstance(scene_data["assets"], list):
        raise HTTPException(
            status_code=422,
            detail="Scene assets must be a list."
        )

    for index, asset in enumerate(scene_data["assets"]):
        if not isinstance(asset, dict) or not asset.get("asset"):
            raise HTTPException(
                status_code=422,
                detail=f"Invalid furniture asset at index {index}."
            )

        for key in ("position", "rotation", "scale"):
            values = asset.get(key)

            if not isinstance(values, list) or len(values) != 3:
                raise HTTPException(
                    status_code=422,
                    detail=(
                        f"Asset {index} must have three values "
                        f"for '{key}'."
                    )
                )

            try:
                valid_values = all(
                    math.isfinite(float(value)) for value in values
                )
            except (TypeError, ValueError):
                valid_values = False

            if not valid_values:
                raise HTTPException(
                    status_code=422,
                    detail=f"Asset {index} has invalid '{key}' values."
                )

    for section, keys in (
        ("camera", ("position", "target")),
    ):
        for key in keys:
            values = scene_data[section].get(key)

            if not isinstance(values, (list, tuple)) or len(values) != 3:
                raise HTTPException(
                    status_code=422,
                    detail=f"Camera '{key}' must contain three values."
                )

            try:
                valid_values = all(
                    math.isfinite(float(value)) for value in values
                )
            except (TypeError, ValueError):
                valid_values = False

            if not valid_values:
                raise HTTPException(
                    status_code=422,
                    detail=f"Camera '{key}' contains invalid values."
                )

    # 10. Save the JSON that Blender will read.
    try:
        os.makedirs(os.path.dirname(SCENE_FILE), exist_ok=True)

        with open(SCENE_FILE, "w", encoding="utf-8") as scene_file:
            json.dump(scene_data, scene_file, indent=4)

        # Read it back to confirm the saved file is valid JSON.
        with open(SCENE_FILE, "r", encoding="utf-8") as scene_file:
            saved_scene = json.load(scene_file)

        missing_saved_sections = [
            key for key in required_sections if key not in saved_scene
        ]

        if missing_saved_sections:
            raise ValueError(
                f"Saved JSON is missing: {missing_saved_sections}"
            )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Could not save or validate scene JSON: {exc}"
        ) from exc

    print("\n==========================================")
    print("IMAGE -> BLENDER GENERATION")
    print("==========================================")
    print("Image:", original_name)
    print("Room:", room_type)
    print("Confidence:", design_intent.get("room_confidence"))
    print("Layout score:", layout_score)
    print("Furniture assets:", len(assets))
    print("Scene JSON:", SCENE_FILE)

    # 11. Confirm Blender paths exist.
    if not os.path.exists(BLENDER_EXE):
        raise HTTPException(
            status_code=500,
            detail=f"Blender executable not found: {BLENDER_EXE}"
        )

    if not os.path.exists(BLENDER_SCRIPT):
        raise HTTPException(
            status_code=500,
            detail=f"Blender generator script not found: {BLENDER_SCRIPT}"
        )

    # 12. Run Blender.
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
            detail="Blender generation timed out after 300 seconds."
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Could not start Blender: {exc}"
        ) from exc

    print("\n--- Blender stdout ---")
    print(result.stdout[-6000:])

    if result.returncode != 0:
        print("\n--- Blender stderr ---")
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

    # 13. Verify the output files were created or updated.
    blend_file = os.path.join(
        PROJECT_DIR, "projects", "AI_Interior_Final.blend"
    )
    render_file = os.path.join(
        PROJECT_DIR, "renders", "AI_Interior_Final.png"
    )

    for output_file in (blend_file, render_file):
        if (
            not os.path.exists(output_file)
            or os.path.getsize(output_file) == 0
        ):
            raise HTTPException(
                status_code=500,
                detail=f"Blender output is missing or empty: {output_file}"
            )

    print("\n==========================================")
    print("IMAGE GENERATION SUCCESSFUL")
    print("==========================================")
    print("Blend:", blend_file)
    print("Render:", render_file)

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
            "door_count": len(architecture_for_layout.get("doors", [])),
            "window_count": len(architecture_for_layout.get("windows", [])),
            "dimensions_are_estimates": architecture_for_layout.get(
                "dimensions_are_estimates", True
            ),
        },
        "design_intent": design_intent,
    }
'''

# Keep the next route separate and preserve the rest of main.py.
updated = source[:start] + new_endpoint.strip() + "\n\n\n" + source[end:].lstrip("\n")

# Refuse to overwrite if the result appears to have lost later routes.
if updated.count('@app.post("/generate-from-image")') != 1:
    raise SystemExit("Replacement check failed; original file was not changed.")

backup_path = Path("api/main.py.backup")
if not backup_path.exists():
    raise SystemExit("Backup not found; original file was not changed.")

main_path.write_text(updated, encoding="utf-8")
print("Updated api/main.py successfully.")
print("Backup remains at api/main.py.backup")