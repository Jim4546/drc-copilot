"""Parse a KLayout report database (.lyrdb) produced by a DRC run."""
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Violation:
    rule: str            # category name, e.g. "m1.1"
    cell: str            # cell where the marker sits
    values: List[str] = field(default_factory=list)  # marker geometry as KLayout writes it


@dataclass
class Report:
    top_cell: str
    descriptions: Dict[str, str]   # rule -> description text from the DRC deck
    violations: List[Violation]


def _unquote(s: str) -> str:
    s = (s or "").strip()
    if len(s) >= 2 and s[0] == s[-1] == "'":
        s = s[1:-1]
    return s


def _walk_categories(node, prefix, out):
    for cat in node.findall("category"):
        name = _unquote(cat.findtext("name", ""))
        full = f"{prefix}.{name}" if prefix else name
        out[full] = (cat.findtext("description") or "").strip()
        sub = cat.find("categories")
        if sub is not None:
            _walk_categories(sub, full, out)


def parse(path: str) -> Report:
    root = ET.parse(path).getroot()
    descriptions: Dict[str, str] = {}
    cats = root.find("categories")
    if cats is not None:
        _walk_categories(cats, "", descriptions)

    violations = []
    items = root.find("items")
    for item in (items.findall("item") if items is not None else []):
        # nested category paths are written like 'parent'.'child'
        rule = ".".join(_unquote(p) for p in (item.findtext("category") or "").split("'.'"))
        rule = _unquote(rule)
        cell = _unquote(item.findtext("cell", ""))
        values = [v.text or "" for v in item.findall("values/value")]
        violations.append(Violation(rule=rule, cell=cell, values=values))

    return Report(top_cell=root.findtext("top-cell", ""), descriptions=descriptions, violations=violations)
