# DRC Copilot — evaluation

- Benchmark: `bench_truth.json` (seed 20261011), run: `bench_glm.json` (103.9 s)

## 1. Detection (official SKY130 KLayout deck)
- Violating sites flagged: **334/334 (100.0%)**
- At-limit legal controls flagged (false positives): **0/48 (0.0%)**
- Markers not matched to any injected site: 0

## 2. Triage
- 388 markers -> **16 rule groups**

## 3. Rule-text retrieval (top-1 manual rule == ground truth)
- DRC Copilot (id normalization + type-consistency check): **16/16 (100.0%)**
- Naive baseline (id lookup only): 15/16 (93.8%)

| Deck rule | Ground truth | Retrieved | How | Naive |
|---|---|---|---|---|
| `m1_OFFGRID` | `x.1b` | `x.1b` | normalized | `x.1b` |
| `m2.1` | `m2.1` | `m2.1` | exact | `m2.1` |
| `li.3` | `li.3` | `li.3` | exact | `li.3` |
| `m1.2` | `m1.2` | `m1.2` | exact | `m1.2` |
| `m2.6` | `m2.6` | `m2.6` | exact | `m2.6` |
| `m3.6` | `m3.6` | `m3.6` | exact | `m3.6` |
| `li.1` | `li.1` | `li.1` | exact | `li.1` |
| `m3.1` | `m3.1` | `m3.1` | exact | `m3.1` |
| `li.6` | `li.6` | `li.6` | exact | `li.6` |
| `m2.2` | `m2.2` | `m2.2` | exact | `m2.2` |
| `nsdm.2` | `nsd.1` | `nsd.1` | corrected | `nsd.2` |
| `m1.1` | `m1.1` | `m1.1` | exact | `m1.1` |
| `poly.2` | `poly.2` | `poly.2` | exact | `poly.2` |
| `m1.6` | `m1.6` | `m1.6` | exact | `m1.6` |
| `m3.2` | `m3.2` | `m3.2` | exact | `m3.2` |
| `poly.1a` | `poly.1a` | `poly.1a` | exact | `poly.1a` |

## 4. Model explanations
- Groups sent to the model: 16; valid JSON answers: **16/16 (100.0%)**
- Quote the correct limit: **15/15 (100.0%)** · quote the worst measured value: **15/15 (100.0%)** (groups with a numeric limit)
- Self-reported grounded in the retrieved text: 15/16 (93.8%)
