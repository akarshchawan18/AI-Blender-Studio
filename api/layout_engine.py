import math

from api.asset_dimensions import get_asset_dimensions

from api.architectural_rules import (
    get_default_architecture,
    validate_architecture
)
from api.space_rules import validate_space_rules
# ============================================================
# FOOTPRINT HELPER
# ============================================================

def get_footprint(asset):
    """
    Returns the world-space width and depth
    of an asset, taking scale and Z rotation
    into account.
    """

    dimensions = get_asset_dimensions(
        asset["asset"]
    )

    width = dimensions["width"]
    depth = dimensions["depth"]

    scale = asset.get(
        "scale",
        [1, 1, 1]
    )

    rotation = asset.get(
        "rotation",
        [0, 0, 0]
    )

    width *= float(scale[0])
    depth *= float(scale[1])

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
        width * cos_r +
        depth * sin_r
    )

    world_depth = (
        width * sin_r +
        depth * cos_r
    )

    return world_width, world_depth
# =========================================================
# ASSET CREATOR
# =========================================================

def create_asset(
    name,
    position,
    rotation=(0, 0, 0),
    scale=(1, 1, 1)
):
    return {
        "asset": name,
        "position": list(position),
        "rotation": list(rotation),
        "scale": list(scale)
    }


# =========================================================
# ROOM UTILITIES
# =========================================================

def room_limits(room_width, room_length, clearance=0.15):
    """
    Returns usable room boundaries.

    Room origin is assumed to be at the center.
    """

    return {
        "min_x": -room_width / 2 + clearance,
        "max_x": room_width / 2 - clearance,
        "min_y": -room_length / 2 + clearance,
        "max_y": room_length / 2 - clearance
    }


def asset_footprint(asset):
    """
    Returns the rotated world-space footprint
    of an asset as (width, depth).

    Takes into account:
    - asset dimensions
    - X/Y scale
    - Z rotation
    """

    name = asset["asset"]

    dimensions = get_asset_dimensions(name)

    # Safe scale values
    scale = asset.get("scale", [1.0, 1.0, 1.0])

    scale_x = float(scale[0])
    scale_y = float(scale[1])

    width = dimensions["width"] * scale_x
    depth = dimensions["depth"] * scale_y

    # Safe Z rotation
    rotation = asset.get("rotation", [0.0, 0.0, 0.0])

    rotation_z = math.radians(float(rotation[2]))

    cos_r = abs(math.cos(rotation_z))
    sin_r = abs(math.sin(rotation_z))

    # Rotated AABB footprint
    world_width = (
        width * cos_r +
        depth * sin_r
    )

    world_depth = (
        width * sin_r +
        depth * cos_r
    )

    return world_width, world_depth
# =========================================================
# CHECK WHETHER ASSET FITS INSIDE ROOM
# =========================================================

def fits_inside_room(
    asset,
    room_width,
    room_length,
    clearance=0.10
):
    width, depth = asset_footprint(asset)

    x = asset["position"][0]
    y = asset["position"][1]

    half_width = width / 2
    half_depth = depth / 2

    return (
        x - half_width >= -room_width / 2 + clearance
        and
        x + half_width <= room_width / 2 - clearance
        and
        y - half_depth >= -room_length / 2 + clearance
        and
        y + half_depth <= room_length / 2 - clearance
    )


# =========================================================
# COLLISION CHECK
# =========================================================

def assets_overlap(
    asset_a,
    asset_b,
    clearance=0.10
):
    width_a, depth_a = asset_footprint(asset_a)
    width_b, depth_b = asset_footprint(asset_b)

    ax = asset_a["position"][0]
    ay = asset_a["position"][1]

    bx = asset_b["position"][0]
    by = asset_b["position"][1]

    horizontal_distance = abs(ax - bx)
    vertical_distance = abs(ay - by)

    required_x = (width_a + width_b) / 2 + clearance
    required_y = (depth_a + depth_b) / 2 + clearance

    return (
        horizontal_distance < required_x
        and
        vertical_distance < required_y
    )


# =========================================================
# CHECK ENTIRE LAYOUT
# =========================================================

def layout_is_valid(
    assets,
    room_width,
    room_length
):
    for asset in assets:

        if not fits_inside_room(
            asset,
            room_width,
            room_length
        ):
            return False

    for i in range(len(assets)):

        for j in range(i + 1, len(assets)):

            if assets_overlap(
                assets[i],
                assets[j]
            ):
                return False

    return True


# =========================================================
# BEST POSITION SEARCH
# =========================================================

def find_best_position(
    asset,
    existing_assets,
    room_width,
    room_length
):
    """
    Search multiple candidate positions and choose
    the first position that satisfies all constraints.
    """

    original_x = asset["position"][0]
    original_y = asset["position"][1]

    candidates = [

        # Center
        (0, 0),

        # Back wall
        (0, room_length * 0.35),

        # Front wall
        (0, -room_length * 0.35),

        # Left side
        (-room_width * 0.30, 0),

        # Right side
        (room_width * 0.30, 0),

        # Corners
        (-room_width * 0.30, room_length * 0.30),
        (room_width * 0.30, room_length * 0.30),

        (-room_width * 0.30, -room_length * 0.30),
        (room_width * 0.30, -room_length * 0.30),

        # Additional center positions
        (0, room_length * 0.15),
        (0, -room_length * 0.15),
        (room_width * 0.20, 0),
        (-room_width * 0.20, 0),
    ]

    best_position = None
    best_score = float("inf")

    for x, y in candidates:

        candidate = dict(asset)

        candidate["position"] = [
            x,
            y,
            asset["position"][2]
        ]

        if not fits_inside_room(
            candidate,
            room_width,
            room_length
        ):
            continue

        collision = False

        for other in existing_assets:

            if assets_overlap(
                candidate,
                other
            ):
                collision = True
                break

        if collision:
            continue

        # Prefer positions close to original position
        distance = math.sqrt(
            (x - original_x) ** 2 +
            (y - original_y) ** 2
        )

        if distance < best_score:

            best_score = distance
            best_position = candidate["position"]

    return best_position


# =========================================================
# SMART LIVING ROOM
# =========================================================

def smart_living_room_layout(
    room_width,
    room_length
):
    assets = []

    # -----------------------------------------------------
    # SOFA
    # -----------------------------------------------------

    sofa = create_asset(
        "Sofa_Modern",
        [0, room_length * 0.22, 0],
        [0, 0, 0],
        [1, 1, 1]
    )

    assets.append(sofa)

    # -----------------------------------------------------
    # TV UNIT
    # -----------------------------------------------------

    tv = create_asset(
        "TVUnit_Wood",
        [0, -room_length * 0.32, 0],
        [0, 0, 0],
        [1, 1, 1]
    )

    assets.append(tv)

    # -----------------------------------------------------
    # COFFEE TABLE
    # -----------------------------------------------------

    table = create_asset(
        "CoffeeTable_Modern",
        [0, -room_length * 0.05, 0],
        [0, 0, 0],
        [1, 1, 1]
    )

    assets.append(table)

    return assets


# =========================================================
# SMART BEDROOM
# =========================================================

def smart_bedroom_layout(
    room_width,
    room_length
):
    assets = []

    bed = create_asset(
        "Bed_Modern",
        [0, room_length * 0.12, 0],
        [0, 0, 0],
        [1, 1, 1]
    )

    assets.append(bed)

    wardrobe = create_asset(
        "Wardrobe_Modern",
        [
            room_width * 0.30,
            -room_length * 0.28,
            0
        ],
        [0, 0, 0],
        [1, 1, 1]
    )

    assets.append(wardrobe)

    lamp = create_asset(
        "Lamp_Modern",
        [
            -room_width * 0.30,
            room_length * 0.10,
            0
        ],
        [0, 0, 0],
        [1, 1, 1]
    )

    assets.append(lamp)

    return assets


# =========================================================
# SMART OFFICE
# =========================================================

def smart_office_layout(
    room_width,
    room_length
):
    assets = []

    desk = create_asset(
        "Desk_Modern",
        [0, room_length * 0.20, 0],
        [0, 0, 0],
        [1, 1, 1]
    )

    assets.append(desk)

    chair = create_asset(
        "Chair_Modern",
        [0, -room_length * 0.02, 0],
        [0, 0, 0],
        [1, 1, 1]
    )

    assets.append(chair)

    lamp = create_asset(
        "Lamp_Modern",
        [
            room_width * 0.30,
            room_length * 0.20,
            0
        ],
        [0, 0, 0],
        [1, 1, 1]
    )

    assets.append(lamp)

    return assets


# =========================================================
# SMART DINING ROOM
# =========================================================

def smart_dining_room_layout(
    room_width,
    room_length
):
    assets = []

    table = create_asset(
        "DiningTable_Modern",
        [0, 0, 0],
        [0, 0, 0],
        [1, 1, 1]
    )

    assets.append(table)

    chair_positions = [
        [0, 1.35, 0],
        [0, -1.35, 0],
        [1.65, 0, 0],
        [-1.65, 0, 0]
    ]

    chair_rotations = [
        [0, 0, 0],
        [0, 0, 180],
        [0, 0, 90],
        [0, 0, -90]
    ]

    for position, rotation in zip(
        chair_positions,
        chair_rotations
    ):

        assets.append(
            create_asset(
                "Chair_Modern",
                position,
                rotation,
                [1, 1, 1]
            )
        )

    lamp = create_asset(
        "Lamp_Modern",
        [0, 0, 0],
        [0, 0, 0],
        [1, 1, 1]
    )

    assets.append(lamp)

    return assets


# =========================================================
# SMART LAYOUT GENERATOR
# =========================================================

def generate_layout(
    room_type,
    room_width,
    room_length
):

    if room_type == "bedroom":

        return smart_bedroom_layout(
            room_width,
            room_length
        )

    elif room_type == "office":

        return smart_office_layout(
            room_width,
            room_length
        )

    elif room_type == "dining_room":

        return smart_dining_room_layout(
            room_width,
            room_length
        )

    else:

        return smart_living_room_layout(
            room_width,
            room_length
        )


# =========================================================
# SMART VALIDATION + REPOSITIONING
# =========================================================

def optimize_layout(
    assets,
    room_width,
    room_length
):

    optimized = []

    adjustments = []

    for asset in assets:

        best_position = find_best_position(
            asset,
            optimized,
            room_width,
            room_length
        )

        if best_position is None:

            optimized.append(asset)

            adjustments.append({
                "asset": asset["asset"],
                "status": "needs_review",
                "reason": "No collision-free position found"
            })

            continue

        original_position = asset["position"]

        if original_position != best_position:

            asset["position"] = best_position

            adjustments.append({
                "asset": asset["asset"],
                "status": "repositioned",
                "from": original_position,
                "to": best_position
            })

        optimized.append(asset)

    return optimized, adjustments


# =========================================================
# MAIN SMART ENGINE
# =========================================================
# =========================================================
# SPACE-RULE OPTIMIZER
# =========================================================

def optimize_space_rules(
    assets,
    room_width,
    room_length
):
    """
    Automatically moves furniture that blocks
    the entrance.

    Returns:
        optimized_assets
        adjustments
        warnings
    """

    adjustments = []
    warnings = []

    # -----------------------------------------------------
    # Check current layout
    # -----------------------------------------------------

    result = validate_space_rules(
        assets,
        room_width,
        room_length
    )

    # Already valid
    if result["valid"]:
        return assets, adjustments, warnings

    # -----------------------------------------------------
    # Try moving problematic assets
    # -----------------------------------------------------

    for warning in result["warnings"]:

        # Example:
        # "TVUnit_Wood blocks the entrance."

        asset_name = warning.split(
            " blocks"
        )[0]

        target_asset = None

        for asset in assets:

            if asset["asset"] == asset_name:

                target_asset = asset
                break

        if target_asset is None:
            continue

        original_position = list(
            target_asset["position"]
        )

        original_rotation = list(
            target_asset["rotation"]
        )

        # -------------------------------------------------
        # Candidate positions
        # -------------------------------------------------

        candidates = [

            # Move backward
            [
                original_position[0],
                original_position[1] + 0.50,
                original_position[2]
            ],

            [
                original_position[0],
                original_position[1] + 0.75,
                original_position[2]
            ],

            [
                original_position[0],
                original_position[1] + 1.00,
                original_position[2]
            ],

            # Move left
            [
                original_position[0] - 0.75,
                original_position[1],
                original_position[2]
            ],

            # Move right
            [
                original_position[0] + 0.75,
                original_position[1],
                original_position[2]
            ]
        ]

        found_position = None

        # -------------------------------------------------
        # Test candidates
        # -------------------------------------------------

        for candidate in candidates:

            target_asset["position"] = candidate

            # First check overall room boundaries
            width, depth = get_footprint(
                target_asset
            )

            x = candidate[0]
            y = candidate[1]

            inside_room = (
                x - width / 2 >= -room_width / 2
                and
                x + width / 2 <= room_width / 2
                and
                y - depth / 2 >= -room_length / 2
                and
                y + depth / 2 <= room_length / 2
            )

            if not inside_room:
                continue

            # -------------------------------------------------
            # Check collision with other furniture
            # -------------------------------------------------

            collision = False

            for other in assets:

                if other is target_asset:
                    continue

                if assets_overlap(
                    target_asset,
                    other
                ):

                    collision = True
                    break

            if collision:
                continue

            # -------------------------------------------------
            # Check entrance again
            # -------------------------------------------------

            space_result = validate_space_rules(
                assets,
                room_width,
                room_length
            )

            if space_result["valid"]:

                found_position = list(candidate)
                break

        # -------------------------------------------------
        # Candidate found
        # -------------------------------------------------

        if found_position is not None:

            target_asset["position"] = found_position

            adjustments.append({
                "asset": asset_name,
                "status": "moved_for_entrance_clearance",
                "from": original_position,
                "to": found_position
            })

        else:

            # Restore original position
            target_asset["position"] = original_position

            warnings.append(
                f"Could not clear entrance for {asset_name}."
            )

            # Restore rotation too
            target_asset["rotation"] = original_rotation

    # -----------------------------------------------------
    # Final validation
    # -----------------------------------------------------

    final_result = validate_space_rules(
        assets,
        room_width,
        room_length
    )

    warnings.extend(
        final_result["warnings"]
    )

    return assets, adjustments, warnings
# =========================================================
# SMART LAYOUT GENERATOR
def optimize_architecture(
        assets,
        room_width,
        room_length
):
    """
    Repositions furniture to avoid doors and windows.

    Uses a larger candidate search so the optimizer
    can find a valid architectural layout.
    """

    architecture = get_default_architecture(
        room_width,
        room_length
    )

    adjustments = []
    warnings = []

    # --------------------------------------------------------
    # Initial architectural validation
    # --------------------------------------------------------

    initial_result = validate_architecture(
        assets,
        room_width,
        room_length,
        architecture
    )

    if initial_result["valid"]:
        return assets, adjustments, warnings

    # --------------------------------------------------------
    # Process each obstruction
    # --------------------------------------------------------

    for warning in initial_result["warnings"]:

        if " blocks the door." in warning:

            asset_name = warning.split(
                " blocks the door."
            )[0]

        elif " blocks the window." in warning:

            asset_name = warning.split(
                " blocks the window."
            )[0]

        else:
            continue

        # ----------------------------------------------------
        # Find blocked asset
        # ----------------------------------------------------

        target_asset = None

        for asset in assets:

            if asset["asset"] == asset_name:
                target_asset = asset
                break

        if target_asset is None:
            continue

        original_position = list(
            target_asset["position"]
        )

        # ----------------------------------------------------
        # Generate many candidate positions
        # ----------------------------------------------------

        candidate_offsets = [
            # Forward / backward
            (0.00, 0.25),
            (0.00, 0.50),
            (0.00, 0.75),
            (0.00, 1.00),
            (0.00, 1.25),
            (0.00, 1.50),
            (0.00, 1.75),
            (0.00, 2.00),

            # Left
            (-0.25, 0.00),
            (-0.50, 0.00),
            (-0.75, 0.00),
            (-1.00, 0.00),
            (-1.25, 0.00),
            (-1.50, 0.00),
            (-1.75, 0.00),
            (-2.00, 0.00),

            # Right
            (0.25, 0.00),
            (0.50, 0.00),
            (0.75, 0.00),
            (1.00, 0.00),
            (1.25, 0.00),
            (1.50, 0.00),
            (1.75, 0.00),
            (2.00, 0.00),

            # Diagonal
            (-0.50, 0.50),
            (0.50, 0.50),
            (-0.75, 0.75),
            (0.75, 0.75),
            (-1.00, 1.00),
            (1.00, 1.00),
            (-1.50, 1.00),
            (1.50, 1.00)
        ]

        found_position = None

        # ----------------------------------------------------
        # Try every candidate
        # ----------------------------------------------------

        for offset_x, offset_y in candidate_offsets:

            candidate = [
                original_position[0] + offset_x,
                original_position[1] + offset_y,
                original_position[2]
            ]

            target_asset["position"] = candidate

            # ------------------------------------------------
            # Check room boundaries
            # ------------------------------------------------

            width, depth = asset_footprint(
                target_asset
            )

            x = candidate[0]
            y = candidate[1]

            inside_room = (
                    x - width / 2 >= -room_width / 2
                    and
                    x + width / 2 <= room_width / 2
                    and
                    y - depth / 2 >= -room_length / 2
                    and
                    y + depth / 2 <= room_length / 2
            )

            if not inside_room:
                continue

            # ------------------------------------------------
            # Check furniture collision
            # ------------------------------------------------

            collision = False

            for other in assets:

                if other is target_asset:
                    continue

                if assets_overlap(
                        target_asset,
                        other
                ):
                    collision = True
                    break

            if collision:
                continue

            # ------------------------------------------------
            # Check architectural rules
            # ------------------------------------------------

            architecture_result = validate_architecture(
                assets,
                room_width,
                room_length,
                architecture
            )

            if architecture_result["valid"]:
                found_position = list(candidate)
                break

        # ----------------------------------------------------
        # Candidate found
        # ----------------------------------------------------

        if found_position is not None:

            target_asset["position"] = found_position

            adjustments.append({
                "asset": asset_name,
                "status": "moved_for_architecture",
                "from": original_position,
                "to": found_position
            })

        # ----------------------------------------------------
        # No candidate found
        # ----------------------------------------------------

        else:

            target_asset["position"] = original_position

            warnings.append(
                f"Could not clear architectural obstruction "
                f"for {asset_name}."
            )

    # --------------------------------------------------------
    # Final validation
    # --------------------------------------------------------

    final_result = validate_architecture(
        assets,
        room_width,
        room_length,
        architecture
    )

    warnings.extend(
        final_result["warnings"]
    )

    return assets, adjustments, warnings


# =========================================================
def generate_smart_layout(
    room_type,
    room_width,
    room_length
):
    """
    Complete intelligent room layout pipeline.

    Order:

    1. Generate room-specific layout
    2. Optimize furniture collisions
    3. Optimize entrance/space rules
    4. Optimize doors/windows
    5. Final validation
    """

    # --------------------------------------------------------
    # STEP 1
    # Generate initial layout
    # --------------------------------------------------------

    assets = generate_layout(
        room_type,
        room_width,
        room_length
    )

    # --------------------------------------------------------
    # STEP 2
    # Furniture collision optimization
    # --------------------------------------------------------

    assets, layout_adjustments = optimize_layout(
        assets,
        room_width,
        room_length
    )

    # --------------------------------------------------------
    # STEP 3
    # Entrance / space rules
    # --------------------------------------------------------

    assets, space_adjustments, space_warnings = (
        optimize_space_rules(
            assets,
            room_width,
            room_length
        )
    )

    # --------------------------------------------------------
    # STEP 4
    # Door / window architecture
    # --------------------------------------------------------

    assets, architecture_adjustments, architecture_warnings = (
        optimize_architecture(
            assets,
            room_width,
            room_length
        )
    )

    # --------------------------------------------------------
    # STEP 5
    # Final collision validation
    # --------------------------------------------------------

    valid = layout_is_valid(
        assets,
        room_width,
        room_length
    )

    # --------------------------------------------------------
    # Combine adjustments
    # --------------------------------------------------------

    adjustments = (
        layout_adjustments
        + space_adjustments
        + architecture_adjustments
    )

    # --------------------------------------------------------
    # Combine warnings
    # --------------------------------------------------------

    warnings = (
        space_warnings
        + architecture_warnings
    )

    validation = {
        "valid": (
            valid
            and len(warnings) == 0
        ),
        "adjustments": adjustments,
        "warnings": warnings
    }

    return assets, validation
# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("DAY 14 SMART LAYOUT ENGINE TEST")
    print("=" * 60)

    room_width = 5.5
    room_length = 5.0

    assets, validation = generate_smart_layout(
        "living_room",
        room_width,
        room_length
    )

    print()
    print("ROOM")
    print("Width :", room_width)
    print("Length:", room_length)

    print()
    print("ASSETS")

    for asset in assets:

        print(
            f"{asset['asset']:25}"
            f" Position: {asset['position']}"
        )

    print()
    print("VALIDATION")
    print("Valid       :", validation["valid"])
    print(
        "Adjustments:",
        len(validation["adjustments"])
    )
    print(
        "Warnings   :",
        len(validation["warnings"])
    )

    for adjustment in validation["adjustments"]:

        print(
            "ADJUSTMENT:",
            adjustment
        )

    for warning in validation["warnings"]:

        print(
            "WARNING:",
            warning
        )

    print()
    print("=" * 60)