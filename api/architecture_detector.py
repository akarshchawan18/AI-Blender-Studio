"""
DAY 18 - IMAGE ARCHITECTURE DETECTOR

Local-first architecture detection.

Detects:
- Structural lines
- Horizontal wall/floor/ceiling candidates
- Vertical wall candidates
- Possible door candidates
- Possible window candidates

This is an estimation system.

It does NOT claim exact architectural measurements
from a single photograph.
"""

from pathlib import Path
from typing import Dict, Any

import cv2
import numpy as np


# ============================================================
# SETTINGS
# ============================================================

SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp"
}

CANNY_LOW = 50
CANNY_HIGH = 150

HOUGH_THRESHOLD = 60
MIN_LINE_LENGTH_RATIO = 0.15
MAX_LINE_GAP = 20

MIN_DOOR_ASPECT_RATIO = 1.4
MIN_WINDOW_ASPECT_RATIO = 1.2


# ============================================================
# IMAGE LOADING
# ============================================================

def load_image(image_path: str):

    path = Path(image_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported image type: {path.suffix}"
        )

    image = cv2.imread(
        str(path)
    )

    if image is None:
        raise ValueError(
            f"Unable to read image: {image_path}"
        )

    return image


# ============================================================
# EDGE DETECTION
# ============================================================

def detect_edges(image):

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    blurred = cv2.GaussianBlur(
        gray,
        (5, 5),
        0
    )

    edges = cv2.Canny(
        blurred,
        CANNY_LOW,
        CANNY_HIGH
    )

    return edges


# ============================================================
# LINE DETECTION
# ============================================================

def detect_lines(
    edges,
    image_width,
    image_height
):

    min_line_length = int(
        min(
            image_width,
            image_height
        )
        * MIN_LINE_LENGTH_RATIO
    )

    lines = cv2.HoughLinesP(
        edges,
        rho=1,
        theta=np.pi / 180,
        threshold=HOUGH_THRESHOLD,
        minLineLength=min_line_length,
        maxLineGap=MAX_LINE_GAP
    )

    if lines is None:
        return []

    detected = []

    for line in lines:

        x1, y1, x2, y2 = line[0]

        dx = x2 - x1
        dy = y2 - y1

        length = float(
            np.sqrt(
                dx * dx
                + dy * dy
            )
        )

        angle = float(
            np.degrees(
                np.arctan2(
                    dy,
                    dx
                )
            )
        )

        # Normalize angle.
        if angle < -90:
            angle += 180

        if angle > 90:
            angle -= 180

        detected.append({
            "x1": int(x1),
            "y1": int(y1),
            "x2": int(x2),
            "y2": int(y2),
            "length": round(length, 2),
            "angle": round(angle, 2)
        })

    detected.sort(
        key=lambda item: item["length"],
        reverse=True
    )

    return detected


# ============================================================
# LINE CLASSIFICATION
# ============================================================

def classify_lines(lines):

    horizontal = []
    vertical = []
    diagonal = []

    for line in lines:

        angle = abs(
            line["angle"]
        )

        if angle <= 10:

            horizontal.append(line)

        elif angle >= 80:

            vertical.append(line)

        else:

            diagonal.append(line)

    return {
        "horizontal": horizontal,
        "vertical": vertical,
        "diagonal": diagonal
    }


# ============================================================
# NORMALIZED LINE
# ============================================================

def normalize_line(
    line,
    image_width,
    image_height
):

    return {
        "x1": round(
            line["x1"] / image_width,
            4
        ),

        "y1": round(
            line["y1"] / image_height,
            4
        ),

        "x2": round(
            line["x2"] / image_width,
            4
        ),

        "y2": round(
            line["y2"] / image_height,
            4
        ),

        "length": line["length"],

        "angle": line["angle"]
    }


# ============================================================
# WALL CANDIDATES
# ============================================================

def detect_wall_candidates(
    classified_lines,
    image_width,
    image_height
):

    candidates = []

    all_lines = (
        classified_lines["horizontal"]
        +
        classified_lines["vertical"]
    )

    if not all_lines:
        return candidates

    maximum_length = max(
        line["length"]
        for line in all_lines
    )

    if maximum_length <= 0:
        return candidates

    for line in all_lines:

        relative_length = (
            line["length"]
            / maximum_length
        )

        # Long lines are more likely to
        # correspond to room boundaries.
        if relative_length < 0.35:
            continue

        normalized = normalize_line(
            line,
            image_width,
            image_height
        )

        normalized["relative_length"] = round(
            relative_length,
            3
        )

        candidates.append(
            normalized
        )

    return candidates


# ============================================================
# RECTANGLE CANDIDATES
# ============================================================

def detect_rectangular_candidates(
    edges,
    image_width,
    image_height
):

    contours, _ = cv2.findContours(
        edges,
        cv2.RETR_LIST,
        cv2.CHAIN_APPROX_SIMPLE
    )

    candidates = []

    image_area = (
        image_width
        * image_height
    )

    for contour in contours:

        x, y, width, height = cv2.boundingRect(
            contour
        )

        if width < 30 or height < 30:
            continue

        area = width * height

        relative_area = (
            area / image_area
        )

        if relative_area < 0.01:
            continue

        aspect_ratio = (
            width / height
        )

        candidates.append({
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "aspect_ratio": round(
                aspect_ratio,
                3
            ),
            "relative_area": round(
                relative_area,
                5
            )
        })

    candidates.sort(
        key=lambda item: item["relative_area"],
        reverse=True
    )

    return candidates[:50]


# ============================================================
# DOOR CANDIDATES
# ============================================================

def detect_door_candidates(
    rectangles,
    image_width,
    image_height
):

    doors = []

    for rectangle in rectangles:

        width = rectangle["width"]
        height = rectangle["height"]

        aspect_ratio = (
            max(width, height)
            / max(
                1,
                min(width, height)
            )
        )

        # Doors are generally vertically oriented.
        if height <= width:
            continue

        if aspect_ratio < MIN_DOOR_ASPECT_RATIO:
            continue

        relative_height = (
            height
            / image_height
        )

        if relative_height < 0.15:
            continue

        center_x = (
            rectangle["x"]
            + width / 2
        )

        center_y = (
            rectangle["y"]
            + height / 2
        )

        confidence = min(
            0.95,
            0.30
            + relative_height * 0.5
            + min(
                aspect_ratio / 10,
                0.20
            )
        )

        doors.append({
            "type": "door_candidate",

            "center": {
                "x": round(
                    center_x / image_width,
                    4
                ),

                "y": round(
                    center_y / image_height,
                    4
                )
            },

            "bounding_box": {
                "x": rectangle["x"],
                "y": rectangle["y"],
                "width": width,
                "height": height
            },

            "aspect_ratio": round(
                aspect_ratio,
                3
            ),

            "confidence": round(
                confidence,
                3
            ),

            "source": "opencv_geometry"
        })

    doors.sort(
        key=lambda item: item["confidence"],
        reverse=True
    )

    return doors[:10]


# ============================================================
# WINDOW CANDIDATES
# ============================================================

def detect_window_candidates(
    rectangles,
    image_width,
    image_height
):

    windows = []

    for rectangle in rectangles:

        width = rectangle["width"]
        height = rectangle["height"]

        aspect_ratio = (
            max(width, height)
            / max(
                1,
                min(width, height)
            )
        )

        if aspect_ratio < MIN_WINDOW_ASPECT_RATIO:
            continue

        relative_area = rectangle[
            "relative_area"
        ]

        if relative_area < 0.015:
            continue

        center_x = (
            rectangle["x"]
            + width / 2
        )

        center_y = (
            rectangle["y"]
            + height / 2
        )

        confidence = min(
            0.90,
            0.25
            + relative_area * 2.0
        )

        windows.append({
            "type": "window_candidate",

            "center": {
                "x": round(
                    center_x / image_width,
                    4
                ),

                "y": round(
                    center_y / image_height,
                    4
                )
            },

            "bounding_box": {
                "x": rectangle["x"],
                "y": rectangle["y"],
                "width": width,
                "height": height
            },

            "aspect_ratio": round(
                aspect_ratio,
                3
            ),

            "confidence": round(
                confidence,
                3
            ),

            "source": "opencv_geometry"
        })

    windows.sort(
        key=lambda item: item["confidence"],
        reverse=True
    )

    return windows[:10]


# ============================================================
# CANDIDATE OVERLAP
# ============================================================

def intersection_over_union(
    box_a,
    box_b
):

    ax1 = box_a["x"]
    ay1 = box_a["y"]

    ax2 = (
        ax1
        + box_a["width"]
    )

    ay2 = (
        ay1
        + box_a["height"]
    )

    bx1 = box_b["x"]
    by1 = box_b["y"]

    bx2 = (
        bx1
        + box_b["width"]
    )

    by2 = (
        by1
        + box_b["height"]
    )

    intersection_x1 = max(
        ax1,
        bx1
    )

    intersection_y1 = max(
        ay1,
        by1
    )

    intersection_x2 = min(
        ax2,
        bx2
    )

    intersection_y2 = min(
        ay2,
        by2
    )

    intersection_width = max(
        0,
        intersection_x2
        - intersection_x1
    )

    intersection_height = max(
        0,
        intersection_y2
        - intersection_y1
    )

    intersection_area = (
        intersection_width
        * intersection_height
    )

    area_a = (
        box_a["width"]
        * box_a["height"]
    )

    area_b = (
        box_b["width"]
        * box_b["height"]
    )

    union_area = (
        area_a
        + area_b
        - intersection_area
    )

    if union_area <= 0:
        return 0.0

    return (
        intersection_area
        / union_area
    )


# ============================================================
# GROUP WINDOW CANDIDATES
# ============================================================

def group_window_candidates(
    windows,
    x_threshold=0.12,
    y_threshold=0.18
):

    """
    Group nearby window candidates that likely
    belong to the same physical opening.
    """

    if not windows:
        return []

    windows = sorted(
        windows,
        key=lambda item: item.get(
            "confidence",
            0.0
        ),
        reverse=True
    )

    groups = []

    for window in windows:

        center = window["center"]

        placed = False

        for group in groups:

            group_center = group["center"]

            dx = abs(
                center["x"]
                - group_center["x"]
            )

            dy = abs(
                center["y"]
                - group_center["y"]
            )

            if (
                dx <= x_threshold
                and
                dy <= y_threshold
            ):

                group["items"].append(
                    window
                )

                count = len(
                    group["items"]
                )

                group["center"] = {
                    "x": sum(
                        item["center"]["x"]
                        for item in group["items"]
                    ) / count,

                    "y": sum(
                        item["center"]["y"]
                        for item in group["items"]
                    ) / count
                }

                placed = True

                break

        if not placed:

            groups.append({
                "center": {
                    "x": center["x"],
                    "y": center["y"]
                },

                "items": [
                    window
                ]
            })

    final_windows = []

    for group in groups:

        best = max(
            group["items"],
            key=lambda item: item.get(
                "confidence",
                0.0
            )
        )

        confidence_values = [
            item.get(
                "confidence",
                0.0
            )
            for item in group["items"]
        ]

        average_confidence = (
            sum(confidence_values)
            / len(confidence_values)
        )

        best = dict(best)

        best["group_size"] = len(
            group["items"]
        )

        best["group_confidence"] = round(
            average_confidence,
            3
        )

        final_windows.append(
            best
        )

    final_windows.sort(
        key=lambda item: item.get(
            "confidence",
            0.0
        ),
        reverse=True
    )

    return final_windows


# ============================================================
# FILTER ARCHITECTURE CANDIDATES
# ============================================================
def estimate_wall_side(center_x, center_y):
    """
    Estimate which image-side region an architectural
    candidate belongs to.

    This is a visual heuristic, not an exact
    3D reconstruction.
    """

    if center_x <= 0.25:
        return "left"

    if center_x >= 0.75:
        return "right"

    if center_y <= 0.30:
        return "back"

    if center_y >= 0.70:
        return "front"

    return "unknown"
def assign_architecture_walls(
    doors,
    windows
):
    """
    Assign approximate wall labels to detected
    doors and windows.
    """

    for door in doors:

        center = door["center"]

        wall = estimate_wall_side(
            center["x"],
            center["y"]
        )

        door["wall"] = wall

        if wall == "unknown":
            door["wall_confidence"] = 0.30
        else:
            door["wall_confidence"] = 0.60

    for window in windows:

        center = window["center"]

        wall = estimate_wall_side(
            center["x"],
            center["y"]
        )

        window["wall"] = wall

        if wall == "unknown":
            window["wall_confidence"] = 0.30
        else:
            window["wall_confidence"] = 0.60

    return doors, windows
def filter_architecture_candidates(
    doors,
    windows,
    max_doors=3,
    max_windows=6
):

    """
    Clean architecture candidates.

    Rules:
    1. Sort by confidence.
    2. Remove windows overlapping doors.
    3. Remove duplicate windows.
    4. Group nearby windows.
    5. Keep strongest candidates.
    """

    doors = sorted(
        doors,
        key=lambda item: item.get(
            "confidence",
            0.0
        ),
        reverse=True
    )

    windows = sorted(
        windows,
        key=lambda item: item.get(
            "confidence",
            0.0
        ),
        reverse=True
    )

    # --------------------------------------------------------
    # REMOVE WINDOWS OVERLAPPING DOORS
    # --------------------------------------------------------

    filtered_windows = []

    for window in windows:

        window_box = window[
            "bounding_box"
        ]

        overlaps_door = False

        for door in doors:

            door_box = door[
                "bounding_box"
            ]

            iou = intersection_over_union(
                window_box,
                door_box
            )

            if iou > 0.30:

                overlaps_door = True

                break

        if not overlaps_door:

            filtered_windows.append(
                window
            )

    # --------------------------------------------------------
    # REMOVE DUPLICATE WINDOWS
    # --------------------------------------------------------

    unique_windows = []

    for window in filtered_windows:

        duplicate = False

        for existing in unique_windows:

            iou = intersection_over_union(
                window["bounding_box"],
                existing["bounding_box"]
            )

            if iou > 0.50:

                duplicate = True

                break

        if not duplicate:

            unique_windows.append(
                window
            )

    # --------------------------------------------------------
    # GROUP NEARBY WINDOWS
    # --------------------------------------------------------

    grouped_windows = (
        group_window_candidates(
            unique_windows
        )
    )

    # --------------------------------------------------------
    # LIMIT RESULTS
    # --------------------------------------------------------

    doors = doors[:max_doors]

    grouped_windows = (
        grouped_windows[:max_windows]
    )

    return (
        doors,
        grouped_windows
    )


# ============================================================
# DEBUG VISUALIZATION
# ============================================================

def create_debug_image(
    image,
    lines,
    doors,
    windows,
    output_path
):

    """
    Creates a visual debugging image.

    Colors:
        Green = structural line candidates
        Red   = door candidates
        Blue  = window candidates
    """

    debug = image.copy()

    # --------------------------------------------------------
    # DRAW STRUCTURAL LINES
    # --------------------------------------------------------

    for line in lines:

        x1 = int(
            line["x1"]
            * image.shape[1]
        )

        y1 = int(
            line["y1"]
            * image.shape[0]
        )

        x2 = int(
            line["x2"]
            * image.shape[1]
        )

        y2 = int(
            line["y2"]
            * image.shape[0]
        )

        cv2.line(
            debug,
            (x1, y1),
            (x2, y2),
            (0, 255, 0),
            2
        )

    # --------------------------------------------------------
    # DRAW DOORS
    # --------------------------------------------------------

    for index, door in enumerate(doors):

        box = door[
            "bounding_box"
        ]

        x = box["x"]
        y = box["y"]

        width = box["width"]
        height = box["height"]

        cv2.rectangle(
            debug,
            (x, y),
            (x + width, y + height),
            (0, 0, 255),
            3
        )

        label = (
            f"DOOR {index + 1} "
            f"{door['confidence']:.2f}"
        )

        cv2.putText(
            debug,
            label,
            (x, max(25, y - 8)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255),
            2
        )

    # --------------------------------------------------------
    # DRAW WINDOWS
    # --------------------------------------------------------

    for index, window in enumerate(windows):

        box = window[
            "bounding_box"
        ]

        x = box["x"]
        y = box["y"]

        width = box["width"]
        height = box["height"]

        cv2.rectangle(
            debug,
            (x, y),
            (x + width, y + height),
            (255, 0, 0),
            3
        )

        label = (
            f"WINDOW {index + 1} "
            f"{window['confidence']:.2f}"
        )

        cv2.putText(
            debug,
            label,
            (x, max(25, y - 8)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 0, 0),
            2
        )

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    output_path = str(
        Path(output_path)
    )

    cv2.imwrite(
        output_path,
        debug
    )

    return output_path


# ============================================================
# MAIN ARCHITECTURE ANALYSIS
# ============================================================
def calculate_wall_position(center_x, center_y, wall):
    """
    Convert normalized image coordinates into a normalized
    position along the assigned wall.

    This is a heuristic image-space estimate.
    It is NOT a real-world measurement.
    """

    if wall == "left" or wall == "right":
        # Vertical wall:
        # Y determines position along the wall.
        return round(center_y, 4)

    if wall == "front" or wall == "back":
        # Horizontal wall:
        # X determines position along the wall.
        return round(center_x, 4)

    return None


def enrich_architecture_candidates(doors, windows):
    """
    Add normalized position-along-wall metadata to
    detected architectural candidates.
    """

    for door in doors:
        center = door.get("center", {})
        wall = door.get("wall", "unknown")

        position_along_wall = calculate_wall_position(
            center.get("x", 0.5),
            center.get("y", 0.5),
            wall
        )

        door["position_along_wall"] = position_along_wall

    for window in windows:
        center = window.get("center", {})
        wall = window.get("wall", "unknown")

        position_along_wall = calculate_wall_position(
            center.get("x", 0.5),
            center.get("y", 0.5),
            wall
        )

        window["position_along_wall"] = position_along_wall

    return doors, windows
def detect_architecture(
    image_path: str
) -> Dict[str, Any]:

    image = load_image(
        image_path
    )

    image_height, image_width = (
        image.shape[:2]
    )

    # --------------------------------------------------------
    # EDGES
    # --------------------------------------------------------

    edges = detect_edges(
        image
    )

    # --------------------------------------------------------
    # LINES
    # --------------------------------------------------------

    lines = detect_lines(
        edges,
        image_width,
        image_height
    )

    classified = classify_lines(
        lines
    )

    # --------------------------------------------------------
    # WALL CANDIDATES
    # --------------------------------------------------------

    wall_candidates = detect_wall_candidates(
        classified,
        image_width,
        image_height
    )

    # --------------------------------------------------------
    # RECTANGLES
    # --------------------------------------------------------

    rectangles = detect_rectangular_candidates(
        edges,
        image_width,
        image_height
    )

    # --------------------------------------------------------
    # DOORS
    # --------------------------------------------------------

    door_candidates = detect_door_candidates(
        rectangles,
        image_width,
        image_height
    )


    # --------------------------------------------------------
    # WINDOWS
    # --------------------------------------------------------

    window_candidates = detect_window_candidates(
        rectangles,
        image_width,
        image_height
    )

    # --------------------------------------------------------
    # CLEAN ARCHITECTURE CANDIDATES
    # --------------------------------------------------------

    (
        door_candidates,
        window_candidates
    ) = filter_architecture_candidates(
        door_candidates,
        window_candidates
    )
    (
        door_candidates,
        window_candidates
    ) = assign_architecture_walls(
        door_candidates,
        window_candidates
    )
    door_candidates, window_candidates = enrich_architecture_candidates(
        door_candidates,
        window_candidates
    )

    # --------------------------------------------------------
    # CONFIDENCE
    # --------------------------------------------------------

    horizontal_count = len(
        classified["horizontal"]
    )

    vertical_count = len(
        classified["vertical"]
    )

    total_structural_lines = (
        horizontal_count
        + vertical_count
    )

    if total_structural_lines == 0:

        architecture_confidence = 0.0

    else:

        long_line_ratio = min(
            len(wall_candidates)
            / max(
                total_structural_lines,
                1
            ),
            1.0
        )

        architecture_confidence = min(
            0.85,
            0.20
            + long_line_ratio * 0.65
        )

    # --------------------------------------------------------
    # DEBUG IMAGE
    # --------------------------------------------------------

    debug_output = (
        Path(image_path).parent
        / (
            Path(image_path).stem
            + "_architecture_debug.jpg"
        )
    )

    create_debug_image(
        image=image,
        lines=wall_candidates,
        doors=door_candidates,
        windows=window_candidates,
        output_path=debug_output
    )

    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    return {

        "status": "success",

        "source": "opencv_geometry",

        "confidence": round(
            architecture_confidence,
            3
        ),

        "debug_image": str(
            debug_output
        ),

        "image": {
            "width": image_width,
            "height": image_height
        },

        "lines": {
            "total": len(lines),

            "horizontal": horizontal_count,

            "vertical": vertical_count,

            "diagonal": len(
                classified["diagonal"]
            )
        },

        "walls": wall_candidates,

        "doors": door_candidates,

        "windows": window_candidates,

        "rectangle_candidates": rectangles
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    import sys

    print("=" * 70)

    print(
        "DAY 18 - IMAGE ARCHITECTURE DETECTOR"
    )

    print("=" * 70)

    if len(sys.argv) < 2:

        print("\nUsage:")

        print(
            "python -m api.architecture_detector "
            "path_to_image"
        )

        sys.exit(1)

    image_path = sys.argv[1]

    print(
        "\nIMAGE:",
        image_path
    )

    result = detect_architecture(
        image_path
    )

    print(
        "\nSTATUS:",
        result["status"]
    )

    print(
        "SOURCE:",
        result["source"]
    )

    print(
        "CONFIDENCE:",
        result["confidence"]
    )

    print(
        "\nDEBUG IMAGE:"
    )

    print(
        result["debug_image"]
    )

    print(
        "\nIMAGE:"
    )

    print(
        result["image"]
    )

    print(
        "\nLINES:"
    )

    print(
        result["lines"]
    )

    print(
        "\nWALL CANDIDATES:",
        len(result["walls"])
    )

    for wall in result["walls"][:10]:

        print(
            wall
        )

    print(
        "\nDOOR CANDIDATES:",
        len(result["doors"])
    )

    for door in result["doors"][:10]:

        print(
            door
        )

    print(
        "\nWINDOW CANDIDATES:",
        len(result["windows"])
    )

    for window in result["windows"][:10]:

        print(
            window
        )

    print(
        "\n" + "=" * 70
    )