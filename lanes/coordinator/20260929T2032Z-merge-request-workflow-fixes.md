---
cursor:
  subagentId: "bc-d66f1270-7ec2-58a6-925c-0b2e1b3c1fd2"
---

lane: coordinator · kind: merge-request · from: merge-workflow review (bc-d66f1270) · to: research coordinator (bc-8ece7cde); cc
verity-root · created: 2026-09-29T20:32Z · repo: danielreuter/verity · about: [#437](https://github.com/danielreuter/verity/pull/437)
`cursor/lean-audit-key-without-check-1fd2` at `16739c6c` and [#438](https://github.com/danielreuter/verity/pull/438)
`cursor/check-fail-fast-1fd2` at `baa24d09`, both on `main` `33828711`

# Merge request: #437 and #438, the check workflow fixes (review changes 1 and 2, approved by Daniel)

**What:** changes 1 (the code part) and 2 of `docs/merge-workflow-review.md`. #438 is stacked on #437: its branch contains
#437's commit and targets `main`. Land them in one train, #437 first, or #438's head alone, which carries both.

- **#437:** `lean_audit.py` no longer loads `check.py`. Its four helpers (`cache_dir`, `cores`, `_sha256`, `tracked_files`)
  move to `tools/check/common.py`, which is standard library only. `lean_audit.key` hashes `common.py` instead of `check.py`,
  and `check.py` keeps the same names as aliases.
- **#438:**
  - A preflight runs before the three groups: `uv lock --check`, `tests/test_no_wall_clock.py`, and the blob cap in
    `tests/test_repository.py`, about 6 s in all.
  - A failed step stops the others: SIGINT to their process trees, then SIGKILL after 60 s; their status is `stopped`.
  - Each step's record is appended to `steps.jsonl` as the step ends, and it is published with the result.
  - `--keep-going` keeps today's behaviour.

**#437 changes the Lean audit key once.** Every package's key hashes a different file list, so the first check after it
lands re-audits all four Lean packages cold for the key; allow for that in the first Lean train. After that, a
`check.py`-only edit keeps every package's verdict, including through `--verdicts-in`. #438 doesn't touch `lean_audit.py`,
`common.py` or `tools/lean/`, so it doesn't change the key again.

**What changes for your launches after #438:**
- **Lints:** the wall-clock lint and the blob cap run at the start of every check. The by-hand lint before each launch is no
  longer needed.
- **Early failures:** a failure is visible in the run directory's `steps.jsonl` as soon as its step ends.
- **When to pass `--keep-going`:** a stopped step stores no verdict. For a check whose passing verdicts you want to keep
  after a failure, pass `--keep-going` (`check.py --record ... --keep-going` passes it through), for example so that the MoE
  tests' verdict survives when you eject a Lean PR. A plain check stops everything on the first failure.

**Scope:**
- Only `tools/check/` changes: `check.py`, `lean_audit.py`, the new `common.py`, `pyproject.toml` (two lint files added as
  test inputs) and tests. Nothing under `backends/flock/`, so `lean-agreement` doesn't apply.
- No Lean, no pin, no statement, so no grant is needed.

**Checks here:**
- `uv run tools/check/suites.py tools/check repository --fresh` at `baa24d09`: verity-check 68 passed, repository 29 passed.
  These are the only suites whose inputs include `tools/check`.
- The stop test passed 15 runs in a row.
- #437's two key tests fail with `check.py` put back into the key.
- No pod runs on my side. Please record `check` on the train with `tools/check/check.py --record --on MACHINE`.
