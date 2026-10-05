"""
DAY 14 - ROOM SIZE ENGINE
Detects room size from natural language prompts.
"""

ROOM_DIMENSIONS = {
    "small": {
        "width": 3.5,
        "length": 3.0,
        "height": 2.8,
        "scale": 0.82,
        "spacing": 0.75
    },

    "medium": {
        "width": 4.572,
        "length": 3.658,
        "height": 3.048,
        "scale": 1.00,
        "spacing": 1.00
    },

    "large": {
        "width": 6.0,
        "length": 5.0,
        "height": 3.2,
        "scale": 1.12,
        "spacing": 1.25
    }
}


def detect_room_size(prompt):

    prompt = prompt.lower().strip()

    # --------------------------------------------------
    # LARGE
    # --------------------------------------------------

    large_keywords = [
        "large",
        "spacious",
        "big",
        "huge",
        "very large",
        "large-sized",
        "oversized"
    ]

    for keyword in large_keywords:
        if keyword in prompt:
            return "large"

    # --------------------------------------------------
    # SMALL
    # --------------------------------------------------

    small_keywords = [
        "small",
        "compact",
        "tiny",
        "cozy",
        "little"
    ]

    for keyword in small_keywords:
        if keyword in prompt:
            return "small"

    # --------------------------------------------------
    # MEDIUM / DEFAULT
    # --------------------------------------------------

    return "medium"


def get_room_config(room_size):

    return ROOM_DIMENSIONS.get(
        room_size,
        ROOM_DIMENSIONS["medium"]
    ).copy()


def get_room_dimensions(room_size):

    config = get_room_config(room_size)

    return {
        "width": config["width"],
        "length": config["length"],
        "height": config["height"]
    }


def apply_room_size_to_assets(assets, room_size):

    config = get_room_config(room_size)

    scale_factor = config["scale"]
    spacing_factor = config["spacing"]

    for asset in assets:

        # ----------------------------------------------
        # SCALE
        # ----------------------------------------------

        original_scale = asset.get(
            "scale",
            [1, 1, 1]
        )

        asset["scale"] = [
            original_scale[0] * scale_factor,
            original_scale[1] * scale_factor,
            original_scale[2] * scale_factor
        ]

        # ----------------------------------------------
        # POSITION
        # ----------------------------------------------

        position = asset.get(
            "position",
            [0, 0, 0]
        )

        asset["position"] = [
            position[0] * spacing_factor,
            position[1] * spacing_factor,
            position[2]
        ]

    return assets


if __name__ == "__main__":

    print("=" * 60)
    print("ROOM SIZE ENGINE TEST")
    print("=" * 60)

    test_prompts = [
        "Create a small living room",
        "Create a medium living room",
        "Create a large modern living room",
        "Create a spacious bedroom",
        "Create a compact office"
    ]

    for prompt in test_prompts:

        size = detect_room_size(prompt)
        dimensions = get_room_dimensions(size)

        print("\nPrompt:", prompt)
        print("Detected:", size)
        print("Dimensions:", dimensions)

    print("\n" + "=" * 60)