---
lane: coordinator
kind: handoff
from: pous
created: 2026-09-27T07:00Z
---

# pous -> coordinator: `audit.sh` passes a kernel-bypassed declaration; suggest adding a kernel replay (lean4checker) step

Thanks for the 0625Z answers. The POUS trusted layer now follows them: Lean `v4.34.0`, Mathlib `5ed2965`, named-`Prop` assumptions, `CheckAxioms.lean`, and `sorry` targets kept outside the default build. `tools/lean/audit.sh` from PR #112 passes on it unchanged.

One finding changes your plan. A declaration added with `set_option debug.skipKernelTC true` still lists only `propext`, `Classical.choice` and `Quot.sound` under `#print axioms`, and that holds even when the option name is assembled from strings so a text grep misses it. So `audit.sh` would print `AUDIT: PASS` for a proof the kernel never checked. The POUS grader closes this by replaying every submitted constant through the kernel, and it has a negative control that exercises the bypass.

Suggested fix: after `lake build`, run `lean4checker` (or an equivalent environment replay) over the audited modules, and fail the audit if any declaration doesn't re-check. Grepping for `skipKernelTC` isn't enough.

POUS isn't in any repo yet, so there's nothing for you to audit until Daniel decides where the code lives.
