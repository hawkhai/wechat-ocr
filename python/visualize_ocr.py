"""
visualize_ocr.py - Visualize WeChat OCR results on images.

JSON format fields used:
  imgpath, width, height, ocr_response[]:
    text, rate, bold, line_box (4 corners), details[]: chars + ltrb bbox

Usage:
  python visualize_ocr.py [json_path] [output_path]
  python visualize_ocr.py               # defaults to test.json
"""

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def load_result(json_path):
    for enc in ("utf-8", "utf-8-sig", "gbk", "gb2312"):
        try:
            with open(json_path, "r", encoding=enc) as f:
                return json.load(f)
        except (UnicodeDecodeError, ValueError):
            continue
    raise RuntimeError(f"Cannot decode JSON file: {json_path}")


def get_font(size=14):
    font_candidates = [
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simsun.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for fp in font_candidates:
        if Path(fp).exists():
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                continue
    return ImageFont.load_default()


def draw_polygon(draw, points, color, width=2):
    """Draw a closed polygon from a list of (x, y) points."""
    for i in range(len(points)):
        p1 = points[i]
        p2 = points[(i + 1) % len(points)]
        draw.line([p1, p2], fill=color, width=width)


def confidence_color(confidence):
    """Map confidence (0.0-1.0) to red(low) -> yellow(mid) -> green(high)."""
    if confidence is None:
        return (128, 128, 128)
    c = max(0.0, min(1.0, confidence))
    if c < 0.5:
        r, g = 255, int(255 * c * 2)
    else:
        r, g = int(255 * (1.0 - c) * 2), 255
    return (r, g, 0)


def split_overlapping_boxes(boxes):
    """Resolve horizontal overlaps between adjacent char boxes by splitting at midpoints.

    Each box is (left, top, right, bottom). For each adjacent pair where
    boxes[i].right > boxes[i+1].left, replace the boundary with their midpoint.
    """
    if not boxes:
        return boxes
    boxes = list(boxes)
    for i in range(len(boxes) - 1):
        l0, t0, r0, b0 = boxes[i]
        l1, t1, r1, b1 = boxes[i + 1]
        if r0 > l1:
            mid = (r0 + l1) / 2.0
            boxes[i]     = (l0, t0, mid, b0)
            boxes[i + 1] = (mid, t1, r1, b1)
    return boxes


def visualize_ocr(json_path, output_path=None):
    data = load_result(json_path)

    img_file = data.get("imgpath", str(Path(json_path).with_suffix(".png")))
    img = Image.open(img_file).convert("RGB")
    draw = ImageDraw.Draw(img)

    font = get_font(16)
    font_small = get_font(12)

    line_color = (255, 0, 0)       # red for line_box outline
    char_color = (0, 128, 255)     # blue for character boxes
    text_color = (0, 200, 0)       # green for line text labels
    bold_color = (255, 128, 0)     # orange for bold lines
    info_color = (200, 200, 0)     # yellow for metadata

    # Draw image-level metadata
    items = data.get("ocr_response", [])
    meta = f"Lines: {len(items)}  Size: {data.get('width', '?')}x{data.get('height', '?')}  Time: {data.get('time_used', '?')}ms"
    draw.text((5, 5), meta, fill=info_color, font=font_small)

    for item in items:
        rate = item.get("rate")
        bold = item.get("bold", False)
        current_line_color = bold_color if bold else line_color

        # Draw line_box polygon (4 corner points)
        line_box = item.get("line_box")
        if line_box and len(line_box) == 4:
            pts = [tuple(p) for p in line_box]
            draw_polygon(draw, pts, current_line_color, width=2)

            # Text label above the first corner
            min_x = min(p[0] for p in pts)
            min_y = min(p[1] for p in pts)
            label = item.get("text", "")
            rate_tag = f" [{rate:.2f}]" if rate is not None else ""
            bold_tag = " [B]" if bold else ""
            draw.text((min_x, max(min_y - 20, 0)), label + rate_tag + bold_tag,
                      fill=text_color, font=font)

        # Draw character-level bounding boxes (split overlaps at midpoints)
        details = item.get("details", [])
        boxes = [(d["left"], d["top"], d["right"], d["bottom"]) for d in details]
        boxes = split_overlapping_boxes(boxes)
        for detail, (l, t, r, b) in zip(details, boxes):
            draw.rectangle([l, t, r, b], outline=char_color, width=1)
            draw.text((l, max(t - 14, 0)), detail["chars"], fill=char_color, font=font_small)

    if output_path is None:
        stem = Path(json_path).stem
        output_path = Path(json_path).parent / f"{stem}_vis.png"

    img.save(output_path)
    print(f"Saved visualization to: {output_path}")
    img.show()


if __name__ == "__main__":
    base_dir = Path(__file__).parent
    json_path = base_dir / "test.json"

    if len(sys.argv) >= 2:
        json_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) >= 3 else None

    visualize_ocr(str(json_path), output_path)
