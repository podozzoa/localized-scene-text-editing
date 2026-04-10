from __future__ import annotations

from app.domain.models import BBox, Point


def clamp_bbox(bbox: BBox, image_width: int, image_height: int) -> BBox:
    x, y, w, h = bbox
    x = max(0, min(x, image_width - 1))
    y = max(0, min(y, image_height - 1))
    w = max(1, min(w, image_width - x))
    h = max(1, min(h, image_height - y))
    return (x, y, w, h)


def polygon_to_bbox(polygon: list[Point]) -> BBox:
    xs = [p[0] for p in polygon]
    ys = [p[1] for p in polygon]
    min_x = min(xs)
    min_y = min(ys)
    max_x = max(xs)
    max_y = max(ys)
    return (min_x, min_y, max_x - min_x, max_y - min_y)
