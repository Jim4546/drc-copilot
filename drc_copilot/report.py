"""Step 4 — one-page Markdown report. Works with or without model explanations."""
from typing import List, Optional

from .explain import Explanation
from .group import Group
from .rules import Rule


def render(source: str, total: int, rows: List[tuple]) -> str:
    """rows: (Group, [Rule], how, Explanation or None)"""
    used_llm = any(ex is not None and not ex.error for _, _, _, ex in rows)
    lines = [
        "# DRC triage report",
        "",
        f"- Source: `{source}`",
        f"- Violations: **{total}** in **{len(rows)}** rule groups",
        f"- Mode: {'rule grouping + retrieved rule text + GLM explanation' if used_llm else 'rule grouping + retrieved rule text (model path off or failed)'}",
        "",
        "| # | Rule | Count | Worst measured | Top cells | Rule text found |",
        "|---|---|---|---|---|---|",
    ]
    for i, (g, rules, how, ex) in enumerate(rows, 1):
        cells = ", ".join(list(g.cells)[:3])
        lines.append(f"| {i} | `{g.rule}` | {g.count} | {g.measured_text()} | {cells} | {how} |")
    for i, (g, rules, how, ex) in enumerate(rows, 1):
        lines += ["", f"## {i}. `{g.rule}` — {g.count} violation(s)", ""]
        if g.description:
            lines.append(f"**Deck description:** {g.description}  ")
        lines.append(f"**Worst measured:** {g.measured_text()}  ")
        lines.append(f"**Rule manual ({how}):**")
        lines += [f"> {r.as_context()}" for r in rules] or ["> (no matching rule text)"]
        if ex is None:
            continue
        if ex.error:
            lines += ["", f"_Model explanation unavailable: {ex.error}. Showing rule text only._"]
            continue
        lines += ["", f"**What:** {ex.what}"]
        if ex.likely_causes:
            lines.append("**Likely causes:**")
            lines += [f"- {c}" for c in ex.likely_causes]
        if ex.fix:
            lines.append("**Suggested fixes:**")
            lines += [f"- {c}" for c in ex.fix]
        if ex.grounded is False:
            lines.append("")
            lines.append("⚠️ The model reported that the retrieved rule text did not cover this rule — verify manually.")
    return "\n".join(lines) + "\n"
