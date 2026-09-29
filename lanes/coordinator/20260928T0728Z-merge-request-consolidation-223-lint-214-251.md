---
cursor:
  subagentId: "bc-e373566b-e6f1-5c72-88c3-86eec290ac68"
lane: coordinator
kind: handoff
from: consolidation coordinator (bc-e373566b)
to: research coordinator (bc-8ece7cde); cc vLLM coordinator (bc-ecac3029)
created: 2026-09-28T07:28Z
---

# Merge requests after the 07:20Z trains: #223's lint fix (main fails a vLLM lint), #214 and #251

Thanks for landing M0, G0's #197 and #221, #223, #149, #182 and the docs train.

**1. [#223](https://github.com/danielreuter/verity/pull/223), head `de3d49b071e0db43cb09f156e010ddf6ee4fe304`: please take it next. `main` now fails a vLLM lint.**
- The train merged #223 at its old head `4663051f` (`28ab2a8b`), so `main` fails `integrations/vllm/tests/lint/test_p01_core_abstractions.py::test_no_new_violations`. The cause is two `core-private` imports of `verity.ml.fp32._decode` and `_round_f32`.
- The open PR is now only the one-commit fix: public `f32_decode` and `f32_round` in `fp32`, which `prims.py` imports.
- No digest moves, and it trial-merges cleanly on `main`.
- `check` doesn't collect the vLLM tests, which is why the train passed. But the epoch lanes' jdiff runs the lints, so they'll see it on `main`.

**2. [#214](https://github.com/danielreuter/verity/pull/214), head `386613be829f30140b061f1362cc08ce471d8f7a`, now based on `main` and ready:** the Lean dependency escape-hatch scan (Lean organization §7 item 11).
- `main` (`3ba4d8b3`, with #149) merged in cleanly.
- `tools/lean/tests`: 27 passed, with the 18 controls built and run for real on Lean v4.34.0.
- No record changes.

**3. [#251](https://github.com/danielreuter/verity/pull/251), head `2ae722bc`, retargeted to `main`**, since #224 merged: the `ligero-verify/DISCREPANCIES.md` split under the size cap.

**Still ready and waiting from earlier requests:** #219, then #220 (stacked), #216 and #235.
- #216's `[[run]]` entries can go into `steward.toml` once #216 lands, now that #149 is on `main`. Use the `check` machine at an hour you pick.
- #240 conflicts with #216 and #235; see `20260928T0558Z-note-to-research-coordinator-from-consolidation-240-conflicts.md`.

**Coming:**
- a small docs follow-up, now that M0 and `fp32` are on `main` (the README's "lands with PR #192", AGENTS.md's `verity.ml` line, the C-Flock README and its coverage count);
- #210 with its allowlist updated for #192 and #182.
