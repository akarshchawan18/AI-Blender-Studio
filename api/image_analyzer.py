import os
from collections import Counter

from PIL import Image, ImageStat
from api.architecture_mapper import map_architecture
from api.room_classifier import classify_room
from api.furniture_detection_pipeline import detect_furniture_pipeline
from api.image_furniture import build_furniture_intent
from api.architecture_detector import detect_architecture
from api.local_furniture_fallback import infer_furniture_from_room
SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}


def _classify_brightness(value):
    if value < 70:
        return "dark"
    elif value < 120:
        return "medium_dark"
    elif value < 180:
        return "medium"
    elif value < 220:
        return "bright"
    else:
        return "very_bright"


def _classify_color(r, g, b):
    maximum = max(r, g, b)
    minimum = min(r, g, b)
    saturation = maximum - minimum

    if saturation < 20:
        if maximum < 60:
            return "black"

        if maximum < 120:
            return "dark_grey"

        if maximum < 190:
            return "grey"

        return "white"

    if r > g * 1.15 and r > b * 1.15:
        if r > 170 and g > 100:
            return "beige_warm"

        return "brown_red"

    if r > b * 1.25 and g > b * 1.15 and r > 70:
        return "brown"

    if g > r * 1.15 and g > b * 1.05:
        return "green"

    if b > r * 1.15 and b > g * 1.05:
        return "blue"

    if r > 140 and g > 120 and b < 100:
        return "yellow"

    if r > 150 and g > 70 and g < 150 and b < 100:
        return "orange"

    if r > 90 and b > 90 and g < r * 0.8:
        return "purple"

    return "mixed"


def _extract_dominant_colors(image, sample_size=40):
    small = image.copy()

    small.thumbnail(
        (
            sample_size,
            sample_size
        )
    )

    pixels = list(
        small.convert("RGB").getdata()
    )

    classified = []

    for r, g, b in pixels:

        if r < 15 and g < 15 and b < 15:
            continue

        classified.append(
            _classify_color(r, g, b)
        )

    counts = Counter(classified)

    total = sum(counts.values())

    if total == 0:
        return []

    results = []

    for name, count in counts.most_common(5):

        percentage = round(
            (count / total) * 100,
            1
        )

        results.append(
            {
                "name": name,
                "percentage": percentage
            }
        )

    return results


def _analyze_brightness(image):

    grayscale = image.convert("L")

    statistics = ImageStat.Stat(
        grayscale
    )

    mean_brightness = round(
        statistics.mean[0],
        2
    )

    return {
        "value": mean_brightness,
        "level": _classify_brightness(
            mean_brightness
        )
    }


def _estimate_visual_complexity(image):

    grayscale = image.convert("L")

    entropy = round(
        grayscale.entropy(),
        3
    )

    if entropy < 4:
        level = "low"

    elif entropy < 6:
        level = "medium"

    else:
        level = "high"

    return {
        "entropy": entropy,
        "level": level
    }

def _detect_furniture_safe(image_path, room_type="unknown"):
    """
    Run the complete furniture detection pipeline.

    Detection priority:

        YOLO
        ↓
        SAM 3
        ↓
        room inference fallback

    The pipeline is designed to never crash
    image analysis when an optional detector
    is unavailable.
    """

    try:
        return detect_furniture_pipeline(
            image_path=image_path,
            room_type=room_type,
        )

    except Exception as error:

        fallback_furniture = infer_furniture_from_room(
            room_type
        )

        return {
            "status": "fallback",
            "source": "room_inference",
            "detections": [],
            "furniture": fallback_furniture,
            "fallback_used": True,
            "detector_chain": [
                "yolo",
                "sam3",
                "room_inference",
            ],
            "error": str(error),
        }

def _detect_architecture_safe(image_path):
        try:
            return detect_architecture(image_path)

        except Exception as error:

            return {
                "status": "fallback",
                "source": "architecture_fallback",
                "confidence": 0.0,

                "walls": [],
                "doors": [],
                "windows": [],

                "rectangle_candidates": [],

                "error": str(error)
            }
def analyze_room_image(image_path: str):

    if not os.path.exists(image_path):
        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    extension = os.path.splitext(
        image_path
    )[1].lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported image type: {extension}"
        )

    with Image.open(image_path) as image:

        width, height = image.size

        aspect_ratio = width / height

        if aspect_ratio > 1.15:
            orientation = "landscape"

        elif aspect_ratio < 0.85:
            orientation = "portrait"

        else:
            orientation = "square"

        if width >= 1920 and height >= 1080:
            quality = "high"

        elif width >= 1000 and height >= 700:
            quality = "medium"

        else:
            quality = "low"

        dominant_colors = (
            _extract_dominant_colors(image)
        )

        brightness = _analyze_brightness(
            image
        )

        complexity = (
            _estimate_visual_complexity(
                image
            )
        )

        analysis = {

            "image": {
                "filename": os.path.basename(
                    image_path
                ),
                "width": width,
                "height": height,
                "aspect_ratio": round(
                    aspect_ratio,
                    3
                ),
                "orientation": orientation,
                "quality": quality
            },

            "visual": {
                "brightness": brightness,
                "dominant_colors": dominant_colors,
                "complexity": complexity
            },

            "room": {
                "type": "unknown",
                "estimated_size": "unknown"
            },

            "architecture": {
                "status": "not_run",
                "source": "not_run",
                "confidence": 0.0,
                "walls": [],
                "doors": [],
                "windows": [],
                "rectangle_candidates": []
            },

            "furniture": [],

            "furniture_detection": {
                "status": "not_run",
                "detections": [],
                "furniture": []
            },

            "colors": [
                color["name"]
                for color in dominant_colors
            ],

            "style": "unknown",

            "lighting": "unknown",

            "confidence": 0.0
        }

        # ---------------------------------------------------------
        # ROOM CLASSIFICATION
        # ---------------------------------------------------------

        room_classification = classify_room(
            analysis
        )

        analysis["room"]["type"] = (
            room_classification["type"]
        )

        analysis["room"]["confidence"] = (
            room_classification["confidence"]
        )

        analysis["room"]["confidence_level"] = (
            room_classification.get(
                "confidence_level",
                "unknown"
            )
        )

        analysis["room"]["candidates"] = (
            room_classification["candidates"]
        )

        analysis["confidence"] = (
            room_classification["confidence"]
        )

        # ---------------------------------------------------------
        # FURNITURE DETECTION
        # ---------------------------------------------------------

        furniture_result = _detect_furniture_safe(
            image_path,
            analysis["room"]["type"]
        )

        analysis["furniture_detection"] = furniture_result
        analysis["furniture"] = furniture_result.get("furniture", [])

        # --------------------------------------------------------
        # ARCHITECTURE DETECTION
        # --------------------------------------------------------

        architecture_result = _detect_architecture_safe(image_path)

        # Map image-based architecture into estimated room coordinates.
        # Current image-generation pipeline uses a 4m x 5m test room.
        mapped_architecture = map_architecture(
            architecture=architecture_result,
            room_width=4.0,
            room_length=5.0
        )

        architecture_result["mapped_room"] = mapped_architecture

        analysis["architecture"] = architecture_result

        return analysis