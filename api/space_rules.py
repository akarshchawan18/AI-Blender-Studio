# =========================================================
# AI INTERIOR DESIGNER
# DAY 14 - SPACE RULES
# =========================================================

import math

from api.asset_dimensions import get_asset_dimensions


# =========================================================
# CLEARANCES
# =========================================================

DOOR_CLEARANCE = 0.10
DOOR_WIDTH = 0.90
ENTRANCE_DEPTH = 0.35


# =========================================================
# ASSET FOOTPRINT
# =========================================================

def get_footprint(asset):

    dimensions = get_asset_dimensions(
        asset["asset"]
    )

    width = (
        dimensions["width"]
        * asset["scale"][0]
    )

    depth = (
        dimensions["depth"]
        * asset["scale"][1]
    )

    rotation = math.radians(
        asset["rotation"][2]
    )

    cos_r = abs(math.cos(rotation))
    sin_r = abs(math.sin(rotation))

    world_width = (
        width * cos_r
        + depth * sin_r
    )

    world_depth = (
        width * sin_r
        + depth * cos_r
    )

    return world_width, world_depth


# =========================================================
# ASSET BOUNDS
# =========================================================

def get_bounds(asset):

    width, depth = get_footprint(asset)

    x = asset["position"][0]
    y = asset["position"][1]

    return {
        "min_x": x - width / 2,
        "max_x": x + width / 2,
        "min_y": y - depth / 2,
        "max_y": y + depth / 2
    }


# =========================================================
# DOOR BLOCKING
# =========================================================

def blocks_door(
    asset,
    door_position,
    door_width=DOOR_WIDTH
):

    bounds = get_bounds(asset)

    door_x = door_position[0]
    door_y = door_position[1]

    # Door opening width
    half_width = door_width / 2

    door_min_x = (
        door_x
        - half_width
        - DOOR_CLEARANCE
    )

    door_max_x = (
        door_x
        + half_width
        + DOOR_CLEARANCE
    )

    # Only the small area immediately inside
    # the entrance is considered the doorway zone.

    entrance_min_y = (
        door_y
        - 0.05
    )

    entrance_max_y = (
        door_y
        + ENTRANCE_DEPTH
    )

    overlaps_x = (
        bounds["max_x"] >= door_min_x
        and
        bounds["min_x"] <= door_max_x
    )

    overlaps_y = (
        bounds["max_y"] >= entrance_min_y
        and
        bounds["min_y"] <= entrance_max_y
    )

    return overlaps_x and overlaps_y


# =========================================================
# ROOM ACCESS CHECK
# =========================================================

def check_room_access(
    assets,
    room_width,
    room_length
):

    warnings = []

    # Door located at the center
    # of the front wall.

    door_position = (
        0,
        -room_length / 2
    )

    # -----------------------------------------------------
    # CHECK DOOR
    # -----------------------------------------------------

    for asset in assets:

        if blocks_door(
            asset,
            door_position
        ):

            warnings.append(
                f"{asset['asset']} blocks the entrance."
            )

    return warnings


# =========================================================
# SPACE VALIDATION
# =========================================================

def validate_space_rules(
    assets,
    room_width,
    room_length
):

    warnings = check_room_access(
        assets,
        room_width,
        room_length
    )

    return {
        "valid": len(warnings) == 0,
        "warnings": warnings
    }


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("DAY 14 SPACE RULES TEST")
    print("=" * 60)

    room_width = 5.5
    room_length = 5.0

    assets = [

        {
            "asset": "Sofa_Modern",
            "position": [0, 1.2, 0],
            "rotation": [0, 0, 0],
            "scale": [1, 1, 1]
        },

        {
            "asset": "CoffeeTable_Modern",
            "position": [0, -0.1, 0],
            "rotation": [0, 0, 0],
            "scale": [1, 1, 1]
        },

        {
            "asset": "TVUnit_Wood",
            "position": [0, -1.8, 0],
            "rotation": [0, 0, 0],
            "scale": [1, 1, 1]
        }
    ]

    result = validate_space_rules(
        assets,
        room_width,
        room_length
    )

    print()
    print("ROOM")
    print("Width :", room_width)
    print("Length:", room_length)

    print()
    print("ROOM ACCESS")
    print("Valid:", result["valid"])

    print()
    print("WARNINGS:")

    if not result["warnings"]:

        print("None")

    else:

        for warning in result["warnings"]:

            print(
                "WARNING:",
                warning
            )

    print()
    print("=" * 60)