"""
DAY 14 - ARCHITECTURAL RULES

Handles:
- Door positions
- Window positions
- Door clearance
- Window clearance
- Furniture blocking architectural elements
"""

from api.asset_dimensions import get_asset_dimensions


# ============================================================
# DEFAULT ARCHITECTURAL SETTINGS
# ============================================================

DOOR_WIDTH = 0.90
DOOR_CLEARANCE = 0.20

WINDOW_WIDTH = 1.80
WINDOW_CLEARANCE = 0.30

WALL_TOLERANCE = 0.15


# ============================================================
# ARCHITECTURAL ELEMENTS
# ============================================================

def get_default_architecture(room_width, room_length):
    """
    Returns default door and window positions.

    Coordinate system:

        +Y
         ↑
         |
    -X ← ROOM → +X
         |
         ↓
        -Y

    Door:
        centered on the front (-Y) wall

    Window:
        centered on the back (+Y) wall
    """

    architecture = {
        "door": {
            "position": [0.0, -room_length / 2],
            "width": DOOR_WIDTH,
            "wall": "front"
        },

        "windows": [
            {
                "position": [0.0, room_length / 2],
                "width": WINDOW_WIDTH,
                "wall": "back"
            }
        ]
    }

    return architecture


# ============================================================
# ASSET FOOTPRINT
# ============================================================

def get_asset_footprint(asset):
    """
    Returns approximate world-space width/depth.
    """

    name = asset["asset"]

    dimensions = get_asset_dimensions(name)

    scale = asset.get(
        "scale",
        [1.0, 1.0, 1.0]
    )

    width = dimensions["width"] * scale[0]
    depth = dimensions["depth"] * scale[1]

    return width, depth


# ============================================================
# DOOR COLLISION
# ============================================================

def blocks_door(
    asset,
    door,
    room_width,
    room_length
):
    """
    Checks whether furniture blocks the doorway.
    """

    width, depth = get_asset_footprint(asset)

    x = asset["position"][0]
    y = asset["position"][1]

    door_x = door["position"][0]
    door_y = door["position"][1]

    half_asset_width = width / 2
    half_asset_depth = depth / 2

    half_door_width = door["width"] / 2

    # Front wall doorway extends slightly into the room
    door_min_x = door_x - half_door_width
    door_max_x = door_x + half_door_width

    door_min_y = door_y
    door_max_y = door_y + DOOR_CLEARANCE + 0.35

    asset_min_x = x - half_asset_width
    asset_max_x = x + half_asset_width

    asset_min_y = y - half_asset_depth
    asset_max_y = y + half_asset_depth

    overlap_x = (
        asset_max_x > door_min_x
        and asset_min_x < door_max_x
    )

    overlap_y = (
        asset_max_y > door_min_y
        and asset_min_y < door_max_y
    )

    return overlap_x and overlap_y


# ============================================================
# WINDOW COLLISION
# ============================================================

def blocks_window(
    asset,
    window,
    room_width,
    room_length
):
    """
    Checks whether furniture is directly blocking
    a window on the back wall.
    """

    width, depth = get_asset_footprint(asset)

    x = asset["position"][0]
    y = asset["position"][1]

    window_x = window["position"][0]
    window_y = window["position"][1]

    half_asset_width = width / 2
    half_asset_depth = depth / 2

    half_window_width = window["width"] / 2

    window_min_x = (
        window_x
        - half_window_width
    )

    window_max_x = (
        window_x
        + half_window_width
    )

    window_min_y = (
        window_y
        - WINDOW_CLEARANCE
    )

    window_max_y = window_y

    asset_min_x = x - half_asset_width
    asset_max_x = x + half_asset_width

    asset_min_y = y - half_asset_depth
    asset_max_y = y + half_asset_depth

    overlap_x = (
        asset_max_x > window_min_x
        and asset_min_x < window_max_x
    )

    overlap_y = (
        asset_max_y > window_min_y
        and asset_min_y < window_max_y
    )

    return overlap_x and overlap_y


# ============================================================
# ARCHITECTURAL VALIDATION
# ============================================================

def validate_architecture(
    assets,
    room_width,
    room_length,
    architecture=None
):
    """
    Validates furniture against doors and windows.
    """

    if architecture is None:
        architecture = get_default_architecture(
            room_width,
            room_length
        )

    warnings = []

    door = architecture["door"]

    for asset in assets:

        if blocks_door(
            asset,
            door,
            room_width,
            room_length
        ):
            warnings.append(
                f'{asset["asset"]} blocks the door.'
            )

    for window in architecture["windows"]:

        for asset in assets:

            if blocks_window(
                asset,
                window,
                room_width,
                room_length
            ):
                warnings.append(
                    f'{asset["asset"]} blocks the window.'
                )

    return {
        "valid": len(warnings) == 0,
        "warnings": warnings
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("DAY 14 - ARCHITECTURAL RULES TEST")
    print("=" * 60)

    room_width = 5.5
    room_length = 5.0

    architecture = get_default_architecture(
        room_width,
        room_length
    )

    print("\nARCHITECTURE")

    print(
        "Door:",
        architecture["door"]
    )

    print(
        "Windows:",
        architecture["windows"]
    )

    # --------------------------------------------------------
    # TEST FURNITURE
    # --------------------------------------------------------

    assets = [

        {
            "asset": "Sofa_Modern",
            "position": [0, 1.0, 0],
            "rotation": [0, 0, 0],
            "scale": [1, 1, 1]
        },

        {
            "asset": "CoffeeTable_Modern",
            "position": [0, -0.5, 0],
            "rotation": [0, 0, 0],
            "scale": [1, 1, 1]
        },

        {
            "asset": "TVUnit_Wood",
            "position": [0, -1.5, 0],
            "rotation": [0, 0, 0],
            "scale": [1, 1, 1]
        }
    ]

    result = validate_architecture(
        assets,
        room_width,
        room_length,
        architecture
    )

    print("\nARCHITECTURAL VALIDATION")

    print(
        "Valid:",
        result["valid"]
    )

    if result["warnings"]:

        print("\nWARNINGS:")

        for warning in result["warnings"]:
            print(
                "WARNING:",
                warning
            )

    else:

        print("\nWARNINGS:")
        print("None")

    print("\n" + "=" * 60)