import math
from copy import deepcopy

from api.asset_dimensions import get_asset_dimensions


# ============================================================
# SETTINGS
# ============================================================

MIN_CLEARANCE = 0.10
WALL_CLEARANCE = 0.08

MAX_FIX_PASSES = 8

# Candidate movement distances
MOVE_STEPS = [
    0.10,
    0.20,
    0.30,
    0.40,
    0.50,
    0.60,
    0.75,
    1.00,
    1.25,
    1.50,
    2.00
]


# ============================================================
# DIMENSIONS
# ============================================================

def get_scaled_dimensions(asset):

    dimensions = get_asset_dimensions(
        asset["asset"]
    )

    scale = asset.get(
        "scale",
        [1.0, 1.0, 1.0]
    )

    return {
        "width":
            dimensions["width"]
            * abs(scale[0]),

        "depth":
            dimensions["depth"]
            * abs(scale[1]),

        "height":
            dimensions["height"]
            * abs(scale[2])
    }


# ============================================================
# ROTATION
# ============================================================

def get_rotation_z(asset):

    rotation = asset.get(
        "rotation",
        [0, 0, 0]
    )

    return math.radians(
        rotation[2]
    )


# ============================================================
# ROTATION-AWARE FOOTPRINT
# ============================================================

def get_rotated_footprint(asset):

    dimensions = get_scaled_dimensions(
        asset
    )

    width = dimensions["width"]
    depth = dimensions["depth"]

    angle = get_rotation_z(
        asset
    )

    cos_a = abs(
        math.cos(angle)
    )

    sin_a = abs(
        math.sin(angle)
    )

    world_width = (
        width * cos_a
        +
        depth * sin_a
    )

    world_depth = (
        width * sin_a
        +
        depth * cos_a
    )

    return (
        world_width,
        world_depth
    )


# ============================================================
# CENTER
# ============================================================

def get_asset_center(asset):

    position = asset.get(
        "position",
        [0, 0, 0]
    )

    return (
        position[0],
        position[1]
    )


# ============================================================
# BOUNDS
# ============================================================

def get_asset_bounds(asset):

    width, depth = get_rotated_footprint(
        asset
    )

    center_x, center_y = get_asset_center(
        asset
    )

    half_width = width / 2
    half_depth = depth / 2

    return {
        "min_x":
            center_x - half_width,

        "max_x":
            center_x + half_width,

        "min_y":
            center_y - half_depth,

        "max_y":
            center_y + half_depth
    }


# ============================================================
# ROOM CHECK
# ============================================================

def check_inside_room(
    asset,
    room_width,
    room_length
):

    bounds = get_asset_bounds(
        asset
    )

    half_room_width = room_width / 2
    half_room_length = room_length / 2

    return (
        bounds["min_x"]
        >=
        -half_room_width
        +
        WALL_CLEARANCE

        and

        bounds["max_x"]
        <=
        half_room_width
        -
        WALL_CLEARANCE

        and

        bounds["min_y"]
        >=
        -half_room_length
        +
        WALL_CLEARANCE

        and

        bounds["max_y"]
        <=
        half_room_length
        -
        WALL_CLEARANCE
    )


# ============================================================
# COLLISION
# ============================================================

def check_overlap(
    asset_a,
    asset_b
):

    a = get_asset_bounds(
        asset_a
    )

    b = get_asset_bounds(
        asset_b
    )

    separated_x = (
        a["max_x"]
        +
        MIN_CLEARANCE
        <=
        b["min_x"]

        or

        b["max_x"]
        +
        MIN_CLEARANCE
        <=
        a["min_x"]
    )

    separated_y = (
        a["max_y"]
        +
        MIN_CLEARANCE
        <=
        b["min_y"]

        or

        b["max_y"]
        +
        MIN_CLEARANCE
        <=
        a["min_y"]
    )

    return not (
        separated_x
        or
        separated_y
    )


# ============================================================
# CHECK AGAINST ALL OTHER ASSETS
# ============================================================

def has_collision_with_others(
    candidate,
    assets,
    ignored_asset
):

    for other in assets:

        if other is ignored_asset:
            continue

        if other is candidate:
            continue

        if check_overlap(
            candidate,
            other
        ):
            return True

    return False


# ============================================================
# MOVE INSIDE ROOM
# ============================================================

def move_inside_room(
    asset,
    room_width,
    room_length
):

    width, depth = get_rotated_footprint(
        asset
    )

    half_room_width = room_width / 2
    half_room_length = room_length / 2

    half_width = width / 2
    half_depth = depth / 2

    position = asset.setdefault(
        "position",
        [0, 0, 0]
    )

    old_position = position.copy()

    min_x = (
        -half_room_width
        +
        WALL_CLEARANCE
        +
        half_width
    )

    max_x = (
        half_room_width
        -
        WALL_CLEARANCE
        -
        half_width
    )

    min_y = (
        -half_room_length
        +
        WALL_CLEARANCE
        +
        half_depth
    )

    max_y = (
        half_room_length
        -
        WALL_CLEARANCE
        -
        half_depth
    )

    # If the asset itself cannot fit.
    if min_x > max_x or min_y > max_y:

        return False

    position[0] = max(
        min_x,
        min(
            max_x,
            position[0]
        )
    )

    position[1] = max(
        min_y,
        min(
            max_y,
            position[1]
        )
    )

    return (
        old_position[0]
        !=
        position[0]

        or

        old_position[1]
        !=
        position[1]
    )


# ============================================================
# TEST CANDIDATE
# ============================================================

def test_candidate_position(
    asset,
    new_x,
    new_y,
    assets,
    room_width,
    room_length
):

    candidate = deepcopy(
        asset
    )

    candidate["position"] = [
        new_x,
        new_y,
        asset["position"][2]
    ]

    # Must stay inside room.
    if not check_inside_room(
        candidate,
        room_width,
        room_length
    ):
        return False

    # Must not collide with anything.
    for other in assets:

        if other is asset:
            continue

        if check_overlap(
            candidate,
            other
        ):
            return False

    return True


# ============================================================
# RESOLVE COLLISION
# ============================================================

def resolve_overlap(
    asset,
    obstacle,
    assets,
    room_width,
    room_length
):

    current_x = asset["position"][0]
    current_y = asset["position"][1]

    obstacle_x = obstacle["position"][0]
    obstacle_y = obstacle["position"][1]

    # --------------------------------------------------------
    # Direction from obstacle toward asset
    # --------------------------------------------------------

    dx = current_x - obstacle_x
    dy = current_y - obstacle_y

    # If same center, prefer moving vertically.
    if abs(dx) < 0.001 and abs(dy) < 0.001:

        dx = 0
        dy = 1

    # Normalize direction.
    length = math.sqrt(
        dx * dx
        +
        dy * dy
    )

    if length > 0:

        dx /= length
        dy /= length

    # --------------------------------------------------------
    # Candidate directions
    # --------------------------------------------------------

    directions = [

        ("away_from_obstacle", dx, dy),

        ("right", 1, 0),

        ("left", -1, 0),

        ("front", 0, 1),

        ("back", 0, -1)
    ]

    # --------------------------------------------------------
    # Try different movement distances
    # --------------------------------------------------------

    for direction_name, dir_x, dir_y in directions:

        for distance in MOVE_STEPS:

            new_x = (
                current_x
                +
                dir_x * distance
            )

            new_y = (
                current_y
                +
                dir_y * distance
            )

            if test_candidate_position(
                asset,
                new_x,
                new_y,
                assets,
                room_width,
                room_length
            ):

                asset["position"] = [
                    new_x,
                    new_y,
                    asset["position"][2]
                ]

                return {
                    "success": True,
                    "direction": direction_name,
                    "distance": round(
                        distance,
                        3
                    )
                }

    # --------------------------------------------------------
    # No solution
    # --------------------------------------------------------

    return {
        "success": False,
        "direction": None,
        "distance": None
    }


# ============================================================
# VALIDATE LAYOUT
# ============================================================

def validate_layout(
    assets,
    room_width,
    room_length
):

    warnings = []
    adjustments = []

    # ========================================================
    # PASS 1
    # Keep every asset inside room
    # ========================================================

    for asset in assets:

        if not check_inside_room(
            asset,
            room_width,
            room_length
        ):

            old_position = asset[
                "position"
            ].copy()

            changed = move_inside_room(
                asset,
                room_width,
                room_length
            )

            if changed:

                adjustments.append({
                    "asset":
                        asset["asset"],

                    "type":
                        "room_boundary",

                    "from":
                        old_position,

                    "to":
                        asset[
                            "position"
                        ].copy()
                })

            else:

                warnings.append(
                    f'{asset["asset"]} '
                    f'cannot fit inside room.'
                )

    # ========================================================
    # PASS 2
    # Resolve collisions
    # ========================================================

    for pass_number in range(
        MAX_FIX_PASSES
    ):

        collision_found = False

        for i in range(
            len(assets)
        ):

            for j in range(
                i + 1,
                len(assets)
            ):

                asset_a = assets[i]
                asset_b = assets[j]

                if not check_overlap(
                    asset_a,
                    asset_b
                ):
                    continue

                collision_found = True

                # Try moving A first.
                result = resolve_overlap(
                    asset_a,
                    asset_b,
                    assets,
                    room_width,
                    room_length
                )

                if result["success"]:

                    adjustments.append({
                        "asset":
                            asset_a["asset"],

                        "type":
                            "collision",

                        "obstacle":
                            asset_b["asset"],

                        "direction":
                            result[
                                "direction"
                            ],

                        "distance":
                            result[
                                "distance"
                            ],

                        "pass":
                            pass_number + 1
                    })

                    continue

                # If A cannot move,
                # try moving B.
                result = resolve_overlap(
                    asset_b,
                    asset_a,
                    assets,
                    room_width,
                    room_length
                )

                if result["success"]:

                    adjustments.append({
                        "asset":
                            asset_b["asset"],

                        "type":
                            "collision",

                        "obstacle":
                            asset_a["asset"],

                        "direction":
                            result[
                                "direction"
                            ],

                        "distance":
                            result[
                                "distance"
                            ],

                        "pass":
                            pass_number + 1
                    })

                    continue

                # Neither can move.
                warnings.append(
                    f'Could not resolve collision '
                    f'between '
                    f'{asset_a["asset"]} '
                    f'and '
                    f'{asset_b["asset"]}.'
                )

        if not collision_found:
            break

    # ========================================================
    # FINAL VALIDATION
    # ========================================================

    final_valid = True

    # Room boundaries.
    for asset in assets:

        if not check_inside_room(
            asset,
            room_width,
            room_length
        ):

            final_valid = False

            warnings.append(
                f'{asset["asset"]} remains '
                f'outside room boundary.'
            )

    # Final collisions.
    for i in range(
        len(assets)
    ):

        for j in range(
            i + 1,
            len(assets)
        ):

            if check_overlap(
                assets[i],
                assets[j]
            ):

                final_valid = False

                message = (
                    f'Final collision: '
                    f'{assets[i]["asset"]} '
                    f'with '
                    f'{assets[j]["asset"]}.'
                )

                # Avoid duplicate warnings.
                if message not in warnings:

                    warnings.append(
                        message
                    )

    return {
        "valid":
            final_valid,

        "adjustments":
            adjustments,

        "warnings":
            warnings
    }


# ============================================================
# PUBLIC API
# ============================================================

def validate_and_fix_layout(
    assets,
    room_width,
    room_length
):

    validated_assets = deepcopy(
        assets
    )

    validation = validate_layout(
        validated_assets,
        room_width,
        room_length
    )

    return (
        validated_assets,
        validation
    )


# ============================================================
# TEST
# ============================================================

def test_rotation_collision():

    print("\n")
    print("=" * 65)
    print("DAY 13 - PART 9")
    print("ROTATION-AWARE COLLISION TEST")
    print("=" * 65)
    room_width = 5.5
    room_length = 5.0

    assets = [

        {
            "asset": "Sofa_Modern",
            "position": [0, 1.5, 0],
            "rotation": [0, 0, 35],
            "scale": [1, 1, 1]
        },

        {
            "asset": "CoffeeTable_Modern",
            "position": [0, 0.0, 0],
            "rotation": [0, 0, 20],
            "scale": [1, 1, 1]
        },

        {
            "asset": "TVUnit_Wood",
            "position": [0, -1.8, 0],
            "rotation": [0, 0, 0],
            "scale": [1, 1, 1]
        }
    ]
    # ========================================================
    # INITIAL
    # ========================================================

    print("\nINITIAL ASSETS")

    for asset in assets:

        print(
            f'{asset["asset"]}: '
            f'position='
            f'{asset["position"]} '
            f'rotation='
            f'{asset["rotation"][2]}°'
        )

        width, depth = (
            get_rotated_footprint(
                asset
            )
        )

        print(
            f"  Rotated footprint: "
            f"{width:.3f}m × "
            f"{depth:.3f}m"
        )

    # ========================================================
    # VALIDATE
    # ========================================================

    validated_assets, validation = (
        validate_and_fix_layout(
            assets,
            room_width,
            room_length
        )
    )

    # ========================================================
    # RESULTS
    # ========================================================

    print("\nFINAL POSITIONS")

    for asset in validated_assets:

        print(
            f'{asset["asset"]}: '
            f'{asset["position"]}'
        )

    print("\nVALIDATION")

    print(
        f'Valid       : '
        f'{validation["valid"]}'
    )

    print(
        f'Adjustments : '
        f'{len(validation["adjustments"])}'
    )

    print(
        f'Warnings    : '
        f'{len(validation["warnings"])}'
    )

    if validation["adjustments"]:

        print("\nADJUSTMENTS")

        for adjustment in validation[
            "adjustments"
        ]:

            print(
                adjustment
            )

    if validation["warnings"]:

        print("\nWARNINGS")

        for warning in validation[
            "warnings"
        ]:

            print(
                "WARNING:",
                warning
            )

    print("\n")

    if validation["valid"]:

        print(
            "ROTATION-AWARE "
            "VALIDATION: SUCCESS"
        )

    else:

        print(
            "ROTATION-AWARE "
            "VALIDATION: NEEDS REVIEW"
        )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    test_rotation_collision()