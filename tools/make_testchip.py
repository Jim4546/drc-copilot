#!/usr/bin/python3
"""Build a small, realistic test layout: one row of abutted SKY130 standard cells.

    /usr/bin/python3 tools/make_testchip.py  ->  work/testchip_clean.gds  (top cell TOP)
"""
import os

import klayout.db as db

PDK = os.path.expanduser("~/.volare/sky130A")
LIB = os.path.join(PDK, "libs.ref/sky130_fd_sc_hd/gds/sky130_fd_sc_hd.gds")
OUT = os.path.join(os.path.dirname(__file__), "..", "work", "testchip_clean.gds")
PR_BOUNDARY = (235, 4)   # place-and-route boundary: cells abut on it

CELLS = [
    "sky130_fd_sc_hd__tapvpwrvgnd_1", "sky130_fd_sc_hd__inv_1", "sky130_fd_sc_hd__nand2_1",
    "sky130_fd_sc_hd__nor2_1", "sky130_fd_sc_hd__and2_1", "sky130_fd_sc_hd__or2_1",
    "sky130_fd_sc_hd__xor2_1", "sky130_fd_sc_hd__mux2_1", "sky130_fd_sc_hd__a21oi_1",
    "sky130_fd_sc_hd__o21ai_1", "sky130_fd_sc_hd__dfxtp_1", "sky130_fd_sc_hd__buf_2",
    "sky130_fd_sc_hd__tapvpwrvgnd_1",
]


def main():
    lib = db.Layout()
    lib.read(LIB)
    out = db.Layout()
    out.dbu = lib.dbu
    top = out.create_cell("TOP")
    pr = lib.layer(*PR_BOUNDARY)

    x = 0
    for name in CELLS:
        src = lib.cell(name)
        if src is None:
            raise SystemExit(f"cell not found: {name}")
        tgt = out.create_cell(name) if out.cell(name) is None else out.cell(name)
        if tgt.is_empty():
            tgt.copy_tree(src)
        box = src.bbox_per_layer(pr)
        if box.empty():
            box = src.bbox()
        top.insert(db.CellInstArray(tgt.cell_index(), db.Trans(x - box.left, 0)))
        x += box.width()

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    out.write(OUT)
    print(f"wrote {os.path.normpath(OUT)}: {len(CELLS)} cells, row width {x * out.dbu:.2f} um")


if __name__ == "__main__":
    main()
