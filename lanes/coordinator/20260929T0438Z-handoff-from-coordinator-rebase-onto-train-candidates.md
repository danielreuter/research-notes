---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: coordinator
kind: handoff
from: coordinator
to: refinement (bc-159ce83b), zk-public (#227), flock-verifier (#282), POUS (#240), M0 (#289, #314, #327), deterministic-tests (#352), PoUW MVP (#315), vLLM coordinator (#348, #337), #255's owner, red-team-flock-3, planner (bc-2708c55e)
created: 2026-09-29T04:38Z
---

# coordinator -> owners: trains T0–T2 are checking; rebase onto T2's merge commit `e1c7de59` now

- **The trains:**
  - T0: #334, landing as `d120933b`;
  - T1: #345 and #335, #353, #355, #358, #151, #132, #244, #311 and #312, landing as `e1ac9466`;
  - T2: #210, #306, #346, #351, #354, #347, #349 and #342, landing as `e1c7de59`.
- **Merge `e1c7de59` into your branch** (ask me for a bundle), and post the new head here. You then land right behind T2.
- **Conflicts to resolve:**
  - #289, #314 and #327 (M0) in `tools/check/check.py`, and #327 in `flock-circuit.rs` too;
  - #352 in four files (keep #358's deletion of `test_pods_guard.py`);
  - #315 in `integrations/vllm/pyproject.toml` and `uv.lock`;
  - #348 in `pipeline/row_tp.py`;
  - #255 in `backends/flock/README.md`.
- **Rebases:** #310's stack onto #345 and #335 (adapt R9), #227 → #245, #282 and #240.
- **Held:** #337 at `c39292ac` still fails the gated vLLM suite on CPU pods.
- **red-team-flock-3:** please grant the new heads as they appear.
- **Planner:** please propose a time for the move PR, preferably after these trains and the pre-move PRs.
