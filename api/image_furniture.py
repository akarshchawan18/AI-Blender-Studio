from typing import Dict, List


FURNITURE_ASSET_MAP = {
    "sofa": "Sofa_Modern",
    "l_shaped_sofa": "Sofa_LShape",
    "coffee_table": "CoffeeTable_Modern",
    "tv_unit": "TVUnit_Wood",
    "chair": "Chair_Modern",
    "bed": "Bed_Modern",
    "wardrobe": "Wardrobe_Modern",
    "desk": "Desk_Modern",
    "dining_table": "DiningTable_Modern",
    "lamp": "Lamp_Modern",
}


def normalize_furniture_name(name: str) -> str:
    name = str(name).lower().strip()

    aliases = {
        "couch": "sofa",
        "sectional sofa": "l_shaped_sofa",
        "sectional": "l_shaped_sofa",
        "center table": "coffee_table",
        "coffee table": "coffee_table",
        "tv": "tv_unit",
        "television": "tv_unit",
        "tv cabinet": "tv_unit",
        "office chair": "chair",
        "dining chair": "chair",
        "work desk": "desk",
        "study table": "desk",
        "bedside lamp": "lamp",
        "floor lamp": "lamp",
    }

    return aliases.get(name, name)


def map_furniture_to_asset(name: str):
    normalized = normalize_furniture_name(name)

    return FURNITURE_ASSET_MAP.get(normalized)


def build_furniture_intent(
    detections: List[Dict]
) -> List[Dict]:

    furniture = []

    for detection in detections:

        name = detection.get("object")

        if not name:
            continue

        normalized = normalize_furniture_name(name)

        asset = FURNITURE_ASSET_MAP.get(normalized)

        if asset is None:
            continue

        confidence = detection.get(
            "confidence",
            0.0
        )

        try:
            confidence = float(confidence)
        except (TypeError, ValueError):
            confidence = 0.0

        furniture.append(
            {
                "detected_object": normalized,
                "asset": asset,
                "confidence": round(
                    confidence,
                    3
                ),
                "bounding_box": detection.get(
                    "bounding_box"
                )
            }
        )

    return furniture