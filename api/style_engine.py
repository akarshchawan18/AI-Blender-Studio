# =========================================================
# AI INTERIOR DESIGN STUDIO
# STYLE ENGINE
# =========================================================

# =========================================================
# STYLE CONFIGURATIONS
# =========================================================

STYLE_CONFIGS = {

    "modern": {
        "scale": 1.00,
        "wall": "#E8DED0",
        "floor": "#8B5E3C",
        "ceiling": "#F5F5F5",
        "sofa": "#C8B39A",
        "wood": "#6B4226",
        "black": "#111111",
        "lighting_type": "warm",
        "brightness": 1.0
    },

    "luxury": {
        "scale": 1.08,
        "wall": "#E6DED2",
        "floor": "#5A3825",
        "ceiling": "#FAFAFA",
        "sofa": "#D8C3A5",
        "wood": "#4A2F1B",
        "black": "#151515",
        "lighting_type": "warm",
        "brightness": 1.25
    },

    "minimal": {
        "scale": 0.92,
        "wall": "#F2F2F2",
        "floor": "#C9C9C9",
        "ceiling": "#FFFFFF",
        "sofa": "#D9D9D9",
        "wood": "#B8A58D",
        "black": "#222222",
        "lighting_type": "daylight",
        "brightness": 1.15
    },

    "industrial": {
        "scale": 1.00,
        "wall": "#555555",
        "floor": "#5B4636",
        "ceiling": "#D8D8D8",
        "sofa": "#444444",
        "wood": "#4A3322",
        "black": "#111111",
        "lighting_type": "cool",
        "brightness": 1.05
    },

    "traditional": {
        "scale": 1.04,
        "wall": "#E7D6BF",
        "floor": "#6E4429",
        "ceiling": "#F3EDE4",
        "sofa": "#A9825B",
        "wood": "#59351F",
        "black": "#191919",
        "lighting_type": "warm",
        "brightness": 0.95
    }
}


# =========================================================
# GET STYLE
# =========================================================

def get_style_config(style):

    style = style.lower().strip()

    return STYLE_CONFIGS.get(
        style,
        STYLE_CONFIGS["modern"]
    )


# =========================================================
# APPLY STYLE TO ASSETS
# =========================================================

def apply_style_to_assets(
    assets,
    style
):

    config = get_style_config(style)

    scale_factor = config["scale"]

    styled_assets = []

    for item in assets:

        new_item = item.copy()

        original_scale = item.get(
            "scale",
            [1, 1, 1]
        )

        new_item["scale"] = [

            original_scale[0] * scale_factor,

            original_scale[1] * scale_factor,

            original_scale[2] * scale_factor

        ]

        styled_assets.append(new_item)

    return styled_assets


# =========================================================
# GET STYLE MATERIALS
# =========================================================

def get_style_materials(style):

    config = get_style_config(style)

    return {

        "wall": config["wall"],

        "floor": config["floor"],

        "ceiling": config["ceiling"],

        "sofa": config["sofa"],

        "wood": config["wood"],

        "black": config["black"]

    }


# =========================================================
# GET STYLE LIGHTING
# =========================================================

def get_style_lighting(style):

    config = get_style_config(style)

    return {

        "type": config["lighting_type"],

        "brightness": config["brightness"]

    }