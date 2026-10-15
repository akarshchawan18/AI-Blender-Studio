"""
DAY 15 - DESIGN LAYOUT ADAPTER

Converts natural-language design intent into
layout instructions that the existing layout
engine can understand.

This file does NOT modify Blender.
"""

from api.design_intent import parse_design_intent


# ---------------------------------------------------------
# DEFAULT ROOM FURNITURE
# ---------------------------------------------------------

DEFAULT_ROOM_ASSETS = {
    "living_room": [
        "Sofa_Modern",
        "CoffeeTable_Modern",
        "TVUnit_Wood"
    ],

    "bedroom": [
        "Bed_Modern",
        "Wardrobe_Modern",
        "Lamp_Modern"
    ],

    "office": [
        "Desk_Modern",
        "Chair_Modern",
        "Lamp_Modern"
    ],

    "dining_room": [
        "DiningTable_Modern",
        "Chair_Modern",
        "Lamp_Modern"
    ],

    "kitchen": []
}


# ---------------------------------------------------------
# DESIGN INTENT → ASSET SELECTION
# ---------------------------------------------------------

def select_assets(intent):
    """
    Determine the final furniture list.

    Explicit user requests take priority over defaults.
    """

    room_type = intent.get("room_type")

    default_assets = DEFAULT_ROOM_ASSETS.get(
        room_type,
        []
    )

    requested_assets = intent.get(
        "requested_assets",
        []
    )

    assets = list(default_assets)

    # Replace default sofa with requested sofa.
    for requested in requested_assets:

        if requested == "Sofa_LShape":

            if "Sofa_Modern" in assets:
                assets.remove("Sofa_Modern")

            if "Sofa_LShape" not in assets:
                assets.append("Sofa_LShape")

    # Add other explicitly requested furniture.
    for requested in requested_assets:

        if requested not in assets:
            assets.append(requested)

    return assets


# ---------------------------------------------------------
# ORIENTATION RULES
# ---------------------------------------------------------

def extract_orientation_rules(intent):
    """
    Convert orientation instructions into
    simple layout rules.
    """

    rules = []

    for instruction in intent.get(
        "orientation",
        []
    ):

        if instruction.get("type") == "face":

            rules.append({
                "type": "face",
                "subject": instruction.get("subject"),
                "target": instruction.get("target")
            })

        elif instruction.get("type") == "center":

            rules.append({
                "type": "center",
                "asset": instruction.get("asset")
            })

    return rules


# ---------------------------------------------------------
# COLOR RULES
# ---------------------------------------------------------

def extract_color_rules(
    design_intent
):
    colors = design_intent.get(
        "colors",
        []
    )

    assets = design_intent.get(
        "requested_assets",
        []
    )

    if not colors:
        return []

    if not assets:
        return []

    rules = []

    # Prefer the first explicitly requested furniture asset.
    target_asset = assets[0]

    color_map = {
        "grey": "#808080",
        "gray": "#808080",
        "white": "#FFFFFF",
        "black": "#000000",
        "brown": "#8B4513",
        "blue": "#4169E1",
        "green": "#228B22",
        "yellow": "#FFD700",
        "orange": "#FF8C00",
        "purple": "#800080",
        "beige": "#D8C3A5",
        "red": "#B22222",
    }

    for color in colors:
        color_name = str(color).lower()

        if color_name in color_map:
            rules.append({
                "asset": target_asset,
                "color": color_map[color_name]
            })

    return rules

# ---------------------------------------------------------
# SPACE RULES
# ---------------------------------------------------------

def extract_space_rules(intent):

    preferences = intent.get(
        "space_preferences",
        []
    )

    rules = []

    if "keep_entrance_clear" in preferences:

        rules.append({
            "type": "keep_entrance_clear"
        })

    if "maximize_walking_space" in preferences:

        rules.append({
            "type": "maximize_walking_space"
        })

    if "maximize_open_space" in preferences:

        rules.append({
            "type": "maximize_open_space"
        })

    return rules


# ---------------------------------------------------------
# LIGHTING
# ---------------------------------------------------------

def extract_lighting(intent):

    lighting = intent.get("lighting")

    if lighting is None:
        return None

    return {
        "type": lighting
    }


# ---------------------------------------------------------
# BUILD FINAL LAYOUT INSTRUCTIONS
# ---------------------------------------------------------

def build_layout_instructions(intent):

    instructions = {
        "room_type": intent.get("room_type"),
        "room_size": intent.get("room_size"),
        "style": intent.get("style"),

        "assets": select_assets(intent),

        "orientation": extract_orientation_rules(intent),

        "colors": extract_color_rules(intent),

        "space_rules": extract_space_rules(intent),

        "lighting": extract_lighting(intent)
    }

    return instructions


# ---------------------------------------------------------
# MAIN ADAPTER
# ---------------------------------------------------------

def create_layout_instructions(prompt):

    intent = parse_design_intent(prompt)

    instructions = build_layout_instructions(
        intent
    )

    return {
        "intent": intent,
        "layout": instructions
    }


# ---------------------------------------------------------
# TEST
# ---------------------------------------------------------

if __name__ == "__main__":

    test_prompt = (
        "Create a large luxury living room with a grey "
        "L-shaped sofa facing the TV, a coffee table in "
        "the center, warm lighting and more walking space."
    )

    result = create_layout_instructions(
        test_prompt
    )

    print()
    print("=" * 70)
    print("DAY 15 - DESIGN LAYOUT ADAPTER TEST")
    print("=" * 70)

    print()
    print("PROMPT:")
    print(test_prompt)

    print()
    print("SELECTED ASSETS:")

    for asset in result["layout"]["assets"]:
        print(" -", asset)

    print()
    print("ORIENTATION RULES:")

    for rule in result["layout"]["orientation"]:
        print(" -", rule)

    print()
    print("COLOR RULES:")

    for rule in result["layout"]["colors"]:
        print(" -", rule)

    print()
    print("SPACE RULES:")

    for rule in result["layout"]["space_rules"]:
        print(" -", rule)

    print()
    print("LIGHTING:")
    print(result["layout"]["lighting"])

    print()
    print("ROOM:")
    print(result["layout"]["room_type"])

    print()
    print("SIZE:")
    print(result["layout"]["room_size"])

    print()
    print("STYLE:")
    print(result["layout"]["style"])

    print()
    print("=" * 70)