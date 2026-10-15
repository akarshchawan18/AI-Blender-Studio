from pathlib import Path

from ultralytics import YOLO


PROJECT_DIR = Path(__file__).resolve().parent.parent

MODEL_DIR = PROJECT_DIR / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH = MODEL_DIR / "yolo26n.pt"

MODEL = None


# COCO classes -> our interior-design categories
OBJECT_MAP = {
    "couch": "sofa",
    "chair": "chair",
    "dining table": "dining_table",
    "bed": "bed",
    "tv": "tv",
    "laptop": "laptop",
}


# Classes that are actually useful for interior reconstruction.
INTERIOR_CLASSES = {
    "couch",
    "chair",
    "dining table",
    "bed",
    "tv",
}


def get_model():
    global MODEL

    if MODEL is None:
        MODEL = YOLO(str(MODEL_PATH))

    return MODEL


def _calculate_area(box):
    x1, y1, x2, y2 = box

    width = max(0.0, x2 - x1)
    height = max(0.0, y2 - y1)

    return width * height


def _calculate_center(box):
    x1, y1, x2, y2 = box

    return {
        "x": round((x1 + x2) / 2, 2),
        "y": round((y1 + y2) / 2, 2),
    }


def detect_furniture(
    image_path: str,
    confidence_threshold: float = 0.10,
    image_size: int = 1280,
):
    """
    Detect furniture/interior objects using YOLO26.

    This is intentionally conservative:
    - Only interior-relevant COCO classes are accepted.
    - Very low-confidence detections are allowed because
      indoor furniture can be difficult for generic COCO models.
    - Results are filtered and normalized before being returned.
    """

    image_path = str(image_path)

    model = get_model()

    results = model.predict(
        source=image_path,
        conf=confidence_threshold,
        imgsz=image_size,
        verbose=False,
    )

    detections = []

    for result in results:

        if result.boxes is None:
            continue

        image_width = None
        image_height = None

        if result.orig_shape:
            image_height, image_width = result.orig_shape

        for box in result.boxes:

            class_id = int(box.cls[0])
            confidence = float(box.conf[0])

            original_name = result.names[class_id]

            if original_name not in INTERIOR_CLASSES:
                continue

            normalized_name = OBJECT_MAP.get(original_name)

            if normalized_name is None:
                continue

            xyxy = box.xyxy[0].tolist()

            x1, y1, x2, y2 = xyxy

            area = _calculate_area(xyxy)

            image_area = None

            if image_width and image_height:
                image_area = float(image_width * image_height)

            relative_area = 0.0

            if image_area and image_area > 0:
                relative_area = area / image_area

            detections.append(
                {
                    "object": normalized_name,
                    "source_class": original_name,
                    "confidence": round(confidence, 3),

                    "bounding_box": {
                        "x1": round(x1, 2),
                        "y1": round(y1, 2),
                        "x2": round(x2, 2),
                        "y2": round(y2, 2),
                    },

                    "center": _calculate_center(xyxy),

                    "area": round(area, 2),

                    "relative_area": round(
                        relative_area,
                        5
                    ),
                }
            )

    # Highest-confidence detections first.
    detections.sort(
        key=lambda item: item["confidence"],
        reverse=True
    )

    return detections