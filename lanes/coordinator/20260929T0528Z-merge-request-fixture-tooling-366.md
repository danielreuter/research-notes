---
lane: coordinator
kind: handoff
from: fixture-process (bc-dc2611ba)
to: research coordinator (bc-8ece7cde)
created: 2026-09-29T05:28Z
---

# Merge request: #366, fixture tooling (256 KiB rule, fetch-fixtures, export); please record `check` on `1127d89f`

[#366](https://github.com/danielreuter/verity/pull/366), branch `cursor/fixture-fetch-tooling-c4a4`, head `1127d89f`, on `main` `d120933b`.
Step 0 of the fixture process plan that Daniel accepted (Project store `docs/fixture-process-plan.md`). It moves no fixture; the
migration PR follows it.

- **What changes:**
  - `tests/test_repository.py`: a tracked file is at most 256 KiB, source code aside, with an 11-file allowlist. The 111
    fixtures over the cap are grandfathered in `PENDING_REGISTRATION` (each capped at its size) until the migration PR. A 40 MiB
    budget covers the rest of the tracked data.
  - `research.store.fetchset`: a parallel fetcher for any set of ids, checking every byte.
  - `research data fetch-fixtures`, and `research data export` with `--verify-url`.
  - `tools/check/suites.py` fetches the registry's fetched entries before the suites whose inputs hold them, and keys each suite
    on their ids.
- **Behavior today:** unchanged. No registry entry is fetched yet, so no suite fetches anything. `suites.py` itself changed, so
  every suite's key moves once and the first `check` runs cold.
- **Checks:** the new tests and the repository and `check` suites pass on this VM. `lean-agreement` doesn't apply (nothing under
  `backends/flock/`). No statement or pin changes, so no reviewer is needed.
- **No pod spend of mine.** Please record `check` on `1127d89f` and take it into the next train.
