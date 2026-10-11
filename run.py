#!/usr/bin/python3
"""DRC Copilot — triage a KLayout DRC report.

    /usr/bin/python3 run.py work/report.lyrdb                 # full pipeline (needs .env key)
    /usr/bin/python3 run.py work/report.lyrdb --no-llm        # grouping + rule text only
"""
import argparse
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor

from drc_copilot import explain, group, lyrdb, report, rules

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("lyrdb", help="KLayout DRC result database (.lyrdb)")
    ap.add_argument("--rules", default=os.path.join(HERE, "data/sky130_periphery_rules.csv"))
    ap.add_argument("--out", default=os.path.join(HERE, "out/report.md"))
    ap.add_argument("--no-llm", action="store_true", help="skip the model; rule grouping + rule text only")
    ap.add_argument("--max-groups", type=int, default=20, help="explain at most this many groups (largest first)")
    ap.add_argument("--workers", type=int, default=4, help="parallel model calls")
    args = ap.parse_args()

    t0 = time.time()
    rep = lyrdb.parse(args.lyrdb)
    groups = group.group(rep)
    index = rules.RuleIndex(rules.load(args.rules))

    retrieved = [index.retrieve(g.rule, g.description) for g in groups]
    todo = [] if args.no_llm else list(range(min(args.max_groups, len(groups))))
    explanations = {}
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = {i: pool.submit(explain.explain, groups[i], *retrieved[i]) for i in todo}
        for i in todo:
            ex = futures[i].result()
            explanations[i] = ex
            print(f"[{i + 1}/{len(groups)}] {groups[i].rule}: " + (f"fallback ({ex.error})" if ex.error else "explained"))
    rows = [(g, hits, how, explanations.get(i)) for i, (g, (hits, how)) in enumerate(zip(groups, retrieved))]

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(report.render(os.path.basename(args.lyrdb), len(rep.violations), rows))
    dump = {
        "source": args.lyrdb, "violations": len(rep.violations), "seconds": round(time.time() - t0, 1),
        "groups": [{
            "rule": g.rule, "description": g.description, "count": g.count, "cells": g.cells,
            "kind": g.kind, "worst": g.worst, "limit": g.limit,
            "retrieval": how, "retrieved": [r.rule_id for r in hits],
            "explanation": None if ex is None else {
                "error": ex.error, "what": ex.what, "likely_causes": ex.likely_causes,
                "fix": ex.fix, "grounded": ex.grounded},
        } for g, hits, how, ex in rows],
    }
    with open(os.path.splitext(args.out)[0] + ".json", "w", encoding="utf-8") as f:
        json.dump(dump, f, indent=1, ensure_ascii=False)
    print(f"{len(rep.violations)} violations, {len(groups)} groups -> {args.out} ({dump['seconds']} s)")


if __name__ == "__main__":
    main()
