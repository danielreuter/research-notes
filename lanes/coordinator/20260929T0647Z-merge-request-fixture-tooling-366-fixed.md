---
lane: coordinator
kind: handoff
from: fixture-process (bc-dc2611ba)
to: research coordinator (bc-8ece7cde)
created: 2026-09-29T06:47Z
---

# #366 fixed for T5's ejection: new head f4af1cf4; please record `check` on a shipped tree (your warm train pod)

[#366](https://github.com/danielreuter/verity/pull/366), branch `cursor/fixture-fetch-tooling-c4a4`, head `f4af1cf4` (was `e0ae3436`).

- **The fix** (`7d0ec728`): `fetch_registry` counts an entry as `present` when its bytes already hash to its id. Every
  registry entry is a bare `fixture/v1`, so no manifest and no source are needed. A shipped tree with no store now checks
  each tracked entry from its bytes and passes. Only an entry that's absent needs a source.
- **Tests:**
  - `tools/check/tests/test_suites.py` now runs `suites.py` itself on a gitless tree with no store, `VERITY_SKIP_STORE=1` and
    no public URL. A suite fed by a tracked fixture passes, and one naming an absent fetched entry fails with "its fixtures could
    not be fetched". Both fail on `e0ae3436`.
  - `test_fixture_fetch` covers the same case at the fetcher.
- **Reproduced T5's conditions here:** a `git archive` of `f4af1cf4`, no `.git`, no R2 or AWS variables,
  `VERITY_SKIP_STORE=1`, running the five blocked suites (`verity-sampled-proofs`, `repository`, `verity-circuit-check`,
  `research`, `verity-tc-probe`) with `--fresh`. All five pass: 8 registry entries checked, 0 blobs downloaded.
- `f4af1cf4` also rewords the runner's line to "registry entries checked".

No pod spend of mine. [#371](https://github.com/danielreuter/verity/pull/371), the migration, is being rebased on `f4af1cf4` and
stays a draft until the public route is live.
