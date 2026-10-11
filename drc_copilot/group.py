"""Step 1 — deterministic grouping. This is also the fallback when the LLM path fails."""
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Dict, List, Optional

from . import measure
from .lyrdb import Report, Violation


@dataclass
class Group:
    rule: str
    description: str
    count: int
    cells: Dict[str, int]          # cell -> violations in that cell
    samples: List[Violation]       # a few markers to show the model / the reader
    kind: Optional[str] = None     # 'distance' or 'area', when markers could be measured
    worst: Optional[float] = None  # smallest measured value in the group (µm or µm²)
    limit: Optional[float] = None  # required value parsed from the deck description

    def measured_text(self) -> str:
        if self.worst is None:
            return "—"
        unit = "µm²" if self.kind == "area" else "µm"
        lim = f" (required ≥ {self.limit:g} {unit})" if self.limit is not None else ""
        return f"{self.worst:g} {unit}{lim}"


def group(report: Report, samples_per_rule: int = 3) -> List[Group]:
    by_rule: Dict[str, List[Violation]] = defaultdict(list)
    for v in report.violations:
        by_rule[v.rule].append(v)
    groups = []
    for rule, vs in by_rule.items():
        desc = report.descriptions.get(rule, "")
        values = [m for v in vs for m in (measure.measure(x) for x in v.values) if m]
        kinds = {k for k, _ in values}
        kind = kinds.pop() if len(kinds) == 1 else None
        req = measure.required(desc)
        if not req or req[0] != kind:      # only report a measurement we can compare with a stated limit
            kind = None
        groups.append(Group(
            rule=rule, description=desc, count=len(vs),
            cells=dict(Counter(v.cell for v in vs).most_common()),
            samples=vs[:samples_per_rule],
            kind=kind,
            worst=min(x for _, x in values) if kind else None,
            limit=req[1] if kind else None,
        ))
    groups.sort(key=lambda g: (-g.count, g.rule))
    return groups
