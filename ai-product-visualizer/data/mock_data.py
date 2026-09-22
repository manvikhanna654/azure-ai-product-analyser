"""Placeholder data used to preview the interface.

Nothing here is produced by a model. Every structure mirrors the shape the
UI expects, so a real response can be dropped in later without touching the
view code.

Expected analysis contract
--------------------------
{
    "overview":   {"category", "product_type", "primary_color", "material", "style"},
    "attributes": {"colors": [{"name", "hex"}], "material": [...], "shape": [...],
                   "style": [...], "features": [...]},
    "description": str,
    "confidence":  {"label": str, "score": int}   # score 0-100
}
"""

from datetime import datetime

# --- previewed analysis ------------------------------------------------------

SAMPLE_ANALYSIS = {
    "overview": {
        "Category": "Footwear",
        "Product Type": "Low-top sneaker",
        "Primary Color": "Off-white",
        "Material": "Leather / textile",
        "Style": "Minimal streetwear",
    },
    "attributes": {
        "Colors": [
            {"name": "Off-white", "hex": "#E9E5DC"},
            {"name": "Slate grey", "hex": "#5A6472"},
            {"name": "Gum brown", "hex": "#9C6B45"},
        ],
        "Material": ["Smooth leather upper", "Textile lining", "Rubber outsole"],
        "Shape": ["Low-top silhouette", "Rounded toe box", "Flat sole profile"],
        "Style": ["Minimal", "Everyday casual", "Unisex"],
        "Features": [
            "Perforated side panel",
            "Padded collar",
            "Flat cotton laces",
            "Stitched side overlay",
        ],
    },
    "description": (
        "A low-top sneaker built around a clean, uninterrupted upper. The off-white "
        "leather is broken only by a slate-grey side overlay and a perforated panel "
        "that runs toward the midfoot. A gum-brown rubber outsole wraps the base with "
        "a shallow tread, and the padded collar sits low at the ankle. The overall "
        "read is minimal and versatile: a neutral everyday shoe that leans casual "
        "rather than athletic."
    ),
    "confidence": {"label": "High confidence", "score": 94},
}

# --- previewed Q&A -----------------------------------------------------------

SUGGESTED_QUESTIONS = [
    "What material does this product appear to use?",
    "What are its main visual features?",
    "How would you describe its style?",
]

SAMPLE_ANSWERS = {
    SUGGESTED_QUESTIONS[0]: (
        "The upper reads as smooth leather with a textile lining, and the sole "
        "appears to be moulded rubber."
    ),
    SUGGESTED_QUESTIONS[1]: (
        "A perforated side panel, a stitched grey overlay, a padded collar and flat "
        "cotton laces are the elements that stand out most."
    ),
    SUGGESTED_QUESTIONS[2]: (
        "Minimal and neutral. It sits closer to everyday casual wear than to "
        "performance footwear."
    ),
}

DEFAULT_ANSWER = (
    "This panel is a layout preview. Once the model is connected, answers about the "
    "uploaded image will appear here."
)

# --- previewed history -------------------------------------------------------

SAMPLE_HISTORY = [
    {
        "id": "an_1042",
        "name": "Low-top sneaker",
        "category": "Footwear",
        "date": "18 Sep 2026",
        "tint": "#8A93A3",
        "image_url": "https://images.unsplash.com/photo-1608231387042-66d1773070a5?auto=format&fit=crop&w=900&q=85",
        "analysis": SAMPLE_ANALYSIS,
    },
    {
        "id": "an_1041",
        "name": "Ceramic pour-over mug",
        "category": "Kitchenware",
        "date": "16 Sep 2026",
        "tint": "#C9A27A",
        "image_url": "https://www.publicgoods.com/cdn/shop/files/pour_over_coffee_maker_lifestyle_01.jpg?v=1752895636",
        "analysis": SAMPLE_ANALYSIS,
    },
    {
        "id": "an_1039",
        "name": "Canvas weekender bag",
        "category": "Bags & luggage",
        "date": "12 Sep 2026",
        "tint": "#6F8A72",
        "image_url": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=900&q=85",
        "analysis": SAMPLE_ANALYSIS,
    },
    {
        "id": "an_1036",
        "name": "Wireless over-ear headphones",
        "category": "Electronics",
        "date": "09 Sep 2026",
        "tint": "#7C5CFF",
        "image_url": "https://images.unsplash.com/photo-1599955051125-571f47e04316?auto=format&fit=crop&w=900&q=85",
        "analysis": SAMPLE_ANALYSIS,
    },
]


def new_history_entry(name: str, analysis: dict, tint: str = "#7C5CFF") -> dict:
    """Build a history record for an analysis produced in this session."""
    return {
        "id": f"an_{datetime.now().strftime('%H%M%S')}",
        "name": name,
        "category": analysis["overview"]["Category"],
        "date": datetime.now().strftime("%d %b %Y"),
        "tint": tint,
        "analysis": analysis,
    }
