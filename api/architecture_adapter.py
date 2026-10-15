
"""
DAY 19 - ARCHITECTURE ADAPTER

Converts mapped image detections into the format expected
by architectural_rules.py.

Only candidates with valid mapped positions and recognized
wall assignments are passed to the validator.
"""

from typing import Any, Dict, List, Optional


DEFAULT_DOOR_WIDTH = 0.90
DEFAULT_WINDOW_WIDTH = 1.80


def _valid_position(position: Any) -> bool:
    """Return True only for a valid two-dimensional position."""
    if not isinstance(position, (list, tuple)) or len(position) < 2:
        return False

    try:
        float(position[0])
        float(position[1])
        return True
    except (TypeError, ValueError):
        return False


def _convert_candidate(
    candidate: Dict[str, Any],
    element_type: str,
    default_width: float,
) -> Optional[Dict[str, Any]]:
    """Convert one mapped door or window candidate."""

    if not isinstance(candidate, dict):
        return None

    # Never invent a position for an unmapped detection.
    if candidate.get("mapping_status") != "estimated":
        return None

    position = candidate.get("room_position")

    if not _valid_position(position):
        return None

    wall = str(candidate.get("wall", "unknown")).lower().strip()

    if wall not in {"front", "back", "left", "right"}:
        return None

    try:
        width = float(candidate.get("estimated_width", default_width))
        confidence = float(candidate.get("confidence", 0.0))
    except (TypeError, ValueError):
        return None

    if width <= 0:
        return None

    confidence = max(0.0, min(1.0, confidence))

    return {
        "position": [float(position[0]), float(position[1])],
        "width": width,
        "wall": wall,
        "type": element_type,
        "confidence": confidence,
    }


def adapt_architecture(
    mapped_architecture: Dict[str, Any],
    room_width: float,
    room_length: float,
) -> Dict[str, Any]:
    """
    Convert architecture_mapper output into architectural_rules format.

    Coordinates and dimensions are estimates. Default widths are
    placeholders until reliable real-world measurements are available.
    """

    if not isinstance(mapped_architecture, dict):
        mapped_architecture = {}

    doors: List[Dict[str, Any]] = []
    windows: List[Dict[str, Any]] = []

    for candidate in mapped_architecture.get("doors", []):
        converted = _convert_candidate(
            candidate=candidate,
            element_type="door",
            default_width=DEFAULT_DOOR_WIDTH,
        )
        if converted is not None:
            doors.append(converted)

    for candidate in mapped_architecture.get("windows", []):
        converted = _convert_candidate(
            candidate=candidate,
            element_type="window",
            default_width=DEFAULT_WINDOW_WIDTH,
        )
        if converted is not None:
            windows.append(converted)

    walls = [
        {
            "wall": "front",
            "axis": "x",
            "position": -room_length / 2,
            "length": room_width,
        },
        {
            "wall": "back",
            "axis": "x",
            "position": room_length / 2,
            "length": room_width,
        },
        {
            "wall": "left",
            "axis": "y",
            "position": -room_width / 2,
            "length": room_length,
        },
        {
            "wall": "right",
            "axis": "y",
            "position": room_width / 2,
            "length": room_length,
        },
    ]

    return {
        "source": mapped_architecture.get("source", "image_estimation"),
        "confidence": mapped_architecture.get("confidence", 0.0),
        "walls": walls,
        "doors": doors,
        "door": doors[0] if doors else None,
        "windows": windows,
        "room": {
            "width": room_width,
            "length": room_length,
        },
        "mapping_status": mapped_architecture.get("status", "unknown"),
        "dimensions_are_estimates": True,
    }


if __name__ == "__main__":
    sample = {
        "source": "opencv_geometry",
        "confidence": 0.263,
        "status": "success",
        "doors": [
            {
                "wall": "right",
                "confidence": 0.629,
                "room_position": [2.0, -0.4045],
                "mapping_status": "estimated",
            }
        ],
        "windows": [
            {
                "wall": "left",
                "confidence": 0.409,
                "room_position": [-2.0, -1.5],
                "mapping_status": "estimated",
            },
            {
                "wall": "unknown",
                "confidence": 0.299,
                "room_position": None,
                "mapping_status": "unmapped",
            },
        ],
    }

    result = adapt_architecture(
        mapped_architecture=sample,
        room_width=4.0,
        room_length=5.0,
    )

    print("DAY 19 - ARCHITECTURE ADAPTER TEST")
    print("Source:", result["source"])
    print("Walls:", len(result["walls"]))
    print("Mapped doors:", len(result["doors"]))
    print("Mapped windows:", len(result["windows"]))
    print("Door:", result["doors"][0])
    print("Window:", result["windows"][0])
    print("Unknown window correctly excluded:", len(result["windows"]) == 1)