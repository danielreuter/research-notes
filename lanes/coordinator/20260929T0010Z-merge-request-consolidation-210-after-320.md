---
cursor:
  subagentId: "bc-e373566b-e6f1-5c72-88c3-86eec290ac68"
lane: coordinator
kind: handoff
from: consolidation coordinator (bc-e373566b)
to: research coordinator (bc-8ece7cde)
created: 2026-09-29T00:10Z
---

# #210 new head `7a8afa30`, fixed for D3′ + W's check `r20260928-222342-152c`

- **PR:** [#210](https://github.com/danielreuter/verity/pull/210), branch `cursor/core-boundaries-ac68`, head **`7a8afa3080bffe1c4e3203e6bac3fd8f07d82435`**, with `main` `5810574d` (after #134 and #320) merged in. The only conflict was the root `pyproject.toml`, where `main`'s per-suite layout was taken.
- **Fix 1, #320's read guard:** `tools/tc_probe/pyproject.toml` lists `fixtures/discrepancy_log.json` under `[tool.verity.tests] inputs`. The trust tests #210 moves into that suite read it.
- **Fix 2, #236's site:** `KNOWN` lists `backends/flock/tests/test_lean_typed_statement.py → verity_vllm.program.registry.prims` ahead of #236.
  - A listed file that doesn't exist yet no longer counts as "gone"; once it exists, its entry must match its imports.
  - So #210 passes on `main` alone, and with #236 merged in, in either order. Both were checked.
- **`uv run tools/check/suites.py verity-tc-probe repository verity --fresh`**, with the read guard on:
  - `repository`: 18 passed;
  - `verity-tc-probe`: 42 passed, 3 skipped;
  - `verity`: 1,305 passed.
