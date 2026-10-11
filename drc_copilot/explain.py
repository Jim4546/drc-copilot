"""Step 3 — ask GLM to explain one violation group, grounded in the retrieved rule text."""
import json
import re
from dataclasses import dataclass, field
from typing import List, Optional

from . import glm
from .group import Group
from .rules import Rule

SYSTEM = (
    "You are a physical-verification assistant for the SKY130 process. "
    "Explain DRC violations to a junior layout engineer. "
    "Base every statement on the rule text you are given; if the rule text does not support a claim, "
    "say 'not stated in the rule text' instead of guessing. Answer with JSON only."
)

TEMPLATE = """DRC rule id: {rule}
Rule description from the DRC deck: {deck}
Rule text retrieved from the SKY130 design-rule manual ({how} match):
{context}
Violations of this rule: {count}, in cells: {cells}
Measured by the checker (deterministic, trust these numbers): worst case {measured}
Sample marker geometry (KLayout format, µm): {samples}

Return JSON with exactly these keys:
{{"what": "one sentence: what the rule requires (quote the limit) and the worst measured value",
  "likely_causes": ["up to 3 short causes"],
  "fix": ["up to 3 concrete layout edits"],
  "grounded": true or false
}}
Set "grounded" to false if the retrieved rule text did not describe this rule."""


@dataclass
class Explanation:
    what: str = ""
    likely_causes: List[str] = field(default_factory=list)
    fix: List[str] = field(default_factory=list)
    grounded: Optional[bool] = None
    error: str = ""          # set when the model path failed -> report falls back to rule text only


def _parse_json(text: str) -> dict:
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
    start, end = text.find("{"), text.rfind("}")
    return json.loads(text[start:end + 1])


def explain(g: Group, rules: List[Rule], how: str) -> Explanation:
    context = "\n".join(r.as_context() for r in rules) or "(nothing found)"
    samples = "; ".join(v for s in g.samples for v in s.values[:1]) or "(none)"
    cells = ", ".join(list(g.cells)[:5])
    prompt = TEMPLATE.format(rule=g.rule, deck=g.description or "(none)", how=how, context=context,
                             count=g.count, cells=cells, measured=g.measured_text(), samples=samples)
    try:
        raw = glm.chat([{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}])
        d = _parse_json(raw)
        return Explanation(
            what=str(d.get("what", "")),
            likely_causes=[str(x) for x in d.get("likely_causes", [])][:3],
            fix=[str(x) for x in d.get("fix", [])][:3],
            grounded=d.get("grounded"),
        )
    except glm.GLMUnavailable as e:
        return Explanation(error=str(e))
    except (ValueError, json.JSONDecodeError):
        return Explanation(error="model answer was not valid JSON")
