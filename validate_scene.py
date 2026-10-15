
import json
from pathlib import Path

SCENE_FILE = Path("scene.json")


def validate_scene(scene):
    errors = []

    room = scene.get("room", {})
    dimensions = ["width", "length", "height"]

    for dimension in dimensions:
        value = room.get(dimension)
        if not isinstance(value, (int, float)) or value <= 0:
            errors.append(f"Invalid room dimension: {dimension}")

    if not isinstance(scene.get("assets"), list):
        errors.append("Assets must be a list.")
        return errors

    materials = scene.get("materials", {})

    for index, asset in enumerate(scene["assets"]):
        name = asset.get("asset", f"asset_{index}")

        for field in ("position", "rotation", "scale"):
            value = asset.get(field)

            if (
                not isinstance(value, list)
                or len(value) != 3
                or not all(
                    isinstance(n, (int, float)) for n in value
                )
            ):
                errors.append(f"{name}: invalid {field}")

        if asset.get("material") not in materials:
            errors.append(f"{name}: unknown material")

    camera = scene.get("camera", {})
    for field in ("position", "target"):
        value = camera.get(field)
        if (
            not isinstance(value, list)
            or len(value) != 3
            or not all(isinstance(n, (int, float)) for n in value)
        ):
            errors.append(f"Camera: invalid {field}")

    return errors


def main():
    if not SCENE_FILE.exists():
        print(f"Scene file not found: {SCENE_FILE.resolve()}")
        return

    try:
        scene = json.loads(SCENE_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON: {exc}")
        return

    errors = validate_scene(scene)

    if errors:
        print("SCENE VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return

    print("SCENE VALIDATION PASSED")
    print(f"Room: {scene['room']['width']} x "
          f"{scene['room']['length']} x "
          f"{scene['room']['height']} metres")
    print(f"Furniture assets: {len(scene['assets'])}")


if __name__ == "__main__":
    main()