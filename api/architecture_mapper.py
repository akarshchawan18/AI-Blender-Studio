"""
DAY 18 - ARCHITECTURE MAPPER

Converts image-based architectural detections into
normalized room coordinates.

IMPORTANT:
This is an estimation layer.

It does NOT claim to recover exact real-world
measurements from a single image.
"""

from typing import Dict, List


def normalized_to_room_coordinate(
    position_along_wall: float,
    wall: str,
    room_width: float,
    room_length: float
):
    """
    Convert normalized wall position (0.0 -> 1.0)
    into approximate room coordinates.

    Coordinate system:

                 BACK
        (-W/2,+L/2) ------ (+W/2,+L/2)
             |                  |
             |                  |
          LEFT                 RIGHT
             |                  |
             |                  |
        (-W/2,-L/2) ------ (+W/2,-L/2)
                 FRONT

    Returns:
        [x, y]
    """

    if position_along_wall is None:
        return None

    try:
        position = float(position_along_wall)
    except (TypeError, ValueError):
        return None

    position = max(0.0, min(1.0, position))

    wall = str(wall).lower().strip()

    if wall == "left":
        x = -room_width / 2
        y = -room_length / 2 + (
            position * room_length
        )

    elif wall == "right":
        x = room_width / 2
        y = -room_length / 2 + (
            position * room_length
        )

    elif wall == "front":
        x = -room_width / 2 + (
            position * room_width
        )
        y = -room_length / 2

    elif wall == "back":
        x = -room_width / 2 + (
            position * room_width
        )
        y = room_length / 2

    else:
        return None

    return [
        round(x, 4),
        round(y, 4)
    ]


def map_architecture_candidate(
    candidate: Dict,
    room_width: float,
    room_length: float
):
    """
    Convert one detected door/window into
    room-space metadata.
    """

    wall = candidate.get("wall", "unknown")

    position_along_wall = candidate.get(
        "position_along_wall"
    )

    room_position = normalized_to_room_coordinate(
        position_along_wall=position_along_wall,
        wall=wall,
        room_width=room_width,
        room_length=room_length
    )

    mapped = dict(candidate)

    mapped["room_position"] = room_position

    if room_position is not None:
        mapped["mapping_status"] = "estimated"
    else:
        mapped["mapping_status"] = "unmapped"

    return mapped


def map_architecture(
    architecture: Dict,
    room_width: float,
    room_length: float
):
    """
    Convert detected architectural candidates
    into room-space coordinates.
    """

    if not isinstance(architecture, dict):
        return {
            "status": "invalid",
            "doors": [],
            "windows": []
        }

    doors = architecture.get("doors", [])
    windows = architecture.get("windows", [])

    mapped_doors = [
        map_architecture_candidate(
            candidate=door,
            room_width=room_width,
            room_length=room_length
        )
        for door in doors
    ]

    mapped_windows = [
        map_architecture_candidate(
            candidate=window,
            room_width=room_width,
            room_length=room_length
        )
        for window in windows
    ]

    return {
        "status": "success",
        "source": architecture.get(
            "source",
            "unknown"
        ),
        "confidence": architecture.get(
            "confidence",
            0.0
        ),
        "room": {
            "width": room_width,
            "length": room_length
        },
        "doors": mapped_doors,
        "windows": mapped_windows
    }


if __name__ == "__main__":

    print("=" * 70)
    print("DAY 18 - ARCHITECTURE MAPPER TEST")
    print("=" * 70)

    test_architecture = {
        "source": "opencv_geometry",
        "confidence": 0.263,
        "doors": [
            {
                "type": "door_candidate",
                "wall": "right",
                "wall_confidence": 0.6,
                "position_along_wall": 0.4191,
                "confidence": 0.629
            }
        ],
        "windows": [
            {
                "type": "window_candidate",
                "wall": "left",
                "wall_confidence": 0.6,
                "position_along_wall": 0.2,
                "confidence": 0.409
            },
            {
                "type": "window_candidate",
                "wall": "left",
                "wall_confidence": 0.6,
                "position_along_wall": 0.4656,
                "confidence": 0.314
            },
            {
                "type": "window_candidate",
                "wall": "unknown",
                "wall_confidence": 0.3,
                "position_along_wall": None,
                "confidence": 0.299
            }
        ]
    }

    result = map_architecture(
        architecture=test_architecture,
        room_width=4.0,
        room_length=5.0
    )

    print("\nMAPPED DOORS:")

    for door in result["doors"]:
        print(door)

    print("\nMAPPED WINDOWS:")

    for window in result["windows"]:
        print(window)

    print("\nDONE")