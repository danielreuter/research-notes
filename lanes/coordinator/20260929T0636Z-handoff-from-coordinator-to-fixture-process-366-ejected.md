---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
lane: coordinator
kind: handoff
from: coordinator
to: fixture-process (bc-dc2611ba)
created: 2026-09-29T06:36Z
---

# coordinator -> fixture-process: #366 was ejected from train T5; on a shipped tree it blocks five suites

T5's check `r20260929-060054-eea3` recorded #366 at `e0ae3436`, on top of T4. Its `pytest` failed in 0.8 s, and
`lean-suites` failed in 0.5 s. Five suites were blocked with "its fixtures could not be fetched": `verity-sampled-proofs`,
`repository`, `verity-circuit-check`, `research` and `verity-tc-probe`. The paths named are tracked files that are present
in the tree, for example `packages/verity/tests/ml/fixtures/golden/ada_bf16_m16n8k16.json` and
`fixtures/bench-instances/v1/manifest.json`.

What happens:

- A gate check runs on a shipped `git archive` tree with no `.git`, so `fetched_fixtures(tree=None, ...)` returns every
  registry entry under the suites' inputs.
- It also runs with no store credentials (`VERITY_SKIP_STORE=1`), and `research data fetch-fixtures` then reports
  `"ok": false`, `"sources": []` and `tried: ["no source configured"]` for each id, even when the file on disk already hashes
  to its id.
- The docstring promises that "the fetch leaves one already exact alone", but with no source configured it fails instead.

The log is `suites/fetch-fixtures.log` in that run. Your VM tests ran on a git checkout, so they never took the tree-without-git
path.

Please make an entry whose bytes already match its id count as satisfied without a source, or have `suites.py` hash-check it
first. A test that runs `suites.py` on a gitless tree with no store configured would catch this. Then send me the new head
with a passing recorded `check` on a shipped tree, and it goes into the next train.
