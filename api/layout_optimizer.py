"""
DAY 15 - NATURAL LANGUAGE DESIGN INTELLIGENCE

Generates multiple candidate layouts,
applies natural-language design intent,
validates them, scores them,
and selects the highest-scoring layout.

Also preserves the original Day 14 find_best_layout()
function so existing main.py code continues to work.

DAY 18:
Adds optional architectural validation.
"""

import copy
import math

from api.architectural_rules import validate_architecture

from api.layout_engine import (
    generate_layout,
    optimize_layout,
    optimize_space_rules,
    optimize_architecture,
    layout_is_valid,
    find_best_position
)

from api.layout_score import score_layout

from api.design_layout_adapter import (
    create_layout_instructions
)


# ============================================================
# DAY 14 — GENERATE NORMAL CANDIDATE
# ============================================================

def create_candidate(
    room_type,
    room_width,
    room_length,
    variation
):
    """
    Creates one normal Day 14 candidate layout.
    """

    assets = generate_layout(
        room_type,
        room_width,
        room_length
    )

    # --------------------------------------------------------
    # Variation
    # --------------------------------------------------------

    if variation == 1:

        for asset in assets:

            if asset["asset"] == "Sofa_Modern":
                asset["position"][1] += 0.30

            elif asset["asset"] == "CoffeeTable_Modern":
                asset["position"][1] += 0.15

    elif variation == 2:

        for asset in assets:

            if asset["asset"] == "Sofa_Modern":
                asset["position"][0] -= 0.50

            elif asset["asset"] == "CoffeeTable_Modern":
                asset["position"][0] -= 0.30

    elif variation == 3:

        for asset in assets:

            if asset["asset"] == "Sofa_Modern":
                asset["position"][0] += 0.50

            elif asset["asset"] == "CoffeeTable_Modern":
                asset["position"][0] += 0.30

    elif variation == 4:

        for asset in assets:

            if asset["asset"] == "Sofa_Modern":
                asset["rotation"][2] = -5

            elif asset["asset"] == "CoffeeTable_Modern":
                asset["rotation"][2] = 5

    # --------------------------------------------------------
    # Collision optimization
    # --------------------------------------------------------

    assets, _ = optimize_layout(
        assets,
        room_width,
        room_length
    )

    # --------------------------------------------------------
    # Entrance optimization
    # --------------------------------------------------------

    assets, _, _ = optimize_space_rules(
        assets,
        room_width,
        room_length
    )

    # --------------------------------------------------------
    # Door/window optimization
    # --------------------------------------------------------

    assets, _, _ = optimize_architecture(
        assets,
        room_width,
        room_length
    )

    return assets


# ============================================================
# DAY 14 — NORMAL MULTI-LAYOUT OPTIMIZER
# ============================================================

def find_best_layout(
    room_type,
    room_width,
    room_length,
    candidate_count=5
):
    """
    Original Day 14 optimizer.

    Kept for backward compatibility with main.py.
    """

    candidates = []

    for variation in range(candidate_count):

        assets = create_candidate(
            room_type,
            room_width,
            room_length,
            variation
        )

        # ----------------------------------------------------
        # Validate
        # ----------------------------------------------------

        valid = layout_is_valid(
            assets,
            room_width,
            room_length
        )

        # ----------------------------------------------------
        # Score
        # ----------------------------------------------------

        score_result = score_layout(
            assets,
            room_width,
            room_length
        )

        candidates.append({
            "variation": variation,
            "valid": valid,
            "score": score_result["score"],
            "reasons": score_result.get(
                "reasons",
                []
            ),
            "assets": copy.deepcopy(
                assets
            )
        })

    candidates.sort(
        key=lambda candidate: (
            candidate["valid"],
            candidate["score"]
        ),
        reverse=True
    )

    best = candidates[0]

    return {
        "best": best,
        "candidates": candidates
    }


# ============================================================
# DAY 15 — DESIGN ASSET SELECTION
# ============================================================

def apply_design_asset_selection(
    assets,
    requested_assets
):
    """
    Applies explicitly requested furniture.

    If Sofa_LShape is requested:
        - Remove all existing sofas.
        - Add exactly one Sofa_LShape.

    Other requested assets are preserved if they already
    exist in the smart layout.
    """

    requested_assets = requested_assets or []

    print("\n[DESIGN ASSET SELECTION]")

    print(
        "Requested assets:",
        requested_assets
    )

    # ========================================================
    # L-SHAPED SOFA PRIORITY
    # ========================================================

    if "Sofa_LShape" in requested_assets:

        # ----------------------------------------------------
        # Remove ALL sofas from default layout
        # ----------------------------------------------------

        assets = [
            asset
            for asset in assets
            if asset["asset"] not in {
                "Sofa_Modern",
                "Sofa_LShape"
            }
        ]

        # ----------------------------------------------------
        # Add exactly ONE L-shaped sofa
        # ----------------------------------------------------

        assets.append({
            "asset": "Sofa_LShape",
            "position": [0, 0.75, 0],
            "rotation": [0, 0, 0],
            "scale": [1, 1, 1]
        })

        print(
            "Selected sofa: Sofa_LShape"
        )

    else:

        # ----------------------------------------------------
        # Add other requested assets
        # ----------------------------------------------------


        existing = {
            asset["asset"]
            for asset in assets
        }

        for asset_name in requested_assets:

            if asset_name not in existing:

                assets.append({
                    "asset": asset_name,
                    "position": [0, 0, 0],
                    "rotation": [0, 0, 0],
                    "scale": [1, 1, 1]
                })

                # Update immediately to prevent duplicates.
                existing.add(asset_name)

                print(
                    f"Added missing requested asset: "
                    f"{asset_name}"
                )

            else:

                for asset in assets:

                    if asset["asset"] == asset_name:

                        print(
                            f"Preserving layout position for "
                            f"{asset_name}: "
                            f"{asset['position']}"
                        )

                        break

    # ========================================================
    # FINAL SOFA CHECK
    # ========================================================

    sofa_assets = [
        asset["asset"]
        for asset in assets
        if asset["asset"].startswith("Sofa_")
    ]

    print(
        "Final sofa assets:",
        sofa_assets
    )

    return assets


# ============================================================
# DAY 15 — ROTATION-AWARE CENTER RULE
# ============================================================

def apply_center_rules(
    assets,
    orientation_rules
):
    """
    Applies center placement rules.

    IMPORTANT:
    A coffee table must NOT blindly be placed at [0, 0].

    When an L-shaped sofa exists, the coffee table is positioned
    using the sofa footprint and its current Z rotation.

    This prevents the CoffeeTable_Modern from overlapping
    Sofa_LShape.
    """

    from api.asset_dimensions import get_asset_dimensions

    for rule in orientation_rules:

        if rule.get("type") != "center":
            continue

        target_asset = rule.get("asset")

        target = None

        # ----------------------------------------------------
        # Find target asset
        # ----------------------------------------------------

        for asset in assets:

            if asset["asset"] == target_asset:
                target = asset
                break

        if target is None:
            continue

        # ====================================================
        # SPECIAL CASE — COFFEE TABLE
        # ====================================================

        if target_asset == "CoffeeTable_Modern":

            sofa = None

            for asset in assets:

                if asset["asset"] in {
                    "Sofa_LShape",
                    "Sofa_Modern"
                }:

                    sofa = asset
                    break

            # ------------------------------------------------
            # No sofa
            # ------------------------------------------------

            if sofa is None:

                target["position"] = [
                    0.0,
                    0.0,
                    0.0
                ]

                print(
                    "Centered: CoffeeTable_Modern"
                )

                continue

            sofa_name = sofa["asset"]

            sofa_position = sofa.get(
                "position",
                [0.0, 0.0, 0.0]
            )

            sofa_rotation = sofa.get(
                "rotation",
                [0.0, 0.0, 0.0]
            )

            sofa_x = float(
                sofa_position[0]
            )

            sofa_y = float(
                sofa_position[1]
            )

            sofa_z_rotation = float(
                sofa_rotation[2]
            )

            # =================================================
            # L-SHAPED SOFA
            # =================================================

            if sofa_name == "Sofa_LShape":

                sofa_dimensions = get_asset_dimensions(
                    "Sofa_LShape"
                )

                table_dimensions = get_asset_dimensions(
                    "CoffeeTable_Modern"
                )

                sofa_width = float(
                    sofa_dimensions["width"]
                )

                sofa_depth = float(
                    sofa_dimensions["depth"]
                )

                table_width = float(
                    table_dimensions["width"]
                )

                table_depth = float(
                    table_dimensions["depth"]
                )

                # ------------------------------------------------
                # Determine rotated footprint.
                #
                # At approximately 90 degrees the X/Y footprint
                # swaps.
                # ------------------------------------------------

                normalized_rotation = (
                    abs(sofa_z_rotation) % 180
                )

                if 45 <= normalized_rotation <= 135:

                    sofa_footprint_x = sofa_depth
                    sofa_footprint_y = sofa_width

                else:

                    sofa_footprint_x = sofa_width
                    sofa_footprint_y = sofa_depth

                sofa_half_x = (
                    sofa_footprint_x / 2.0
                )

                sofa_half_y = (
                    sofa_footprint_y / 2.0
                )

                table_half_x = (
                    table_width / 2.0
                )

                table_half_y = (
                    table_depth / 2.0
                )

                # ------------------------------------------------
                # Minimum clearance
                # ------------------------------------------------

                clearance = 0.10

                # ------------------------------------------------
                # Current sofa rotation is -90 degrees.
                #
                # Put the table to the right of the sofa footprint.
                # ------------------------------------------------

                table_x = (
                    sofa_x
                    + sofa_half_x
                    + table_half_x
                    + clearance
                )

                table_y = sofa_y

                target["position"] = [
                    round(table_x, 3),
                    round(table_y, 3),
                    0.0
                ]

                print(
                    "Placed CoffeeTable_Modern "
                    "beside L-shaped sofa with clearance"
                )

                return assets

            # =================================================
            # NORMAL SOFA
            # =================================================

            sofa_dimensions = get_asset_dimensions(
                "Sofa_Modern"
            )

            table_dimensions = get_asset_dimensions(
                "CoffeeTable_Modern"
            )

            sofa_depth = float(
                sofa_dimensions["depth"]
            )

            table_depth = float(
                table_dimensions["depth"]
            )

            table_x = sofa_x

            table_y = (
                sofa_y
                - sofa_depth / 2.0
                - 0.10
                - table_depth / 2.0
            )

            target["position"] = [
                round(table_x, 3),
                round(table_y, 3),
                0.0
            ]

            print(
                "Placed CoffeeTable_Modern "
                "in front of sofa"
            )

            return assets

        # ====================================================
        # NORMAL CENTER RULE
        # ====================================================

        target["position"][0] = 0.0
        target["position"][1] = 0.0

        print(
            "Centered:",
            target_asset
        )

    return assets


# ============================================================
# DAY 15 — FACING RULE
# ============================================================

def apply_facing_rules(
    assets,
    orientation_rules
):
    """
    Rotates a furniture asset toward another asset.
    """

    for rule in orientation_rules:

        if rule.get("type") != "face":
            continue

        subject = rule.get(
            "subject"
        )

        target = rule.get(
            "target"
        )

        subject_asset = None
        target_asset = None

        for asset in assets:

            if asset["asset"] == subject:
                subject_asset = asset

            if asset["asset"] == target:
                target_asset = asset

        if subject_asset is None:

            print(
                "Facing rule skipped. "
                f"Subject not found: {subject}"
            )

            continue

        if target_asset is None:

            print(
                "Facing rule skipped. "
                f"Target not found: {target}"
            )

            continue

        sx, sy, _ = subject_asset["position"]

        tx, ty, _ = target_asset["position"]

        angle = math.degrees(
            math.atan2(
                ty - sy,
                tx - sx
            )
        )  + 90.0

        subject_asset["rotation"][2] = angle

        print(
            f"{subject} faces {target} "
            f"rotation={angle:.2f}"
        )

    return assets


# ============================================================
# DAY 15 — APPLY DESIGN INTENT
# ============================================================

def apply_design_intent_to_layout(
    assets,
    instructions
):
    """
    Applies the layout generated by
    design_layout_adapter.py.

    Adapter structure:

        instructions
            ├── intent
            └── layout
                 ├── assets
                 ├── orientation
                 ├── colors
                 ├── space_rules
                 └── lighting
    """

    layout = instructions.get(
        "layout",
        {}
    )

    requested_assets = layout.get(
        "assets",
        []
    )

    orientation_rules = layout.get(
        "orientation",
        []
    )

    print("\n[DESIGN INTENT → LAYOUT]")

    print(
        "Requested assets:",
        requested_assets
    )

    # ========================================================
    # ASSET SELECTION
    # ========================================================

    assets = apply_design_asset_selection(
        assets,
        requested_assets
    )

    # ========================================================
    # CENTER RULES
    # ========================================================

    assets = apply_center_rules(
        assets,
        orientation_rules
    )

    # ========================================================
    # FACING RULES
    # ========================================================

    assets = apply_facing_rules(
        assets,
        orientation_rules
    )

    # ========================================================
    # FINAL DEBUG
    # ========================================================

    print(
        "\nFINAL ASSETS AFTER DESIGN INTENT:"
    )

    for asset in assets:

        print(
            f"  {asset['asset']:25}"
            f"Position: {asset['position']} "
            f"Rotation: {asset['rotation']}"
        )

    return assets


# ============================================================
# DAY 15 — DESIGN CANDIDATE
# ============================================================

def create_design_candidate(
    prompt,
    room_type,
    room_width,
    room_length,
    variation=0,
    architecture=None
):
    """
    Creates one Day-15 design-aware candidate.

    Flow:

        1. Generate normal room layout
        2. Create design instructions
        3. Apply design intent ONCE
        4. Apply room-specific variation
        5. Return layout for validation

    IMPORTANT:
    We intentionally do NOT run the old optimize_layout()
    after design intent because that can overwrite intentional
    furniture positions.
    """

    # ========================================================
    # STEP 1 — Generate normal layout
    # ========================================================

    assets = generate_layout(
        room_type,
        room_width,
        room_length
    )

    # ========================================================
    # STEP 2 — Create design instructions
    # ========================================================

    instructions = create_layout_instructions(
        prompt
    )

    # ========================================================
    # STEP 3 — Apply design intent ONCE
    # ========================================================

    assets = apply_design_intent_to_layout(
        assets,
        instructions
    )

    # ========================================================
    # STEP 4 — Room-specific variation
    # ========================================================

    if room_type == "living_room":

        # ----------------------------------------------------
        # These variations only affect Sofa_Modern.
        #
        # If Sofa_LShape is selected, it remains untouched.
        # ----------------------------------------------------

        if variation == 1:

            for asset in assets:

                if asset["asset"] == "Sofa_Modern":

                    asset["position"][1] += 0.30

                elif asset["asset"] == "CoffeeTable_Modern":

                    asset["position"][1] += 0.15

        elif variation == 2:

            for asset in assets:

                if asset["asset"] == "Sofa_Modern":

                    asset["position"][0] -= 0.50

                elif asset["asset"] == "CoffeeTable_Modern":

                    asset["position"][0] -= 0.30

        elif variation == 3:

            for asset in assets:

                if asset["asset"] == "Sofa_Modern":

                    asset["position"][0] += 0.50

                elif asset["asset"] == "CoffeeTable_Modern":

                    asset["position"][0] += 0.30

        elif variation == 4:

            for asset in assets:

                if asset["asset"] == "Sofa_Modern":

                    asset["rotation"][2] = -5

                elif asset["asset"] == "CoffeeTable_Modern":

                    asset["rotation"][2] = 5

    # Find a chair position that satisfies both furniture
    # collision checks and architectural clearance rules.
    chair = next(
        (asset for asset in assets
         if asset.get("asset") == "Chair_Modern"),
        None
    )

    if chair is not None:
        other_assets = [
            asset for asset in assets
            if asset is not chair
        ]

        suggested_position = find_best_position(
            chair,
            other_assets,
            room_width,
            room_length
        )

        position_candidates = []

        if suggested_position is not None:
            position_candidates.append(
                (suggested_position[0], suggested_position[1])
            )

        # Prefer the right side of the room, then try other
        # positions if furniture or architecture blocks it.
        position_candidates.extend([
            (room_width * 0.34, 0.0),
            (room_width * 0.34, -room_length * 0.16),
            (room_width * 0.375, -room_length * 0.18),
            (-room_width * 0.325, -room_length * 0.16),
            (room_width * 0.325, -room_length * 0.16),
            (room_width * 0.325, 0.0),
            (-room_width * 0.325, 0.0),
            (0.0, -room_length * 0.30),
            (0.0, room_length * 0.10),
        ])

        # Remove duplicate positions while preserving their order.
        position_candidates = list(dict.fromkeys(
            (round(x, 4), round(y, 4))
            for x, y in position_candidates
        ))

        selected_position = None
        fallback_position = None

        for x, y in position_candidates:
            test_assets = copy.deepcopy(assets)
            test_chair = next(
                item for item in test_assets
                if item.get("asset") == "Chair_Modern"
            )
            test_chair["position"] = [
                x, y, chair["position"][2]
            ]

            if not layout_is_valid(
                test_assets, room_width, room_length
            ):
                continue

            # Keep a layout-valid fallback if architecture is
            # missing or every tested position triggers a warning.
            if fallback_position is None:
                fallback_position = [x, y, chair["position"][2]]

            if architecture:
                arch_result = validate_architecture(
                    assets=test_assets,
                    room_width=room_width,
                    room_length=room_length,
                    architecture=architecture
                )

                if not arch_result.get("valid", False):
                    continue

            selected_position = [
                x, y, chair["position"][2]
            ]
            break

        if selected_position is not None:
            chair["position"] = selected_position
        elif fallback_position is not None:
            chair["position"] = fallback_position

    return assets


# ============================================================
# DAY 15 + DAY 18 — DESIGN LAYOUT OPTIMIZER
# ============================================================

def find_best_design_layout(
    prompt,
    room_type,
    room_width,
    room_length,
    candidate_count=5,
    architecture=None
):
    """
    Generates multiple layouts while applying
    natural-language design intent and optional
    architectural constraints.
    """

    candidates = []

    instructions = create_layout_instructions(
        prompt
    )

    for variation in range(
        candidate_count
    ):

        assets = create_design_candidate(
            prompt,
            room_type,
            room_width,
            room_length,
            variation,
            architecture=architecture
        )

        # ----------------------------------------------------
        # Basic Layout Validation
        # ----------------------------------------------------

        valid = layout_is_valid(
            assets,
            room_width,
            room_length
        )

        # ----------------------------------------------------
        # Architectural Validation
        # ----------------------------------------------------

        if architecture:

            architecture_validation = validate_architecture(
                assets=assets,
                room_width=room_width,
                room_length=room_length,
                architecture=architecture
            )

        else:

            architecture_validation = {
                "valid": True,
                "warnings": [],
                "blocked_doors": [],
                "blocked_windows": [],
                "architecture_source": "not_provided",
                "architecture_confidence": 0.0,
                "wall_count": 0,
                "door_count": 0,
                "window_count": 0
            }

        # ----------------------------------------------------
        # Combine Validation
        # ----------------------------------------------------

        architecture_valid = (
            architecture_validation["valid"]
        )

        final_valid = (
            valid
            and architecture_valid
        )

        # ----------------------------------------------------
        # Score
        # ----------------------------------------------------

        score_result = score_layout(
            assets,
            room_width,
            room_length
        )

        score = score_result["score"]

        # ----------------------------------------------------
        # Architectural penalties
        # ----------------------------------------------------

        blocked_doors = len(
            architecture_validation.get(
                "blocked_doors",
                []
            )
        )

        blocked_windows = len(
            architecture_validation.get(
                "blocked_windows",
                []
            )
        )

        architecture_penalty = (
            blocked_doors * 25
            +
            blocked_windows * 15
        )

        final_score = max(
            0,
            score - architecture_penalty
        )

        # ----------------------------------------------------
        # Reasons
        # ----------------------------------------------------

        reasons = list(
            score_result.get(
                "reasons",
                []
            )
        )

        reasons.extend(
            architecture_validation.get(
                "warnings",
                []
            )
        )

        # ----------------------------------------------------
        # Candidate
        # ----------------------------------------------------

        candidates.append(
            {
                "variation": variation,

                "assets": copy.deepcopy(
                    assets
                ),

                "score": final_score,

                "base_score": score,

                "valid": final_valid,

                "layout_valid": valid,

                "architecture_valid": architecture_valid,

                "architecture_validation":
                    architecture_validation,

                "architecture_penalty":
                    architecture_penalty,

                "reasons": reasons
            }
        )

    # --------------------------------------------------------
    # Best candidate first
    # --------------------------------------------------------

    candidates.sort(
        key=lambda candidate: (
            candidate["valid"],
            candidate["score"]
        ),
        reverse=True
    )

    best = candidates[0]

    return {
        "prompt": prompt,
        "instructions": instructions,
        "best": best,
        "candidates": candidates
    }