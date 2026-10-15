from pathlib import Path

from ultralytics.models.sam import SAM3SemanticPredictor


PROJECT_DIR = Path(__file__).resolve().parent.parent

MODEL_DIR = PROJECT_DIR / "models"

MODEL_PATH = MODEL_DIR / "sam3.pt"


SAM3_MODEL = None


# Text concepts used by the interior-design system.
FURNITURE_CONCEPTS = [
    "sofa",
    "chair",
    "coffee table",
    "dining table",
    "bed",
    "wardrobe",
    "desk",
    "television",
    "lamp",
]


# SAM 3 concept -> our internal object name.
CONCEPT_MAP = {
    "sofa": "sofa",
    "chair": "chair",
    "coffee table": "coffee_table",
    "dining table": "dining_table",
    "bed": "bed",
    "wardrobe": "wardrobe",
    "desk": "desk",
    "television": "tv_unit",
    "lamp": "lamp",
}


def is_available():
    """
    Check whether the SAM 3 checkpoint exists locally.
    """

    return MODEL_PATH.exists()


def get_model():
    """
    Load SAM 3 only when the checkpoint is available.
    """

    global SAM3_MODEL

    if not is_available():
        raise FileNotFoundError(
            f"SAM 3 checkpoint not found: {MODEL_PATH}"
        )

    if SAM3_MODEL is None:

        overrides = {
            "conf": 0.25,
            "task": "segment",
            "mode": "predict",
            "model": str(MODEL_PATH),
            "verbose": False,
        }

        SAM3_MODEL = SAM3SemanticPredictor(
            overrides=overrides
        )

    return SAM3_MODEL


def _convert_detection(
    result,
    class_id,
    confidence,
    box,
):
    """
    Convert a SAM 3 detection into our internal format.
    """

    names = result.names

    concept = names[class_id]

    normalized_name = CONCEPT_MAP.get(
        concept
    )

    if normalized_name is None:
        return None

    x1, y1, x2, y2 = box

    return {
        "object": normalized_name,
        "source_class": concept,
        "confidence": round(
            float(confidence),
            3
        ),
        "bounding_box": {
            "x1": round(float(x1), 2),
            "y1": round(float(y1), 2),
            "x2": round(float(x2), 2),
            "y2": round(float(y2), 2),
        },
        "source": "sam3",
    }


def detect_furniture_sam3(
    image_path: str,
    confidence_threshold: float = 0.25,
):
    """
    Detect furniture using SAM 3 text concepts.

    Raises FileNotFoundError when sam3.pt
    is not installed.
    """

    if not is_available():
        raise FileNotFoundError(
            f"SAM 3 checkpoint not found: {MODEL_PATH}"
        )

    predictor = get_model()

    predictor.set_image(
        str(image_path)
    )

    results = predictor(
        text=FURNITURE_CONCEPTS
    )

    detections = []

    for result in results:

        if result.boxes is None:
            continue

        boxes = result.boxes

        for index in range(
            len(boxes)
        ):

            confidence = float(
                boxes.conf[index]
            )

            if confidence < confidence_threshold:
                continue

            class_id = int(
                boxes.cls[index]
            )

            xyxy = boxes.xyxy[
                index
            ].tolist()

            detection = _convert_detection(
                result=result,
                class_id=class_id,
                confidence=confidence,
                box=xyxy,
            )

            if detection:
                detections.append(
                    detection
                )

    detections.sort(
        key=lambda item:
        item["confidence"],
        reverse=True,
    )

    return detections