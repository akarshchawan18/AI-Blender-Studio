"""
AI Interior Design Studio
REAL ASSET DIMENSIONS

Dimensions measured directly from Blender asset geometry.
Units: meters
"""

# =========================================================
# REAL BLENDER ASSET DIMENSIONS
# =========================================================

ASSET_DIMENSIONS = {

    "Sofa_Modern": {
        "width": 2.40,
        "depth": 0.85,
        "height": 1.10
    },

    "Sofa_LShape": {
        "width": 2.80,
        "depth": 1.80,
        "height": 1.00
    },

    "CoffeeTable_Modern": {
        "width": 1.50,
        "depth": 0.80,
        "height": 0.55
    },

    "TVUnit_Wood": {
        "width": 2.60,
        "depth": 0.40,
        "height": 1.25
    },

    "Chair_Modern": {
        "width": 0.75,
        "depth": 0.75,
        "height": 1.00
    },

    "Bed_Modern": {
        "width": 2.90,
        "depth": 2.20,
        "height": 1.50
    },

    "Wardrobe_Modern": {
        "width": 2.56,
        "depth": 0.86,
        "height": 2.70
    },

    "Desk_Modern": {
        "width": 2.50,
        "depth": 0.90,
        "height": 1.10
    },

    "DiningTable_Modern": {
        "width": 2.70,
        "depth": 1.50,
        "height": 1.00
    },

    "Lamp_Modern": {
        "width": 0.70,
        "depth": 0.70,
        "height": 1.90
    }
}


# =========================================================
# DEFAULT
# =========================================================

DEFAULT_DIMENSIONS = {
    "width": 1.0,
    "depth": 1.0,
    "height": 1.0
}


# =========================================================
# GET DIMENSIONS
# =========================================================

def get_asset_dimensions(asset_name):

    return ASSET_DIMENSIONS.get(
        asset_name,
        DEFAULT_DIMENSIONS.copy()
    )


# =========================================================
# GET FOOTPRINT
# =========================================================

def get_asset_footprint(asset_name):

    dimensions = get_asset_dimensions(asset_name)

    return (
        dimensions["width"],
        dimensions["depth"]
    )


# =========================================================
# GET HEIGHT
# =========================================================

def get_asset_height(asset_name):

    dimensions = get_asset_dimensions(asset_name)

    return dimensions["height"]


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print("=" * 50)
    print("REAL ASSET DIMENSIONS")
    print("=" * 50)

    for asset_name, dimensions in ASSET_DIMENSIONS.items():

        print(
            f"{asset_name:22}"
            f" W={dimensions['width']:.2f}m"
            f" D={dimensions['depth']:.2f}m"
            f" H={dimensions['height']:.2f}m"
        )

    print("=" * 50)