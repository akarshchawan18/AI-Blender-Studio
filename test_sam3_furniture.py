from ultralytics.models.sam import SAM3SemanticPredictor

IMAGE = r"C:\Users\akars\Pictures\building.jpeg"

CONCEPTS = [
    "sofa",
    "chair",
    "coffee table",
    "bed",
    "wardrobe",
    "desk",
    "dining table",
    "television",
    "lamp",
]

overrides = {
    "conf": 0.20,
    "task": "segment",
    "mode": "predict",
    "model": "sam3.pt",
    "quantize": 16,
    "verbose": False,
}

print("Loading SAM 3...")

predictor = SAM3SemanticPredictor(
    overrides=overrides
)

print("Loading image...")

predictor.set_image(IMAGE)

print("Running concepts...")

results = predictor(
    text=CONCEPTS
)

print()
print("=" * 70)
print("SAM 3 INTERIOR OBJECT DETECTIONS")
print("=" * 70)

for result in results:

    print()
    print("RESULT")

    if result.boxes is None:
        print("No boxes returned.")
        continue

    boxes = result.boxes

    if len(boxes) == 0:
        print("No objects detected.")
        continue

    names = result.names

    for i, box in enumerate(boxes):

        class_id = int(box.cls[i])
        confidence = float(box.conf[i])

        xyxy = box.xyxy[i].tolist()

        class_name = names[class_id]

        print(
            f"{class_name:20s} "
            f"confidence={confidence:.3f} "
            f"box={[round(x, 1) for x in xyxy]}"
        )

print()
print("=" * 70)
print("TEST COMPLETE")
print("=" * 70)
