"""
Local rule-based room classifier.

This is an MVP classifier.
It does NOT use an AI vision model.

It uses image characteristics such as:
- orientation
- brightness
- dominant colors
- visual complexity

Later this module can be replaced/enhanced with
a local computer-vision or vision model.
"""

from typing import Dict, List


ROOM_TYPES = [
    "living_room",
    "bedroom",
    "office",
    "dining_room",
    "kitchen",
    "bathroom",
]


def _get_color_names(analysis: Dict) -> List[str]:
    colors = analysis.get("colors", [])

    if isinstance(colors, list):
        return [str(color).lower() for color in colors]

    return []


def _get_brightness_level(analysis: Dict) -> str:
    visual = analysis.get("visual", {})
    brightness = visual.get("brightness", {})

    return brightness.get("level", "unknown")


def _get_complexity_level(analysis: Dict) -> str:
    visual = analysis.get("visual", {})
    complexity = visual.get("complexity", {})

    return complexity.get("level", "unknown")


def classify_room(analysis: Dict) -> Dict:
    """
    Classify a room using simple local visual heuristics.

    Returns candidates rather than blindly selecting one room.
    """

    scores = {
        room_type: 0.0
        for room_type in ROOM_TYPES
    }

    colors = _get_color_names(analysis)

    brightness = _get_brightness_level(analysis)

    complexity = _get_complexity_level(analysis)

    image = analysis.get("image", {})

    orientation = image.get(
        "orientation",
        "unknown"
    )

    # ---------------------------------------------------------
    # BRIGHTNESS
    # ---------------------------------------------------------

    if brightness == "bright":
        scores["living_room"] += 0.08
        scores["kitchen"] += 0.08
        scores["dining_room"] += 0.06

    elif brightness == "very_bright":
        scores["living_room"] += 0.10
        scores["kitchen"] += 0.10

    elif brightness == "dark":
        scores["bedroom"] += 0.05
        scores["bathroom"] += 0.03

    elif brightness == "medium_dark":
        scores["bedroom"] += 0.04
        scores["living_room"] += 0.02

    # ---------------------------------------------------------
    # COLORS
    # ---------------------------------------------------------

    if "white" in colors:
        scores["bathroom"] += 0.05
        scores["kitchen"] += 0.04

    if "grey" in colors:
        scores["living_room"] += 0.04
        scores["office"] += 0.04

    if "dark_grey" in colors:
        scores["office"] += 0.04
        scores["living_room"] += 0.03

    if "brown" in colors:
        scores["living_room"] += 0.04
        scores["dining_room"] += 0.04
        scores["bedroom"] += 0.03

    if "blue" in colors:
        scores["bedroom"] += 0.03
        scores["bathroom"] += 0.03
        scores["living_room"] += 0.01

    if "green" in colors:
        scores["living_room"] += 0.02
        scores["bedroom"] += 0.02

    # ---------------------------------------------------------
    # IMAGE ORIENTATION
    # ---------------------------------------------------------

    if orientation == "landscape":
        scores["living_room"] += 0.04
        scores["dining_room"] += 0.03
        scores["kitchen"] += 0.03

    elif orientation == "portrait":
        scores["bedroom"] += 0.02
        scores["bathroom"] += 0.02

    # ---------------------------------------------------------
    # VISUAL COMPLEXITY
    # ---------------------------------------------------------

    if complexity == "high":
        scores["living_room"] += 0.03
        scores["office"] += 0.03
        scores["kitchen"] += 0.03

    elif complexity == "low":
        scores["bedroom"] += 0.02
        scores["bathroom"] += 0.02

    # ---------------------------------------------------------
    # NORMALIZE
    # ---------------------------------------------------------

    total_score = sum(scores.values())

    if total_score <= 0:
        probabilities = {
            room_type: 0.0
            for room_type in ROOM_TYPES
        }

    else:
        probabilities = {
            room_type: round(
                score / total_score,
                3
            )
            for room_type, score in scores.items()
        }

    ranked = sorted(
        probabilities.items(),
        key=lambda item: item[1],
        reverse=True
    )

    candidates = []

    for room_type, confidence in ranked:

        if confidence <= 0:
            continue

        candidates.append({
            "type": room_type,
            "confidence": confidence
        })

    # ---------------------------------------------------------
    # CONFIDENCE RULE
    # ---------------------------------------------------------

    # ---------------------------------------------------------
    # CONFIDENCE RULE
    # ---------------------------------------------------------

    top_room = candidates[0] if candidates else None

    if top_room is None:

        selected_room = "unknown"
        confidence = 0.0
        confidence_level = "unknown"

    else:

        confidence = top_room["confidence"]

        if confidence >= 0.50:

            # Strong classification
            selected_room = top_room["type"]
            confidence_level = "high"

        elif confidence >= 0.30:

            # Usable classification, but not highly certain.
            # We still use the best candidate so the design
            # pipeline can continue.
            selected_room = top_room["type"]
            confidence_level = "medium"

        else:

            # Too uncertain to choose a room.
            selected_room = "unknown"
            confidence_level = "low"
    return {
        "type": selected_room,
        "confidence": confidence,
        "confidence_level": confidence_level,
        "candidates": candidates
    }