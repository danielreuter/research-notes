---
cursor:
  subagentId: "bc-dc2611ba-e850-5f2e-8d51-0b023bd3c4a4"
lane: coordinator
kind: handoff
from: fixture-process (bc-dc2611ba)
to: research coordinator
created: 2026-09-29T17:46Z
---

# Merge request: #371, fixture migration (`be6acc18`, on `main` `33828711`). Please record `check` and merge

[#371](https://github.com/danielreuter/verity/pull/371), branch `cursor/fixture-migration-c4a4`, head `be6acc18`, on `main` `33828711`.

**What merging it does:** the 98 fixtures over 256 KiB leave the tracked tree. They become fetched entries of `fixtures/artifacts.json`, which `suites.py` fetches before the suites that read them. This is the history rewrite's last in-repo prerequisite. The rewrite itself stays a separate, gated step.

**What it touches:**
- `fixtures/`, the fixture directories of `backends/ligero-verify`, `ligerito-verify`, `gkr`, `direct` and `sp1`, `integrations/vllm`'s regression expectations, and `packages/verity`'s test fixtures;
- `tools/research`, `tools/check/suites.py` and `tests/test_repository.py`.

It touches nothing under `backends/flock/`, so `lean-agreement` doesn't apply. It changes no Lean, no pin and no statement.

**What's new in this head:**
- `26de2c10` merges `main` `33828711` with no conflicts. `fixtures/artifacts.json` is byte-identical to the `c0fa718c` that was exported.
- `be6acc18` sets `fetchset.PUBLIC_URL = "https://website-docs-sage.vercel.app/store"` (contract v2). `tools/research/tests/conftest.py` now sets `RESEARCH_PUBLIC_URL` to empty, so no test reaches the site.

**Prerequisites met:**

| Step | Result |
|---|---|
| Export `r20260929-173206-2a39` | 244 objects, 162,838,599 bytes, to `verity-public`; one warning, the known lost superseded id `d775cc59` |
| Verify through the bucket's public URL, `r20260929-173311-bc54` | 111 manifests and 133 blobs checked, 0 missing |
| Verify through the site's `/store`, `r20260929-173405-4048` | the same counts |
| Keyless fetch on `be6acc18`, fresh clone | no private credentials and `RESEARCH_PUBLIC_URL` unset: `106 entries: 98 fetched, 8 tracked; 120 blob(s), 159.1 MB fetched from https://website-docs-sage.vercel.app/store`; `--check` gives 98 present |

- All three runs are PRESERVED. Each carries `stage` and `note` labels by `fixture-process`.
- **Local:** `suites.py research repository tools/check --fresh` passes on `be6acc18`: 3 suites passed.

**For the `check` pod:** its first run fetches about 159 MB of fixtures. It uses the private remote where its credentials reach it, and the site otherwise. A fetch failure fails the suite that needed it, and the failure names `fetch-fixtures.log`.

**For lanes after the merge:** `suites.py` fetches on its own. Anyone who runs `pytest` or `cargo test` directly on a fetched fixture runs `uv run research data fetch-fixtures` once. `test_ligero_batch_bound` fails without `b1.proof`, rather than skipping.
