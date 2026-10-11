# DRC triage report

- Source: `bench.lyrdb`
- Violations: **388** in **16** rule groups
- Mode: rule grouping + retrieved rule text + GLM explanation

| # | Rule | Count | Worst measured | Top cells | Rule text found |
|---|---|---|---|---|---|
| 1 | `m1_OFFGRID` | 72 | — | blk_alu, blk_ctrl, blk_mem | normalized |
| 2 | `m2.1` | 29 | 0.065 µm (required ≥ 0.14 µm) | blk_ctrl, blk_mem, blk_io | exact |
| 3 | `li.3` | 28 | 0.08 µm (required ≥ 0.17 µm) | blk_io, blk_ctrl, blk_mem | exact |
| 4 | `m1.2` | 27 | 0.06 µm (required ≥ 0.14 µm) | blk_alu, blk_io, blk_ctrl | exact |
| 5 | `m2.6` | 26 | 0.02102 µm² (required ≥ 0.0676 µm²) | blk_mem, blk_alu, blk_ctrl | exact |
| 6 | `m3.6` | 26 | 0.11903 µm² (required ≥ 0.24 µm²) | blk_io, blk_ctrl, blk_mem | exact |
| 7 | `li.1` | 25 | 0.08 µm (required ≥ 0.17 µm) | blk_ctrl, blk_io, blk_alu | exact |
| 8 | `m3.1` | 24 | 0.155 µm (required ≥ 0.3 µm) | blk_mem, blk_ctrl, blk_alu | exact |
| 9 | `li.6` | 20 | 0.03063 µm² (required ≥ 0.0561 µm²) | blk_ctrl, blk_mem, blk_alu | exact |
| 10 | `m2.2` | 20 | 0.06 µm (required ≥ 0.14 µm) | blk_io, blk_mem, blk_alu | exact |
| 11 | `nsdm.2` | 18 | 0.2 µm (required ≥ 0.38 µm) | blk_alu, blk_io, blk_mem | corrected |
| 12 | `m1.1` | 16 | 0.065 µm (required ≥ 0.14 µm) | blk_mem, blk_io, blk_ctrl | exact |
| 13 | `poly.2` | 16 | 0.105 µm (required ≥ 0.21 µm) | blk_alu, blk_ctrl, blk_io | exact |
| 14 | `m1.6` | 15 | 0.0225 µm² (required ≥ 0.083 µm²) | blk_ctrl, blk_mem, blk_alu | exact |
| 15 | `m3.2` | 15 | 0.165 µm (required ≥ 0.3 µm) | blk_alu, blk_io, blk_mem | exact |
| 16 | `poly.1a` | 11 | 0.095 µm (required ≥ 0.15 µm) | blk_alu, blk_ctrl, blk_io | exact |

## 1. `m1_OFFGRID` — 72 violation(s)

**Deck description:** x.1b : OFFGRID vertex on m1  
**Worst measured:** —  
**Rule manual (normalized):**
> (x.1b) General: Data for SKY130 layout and mask on all layers except those mentioned in 1a must be on a grid of the stated value (except inside Seal ring) [unit corrected: source table says mm] = 0.005 µm

**What:** Rule x.1b requires that m1 (and all layers not exempted in 1a) have all vertices on a 0.005 µm grid ('must be on a grid of the stated value ... = 0.005 µm', except inside the Seal ring); the checker reports 72 violations with sample vertices at coordinates like x=0.003, y=48.003 and 0.503/48.503 µm, i.e. off-grid by about 0.003 µm (3 nm).
**Likely causes:**
- Shapes or vertices placed at coordinates not divisible by 0.005 µm (e.g. 0.003, 48.003, 0.503, 48.503), often from manual edits or pin/marker geometry
- Placement offsets or rotations of cell instances that shift otherwise on-grid geometry onto a fractional grid
- Imported GDS/IP or resized shapes (scaling/rounding) that introduce sub-0.005 µm coordinate components
**Suggested fixes:**
- Snap all m1 vertices in blk_alu, blk_ctrl, blk_mem and blk_io to the 0.005 µm manufacturing grid (e.g. round 0.003 → 0.000 or 0.005, 48.503 → 48.505 or 48.500)
- Check instance placements, origins and rotations of the offending cells for fractional offsets and correct them so all hierarchy levels stay on-grid
- Enable/verify grid snapping in the layout editor (0.005 µm) and re-run DRC to confirm the 72 violations clear

## 2. `m2.1` — 29 violation(s)

**Deck description:** m2.1 : min. m2 width : 0.14um  
**Worst measured:** 0.065 µm (required ≥ 0.14 µm)  
**Rule manual (exact):**
> (m2.1) Metal 2: Width of metal 2 = 0.140 µm

**What:** Rule m2.1 requires the width of metal 2 to be 0.140 µm ('Metal 2: Width of metal 2 = 0.140 µm'), but the worst measured m2 width is 0.065 µm.
**Likely causes:**
- m2 wires drawn below 0.14 µm (markers show 0.12 µm, 0.13 µm and 0.085 µm wide segments, e.g. edges 0.12 µm apart at x=54/54.12)
- router or manual routing using a minimum width smaller than 0.14 µm for m2
- thin m2 slivers or necking left in blk_ctrl, blk_mem, blk_io, blk_alu
**Suggested fixes:**
- Stretch or reshape the flagged m2 shapes so every m2 segment is at least 0.14 µm wide (e.g., widen the 0.065 µm worst-case wire)
- Reroute or edit the affected nets in blk_ctrl, blk_mem, blk_io, blk_alu with m2 minimum width set to 0.14 µm
- Remove or enlarge any stray narrow m2 slivers, then re-run DRC to confirm all 29 violations clear

## 3. `li.3` — 28 violation(s)

**Deck description:** li.3 : min. li spacing outside or crossing areaid:ce : 0.17um  
**Worst measured:** 0.08 µm (required ≥ 0.17 µm)  
**Rule manual (exact):**
> (li.3) Local Interconnect (LI): Spacing of LI to LI (except for li.3a) = 0.170 µm

**What:** The rule requires LI-to-LI spacing of 0.170 µm ('Spacing of LI to LI (except for li.3a) = 0.170 µm'), but the worst measured spacing is 0.08 µm (28 violations across blk_io, blk_ctrl, blk_mem, blk_alu).
**Likely causes:**
- Parallel LI wires routed side-by-side on a pitch tighter than 0.17 µm (markers show parallel vertical edges, e.g., 0.13 µm apart between x=30.5 and x=30.63)
- LI shapes jogged or expanded during routing so adjacent edges ended up closer than the minimum
- Two independent LI nets brought close together near pins or junctions without a final spacing check
**Suggested fixes:**
- Shift or shrink one of the offending LI shapes so the edge-to-edge gap is at least 0.17 µm (e.g., move the edge at x=30.63 to x>=30.67 relative to the edge at x=30.5)
- Reroute one of the two LI wires on a different track or on a different layer (e.g., m1) to open up the required spacing
- If the shapes belong to the same net, merge them into a single LI shape so no spacing rule applies between them

## 4. `m1.2` — 27 violation(s)

**Deck description:** m1.2 : min. m1 spacing : 0.14um  
**Worst measured:** 0.06 µm (required ≥ 0.14 µm)  
**Rule manual (exact):**
> (m1.2) Met1: Spacing of metal1 to metal1 = 0.140 µm

**What:** The rule requires metal1-to-metal1 spacing of 0.140 µm ('Met1: Spacing of metal1 to metal1 = 0.140 µm'), but the checker measured a worst-case spacing of only 0.06 µm across 27 violations in blk_alu, blk_io, blk_ctrl, and blk_mem.
**Likely causes:**
- Parallel metal1 routes (e.g., bus-style routing) drawn with pitch below the 0.140 µm minimum, consistent with marker edge pairs separated by only 0.085–0.10 µm
- Cell-internal metal1 routing in blk_alu, blk_io, blk_ctrl, and blk_mem that violates the spacing, since all 27 violations are concentrated in these four cells
- Not stated in the rule text
**Suggested fixes:**
- Move or reshape one of the offending metal1 edges so the gap to the neighboring metal1 edge is at least 0.140 µm (e.g., the edges at x=12.5 vs x=12.6, x=6.5 vs x=6.59, and x=0.5 vs x=0.585 all need the gap increased)
- Reroute one of the two close metal1 shapes on met2 instead, keeping met1 spacing ≥ 0.140 µm where it remains
- Re-run the m1.2 check after editing to confirm all 27 violations in the four cells are cleared

## 5. `m2.6` — 26 violation(s)

**Deck description:** m2.6 : min. m2 area : 0.0676um²  
**Worst measured:** 0.02102 µm² (required ≥ 0.0676 µm²)  
**Rule manual (exact):**
> (m2.6) Metal 2: Min metal2 area = 0.0676 µm²

**What:** Rule m2.6 requires minimum metal2 area of 0.0676 µm², but the worst measured shape is 0.02102 µm².
**Likely causes:**
- Small square metal2 shapes such as via landing pads or short stubs (the sample markers are 0.15–0.24 µm squares, all below 0.0676 µm²)
- Metal2 shapes trimmed back after routing changes, leaving isolated stubs below the area minimum
- Metal2 fill or patch shapes removed or shrunk during fill generation or edits
**Suggested fixes:**
- Enlarge the offending metal2 squares so their area is at least 0.0676 µm² (e.g., a square of at least 0.26 µm × 0.26 µm)
- Extend the small metal2 shape along an adjacent metal2 route or merge it with a neighboring metal2 shape so the combined polygon meets the area minimum
- If the shape is not needed, delete it entirely rather than leaving an undersized stub

## 6. `m3.6` — 26 violation(s)

**Deck description:** m3.6 : min. m3 area : 0.240um²  
**Worst measured:** 0.11903 µm² (required ≥ 0.24 µm²)  
**Rule manual (exact):**
> (m3.6) Metal 3: Min area of metal3 = 0.240 µm²

**What:** Rule m3.6 requires 'Min area of metal3 = 0.240 µm²', but the worst measured metal3 shape is 0.11903 µm², below the required ≥ 0.24 µm².
**Likely causes:**
- Small square/rect metal3 patches (markers are ~0.37x0.37 to ~0.45x0.45 µm, areas ~0.14–0.20 µm²) such as via landing pads, stubs, or layer-jump squares that are too small.
- Leftover or auto-generated metal3 fill/tie-off shapes that were never sized to the min-area requirement.
- Short metal3 segments in blk_io, blk_ctrl, blk_mem, blk_alu (26 violations) created when trimming routes or connecting vias.
**Suggested fixes:**
- Stretch each violating metal3 shape so width x length ≥ 0.240 µm² (e.g., widen 0.37 µm squares to ~0.49 µm, or extend them to ~0.65 µm at 0.37 µm width).
- Delete any metal3 stubs, dummy squares, or unused landing pads that serve no connectivity purpose.
- Merge or absorb small metal3 patches into adjacent larger metal3 shapes/via stacks so no isolated piece is below 0.240 µm².

## 7. `li.1` — 25 violation(s)

**Deck description:** li.1 : min. li width outside or crossing areaid:ce : 0.17um  
**Worst measured:** 0.08 µm (required ≥ 0.17 µm)  
**Rule manual (exact):**
> (li.1) Local Interconnect (LI): Width of LI (except for li.1a) = 0.170 µm

**What:** Rule li.1 requires the width of Local Interconnect (LI) (except for li.1a) to be 0.170 µm, but the worst measured LI width is 0.08 µm (marker samples show widths of ~0.105, 0.11, and 0.12 µm).
**Likely causes:**
- LI wires drawn or routed with a width below the 0.17 µm minimum
- Default routing width for the LI layer set too narrow in the router or PCell parameters
- Hand-edited LI segments (e.g., short stubs or jogs) resized below the minimum width
**Suggested fixes:**
- Stretch/resize the offending LI shapes in blk_ctrl, blk_io, blk_alu, and blk_mem so every LI segment is at least 0.17 µm wide
- Set the LI routing width to 0.17 µm (or wider) and re-route the affected nets
- Re-run the li.1 check after edits to confirm no LI width remains below 0.17 µm

## 8. `m3.1` — 24 violation(s)

**Deck description:** m3.1 : min. m3 width : 0.3um  
**Worst measured:** 0.155 µm (required ≥ 0.3 µm)  
**Rule manual (exact):**
> (m3.1) Metal 3: Width of metal 3 = 0.300 µm

**What:** Rule m3.1 requires 'Width of metal 3 = 0.300 µm' (minimum m3 width 0.3 µm), but the worst measured m3 width is 0.155 µm across 24 violations in blk_mem, blk_ctrl, blk_alu, and blk_io.
**Likely causes:**
- Narrow metal-3 straps/runs (the markers are short vertical segments ~0.165-0.23 µm wide between y=24 and y=26, e.g., x=30 to 30.165), likely router-generated necking or jumpers drawn below the 0.3 µm minimum
- Router/tech setup using an outdated or wrong min-width setting for the m3 layer
- Hand-drawn m3 connections or via stubs sized without checking the m3.1 width rule
**Suggested fixes:**
- Widen each flagged m3 segment so both edges are at least 0.3 µm apart (e.g., stretch the x=30 edge to x=29.85 or the x=30.165 edge to x=30.3, keeping the run straight)
- Set/verify the router's m3 min-width to 0.3 µm and reroute or re-legalize the affected nets, then re-run DRC on blk_mem, blk_ctrl, blk_alu, and blk_io
- For any hand-drawn m3, snap the shape to a 0.3 µm (or wider) width grid template and re-check all 24 markers

## 9. `li.6` — 20 violation(s)

**Deck description:** li.6 : min. li area : 0.0561um²  
**Worst measured:** 0.03063 µm² (required ≥ 0.0561 µm²)  
**Rule manual (exact):**
> (li.6) Local Interconnect (LI): Min area of LI = 0.0561 µm²

**What:** Rule li.6 requires a minimum Local Interconnect (LI) area of 0.0561 µm² ('Min area of LI = 0.0561 µm²'), but the worst measured LI shape is only 0.03063 µm².
**Likely causes:**
- Small square LI patches around contacts/vias (sample markers are ~0.21-0.22 µm squares, ~0.044-0.048 µm², under the limit)
- Short LI stubs or jumper segments left after routing
- Auto-generated via enclosures on li1 too small to meet min area
**Suggested fixes:**
- Extend one dimension of each undersized LI shape (e.g., lengthen a 0.22 µm-wide shape to ~0.30 µm so the area exceeds 0.0561 µm²)
- Merge each tiny LI square with an adjacent LI shape so the combined polygon meets min area
- Delete unneeded LI stubs, or re-place the via so its li1 enclosure forms a larger rectangle

## 10. `m2.2` — 20 violation(s)

**Deck description:** m2.2 : min. m2 spacing : 0.14um  
**Worst measured:** 0.06 µm (required ≥ 0.14 µm)  
**Rule manual (exact):**
> (m2.2) Metal 2: Spacing of metal 2 to metal 2 = 0.140 µm

**What:** Rule m2.2 requires the spacing of metal 2 to metal 2 to be at least 0.140 µm, but the worst measured m2-to-m2 spacing is 0.06 µm.
**Likely causes:**
- Two m2 wires routed in parallel (the sample markers show vertical m2 edges from y=18 to y=20) with a horizontal gap below 0.14 µm
- Routing pitch set tighter than the m2 minimum spacing (e.g., edge at x=30.57 is only 0.07 µm from the edge at x=30.5)
- Bus/parallel-track routing across blk_io, blk_mem, blk_alu, and blk_ctrl drawn with a uniform but too-small spacing
**Suggested fixes:**
- Shift the offending m2 edges so the gap is ≥ 0.140 µm (e.g., move the edge at x=30.57 to x ≥ 30.64, and the edges at x=36.62 and x=24.62 to x ≥ 36.64 and x ≥ 24.64 respectively)
- Jog one of the two parallel m2 wires so the long parallel run is broken and only momentarily near the neighbor, keeping every m2-to-m2 gap ≥ 0.14 µm
- Re-route one of the conflicting nets on another layer (e.g., m1 or m3) to remove the close m2-to-m2 proximity

## 11. `nsdm.2` — 18 violation(s)

**Deck description:** nsdm.2 : min. nsdm width in periphery : 0.38um  
**Worst measured:** 0.2 µm (required ≥ 0.38 µm)  
**Rule manual (corrected):**
> (nsd.1) N+/P+ Source/Drain Implants (Nsdm and Psdm): Width of nsdm(psdm) = 0.380 µm
> (psd.1) N+/P+ Source/Drain Implants (Nsdm and Psdm): Width of nsdm(psdm) = 0.380 µm

**What:** The rule requires the minimum width of the nsdm (N+ source/drain implant) layer to be at least 0.380 µm ('Width of nsdm(psdm) = 0.380 µm'), but the worst measured nsdm width is 0.2 µm (sample markers also show 0.345, 0.245, and 0.24 µm).
**Likely causes:**
- nsdm implant strips drawn narrower than 0.38 µm (markers show widths of 0.345 µm, 0.245 µm, and 0.24 µm)
- Implant shapes auto-generated or snapped too thin in the affected cells (blk_alu, blk_io, blk_mem, blk_ctrl)
- Merged or trimmed implant rectangles after abutment/routing reduced the strip width below the limit
**Suggested fixes:**
- Stretch the nsdm rectangles at the marker locations (e.g., near x=6, x=12, x=18 at y=42–44) so their width is ≥ 0.380 µm
- Merge adjacent same-type nsdm shapes or widen thin implant strips so no nsdm edge-to-edge span is under 0.380 µm
- Regenerate/re-check the source/drain implant shapes in blk_alu, blk_io, blk_mem, and blk_ctrl with a minimum-width constraint of 0.380 µm

## 12. `m1.1` — 16 violation(s)

**Deck description:** m1.1 : min. m1 width : 0.14um  
**Worst measured:** 0.065 µm (required ≥ 0.14 µm)  
**Rule manual (exact):**
> (m1.1) Met1: Width of metal1 = 0.140 µm

**What:** Rule m1.1 requires Met1 (metal1) shapes to have a minimum width of 0.140 µm, and the checker measured a worst case of 0.065 µm (required ≥ 0.14 µm).
**Likely causes:**
- Met1 segments drawn narrower than 0.14 µm: markers show widths of 0.065 µm (x≈24.0–24.065), 0.12 µm (x≈30.0–30.12), and 0.08 µm (x≈0.0–0.08)
- Narrow Met1 wires or stubs present across blk_mem, blk_io, blk_ctrl, and blk_alu (16 total violations)
**Suggested fixes:**
- Stretch/widen every flagged Met1 shape so all widths are at least 0.14 µm (e.g., add ~0.075 µm to the 0.065 µm segment at x≈24.0–24.065)
- Merge or delete thin Met1 stubs/slivers with adjacent Met1 so no sub-0.14 µm necks remain
- Re-run the m1.1 check to confirm all 16 markers in blk_mem, blk_io, blk_ctrl, and blk_alu are cleared

## 13. `poly.2` — 16 violation(s)

**Deck description:** poly.2 : min. poly spacing : 0.21um  
**Worst measured:** 0.105 µm (required ≥ 0.21 µm)  
**Rule manual (exact):**
> (poly.2) Poly: Spacing of poly to poly except for poly.c2 and poly.c3; Exempt cell: sr_bltd_eq where it is same as poly.c2 = 0.210 µm

**What:** Rule poly.2 requires poly-to-poly spacing of at least 0.210 µm (except where poly.c2 and poly.c3 apply, and in exempt cell sr_bltd_eq), but the checker measured a worst case of 0.105 µm across 16 violations in cells blk_alu, blk_ctrl, blk_io, and blk_mem.
**Likely causes:**
- Parallel poly edges drawn too close: marker edge pairs show gaps of only 0.195 µm (36.695 vs 36.5), 0.16 µm (42.66 vs 42.5), and 0.175 µm (48.675 vs 48.5), all below the 0.21 µm requirement.
- Poly lines routed on a pitch tighter than 0.21 µm spacing in the affected blocks.
- Close spacing was drawn where the poly.c2/poly.c3 exception or the sr_bltd_eq exempt cell does not actually apply.
**Suggested fixes:**
- Shift the inner poly edge of each violating pair (e.g., the edges at x=36.5, x=42.5, x=48.5) outward so the spacing to the neighboring poly edge is ≥ 0.21 µm.
- Increase the poly-to-poly pitch wherever multiple poly lines run in parallel in blk_alu, blk_ctrl, blk_io, and blk_mem, then re-run DRC on all 16 markers.
- If closer spacing is functionally required, restructure the geometry to satisfy the poly.c2/poly.c3 exception conditions or move it into the exempt cell sr_bltd_eq; otherwise reroute the poly.

## 14. `m1.6` — 15 violation(s)

**Deck description:** m1.6 : min. m1 area : 0.083um²  
**Worst measured:** 0.0225 µm² (required ≥ 0.083 µm²)  
**Rule manual (exact):**
> (m1.6) Met1: Min metal 1 area = 0.083 µm²

**What:** Rule m1.6 requires Met1 (metal 1) shapes to have a minimum area of 0.083 µm², but the worst measured shape is only 0.0225 µm².
**Likely causes:**
- Small square Met1 patches (e.g., 0.155 µm × 0.155 µm ≈ 0.024 µm² and 0.185 µm × 0.185 µm ≈ 0.034 µm² in the markers) that are far below the 0.083 µm² minimum
- Metal1 stubs or landing pads left undersized after routing or via placement
- Isolated Met1 fragments not merged with neighboring metal in cells blk_ctrl, blk_mem, blk_alu, blk_io
**Suggested fixes:**
- Enlarge each undersized Met1 shape so its total area is ≥ 0.083 µm² (e.g., a square of at least ~0.288 µm per side)
- Merge tiny Met1 patches into adjacent Met1 shapes to form one compliant polygon
- Delete any unnecessary small Met1 stubs or dummy patches that serve no connection purpose

## 15. `m3.2` — 15 violation(s)

**Deck description:** m3.2 : min. m3 spacing : 0.3um  
**Worst measured:** 0.165 µm (required ≥ 0.3 µm)  
**Rule manual (exact):**
> (m3.2) Metal 3: Spacing of metal 3 to metal 3 = 0.300 µm

**What:** Rule m3.2 requires 'Spacing of metal 3 to metal 3 = 0.300 µm', but the checker measured a worst-case m3-to-m3 spacing of 0.165 µm (required ≥ 0.3 µm) across 15 violations in blk_alu, blk_io, blk_mem, and blk_ctrl.
**Likely causes:**
- Parallel metal 3 routing drawn with a pitch below 0.300 µm — every sample marker is a pair of parallel vertical edges spaced only 0.185–0.29 µm apart
- A repeated routing pattern or bus pitch shared by blk_alu, blk_io, blk_mem, and blk_ctrl reproduces the same sub-0.3 µm gaps in all four cells
- Deeper root cause: not stated in the rule text (the manual specifies only the 0.300 µm spacing limit)
**Suggested fixes:**
- Move or jog one of the two offending M3 shapes sideways so the edge-to-edge gap is ≥ 0.300 µm (at the worst spot that means adding at least 0.135 µm: 0.300 − 0.165)
- Re-space parallel M3 runs so neighbouring M3 edges always leave ≥ 0.300 µm between them, including the sample locations at x≈12.5/12.79, x≈6.5/6.755, and x≈18.5/18.685
- Correct the shared block-level template or routing pitch used by blk_alu, blk_io, blk_mem, and blk_ctrl once, then re-run DRC to clear all 15 violations

## 16. `poly.1a` — 11 violation(s)

**Deck description:** poly.1a : min. poly width : 0.15um  
**Worst measured:** 0.095 µm (required ≥ 0.15 µm)  
**Rule manual (exact):**
> (poly.1a) Poly: Width of poly = 0.150 µm

**What:** Rule poly.1a requires 'Width of poly = 0.150 µm' (minimum poly width 0.150 µm), but the worst measured poly width is 0.095 µm, i.e. 0.055 µm below the limit; 11 violations across blk_alu, blk_ctrl, blk_io, and blk_mem.
**Likely causes:**
- Poly wires drawn or snapped narrower than 0.150 µm — the marker edge-pairs show vertical poly segments about 0.095–0.12 µm wide (e.g. 0.105 µm, 0.12 µm, 0.10 µm spacings)
- Resize/boolean or off-grid snapping operations that thinned poly segments below 0.150 µm
- Generated/routed poly (PCell or script) emitted with a default width below 0.150 µm
**Suggested fixes:**
- Stretch or resize the offending poly shapes in blk_alu, blk_ctrl, blk_io, and blk_mem so every poly width is at least 0.150 µm (fix the worst 0.095 µm segment first)
- Snap all poly edges to the manufacturing grid and widen the narrow vertical poly runs indicated by the markers at x ≈ 6, 12, and 18 (y 36–38)
- Correct the generating source (PCell parameters or layout script) so poly is drawn at ≥ 0.150 µm, then re-run poly.1a
