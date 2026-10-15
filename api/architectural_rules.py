"""
DAY 18 - ARCHITECTURAL RULES

Handles:
- Default door positions
- Default window positions
- Multiple doors/windows
- Door clearance
- Window clearance
- Furniture blocking architectural elements
- Architecture confidence metadata
- Image-detected architecture compatibility

This module is the RULES / VALIDATION layer.

Image detection itself should be handled by:
    api/architecture_detector.py
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

# Approximate wall thickness used later when
# converting detected architecture into Blender geometry.
DEFAULT_WALL_THICKNESS = 0.15


# ============================================================
# ARCHITECTURAL ELEMENTS
# ============================================================

def get_default_architecture(room_width, room_length):
    """
    Returns default architectural elements.

    Coordinate system:

        +Y
         ↑
         |
    -X ← ROOM → +X
         |
         ↓
        -Y

    Default:

        Door   -> front (-Y) wall
        Window -> back (+Y) wall
    """

    architecture = {
        "confidence": 1.0,
        "source": "default_rules",

        "walls": [
            {
                "wall": "front",
                "axis": "x",
                "position": -room_length / 2,
                "length": room_width
            },
            {
                "wall": "back",
                "axis": "x",
                "position": room_length / 2,
                "length": room_width
            },
            {
                "wall": "left",
                "axis": "y",
                "position": -room_width / 2,
                "length": room_length
            },
            {
                "wall": "right",
                "axis": "y",
                "position": room_width / 2,
                "length": room_length
            }
        ],

        "doors": [
            {
                "position": [0.0, -room_length / 2],
                "width": DOOR_WIDTH,
                "wall": "front",
                "type": "door",
                "confidence": 1.0
            }
        ],

        "windows": [
            {
                "position": [0.0, room_length / 2],
                "width": WINDOW_WIDTH,
                "wall": "back",
                "type": "window",
                "confidence": 1.0
            }
        ]
    }

    # Backward compatibility with existing code
    architecture["door"] = architecture["doors"][0]

    return architecture


# ============================================================
# ARCHITECTURE NORMALIZATION
# ============================================================

def normalize_architecture(architecture):
    """
    Makes different architecture sources compatible.

    Supports:

        architecture["door"]
        architecture["doors"]
        architecture["windows"]
        architecture["walls"]
    """

    if not isinstance(architecture, dict):
        return None

    normalized = dict(architecture)

    # --------------------------------------------------------
    # DOORS
    # --------------------------------------------------------

    doors = normalized.get("doors")

    if doors is None:
        door = normalized.get("door")

        if door:
            doors = [door]
        else:
            doors = []

    normalized["doors"] = doors

    # --------------------------------------------------------
    # BACKWARD COMPATIBILITY
    # --------------------------------------------------------

    if "door" not in normalized:
        normalized["door"] = doors[0] if doors else None

    # --------------------------------------------------------
    # WINDOWS
    # --------------------------------------------------------

    windows = normalized.get("windows")

    if windows is None:
        windows = []

    normalized["windows"] = windows

    # --------------------------------------------------------
    # WALLS
    # --------------------------------------------------------

    walls = normalized.get("walls")

    if walls is None:
        walls = []

    normalized["walls"] = walls

    # --------------------------------------------------------
    # METADATA
    # --------------------------------------------------------

    if "source" not in normalized:
        normalized["source"] = "unknown"

    if "confidence" not in normalized:
        normalized["confidence"] = 0.0

    return normalized


# ============================================================
# ASSET FOOTPRINT
# ============================================================

def get_asset_footprint(asset):
    """
    Returns approximate world-space width/depth.

    Rotation-aware handling is intentionally left to the
    layout validator/optimizer.
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

    # --------------------------------------------------------
    # Current Day 14 default assumes front (-Y) wall.
    # --------------------------------------------------------

    wall = door.get("wall", "front")

    if wall == "front":

        door_min_x = door_x - half_door_width
        door_max_x = door_x + half_door_width

        door_min_y = door_y
        door_max_y = (
            door_y
            + DOOR_CLEARANCE
            + 0.35
        )

    elif wall == "back":

        door_min_x = door_x - half_door_width
        door_max_x = door_x + half_door_width

        door_min_y = (
            door_y
            - DOOR_CLEARANCE
            - 0.35
        )
        door_max_y = door_y

    elif wall == "left":

        door_min_x = door_x
        door_max_x = (
            door_x
            + DOOR_CLEARANCE
            + 0.35
        )

        door_min_y = door_y - half_door_width
        door_max_y = door_y + half_door_width

    elif wall == "right":

        door_min_x = (
            door_x
            - DOOR_CLEARANCE
            - 0.35
        )
        door_max_x = door_x

        door_min_y = door_y - half_door_width
        door_max_y = door_y + half_door_width

    else:
        return False

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
    Checks whether furniture directly blocks a window.
    """

    width, depth = get_asset_footprint(asset)

    x = asset["position"][0]
    y = asset["position"][1]

    window_x = window["position"][0]
    window_y = window["position"][1]

    half_asset_width = width / 2
    half_asset_depth = depth / 2

    half_window_width = window["width"] / 2

    wall = window.get("wall", "back")

    # --------------------------------------------------------
    # Back wall
    # --------------------------------------------------------

    if wall == "back":

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

    # --------------------------------------------------------
    # Front wall
    # --------------------------------------------------------

    elif wall == "front":

        window_min_x = (
            window_x
            - half_window_width
        )

        window_max_x = (
            window_x
            + half_window_width
        )

        window_min_y = window_y

        window_max_y = (
            window_y
            + WINDOW_CLEARANCE
        )

    # --------------------------------------------------------
    # Left wall
    # --------------------------------------------------------

    elif wall == "left":

        window_min_x = window_x

        window_max_x = (
            window_x
            + WINDOW_CLEARANCE
        )

        window_min_y = (
            window_y
            - half_window_width
        )

        window_max_y = (
            window_y
            + half_window_width
        )

    # --------------------------------------------------------
    # Right wall
    # --------------------------------------------------------

    elif wall == "right":

        window_min_x = (
            window_x
            - WINDOW_CLEARANCE
        )

        window_max_x = window_x

        window_min_y = (
            window_y
            - half_window_width
        )

        window_max_y = (
            window_y
            + half_window_width
        )

    else:
        return False

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
# WALL CLEARANCE
# ============================================================

def is_near_wall(
    asset,
    room_width,
    room_length,
    tolerance=WALL_TOLERANCE
):
    """
    Determines whether an asset is very close to a room wall.

    This is informational for now.

    The layout validator remains responsible for
    enforcing room boundaries.
    """

    width, depth = get_asset_footprint(asset)

    x = asset["position"][0]
    y = asset["position"][1]

    half_width = width / 2
    half_depth = depth / 2

    left_distance = (
        x
        - half_width
        + room_width / 2
    )

    right_distance = (
        room_width / 2
        - x
        - half_width
    )

    front_distance = (
        y
        - half_depth
        + room_length / 2
    )

    back_distance = (
        room_length / 2
        - y
        - half_depth
    )

    return (
        left_distance <= tolerance
        or right_distance <= tolerance
        or front_distance <= tolerance
        or back_distance <= tolerance
    )


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

    Returns:

        valid
        warnings
        blocked_doors
        blocked_windows
        architecture_source
        architecture_confidence
    """

    if architecture is None:

        architecture = get_default_architecture(
            room_width,
            room_length
        )

    architecture = normalize_architecture(
        architecture
    )

    warnings = []

    blocked_doors = []
    blocked_windows = []

    # --------------------------------------------------------
    # DOORS
    # --------------------------------------------------------

    for door in architecture["doors"]:

        for asset in assets:

            if blocks_door(
                asset,
                door,
                room_width,
                room_length
            ):

                asset_name = asset["asset"]

                blocked_doors.append({
                    "asset": asset_name,
                    "door": door
                })

                warnings.append(
                    f"{asset_name} blocks the door."
                )

    # --------------------------------------------------------
    # WINDOWS
    # --------------------------------------------------------

    for window in architecture["windows"]:

        for asset in assets:

            if blocks_window(
                asset,
                window,
                room_width,
                room_length
            ):

                asset_name = asset["asset"]

                blocked_windows.append({
                    "asset": asset_name,
                    "window": window
                })

                warnings.append(
                    f"{asset_name} blocks the window."
                )

    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    return {
        "valid": len(warnings) == 0,
        "warnings": warnings,

        "blocked_doors": blocked_doors,
        "blocked_windows": blocked_windows,

        "architecture_source": architecture.get(
            "source",
            "unknown"
        ),

        "architecture_confidence": architecture.get(
            "confidence",
            0.0
        ),

        "wall_count": len(
            architecture.get("walls", [])
        ),

        "door_count": len(
            architecture.get("doors", [])
        ),

        "window_count": len(
            architecture.get("windows", [])
        )
    }


# ============================================================
# ARCHITECTURE SUMMARY
# ============================================================

def summarize_architecture(architecture):
    """
    Returns a compact summary suitable for API responses
    and debugging.
    """

    architecture = normalize_architecture(
        architecture
    )

    if architecture is None:
        return {
            "source": "unknown",
            "confidence": 0.0,
            "walls": 0,
            "doors": 0,
            "windows": 0
        }

    return {
        "source": architecture.get(
            "source",
            "unknown"
        ),

        "confidence": architecture.get(
            "confidence",
            0.0
        ),

        "walls": len(
            architecture.get("walls", [])
        ),

        "doors": len(
            architecture.get("doors", [])
        ),

        "windows": len(
            architecture.get("windows", [])
        )
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("DAY 18 - ARCHITECTURAL RULES TEST")
    print("=" * 60)

    room_width = 5.5
    room_length = 5.0

    architecture = get_default_architecture(
        room_width,
        room_length
    )

    print("\nARCHITECTURE")

    print(
        "Source:",
        architecture["source"]
    )

    print(
        "Confidence:",
        architecture["confidence"]
    )

    print(
        "Walls:",
        architecture["walls"]
    )

    print(
        "Doors:",
        architecture["doors"]
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

    print(
        "Source:",
        result["architecture_source"]
    )

    print(
        "Confidence:",
        result["architecture_confidence"]
    )

    print(
        "Walls:",
        result["wall_count"]
    )

    print(
        "Doors:",
        result["door_count"]
    )

    print(
        "Windows:",
        result["window_count"]
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

    print("\nSUMMARY")

    print(
        summarize_architecture(
            architecture
        )
    )

    print("\n" + "=" * 60)