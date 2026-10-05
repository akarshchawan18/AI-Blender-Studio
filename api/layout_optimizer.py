"""
DAY 14 - MULTI-LAYOUT OPTIMIZER

Generates multiple candidate layouts,
validates them, scores them, and selects
the highest-scoring layout.
"""

import copy

from api.layout_engine import (
    generate_layout,
    optimize_layout,
    optimize_space_rules,
    optimize_architecture,
    layout_is_valid
)

from api.layout_score import score_layout


# ============================================================
# GENERATE CANDIDATE
# ============================================================

def create_candidate(
    room_type,
    room_width,
    room_length,
    variation
):
    """
    Creates one candidate layout.

    Variation changes furniture positions
    to create different possibilities.
    """

    assets = generate_layout(
        room_type,
        room_width,
        room_length
    )

    # --------------------------------------------------------
    # Apply variation
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
    # Optimize normal collisions
    # --------------------------------------------------------

    assets, _ = optimize_layout(
        assets,
        room_width,
        room_length
    )

    # --------------------------------------------------------
    # Optimize entrance
    # --------------------------------------------------------

    assets, _, _ = optimize_space_rules(
        assets,
        room_width,
        room_length
    )

    # --------------------------------------------------------
    # Optimize doors/windows
    # --------------------------------------------------------

    assets, _, _ = optimize_architecture(
        assets,
        room_width,
        room_length
    )

    return assets


# ============================================================
# OPTIMIZE
# ============================================================

def find_best_layout(
    room_type,
    room_width,
    room_length,
    candidate_count=5
):
    """
    Generates multiple layouts and returns
    the highest-scoring valid layout.
    """

    candidates = []

    for variation in range(
        candidate_count
    ):

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
            "reasons": score_result["reasons"],
            "assets": copy.deepcopy(
                assets
            )
        })

    # --------------------------------------------------------
    # Sort
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
        "best": best,
        "candidates": candidates
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("DAY 14 - MULTI-LAYOUT OPTIMIZER TEST")
    print("=" * 60)

    room_type = "living_room"

    room_width = 5.5
    room_length = 5.0

    result = find_best_layout(
        room_type,
        room_width,
        room_length,
        candidate_count=5
    )

    print("\nCANDIDATES")

    for candidate in result["candidates"]:

        print(
            f'Layout {candidate["variation"]}: '
            f'Score={candidate["score"]} '
            f'Valid={candidate["valid"]}'
        )

    print("\n" + "-" * 60)

    best = result["best"]

    print("BEST LAYOUT")

    print(
        "Variation:",
        best["variation"]
    )

    print(
        "Score:",
        best["score"]
    )

    print(
        "Valid:",
        best["valid"]
    )

    print("\nASSETS")

    for asset in best["assets"]:

        print(
            f'{asset["asset"]:25}'
            f'Position: {asset["position"]}'
            f'Rotation: {asset["rotation"]}'
        )

    print("\n" + "=" * 60)