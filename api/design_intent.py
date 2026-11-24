"""
DAY 15 - NATURAL LANGUAGE DESIGN INTENT

Converts a natural-language interior prompt
into structured design instructions.
"""

SUPPORTED_ASSETS = {
    "l-shaped sofa": "Sofa_LShape",
    "l shape sofa": "Sofa_LShape",
    "modern sofa": "Sofa_Modern",
    "coffee table": "CoffeeTable_Modern",
    "tv unit": "TVUnit_Wood",
    "television unit": "TVUnit_Wood",
    "chair": "Chair_Modern",
    "bed": "Bed_Modern",
    "wardrobe": "Wardrobe_Modern",
    "desk": "Desk_Modern",
    "dining table": "DiningTable_Modern",
    "lamp": "Lamp_Modern",
    "sofa": "Sofa_Modern",
}


COLOR_MAP = {
    "light grey": "#B8B8B8",
    "dark grey": "#4A4A4A",
    "grey": "#808080",
    "gray": "#808080",
    "white": "#FFFFFF",
    "black": "#111111",
    "brown": "#6B4226",
    "beige": "#D8C3A5",
    "cream": "#E8DED0",
    "blue": "#4169A1",
    "green": "#4F6F52",
    "red": "#8B3A3A",
    "deep teal": "#0E6259",
    "teal": "#0E6259",
}


def normalize_prompt(prompt):
    return " ".join(prompt.lower().strip().split())


def detect_requested_assets(prompt):
    """
    Detect explicitly requested furniture.

    More specific phrases are checked first.
    """

    detected = []

    # Check longest phrases first.
    keywords = sorted(
        SUPPORTED_ASSETS.keys(),
        key=len,
        reverse=True
    )

    for keyword in keywords:

        if keyword in prompt:

            asset_name = SUPPORTED_ASSETS[keyword]

            if asset_name not in detected:
                detected.append(asset_name)

    # If an L-shaped sofa was detected,
    # remove normal sofa.
    if "Sofa_LShape" in detected:
        if "Sofa_Modern" in detected:
            detected.remove("Sofa_Modern")

    return detected


def detect_sofa_asset(prompt):
    """
    Determine which sofa the user requested.
    """

    if "l-shaped sofa" in prompt:
        return "Sofa_LShape"

    if "l shape sofa" in prompt:
        return "Sofa_LShape"

    if "l-shaped" in prompt and "sofa" in prompt:
        return "Sofa_LShape"

    if "l shape" in prompt and "sofa" in prompt:
        return "Sofa_LShape"

    if "sofa" in prompt:
        return "Sofa_Modern"

    return None


def detect_colors(prompt):
    detected = {}

    for color_name, hex_value in COLOR_MAP.items():

        if color_name in prompt:
            detected[color_name] = hex_value

    return detected


def detect_orientation_instructions(prompt):
    """
    Detect spatial relationships between furniture.
    """

    instructions = []

    sofa_asset = detect_sofa_asset(prompt)

    if sofa_asset and "tv" in prompt:

        instructions.append({
            "type": "face",
            "subject": sofa_asset,
            "target": "TVUnit_Wood"
        })

    if "coffee table in the center" in prompt:

        instructions.append({
            "type": "center",
            "asset": "CoffeeTable_Modern"
        })

    elif "coffee table in center" in prompt:

        instructions.append({
            "type": "center",
            "asset": "CoffeeTable_Modern"
        })

    return instructions



def detect_lighting_instruction(prompt):
    """Detect the requested lighting style."""
    prompt = prompt.lower()

    if "warm lighting" in prompt or "warm light" in prompt:
        return "warm"

    if (
        "daylight" in prompt
        or "natural light" in prompt
        or "bright natural lighting" in prompt
    ):
        return "daylight"

    if "cool lighting" in prompt or "cool light" in prompt:
        return "cool"

    return None


def detect_style_instruction(prompt):
    """Detect the requested interior design style."""
    prompt = prompt.lower()

    styles = [
        ("contemporary", ["contemporary"]),
        ("minimalist", ["minimalist", "minimal"]),
        ("industrial", ["industrial"]),
        ("scandinavian", ["scandinavian", "nordic"]),
        ("traditional", ["traditional", "classic"]),
        ("luxury", ["luxury", "luxurious", "high-end"]),
        ("modern", ["modern", "modular"]),
        ("rustic", ["rustic", "farmhouse"]),
    ]

    for style, keywords in styles:
        if any(keyword in prompt for keyword in keywords):
            return style

    return None


def detect_room_instruction(prompt):
    """Detect the intended room type."""
    prompt = prompt.lower()

    if "kitchen" in prompt:
        return "kitchen"

    if "living room" in prompt or "livingroom" in prompt:
        return "living_room"

    if "bedroom" in prompt:
        return "bedroom"

    if "home office" in prompt or "office room" in prompt:
        return "office"

    if "office" in prompt:
        return "office"

    if "dining room" in prompt or "dining area" in prompt:
        return "dining_room"

    return None


def detect_size_instruction(prompt):
    """Detect the requested room size."""
    prompt = prompt.lower()

    large_words = [
        "very large",
        "large",
        "spacious",
        "huge",
        "big",
        "oversized",
    ]

    small_words = [
        "small",
        "compact",
        "tiny",
        "cozy",
        "little",
    ]

    for word in large_words:
        if word in prompt:
            return "large"

    for word in small_words:
        if word in prompt:
            return "small"

    return None


def detect_space_preferences(prompt):
    """Detect requested open space and clear walking paths."""
    prompt = prompt.lower()
    preferences = []

    if (
        "space near the entrance" in prompt
        or "keep the entrance clear" in prompt
        or "clear entrance" in prompt
    ):
        preferences.append("keep_entrance_clear")

    if "open space" in prompt:
        preferences.append("maximize_open_space")

    if (
        "more walking space" in prompt
        or "walking space" in prompt
    ):
        preferences.append("maximize_walking_space")

    return preferences


def parse_design_intent(prompt):
    """Convert a user prompt into structured design instructions."""
    normalized = normalize_prompt(prompt)

    intent = {
        "original_prompt": prompt,
        "room_type": detect_room_instruction(normalized),
        "room_size": detect_size_instruction(normalized),
        "style": detect_style_instruction(normalized),
        "requested_assets": detect_requested_assets(normalized),
        "colors": detect_colors(normalized),
        "lighting": detect_lighting_instruction(normalized),
        "orientation": detect_orientation_instructions(normalized),
        "space_preferences": detect_space_preferences(normalized),
    }

    return intent


if __name__ == "__main__":

    test_prompt = (
        "Create a large luxury living room with a grey "
        "L-shaped sofa facing the TV, a coffee table in "
        "the center, warm lighting and more walking space."
    )

    result = parse_design_intent(test_prompt)

    print()
    print("=" * 60)
    print("DAY 15 - DESIGN INTENT TEST")
    print("=" * 60)

    print("PROMPT:")
    print(test_prompt)

    print()
    print("DESIGN INTENT:")

    for key, value in result.items():
        print(f"{key}: {value}")

    print("=" * 60)