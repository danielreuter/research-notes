---
id: 20260930T0040Z-merge-request-pouw-pearl-baselines-332
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# Merge request: #332 at `189b2528`, both Pearl baselines in the PoUW benchmarks (after #436)

- **PR:** [#332](https://github.com/danielreuter/verity/pull/332), branch `cursor/pouw-gamma-pearl-fa-4f91` at
  `189b2528f3167b26672561b0ddbe5c24b8bb3485`. It is ready for review, and the base is `main`.
- **Order:** after #436, or together with it. #332 contains #436 at `79b877bc`, merged in, because both rewrite
  `benchmarks/pouw/gamma.py`, `gemm_bench.py` and `vllm_bench.py`. It merges cleanly on `main` `62ce91fa`. If #436's
  head moves, I'll merge it forward and refile.
- **What:** Daniel wants both Pearl baselines tracked. The as-shipped reading (F_A keyed by seed_B, so B̃·F_A is paid
  once per weight) stays the headline, and it is `main`'s accounting, unchanged. The whitepaper reading (F_A fresh per
  activation commitment, so B̃·F_A is paid per unit) is added beside it, labelled everywhere:
  - `gamma.py`: rows labelled `pearl-fp8-v4 (as shipped)` and `pearl-fp8-v4 (whitepaper)`;
  - `gemm_bench.py`: `pearl_*` and `pearl_whitepaper_*`;
  - `vllm_bench.py`: modes `pearl` and `pearl-wp`.

  The γ floor at 8192³ is 2.312% as shipped and 3.044% in the whitepaper reading.
- **Touches:** only `benchmarks/pouw/`, so it isn't under the vLLM hold.
- **Needs none of these:** `lean-agreement` (nothing under `backends/flock/`); `circuit-check` (no circuit or Definition
  changes); a statement reviewer (no Lean or pins).
- **Checks at `189b2528`:** `uv run tools/check/suites.py verity-pouw-benchmarks repository`: 13 passed, 29 passed. The
  GPU scripts were not run.
- **`check`:** not recorded, since this VM has no pod. Please take #332 into the train after #436, or into #436's train,
  and record `tools/check/check.py --record` on the merged head.
