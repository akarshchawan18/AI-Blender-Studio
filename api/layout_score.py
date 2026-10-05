"""
DAY 14 - LAYOUT SCORING ENGINE

Scores furniture layouts based on:

- Furniture collisions
- Room boundaries
- Wall clearance
- Door clearance
- Window clearance
- Center balance
"""

import math

from api.asset_dimensions import get_asset_dimensions
from api.architectural_rules import (
    get_default_architecture,
    validate_architecture
)


# ============================================================
# SETTINGS
# ============================================================

IDEAL_WALL_CLEARANCE = 0.30
IDEAL_CENTER_DISTANCE = 1.50
MIN_WALL_CLEARANCE = 0.10


# ============================================================
# ASSET FOOTPRINT
# ============================================================

def get_footprint(asset):
    """
    Returns the approximate world-space footprint
    of an asset.

    Takes scale and Z rotation into account.
    """

    dimensions = get_asset_dimensions(
        asset["asset"]
    )

    scale = asset.get(
        "scale",
        [1.0, 1.0, 1.0]
    )

    width = (
        dimensions["width"]
        * float(scale[0])
    )

    depth = (
        dimensions["depth"]
        * float(scale[1])
    )

    rotation = asset.get(
        "rotation",
        [0.0, 0.0, 0.0]
    )

    rotation_z = math.radians(
        float(rotation[2])
    )

    cos_r = abs(
        math.cos(rotation_z)
    )

    sin_r = abs(
        math.sin(rotation_z)
    )

    world_width = (
        width * cos_r
        + depth * sin_r
    )

    world_depth = (
        width * sin_r
        + depth * cos_r
    )

    return world_width, world_depth


# ============================================================
# ROOM BOUNDARY
# ============================================================

def is_inside_room(
    asset,
    room_width,
    room_length
):
    """
    Checks whether the complete furniture
    footprint is inside the room.
    """

    width, depth = get_footprint(asset)

    x = asset["position"][0]
    y = asset["position"][1]

    return (
        x - width / 2 >= -room_width / 2
        and
        x + width / 2 <= room_width / 2
        and
        y - depth / 2 >= -room_length / 2
        and
        y + depth / 2 <= room_length / 2
    )


# ============================================================
# FURNITURE OVERLAP
# ============================================================

def assets_overlap(
    asset_a,
    asset_b
):
    """
    Checks whether two furniture
    footprints overlap.
    """

    width_a, depth_a = get_footprint(
        asset_a
    )

    width_b, depth_b = get_footprint(
        asset_b
    )

    ax = asset_a["position"][0]
    ay = asset_a["position"][1]

    bx = asset_b["position"][0]
    by = asset_b["position"][1]

    overlap_x = (
        abs(ax - bx)
        < (width_a + width_b) / 2
    )

    overlap_y = (
        abs(ay - by)
        < (depth_a + depth_b) / 2
    )

    return overlap_x and overlap_y


# ============================================================
# WALL CLEARANCE
# ============================================================

def wall_clearance(
    asset,
    room_width,
    room_length
):
    """
    Returns the minimum distance from
    the furniture footprint to any wall.
    """

    width, depth = get_footprint(asset)

    x = asset["position"][0]
    y = asset["position"][1]

    left = (
        x
        - width / 2
        + room_width / 2
    )

    right = (
        room_width / 2
        - x
        - width / 2
    )

    front = (
        y
        - depth / 2
        + room_length / 2
    )

    back = (
        room_length / 2
        - y
        - depth / 2
    )

    return min(
        left,
        right,
        front,
        back
    )


# ============================================================
# CENTER DISTANCE
# ============================================================

def center_distance(asset):
    """
    Distance between furniture center
    and room center.
    """

    x = asset["position"][0]
    y = asset["position"][1]

    return math.sqrt(
        x * x
        + y * y
    )


# ============================================================
# SCORE LAYOUT
# ============================================================

def score_layout(
    assets,
    room_width,
    room_length
):
    """
    Returns a layout score from 0 to 100.

    Higher score = better layout.
    """

    score = 100.0

    reasons = []

    # --------------------------------------------------------
    # ARCHITECTURE
    # --------------------------------------------------------

    architecture = get_default_architecture(
        room_width,
        room_length
    )

    architecture_result = validate_architecture(
        assets,
        room_width,
        room_length,
        architecture
    )

    if not architecture_result["valid"]:

        score -= 50

        reasons.append(
            "Architectural obstruction"
        )

    # --------------------------------------------------------
    # ROOM BOUNDARIES
    # --------------------------------------------------------

    for asset in assets:

        if not is_inside_room(
            asset,
            room_width,
            room_length
        ):

            score -= 30

            reasons.append(
                f'{asset["asset"]} outside room'
            )

    # --------------------------------------------------------
    # FURNITURE COLLISIONS
    # --------------------------------------------------------

    collision_count = 0

    for i in range(len(assets)):

        for j in range(
            i + 1,
            len(assets)
        ):

            asset_a = assets[i]
            asset_b = assets[j]

            if assets_overlap(
                asset_a,
                asset_b
            ):

                collision_count += 1

                reasons.append(
                    f'{asset_a["asset"]} overlaps '
                    f'{asset_b["asset"]}'
                )

    if collision_count > 0:

        score -= (
            collision_count * 25
        )

    # --------------------------------------------------------
    # WALL CLEARANCE
    # --------------------------------------------------------

    for asset in assets:

        clearance = wall_clearance(
            asset,
            room_width,
            room_length
        )

        if clearance < 0:

            # Already outside room.
            continue

        elif clearance < MIN_WALL_CLEARANCE:

            score -= 10

            reasons.append(
                f'{asset["asset"]} too close to wall'
            )

        elif clearance < IDEAL_WALL_CLEARANCE:

            score -= 3

    # --------------------------------------------------------
    # CENTER BALANCE
    # --------------------------------------------------------

    for asset in assets:

        distance = center_distance(
            asset
        )

        if distance > IDEAL_CENTER_DISTANCE:

            score -= 2

    # --------------------------------------------------------
    # FINAL SCORE
    # --------------------------------------------------------

    score = max(
        0.0,
        min(
            100.0,
            round(score, 2)
        )
    )

    return {
        "score": score,
        "reasons": reasons
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("DAY 14 - LAYOUT SCORING TEST")
    print("=" * 60)

    room_width = 5.5
    room_length = 5.0

    # --------------------------------------------------------
    # TEST LAYOUT
    # --------------------------------------------------------

    assets = [

        {
            "asset": "Sofa_Modern",
            "position": [0, 1.20, 0],
            "rotation": [0, 0, 0],
            "scale": [1, 1, 1]
        },

        {
            "asset": "CoffeeTable_Modern",
            "position": [0, 0.00, 0],
            "rotation": [0, 0, 0],
            "scale": [1, 1, 1]
        },

        {
            "asset": "TVUnit_Wood",
            "position": [0, -1.20, 0],
            "rotation": [0, 0, 0],
            "scale": [1, 1, 1]
        }
    ]

    # --------------------------------------------------------
    # SCORE
    # --------------------------------------------------------

    result = score_layout(
        assets,
        room_width,
        room_length
    )

    print("\nLAYOUT SCORE")

    print(
        "Score:",
        result["score"]
    )

    print(
        "\nReasons:"
    )

    if result["reasons"]:

        for reason in result["reasons"]:

            print(
                "-",
                reason
            )

    else:

        print(
            "None"
        )

    print("\n" + "=" * 60)