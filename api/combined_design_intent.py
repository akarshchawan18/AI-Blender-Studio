"""
Combine text-based design intent with image-based design intent.

Priority:
1. Explicit user text instructions
2. High-confidence image analysis
3. Safe defaults

This module does not directly modify Blender layouts.
"""


from typing import Dict, Optional


def combine_design_intent(
    text_intent: Optional[Dict] = None,
    image_intent: Optional[Dict] = None,
) -> Dict:

    text_intent = text_intent or {}
    image_intent = image_intent or {}

    # -------------------------------------------------
    # TEXT VALUES
    # -------------------------------------------------

    text_room = text_intent.get(
        "room_type",
        "unknown"
    )

    text_style = text_intent.get(
        "style",
        "unknown"
    )

    text_assets = text_intent.get(
        "requested_assets",
        []
    )

    text_colors = text_intent.get(
        "colors",
        []
    )

    text_lighting = text_intent.get(
        "lighting",
        "unknown"
    )

    # -------------------------------------------------
    # IMAGE VALUES
    # -------------------------------------------------

    image_room = image_intent.get(
        "room_type",
        "unknown"
    )

    image_confidence = float(
        image_intent.get(
            "room_confidence",
            0.0
        )
    )

    image_style = image_intent.get(
        "style",
        "unknown"
    )

    image_assets = image_intent.get(
        "requested_assets",
        []
    )

    image_colors = image_intent.get(
        "colors",
        []
    )

    image_lighting = image_intent.get(
        "lighting",
        "unknown"
    )

    # -------------------------------------------------
    # ROOM DECISION
    # -------------------------------------------------

    if text_room != "unknown":
        final_room = text_room
        room_source = "text"

    elif (
        image_room != "unknown"
        and image_confidence >= 0.35
    ):
        final_room = image_room
        room_source = "image"

    else:
        final_room = "unknown"
        room_source = "none"

    # -------------------------------------------------
    # STYLE DECISION
    # -------------------------------------------------

    if text_style != "unknown":
        final_style = text_style
        style_source = "text"

    elif image_style != "unknown":
        final_style = image_style
        style_source = "image"

    else:
        final_style = "modern"
        style_source = "default"

    # -------------------------------------------------
    # ASSETS
    # -------------------------------------------------

    if text_assets:
        final_assets = list(text_assets)
        asset_source = "text"

    elif (
        image_assets
        and image_confidence >= 0.35
    ):
        final_assets = list(image_assets)
        asset_source = "image"

    else:
        final_assets = []
        asset_source = "none"

    # -------------------------------------------------
    # COLORS
    # -------------------------------------------------

    if text_colors:
        final_colors = list(text_colors)
        color_source = "text"

    elif image_colors:
        final_colors = list(image_colors)
        color_source = "image"

    else:
        final_colors = []
        color_source = "none"

    # -------------------------------------------------
    # LIGHTING
    # -------------------------------------------------

    if text_lighting != "unknown":
        final_lighting = text_lighting
        lighting_source = "text"

    elif image_lighting != "unknown":
        final_lighting = image_lighting
        lighting_source = "image"

    else:
        final_lighting = "neutral"
        lighting_source = "default"

    # -------------------------------------------------
    # FINAL RESULT
    # -------------------------------------------------

    return {
        "source": "combined",

        "room_type": final_room,
        "room_source": room_source,

        "style": final_style,
        "style_source": style_source,

        "requested_assets": final_assets,
        "asset_source": asset_source,

        "colors": final_colors,
        "color_source": color_source,

        "lighting": final_lighting,
        "lighting_source": lighting_source,

        "image_confidence": image_confidence,

        "image_room_candidates": image_intent.get(
            "room_candidates",
            []
        ),
    }