from typing import Dict, Any

from api.furniture_detector import detect_furniture
from api.image_furniture import build_furniture_intent
from api.local_furniture_fallback import infer_furniture_from_room


def _run_yolo(image_path: str):
    """
    Run the existing YOLO furniture detector.

    Returns:
        detections, error
    """

    try:
        detections = detect_furniture(
            image_path=image_path,
            confidence_threshold=0.10,
            image_size=1280,
        )

        return detections, None

    except Exception as error:
        return [], str(error)


def _run_sam3(image_path: str):
    """
    Run SAM 3 only when the checkpoint is available.

    SAM 3 remains optional so the main application
    never fails because SAM 3 is unavailable.
    """

    try:
        from api.sam3_furniture_detector import (
            is_available,
            detect_furniture_sam3,
        )

        if not is_available():
            return [], "SAM3 checkpoint unavailable"

        detections = detect_furniture_sam3(
            image_path=image_path,
            confidence_threshold=0.25,
        )

        return detections, None

    except Exception as error:
        return [], str(error)


def _convert_to_furniture_intent(detections):
    """
    Convert detector output into the existing
    furniture-intent format.
    """

    if not detections:
        return []

    return build_furniture_intent(
        detections
    )


def detect_furniture_pipeline(
    image_path: str,
    room_type: str = "unknown",
) -> Dict[str, Any]:
    """
    Complete furniture detection pipeline.

    Priority:

        1. YOLO
        2. SAM 3
        3. Room inference fallback

    The pipeline always returns a valid result.
    """

    # --------------------------------------------------
    # 1. YOLO
    # --------------------------------------------------

    yolo_detections, yolo_error = _run_yolo(
        image_path
    )

    if yolo_detections:

        furniture = _convert_to_furniture_intent(
            yolo_detections
        )

        return {
            "status": "success",
            "source": "yolo",
            "detections": yolo_detections,
            "furniture": furniture,
            "fallback_used": False,
            "detector_chain": [
                "yolo"
            ],
            "yolo_error": None,
            "sam3_error": None,
        }

    # --------------------------------------------------
    # 2. SAM 3
    # --------------------------------------------------

    sam3_detections, sam3_error = _run_sam3(
        image_path
    )

    if sam3_detections:

        furniture = _convert_to_furniture_intent(
            sam3_detections
        )

        return {
            "status": "success",
            "source": "sam3",
            "detections": sam3_detections,
            "furniture": furniture,
            "fallback_used": False,
            "detector_chain": [
                "yolo",
                "sam3",
            ],
            "yolo_error": yolo_error,
            "sam3_error": None,
        }

    # --------------------------------------------------
    # 3. Room-based fallback
    # --------------------------------------------------

    fallback_furniture = infer_furniture_from_room(
        room_type
    )

    return {
        "status": "fallback",
        "source": "room_inference",
        "detections": [],
        "furniture": fallback_furniture,
        "fallback_used": True,
        "detector_chain": [
            "yolo",
            "sam3",
            "room_inference",
        ],
        "yolo_error": yolo_error,
        "sam3_error": sam3_error,
    }