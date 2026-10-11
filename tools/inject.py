#!/usr/bin/python3
"""Inject known DRC violations into the clean test chip, and record the ground truth.

    /usr/bin/python3 tools/inject.py  ->  work/testchip_injected.gds + work/ground_truth.json

Each injection sits in its own empty area above the standard-cell row, far enough from its
neighbours that it can only trip the one rule it was designed for. Rule values come from the
SKY130 periphery rule table (data/sky130_periphery_rules.csv).
"""
import json
import os

import klayout.db as db

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "work", "testchip_clean.gds")
OUT = os.path.join(HERE, "..", "work", "testchip_injected.gds")
TRUTH = os.path.join(HERE, "..", "work", "ground_truth.json")

LAYERS = {"poly": (66, 20), "li": (67, 20), "met1": (68, 20), "met2": (69, 20), "met3": (70, 20)}

# id, layer, expected manual rule, kind, size parameter (µm), what the rule requires
INJECTIONS = [
    ("W-m1",   "met1", "m1.1",    "width",   0.10, "metal1 width >= 0.140"),
    ("S-m1",   "met1", "m1.2",    "spacing", 0.10, "metal1 spacing >= 0.140"),
    ("A-m1",   "met1", "m1.6",    "area",    0.20, "metal1 area >= 0.083 um2"),
    ("W-m2",   "met2", "m2.1",    "width",   0.10, "metal2 width >= 0.140"),
    ("S-m2",   "met2", "m2.2",    "spacing", 0.10, "metal2 spacing >= 0.140"),
    ("W-m3",   "met3", "m3.1",    "width",   0.20, "metal3 width >= 0.300"),
    ("W-li",   "li",   "li.1",    "width",   0.12, "li width >= 0.170"),
    ("S-li",   "li",   "li.3",    "spacing", 0.12, "li spacing >= 0.170"),
    ("W-poly", "poly", "poly.1a", "width",   0.10, "poly width >= 0.150"),
    ("S-poly", "poly", "poly.2",  "spacing", 0.15, "poly spacing >= 0.210"),
]

PITCH = 6.0      # µm between injection sites
Y0 = 10.0        # µm, well above the 2.72 µm cell row
LENGTH = 1.5     # µm, long side of each test shape
WIDE = 0.5       # µm, a safely legal width for spacing tests


def um_box(x1, y1, x2, y2):
    return db.DBox(x1, y1, x2, y2)


def main():
    ly = db.Layout()
    ly.read(SRC)
    top = ly.cell("TOP")
    truth = []
    for i, (iid, layer, rule, kind, p, requirement) in enumerate(INJECTIONS):
        li = ly.layer(*LAYERS[layer])
        x, y = i * PITCH, Y0
        if kind == "width":
            shapes = [um_box(x, y, x + p, y + LENGTH)]
        elif kind == "spacing":
            shapes = [um_box(x, y, x + WIDE, y + LENGTH), um_box(x + WIDE + p, y, x + 2 * WIDE + p, y + LENGTH)]
        elif kind == "area":
            shapes = [um_box(x, y, x + p, y + p)]
        else:
            raise ValueError(kind)
        for b in shapes:
            top.shapes(li).insert(b)
        bbox = shapes[0]
        for b in shapes[1:]:
            bbox = bbox + b
        truth.append({
            "id": iid, "layer": layer, "expected_rule": rule, "kind": kind, "param_um": p,
            "requirement": requirement,
            "bbox_um": [round(bbox.left, 3), round(bbox.bottom, 3), round(bbox.right, 3), round(bbox.top, 3)],
        })
    ly.write(OUT)
    with open(TRUTH, "w") as f:
        json.dump(truth, f, indent=2)
    print(f"wrote {os.path.normpath(OUT)} with {len(truth)} injections; truth -> {os.path.normpath(TRUTH)}")


if __name__ == "__main__":
    main()
