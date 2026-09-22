"""Locally generated placeholder imagery and inline icons.

No network requests: thumbnails are drawn with Pillow so the interface can be
previewed offline.
"""

import base64
from io import BytesIO

from PIL import Image, ImageDraw


def _hex_to_rgb(value: str):
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def placeholder_image(
    tint: str = "#7C5CFF", size: int = 480, product: str = ""
) -> Image.Image:
    """Create a polished local product thumbnail for previews and history."""
    base = Image.new("RGB", (size, size), (242, 245, 249))
    draw = ImageDraw.Draw(base, "RGBA")
    r, g, b = _hex_to_rgb(tint)

    # editorial backdrop with a soft color wash
    for i in range(18, 0, -1):
        alpha = int(3 + i * 1.8)
        pad = size * (0.035 * i)
        draw.ellipse(
            [-pad, -pad, size * 0.82 + pad, size * 0.82 + pad],
            fill=(r, g, b, alpha),
        )
    draw.ellipse(
        [size * .18, size * .12, size * .84, size * .82],
        fill=(255, 255, 255, 42),
    )

    key = product.lower()
    ink = (25, 32, 45, 235)
    shadow = (35, 42, 55, 38)

    # Product-specific silhouettes make history cards feel like real product records.
    if "sneaker" in key or "shoe" in key:
        draw.ellipse([size*.18, size*.70, size*.83, size*.82], fill=shadow)
        draw.rounded_rectangle([size*.20, size*.43, size*.75, size*.70], radius=int(size*.09), fill=(248, 247, 242, 255), outline=ink, width=max(2, size//120))
        draw.polygon([(size*.19, size*.59), (size*.48, size*.57), (size*.74, size*.68), (size*.80, size*.75), (size*.22, size*.75)], fill=(234, 230, 220, 255), outline=ink)
        draw.line([size*.43, size*.48, size*.52, size*.64], fill=(r, g, b, 210), width=max(3, size//70))
        draw.line([size*.48, size*.47, size*.57, size*.61], fill=(r, g, b, 180), width=max(2, size//90))
    elif "mug" in key or "ceramic" in key:
        draw.ellipse([size*.27, size*.29, size*.70, size*.42], fill=(248, 245, 238, 255), outline=ink, width=max(2, size//120))
        draw.rounded_rectangle([size*.29, size*.34, size*.68, size*.70], radius=int(size*.08), fill=(244, 239, 229, 255), outline=ink, width=max(2, size//120))
        draw.arc([size*.59, size*.40, size*.84, size*.64], 270, 90, fill=ink, width=max(2, size//110))
        draw.ellipse([size*.34, size*.34, size*.63, size*.41], fill=(r, g, b, 180))
    elif "bag" in key or "weekender" in key:
        draw.ellipse([size*.16, size*.73, size*.85, size*.82], fill=shadow)
        draw.rounded_rectangle([size*.22, size*.34, size*.78, size*.72], radius=int(size*.08), fill=(r, g, b, 210), outline=ink, width=max(2, size//120))
        draw.arc([size*.33, size*.13, size*.67, size*.48], 180, 360, fill=ink, width=max(3, size//85))
        draw.line([size*.31, size*.52, size*.69, size*.52], fill=(255,255,255,90), width=max(2, size//120))
    elif "headphone" in key:
        draw.ellipse([size*.24, size*.22, size*.76, size*.76], outline=ink, width=max(4, size//70))
        draw.rounded_rectangle([size*.17, size*.48, size*.36, size*.72], radius=int(size*.07), fill=(r, g, b, 235), outline=ink, width=max(2, size//120))
        draw.rounded_rectangle([size*.64, size*.48, size*.83, size*.72], radius=int(size*.07), fill=(r, g, b, 235), outline=ink, width=max(2, size//120))
        draw.arc([size*.31, size*.25, size*.69, size*.63], 190, 350, fill=(255,255,255,120), width=max(2, size//100))
    else:
        draw.rounded_rectangle([size*.27, size*.27, size*.73, size*.73], radius=int(size*.08), fill=(r, g, b, 90), outline=(r, g, b, 180), width=max(2, size//120))
        draw.line([size*.31, size*.59, size*.69, size*.59], fill=(r, g, b, 170), width=max(2, size//110))
    return base


def image_data_uri(img: Image.Image, fmt: str = "PNG") -> str:
    buf = BytesIO()
    img.save(buf, format=fmt)
    return f"data:image/{fmt.lower()};base64," + base64.b64encode(buf.getvalue()).decode()


# --- inline icons (stroke inherits from CSS) --------------------------------

ICON_SCAN = (
    '<svg viewBox="0 0 24 24" fill="none" stroke-width="1.8" stroke-linecap="round" '
    'stroke-linejoin="round"><path d="M3 8V5a2 2 0 0 1 2-2h3M16 3h3a2 2 0 0 1 2 2v3'
    'M21 16v3a2 2 0 0 1-2 2h-3M8 21H5a2 2 0 0 1-2-2v-3"/><circle cx="12" cy="12" r="3"/></svg>'
)

ICON_TEXT = (
    '<svg viewBox="0 0 24 24" fill="none" stroke-width="1.8" stroke-linecap="round" '
    'stroke-linejoin="round"><path d="M4 6h16M4 12h16M4 18h10"/></svg>'
)

ICON_CHAT = (
    '<svg viewBox="0 0 24 24" fill="none" stroke-width="1.8" stroke-linecap="round" '
    'stroke-linejoin="round"><path d="M21 12a8 8 0 0 1-8 8H7l-4 3v-5.5A8 8 0 0 1 '
    '11 4h2a8 8 0 0 1 8 8z"/></svg>'
)

ICON_LAYERS = (
    '<svg viewBox="0 0 24 24" fill="none" stroke-width="1.8" stroke-linecap="round" '
    'stroke-linejoin="round"><path d="M12 3 3 8l9 5 9-5-9-5zM3 16l9 5 9-5M3 12l9 5 9-5"/></svg>'
)
