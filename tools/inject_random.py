#!/usr/bin/python3
"""Larger, reproducible benchmark: random DRC violations + legal at-limit controls.

    /usr/bin/python3 tools/inject_random.py [--seed 20261011]
      -> work/bench.gds (top cell TOP) + work/bench_truth.json

* Violations are spread over four sub-blocks so the report has a real cell hierarchy.
* Every coordinate sits on the 0.005 µm manufacturing grid (except the deliberate off-grid cases),
  and shape sizes are chosen so each site can trip only the one rule it was built for.
* Controls are drawn exactly at the limit (or just above it, for area) and must NOT be flagged.
Limits are the SKY130 periphery values (data/sky130_periphery_rules.csv).
"""
import argparse
import json
import math
import os
import random

import klayout.db as db

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "work", "testchip_clean.gds")
OUT = os.path.join(HERE, "..", "work", "bench.gds")
TRUTH = os.path.join(HERE, "..", "work", "bench_truth.json")

LAYERS = {"poly": (66, 20), "li": (67, 20), "met1": (68, 20), "met2": (69, 20), "met3": (70, 20), "nsdm": (93, 44)}
GRID = 0.005
LENGTH = 2.0     # µm, long side of width/spacing test shapes
WIDE = 0.5       # µm, a safely legal width for the two shapes of a spacing test
PITCH = 6.0      # µm between sites
BLOCKS = ["blk_alu", "blk_ctrl", "blk_io", "blk_mem"]

# name, layer, manual rule the site should violate, kind, limit, violating range (lo, hi)
TYPES = [
    ("li.width",   "li",   "li.1",    "width",   0.17,   (0.08, 0.165)),
    ("li.space",   "li",   "li.3",    "spacing", 0.17,   (0.08, 0.165)),
    ("li.area",    "li",   "li.6",    "area",    0.0561, (0.17, 0.23)),
    ("m1.width",   "met1", "m1.1",    "width",   0.14,   (0.06, 0.135)),
    ("m1.space",   "met1", "m1.2",    "spacing", 0.14,   (0.06, 0.135)),
    ("m1.area",    "met1", "m1.6",    "area",    0.083,  (0.14, 0.28)),
    ("m2.width",   "met2", "m2.1",    "width",   0.14,   (0.06, 0.135)),
    ("m2.space",   "met2", "m2.2",    "spacing", 0.14,   (0.06, 0.135)),
    ("m2.area",    "met2", "m2.6",    "area",    0.0676, (0.14, 0.255)),
    ("m3.width",   "met3", "m3.1",    "width",   0.30,   (0.15, 0.295)),
    ("m3.space",   "met3", "m3.2",    "spacing", 0.30,   (0.15, 0.295)),
    ("m3.area",    "met3", "m3.6",    "area",    0.240,  (0.30, 0.48)),
    ("poly.width", "poly", "poly.1a", "width",   0.15,   (0.07, 0.145)),
    ("poly.space", "poly", "poly.2",  "spacing", 0.21,   (0.10, 0.205)),
    ("nsdm.width", "nsdm", "nsd.1",   "width",   0.38,   (0.20, 0.375)),
    ("m1.offgrid", "met1", "x.1b",    "offgrid", 0.005,  (0.001, 0.004)),
]


def snap(v):
    return round(round(v / GRID) * GRID, 3)


def shapes_for(kind, p, x, y):
    """Return list of DBox for one site. p = width / gap / square side / off-grid offset (µm)."""
    if kind == "width":
        return [db.DBox(x, y, x + p, y + LENGTH)]
    if kind == "spacing":
        return [db.DBox(x, y, x + WIDE, y + LENGTH), db.DBox(x + WIDE + p, y, x + 2 * WIDE + p, y + LENGTH)]
    if kind == "area":
        return [db.DBox(x, y, x + p, y + p)]
    if kind == "offgrid":
        return [db.DBox(x + p, y + p, x + p + 0.5, y + p + 0.5)]
    raise ValueError(kind)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=20261011)
    ap.add_argument("--min-per-type", type=int, default=10)
    ap.add_argument("--max-per-type", type=int, default=35)
    ap.add_argument("--controls-per-type", type=int, default=3)
    args = ap.parse_args()
    rng = random.Random(args.seed)

    ly = db.Layout()
    ly.read(SRC)
    top = ly.cell("TOP")
    cells = {b: ly.create_cell(b) for b in BLOCKS}
    sites = {b: 0 for b in BLOCKS}
    cols = 12
    truth = []

    def place(block, tname, layer, rule, kind, p, control):
        n = sites[block]
        sites[block] += 1
        x, y = (n % cols) * PITCH, (n // cols) * PITCH
        boxes = shapes_for(kind, p, x, y)
        li = ly.layer(*LAYERS[layer])
        for b in boxes:
            cells[block].shapes(li).insert(b)
        bb = boxes[0]
        for b in boxes[1:]:
            bb = bb + b
        truth.append({
            "id": f"{tname}#{len(truth)}", "type": tname, "cell": block, "layer": layer,
            "expected_rule": rule, "kind": kind, "param_um": p, "control": control,
            "bbox_um": [round(bb.left, 4), round(bb.bottom, 4), round(bb.right, 4), round(bb.top, 4)],
        })

    for tname, layer, rule, kind, limit, (lo, hi) in TYPES:
        for _ in range(rng.randint(args.min_per_type, args.max_per_type)):
            if kind == "offgrid":
                p = rng.choice([0.001, 0.002, 0.003, 0.004])
            else:
                p = snap(rng.uniform(lo, hi))
            place(rng.choice(BLOCKS), tname, layer, rule, kind, p, control=False)
        for _ in range(args.controls_per_type):
            if kind == "area":
                p = snap(math.ceil(math.sqrt(limit) / GRID) * GRID + GRID)   # just above the area limit
            elif kind == "offgrid":
                p = 0.0                                                      # on grid
            else:
                p = limit                                                    # exactly at the limit
            place(rng.choice(BLOCKS), tname, layer, rule, kind, p, control=True)

    for i, b in enumerate(BLOCKS):   # blocks side by side, well above the standard-cell row
        top.insert(db.CellInstArray(cells[b].cell_index(), db.Trans(db.DPoint(i * 80.0, 20.0).to_itype(ly.dbu))))

    ly.write(OUT)
    with open(TRUTH, "w") as f:
        json.dump({"seed": args.seed, "sites": truth}, f, indent=1)
    v = sum(not t["control"] for t in truth)
    print(f"wrote {os.path.normpath(OUT)}: {v} violating sites + {len(truth) - v} controls in {len(BLOCKS)} blocks")


if __name__ == "__main__":
    main()
