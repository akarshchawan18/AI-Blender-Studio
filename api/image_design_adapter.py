"""
Convert image analysis results into design/layout information.

This module connects Day-16 image analysis
with the existing Day-15 design pipeline.

MVP:
- Uses only high-confidence room classification.
- Uses dominant colors.
- Uses brightness.
- Does not invent furniture or architecture.
"""

from typing import Dict, List


ROOM_DEFAULTS = {
    "living_room": {
        "style": "modern",
        "assets": [
            "Sofa_Modern",
            "CoffeeTable_Modern",
            "TVUnit_Wood",
        ],
    },

    "bedroom": {
        "style": "modern",
        "assets": [
            "Bed_Modern",
            "Wardrobe_Modern",
            "Lamp_Modern",
        ],
    },

    "office": {
        "style": "modern",
        "assets": [
            "Desk_Modern",
            "Chair_Modern",
            "Lamp_Modern",
        ],
    },

    "dining_room": {
        "style": "modern",
        "assets": [
            "DiningTable_Modern",
            "Chair_Modern",
            "Lamp_Modern",
        ],
    },

    "kitchen": {
        "style": "modern",
        "assets": [],
    },

    "bathroom": {
        "style": "modern",
        "assets": [],
    },
}


def _get_room_type(analysis):
    room = analysis.get("room", {})

    room_type = room.get("type", "unknown")

    if not isinstance(room_type, str):
        return "unknown"

    return room_type.lower()


def _get_room_confidence(analysis):
    room = analysis.get("room", {})

    try:
        return float(room.get("confidence", 0.0))
    except (TypeError, ValueError):
        return 0.0


def _get_colors(analysis):
    colors = analysis.get("colors", [])

    if not isinstance(colors, list):
        return []

    return [
        str(color).lower()
        for color in colors
    ]


def _get_brightness(analysis):
    visual = analysis.get("visual", {})

    brightness = visual.get("brightness", {})

    if not isinstance(brightness, dict):
        return "unknown"

    return brightness.get("level", "unknown")


def _get_furniture(analysis):
    furniture_detection = analysis.get(
        "furniture_detection",
        {}
    )

    if not isinstance(furniture_detection, dict):
        return []

    furniture = furniture_detection.get(
        "furniture",
        []
    )

    if not isinstance(furniture, list):
        return []

    return furniture


def create_image_design_intent(
    analysis,
    minimum_confidence=0.30
):
    room_type = _get_room_type(analysis)

    confidence = _get_room_confidence(analysis)

    colors = _get_colors(analysis)

    brightness = _get_brightness(analysis)

    furniture = _get_furniture(analysis)

    confidence_level = (
        analysis
        .get("room", {})
        .get("confidence_level", "unknown")
    )

    # -------------------------------------------------
    # ROOM CONFIDENCE
    # -------------------------------------------------

    if confidence < minimum_confidence:
        selected_room = "unknown"
        fallback_used = False
    else:
        selected_room = room_type
        fallback_used = (
            confidence_level == "medium"
        )

    # -------------------------------------------------
    # ROOM DEFAULTS
    # -------------------------------------------------

    room_defaults = ROOM_DEFAULTS.get(
        selected_room,
        {}
    )

    style = room_defaults.get(
        "style",
        "modern"
    )

    assets = list(
        room_defaults.get(
            "assets",
            []
        )
    )

    # -------------------------------------------------
    # LIGHTING
    # -------------------------------------------------

    if brightness in {
        "dark",
        "medium_dark"
    }:
        lighting = "warm"

    elif brightness in {
        "bright",
        "very_bright"
    }:
        lighting = "natural"

    else:
        lighting = "neutral"

    # -------------------------------------------------
    # FINAL DESIGN INTENT
    # -------------------------------------------------

    return {
        "source": "image",

        "room_type": selected_room,

        "room_confidence": round(
            confidence,
            3
        ),

        "room_confidence_level":
            confidence_level,

        "fallback_used":
            fallback_used,

        "room_candidates":
            analysis
            .get("room", {})
            .get("candidates", []),

        "style": style,

        "requested_assets": assets,

        "colors": colors,

        "lighting": lighting,

        "image_orientation":
            analysis
            .get("image", {})
            .get(
                "orientation",
                "unknown"
            ),

        # NEW
        "furniture": furniture,

        # NEW
        "furniture_detection": {
            "status":
                analysis
                .get(
                    "furniture_detection",
                    {}
                )
                .get(
                    "status",
                    "unknown"
                ),

            "source":
                analysis
                .get(
                    "furniture_detection",
                    {}
                )
                .get(
                    "source",
                    "unknown"
                ),

            "fallback_used":
                analysis
                .get(
                    "furniture_detection",
                    {}
                )
                .get(
                    "fallback_used",
                    False
                ),
        },

        "analysis_confidence":
            round(
                confidence,
                3
            ),
    }