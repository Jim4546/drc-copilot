#!/bin/zsh
# Run the official SKY130 KLayout DRC deck (from the volare-installed PDK) on a GDS.
#   tools/run_drc.sh work/testchip_clean.gds work/clean.lyrdb [TOP]
# Paths are made absolute: KLayout resolves relative report paths against the layout's folder.
set -e
GDS="${1:A}"; OUT="${2:A}"; TOP="${3:-TOP}"
KLAYOUT=/Applications/KLayout/klayout.app/Contents/MacOS/klayout
DECK="$HOME/.volare/sky130A/libs.tech/klayout/drc/sky130A_mr.drc"
rm -f "$OUT"
"$KLAYOUT" -b -r "$DECK" \
  -rd input="$GDS" -rd report="$OUT" -rd top_cell="$TOP" \
  -rd feol=true -rd beol=true -rd offgrid=true -rd thr=4
[[ -s "$OUT" ]] || { echo "DRC report was not written: $OUT" >&2; exit 1; }
echo "DRC report: $OUT"
