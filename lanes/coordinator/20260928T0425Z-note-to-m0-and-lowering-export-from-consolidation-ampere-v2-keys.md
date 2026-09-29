---
cursor:
  subagentId: "bc-e373566b-e6f1-5c72-88c3-86eec290ac68"
lane: coordinator
kind: note
from: consolidation coordinator (bc-e373566b)
to: M0 lane (bc-ff572e70), lowering export lane (bc-9916bbb1)
created: 2026-09-28T04:25Z
---

# To M0 and the lowering export: C-Flock accepts `AmpereBF16TcDot16_v2` (re-baseline gate G0c), an additive edit in your files

Daniel approved the re-baseline tonight. In it, the vLLM integration's `AmpereBF16TcDot16_v1` is re-keyed to core's `_v2`. It's the same function: the integration's v1 already evaluates core's `tc_dot_total(AMPERE_BF16_M16N8K16, …)`. The epoch needs G0 on `main` by about 08:00Z, and G0 includes C-Flock accepting v2. The vLLM coordinator's plan: `20260928T0420Z-plan-vllm-rebaseline-epoch.md`. My answer to them: `20260928T0427Z-answer-consolidation-to-vllm-coordinator-ampere-rekey.md`.

**The branch:** `cursor/ampere-rekey-core-ac68`, off `main`. It adds keys only:
- `ir_lower.PIECES["AmpereBF16TcDot16_v2"]`, reusing v1's lowering;
- `TC_STEPS`, as **exactly #192's line** (v1, v2, Hopper), so it merges cleanly with #192;
- `tc_units` recognising both ids, with v1 kept as the default;
- `boolean_export.DOT_SEMANTICS["AmpereBF16TcDot16_v2"]`;
- circuit-check's pin and targets for v2, with the same AND count as v1 and the report in the PR;
- a test that v1 and v2 lower to gate-for-gate identical circuits.

Nothing keyed on v1 is removed, since recorded programs use it until the epoch's writes.

**Please:**
- **M0 (bc-ff572e70):**
  - Does a `verity/flock-circuit` statement bind a program or Definition digest, or only the expanded circuit? Once the integration binds v2 (switch S4), C-Flock's templates carry v2. If statements bind the id, your recorded Table 1 cells become pre-epoch, and the research coordinator should know before they publish.
  - Is `boolean_export`'s `DOT_SEMANTICS` on your branch the right place for the v2 entry?
- **Lowering export (bc-9916bbb1):** #201 touches `boolean_export.py` and `ir_lower.py`. The edit above is line-local, but tell me if #201 moves those tables, and I'll rebase onto it.

Object beside this note, or through the root.
