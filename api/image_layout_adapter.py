"""
Bridge image/text design intent into the existing Day-15
layout optimizer.

This module does not replace the Day-15 optimizer.
It only converts combined design intent into a format
that the optimizer can consume.
"""

from typing import Dict


def build_layout_prompt_from_intent(design_intent: Dict) -> str:
    room_type = design_intent.get(
        "room_type",
        "unknown"
    )

    style = design_intent.get(
        "style",
        "modern"
    )

    assets = design_intent.get(
        "requested_assets",
        []
    )

    furniture = design_intent.get(
        "furniture",
        []
    )

    colors = design_intent.get(
        "colors",
        []
    )

    lighting = design_intent.get(
        "lighting",
        "neutral"
    )

    # -------------------------------------------------
    # ROOM
    # -------------------------------------------------

    if room_type == "unknown":
        room_text = "room"
    else:
        room_text = room_type.replace(
            "_",
            " "
        )

    prompt_parts = [
        f"Create a {style} {room_text}."
    ]

    # -------------------------------------------------
    # FURNITURE FROM IMAGE
    # -------------------------------------------------

    furniture_assets = []

    for item in furniture:
        if not isinstance(item, dict):
            continue

        asset = item.get("asset")

        if asset and asset not in furniture_assets:
            furniture_assets.append(asset)

    # -------------------------------------------------
    # FALLBACK TO ROOM DEFAULTS
    # -------------------------------------------------

    if furniture_assets:
        assets_to_use = furniture_assets

    else:
        assets_to_use = assets

    if assets_to_use:

        readable_assets = [
            asset.replace("_", " ")
            for asset in assets_to_use
        ]

        prompt_parts.append(
            "Include "
            + ", ".join(readable_assets)
            + "."
        )

    # -------------------------------------------------
    # COLORS
    # -------------------------------------------------

    if colors:

        prompt_parts.append(
            "Use "
            + ", ".join(colors)
            + " colors."
        )

    # -------------------------------------------------
    # LIGHTING
    # -------------------------------------------------

    if lighting != "unknown":

        prompt_parts.append(
            f"Use {lighting} lighting."
        )

    return " ".join(prompt_parts)


def create_layout_request(
    design_intent,
    room_width,
    room_length
):

    prompt = build_layout_prompt_from_intent(
        design_intent
    )

    return {
        "prompt": prompt,

        "room_type":
            design_intent.get(
                "room_type",
                "unknown"
            ),

        "room_width":
            room_width,

        "room_length":
            room_length,

        "design_intent":
            design_intent,
    }