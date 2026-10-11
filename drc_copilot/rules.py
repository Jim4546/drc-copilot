"""Step 2 — retrieval over the SKY130 periphery design-rule table (the "R" in RAG).

Source: google/skywater-pdk docs/rules/periphery/periphery.csv (Apache-2.0), saved in data/.
Lookup order: exact rule id first; if that misses, lexical similarity against the rule text.
"""
import csv
import math
import re
from collections import Counter
from dataclasses import dataclass
from typing import List, Optional, Tuple

HEADER = re.compile(r"^\(([^)]+?)\)$")          # e.g. "(m1.-)", "(li.-.-)", "(n/ psd.-)"
TOKEN = re.compile(r"[a-z0-9]+")
STOP = {"rule", "rules", "min", "max", "minimum", "of", "the", "to", "and", "a", "an", "for", "by", "in", "on",
        "is", "be", "must", "at", "least", "um", "with", "or", "not"}


def _tokens(text: str) -> Counter:
    return Counter(t for t in TOKEN.findall(text.lower()) if t not in STOP)


@dataclass
class Rule:
    rule_id: str      # e.g. "m1.2"
    layer: str        # e.g. "Met1"
    text: str         # e.g. "Spacing of metal1 to metal1"
    value: str        # e.g. "0.140"
    unit: str         # e.g. "µm"
    flags: str        # the "Use" column (P, NC, RC, ...)
    high_voltage: bool

    def as_context(self) -> str:
        v = f" = {self.value} {self.unit}".rstrip() if self.value and self.value != "N/A" else ""
        hv = " [high-voltage section]" if self.high_voltage else ""
        return f"({self.rule_id}) {self.layer}: {self.text}{v}{hv}"


def _prefixes(header: str) -> List[str]:
    """'(m1.-)' -> ['m1'];  '(n/ psd.-)' -> ['nsd', 'psd'];  '(li.-.-)' -> ['li']."""
    base = header.split(".")[0].strip()
    if "/" in base:
        a, b = (s.strip() for s in base.split("/"))
        return [a + b[1:], b]       # "n/ psd" -> nsd, psd
    return [base]


def load(path: str) -> List[Rule]:
    rules: List[Rule] = []
    prefixes: List[str] = []
    layer = ""
    high_voltage = False
    with open(path, encoding="utf-8") as f:
        for row in csv.reader(f):
            row = (row + ["", "", "", "", ""])[:5]
            first, text, flags, value, unit = (c.strip() for c in row)
            m = HEADER.match(first)
            if m:
                prefixes, layer = _prefixes(m.group(1)), text
                if layer.lower().startswith("hvi"):
                    high_voltage = True
                continue
            if not prefixes or not text:
                continue
            text = re.sub(r":drc_tag:`([^`]*)`", r"\1", text.replace("\\n", " ")).strip()
            if not first:                      # continuation row: extends the previous rule's text
                if rules and rules[-1].layer == layer:
                    last = [r for r in rules if r.rule_id == rules[-1].rule_id]
                    for r in last:
                        r.text += f" | {text}" + (f" = {value} {unit}".rstrip() if value and value != "N/A" else "")
                continue
            for num in first.replace("\\n", " ").split():
                num = num.lstrip(".")
                for p in prefixes:
                    rules.append(Rule(f"{p}.{num}".lower(), layer, text, value, unit, flags, high_voltage))
    return apply_errata(rules)


# Known errors in the source table, corrected at load time and labelled in the text.
ERRATA_UNITS = {("x.1a", "mm"): "µm", ("x.1b", "mm"): "µm"}   # grid is 0.001 / 0.005 µm, not mm


def apply_errata(rules: List[Rule]) -> List[Rule]:
    for r in rules:
        fixed = ERRATA_UNITS.get((r.rule_id, r.unit))
        if fixed:
            r.text = r.text.replace("grid of mm", "grid of the stated value") + f" [unit corrected: source table says {r.unit}]"
            r.unit = fixed
    return rules


class RuleIndex:
    def __init__(self, rules: List[Rule]):
        self.rules = rules
        self.by_id = {}
        for r in rules:
            self.by_id.setdefault(r.rule_id, []).append(r)
        self.docs = [_tokens(f"{r.layer} {r.text}") for r in rules]
        df = Counter(t for d in self.docs for t in d)
        n = len(self.docs)
        self.idf = {t: math.log(1 + n / c) for t, c in df.items()}

    def exact(self, rule_id: str) -> List[Rule]:
        rid = rule_id.lower().strip()
        hits = self.by_id.get(rid, [])
        return sorted(hits, key=lambda r: r.high_voltage)   # low-voltage periphery first

    def similar(self, query: str, k: int = 3) -> List[Rule]:
        q = _tokens(query)
        scored = []
        for r, d in zip(self.rules, self.docs):
            s = sum(self.idf.get(t, 0) * min(c, d[t]) for t, c in q.items() if t in d)
            if s > 0:
                scored.append((s, r))
        scored.sort(key=lambda x: -x[0])
        return [r for _, r in scored[:k]]

    def retrieve(self, rule_id: str, description: str = "", k: int = 3) -> Tuple[List[Rule], str]:
        """Returns (rules, how):
        'exact' / 'normalized'  — id lookup (normalized = deck id mapped to a manual id)
        'corrected'             — id lookup hit a rule of a different check type than the deck describes
                                  (e.g. deck says width, manual id says spacing); re-picked by meaning
        'mismatch'              — same, but no rule of the right type was found: flag for a human
        'similar' / 'none'      — no id match; lexical similarity fallback
        """
        want = check_kind(description)
        for n, cand in enumerate(candidates(rule_id)):
            hits = self.exact(cand)
            if not hits:
                continue
            how = "exact" if n == 0 else "normalized"
            if want and check_kind(hits[0].text) not in (None, want):
                fixed = [r for r in self.rules if r.layer == hits[0].layer and check_kind(r.text) == want
                         and r.high_voltage == hits[0].high_voltage]
                return (fixed[:k], "corrected") if fixed else (hits[:k], "mismatch")
            return hits[:k], how
        hits = self.similar(f"{rule_id} {description}", k)
        return hits, ("similar" if hits else "none")


KINDS = (("enclosure", re.compile(r"\benclos")), ("area", re.compile(r"\barea\b")),
         ("spacing", re.compile(r"\bspac(e|ing)\b")), ("width", re.compile(r"\bwidth\b")))


def check_kind(text: str) -> Optional[str]:
    """What a rule measures, from its wording: width / spacing / area / enclosure (whole words only)."""
    t = (text or "").lower()
    for kind, pat in KINDS:
        if pat.search(t):
            return kind
    return None


ALIASES = {"nsdm": "nsd", "psdm": "psd", "pwde": "pwdem", "met1": "m1", "met2": "m2", "met3": "m3", "met4": "m4", "met5": "m5"}


def candidates(rule_id: str) -> List[str]:
    """Deck rule names -> manual rule ids, most specific first.

    'm1.1' -> ['m1.1'];  'nsdm.1' -> ['nsdm.1', 'nsd.1'];  'ct.1_a/b' -> [..., 'ct.1'];
    'm1.3ab' -> [..., 'm1.3a', 'm1.3b'];  'm1_OFFGRID' -> ['x.1b'];  'm1_angle' -> ['x.2', 'x.3a'].
    """
    rid = rule_id.strip().lower()
    if rid.endswith("_offgrid"):
        return [rid, "x.1b"]
    if rid.endswith("_angle"):
        return [rid, "x.2", "x.3a"]
    out = [rid]
    layer, _, num = rid.partition(".")
    layer = ALIASES.get(layer, layer)
    num = num.split("_")[0]                      # drop deck-only suffixes such as _a, _b, _a/b
    base = f"{layer}.{num}" if num else layer
    out.append(base)
    m = re.match(r"^(\d+)([a-z]{2,})$", num)     # '3ab' -> 3a, 3b
    if m:
        out += [f"{layer}.{m.group(1)}{c}" for c in m.group(2)]
        out.append(f"{layer}.{m.group(1)}")
    seen = []
    for c in out:
        if c not in seen:
            seen.append(c)
    return seen
