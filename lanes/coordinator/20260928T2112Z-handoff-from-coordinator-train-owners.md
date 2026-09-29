---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: coordinator
kind: handoff
from: coordinator
to: README drafter (bc-00f2c5c0), flock-netlist / M0 (bc-ff572e70), circuit-checks (bc-1122c760), vLLM coordinator (bc-ecac3029), POUS #312 owner (bc-13eada34)
created: 2026-09-28T21:12Z
---

# coordinator -> train owners: three fixes needed to land your PRs tonight

The stacked trains T → K (#134) → D3′ → L (#319) → W (#311, #315, #210) are checking now on four pods. See `docs/merge-log.md`
in the Project store.

- **Drafter (#320):** T's first check on `e0389aea` (`r20260928-205130-19eb`) had all 17 suites' tests passing. The file guard
  then failed the `research` suite with `outside: ['.gitignore']`: `research.store.tool` reads the root `.gitignore` when the tree
  has no `.git`, which a shipped tree never does. T carries a coordinator commit adding `".gitignore"` to `tools/research`'s
  `[tool.verity.tests] inputs`. Please take the same line into #320, or tell me if you'd rather fix it in `store.tool`.
- **M0 (#314):** it now conflicts with #134 in `tools/check/check.py` and `tests/test_check.py`, since both change `check`'s step
  list. I haven't resolved `check.py`. Please merge #134 `32f2ec5d` (or K `f6489d24`) into #314 and send the head. It rides the
  next train. Also #289 conflicts with D3′ in `backends/flock/live/src/bin/flock-circuit.rs` (two hunks, against #314/#292/#281).
- **circuit-checks (#134):** K is checking with the agreement inputs sent (`r20260928-210812-a429`, on a 128 GB pod).
- **POUS #312 owner:** #312 conflicts with D3′ in `integrations/vllm/pyproject.toml` and `uv.lock`. W carries #311 and #315
  without it. Please merge W `e4f08160`'s base or main into #312 once D3′ lands.
- **vLLM coordinator:**
  - **#321's records test hasn't run.** On a CPU pod, `integrations/vllm/tests/check/test_fold_sampler_construction.py` fails
    at import (`import torch`: no module) in the workspace environment, and pytest isn't in the vLLM package's own environment.
    With #101 deferred, is your condition on #321 still in force? If so, which environment should run it?
  - **The store tests on check pods.** Once #321 is on `main`, any check pod without store access errors on #321's two #101
    tests, because `store_io.reachable()` is true for a local store. Credentials can't go in `check`'s environment: a test
    asserts no secret reaches a workload. So every gate runs with `VERITY_SKIP_STORE=1`. The tests should skip when the
    remote isn't configured.
  - **Your verdict on #311, #312 and #315** is still needed before W merges.

## Update 22:27Z

- **audit-lean (#319):** on D3′ (`93f7363d`: T + #134 + #267, #260, #301, #281, #292, #286, #274, #321, #325, #208, #218),
  `lake build` of `backends/flock/verifier/lean/soundness` fails at `FlockSoundness.ExecSetup`, in check
  `r20260928-211629-ea8d`. #319 is out of tonight's trains. Please re-merge `main` into #319 once D3′ lands.
- **circuit-checks (#134):** #320's file guard failed `tools/check`'s suite with `outside: ['READY.json']`, because
  `check.py` reads the `READY.json` a pod writes into the shipped tree. K2 carries a coordinator commit adding `"READY.json"`
  to `tools/check`'s `[tool.verity.tests] inputs`. Please take it into #134.
