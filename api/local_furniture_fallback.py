ROOM_FURNITURE_DEFAULTS = {
    "living_room": [
        {
            "asset": "Sofa_Modern",
            "detected_object": "sofa",
            "confidence": 0.55,
            "source": "room_inference"
        },
        {
            "asset": "CoffeeTable_Modern",
            "detected_object": "coffee_table",
            "confidence": 0.50,
            "source": "room_inference"
        },
        {
            "asset": "TVUnit_Wood",
            "detected_object": "tv_unit",
            "confidence": 0.45,
            "source": "room_inference"
        }
    ],

    "bedroom": [
        {
            "asset": "Bed_Modern",
            "detected_object": "bed",
            "confidence": 0.60,
            "source": "room_inference"
        },
        {
            "asset": "Wardrobe_Modern",
            "detected_object": "wardrobe",
            "confidence": 0.50,
            "source": "room_inference"
        },
        {
            "asset": "Lamp_Modern",
            "detected_object": "lamp",
            "confidence": 0.40,
            "source": "room_inference"
        }
    ],

    "office": [
        {
            "asset": "Desk_Modern",
            "detected_object": "desk",
            "confidence": 0.60,
            "source": "room_inference"
        },
        {
            "asset": "Chair_Modern",
            "detected_object": "chair",
            "confidence": 0.55,
            "source": "room_inference"
        },
        {
            "asset": "Lamp_Modern",
            "detected_object": "lamp",
            "confidence": 0.40,
            "source": "room_inference"
        }
    ],

    "dining_room": [
        {
            "asset": "DiningTable_Modern",
            "detected_object": "dining_table",
            "confidence": 0.60,
            "source": "room_inference"
        },
        {
            "asset": "Chair_Modern",
            "detected_object": "chair",
            "confidence": 0.50,
            "source": "room_inference"
        },
        {
            "asset": "Lamp_Modern",
            "detected_object": "lamp",
            "confidence": 0.40,
            "source": "room_inference"
        }
    ],

    "kitchen": [],

    "bathroom": []
}


def infer_furniture_from_room(room_type):
    """
    Provides a safe furniture prior when visual detection
    cannot identify furniture.

    IMPORTANT:
    These are NOT visual detections.
    They are room-based assumptions.
    """

    if not isinstance(room_type, str):
        return []

    room_type = room_type.lower().strip()

    furniture = ROOM_FURNITURE_DEFAULTS.get(
        room_type,
        []
    )

    return [
        dict(item)
        for item in furniture
    ]