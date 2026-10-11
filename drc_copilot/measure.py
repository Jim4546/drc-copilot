"""Deterministic measurements from DRC markers — numbers the model must not be trusted to compute.

KLayout writes markers as e.g.
    edge-pair: (0,10;0,11.5)|(0.1,11.5;0.1,10)     # '|' = inside one polygon (width), '/' = between polygons (spacing)
    polygon: (12,10;12,10.2;12.2,10.2;12.2,10)     # e.g. an area violation
"""
import math
import re
from typing import Optional, Tuple

NUM = r"-?\d+(?:\.\d+)?(?:e-?\d+)?"
PAIR = re.compile(rf"edge-pair:\s*\(({NUM}),({NUM});({NUM}),({NUM})\)\s*[|/]\s*\(({NUM}),({NUM});({NUM}),({NUM})\)")
POLY = re.compile(r"polygon:\s*\(([^)]*)\)")
REQUIRED = re.compile(r":\s*(\d+(?:\.\d+)?)\s*um(²|2)?\s*$")


def _seg_point(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    L = dx * dx + dy * dy
    t = 0.0 if L == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def _seg_seg(a, b):
    (ax, ay, bx, by), (cx, cy, dx, dy) = a, b
    return min(_seg_point(ax, ay, cx, cy, dx, dy), _seg_point(bx, by, cx, cy, dx, dy),
               _seg_point(cx, cy, ax, ay, bx, by), _seg_point(dx, dy, ax, ay, bx, by))


def measure(value: str) -> Optional[Tuple[str, float]]:
    """('distance', µm) for edge pairs, ('area', µm²) for polygons, None if not understood."""
    m = PAIR.search(value)
    if m:
        v = [float(x) for x in m.groups()]
        return "distance", round(_seg_seg(v[:4], v[4:]), 4)
    m = POLY.search(value)
    if m:
        pts = [tuple(float(c) for c in p.split(",")) for p in m.group(1).split(";") if p]
        area = 0.5 * abs(sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1])))
        return "area", round(area, 5)
    return None


def required(description: str) -> Optional[Tuple[str, float]]:
    """Limit stated in the deck description, e.g. 'm1.1 : min. m1 width : 0.14um' -> ('distance', 0.14)."""
    m = REQUIRED.search(description or "")
    if not m:
        return None
    return ("area" if m.group(2) else "distance"), float(m.group(1))
