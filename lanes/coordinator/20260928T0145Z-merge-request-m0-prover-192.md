---
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
lane: coordinator
kind: handoff
from: flock-netlist / M0 (bc-ff572e70)
to: research coordinator (bc-8ece7cde), tonight's merge pipeline
created: 2026-09-28T01:45Z
---

# Merge request: PR #192, C-Flock's circuit prover (M0) with inline reads, then #193

Daniel's go is to merge M0 as soon as possible.

## (a) #192

- **The PR:** [#192](https://github.com/danielreuter/verity/pull/192), branch `cursor/flock-m0-prover-4d6a`, head
  **`adcf38bf4a4bd7aacffdd04d2c9539f6c061deda`**, into `main`. It's marked ready, CPU only, and cost $0.
- **Contents:** #83 `73a273d4` with `main` `df3bc5e1` (train K) merged in, plus:
  - naive inline table reads;
  - the lowering lane's `tc_units` resolution;
  - the fixes the merge needed (`tail._f32_div`, and the `circuit_bench` domain field).
- **Split out:** the multi-table glue, now (b).
- **`check` on `adcf38bf`:** passed, in 46 min on the 4-vCPU CPU VM:
  - `pytest`: 3,166 passed, 42 skipped;
  - `circuit-check --all`: 811 targets, 0 new failures, 2 known;
  - `lean-build`, `lean-unit-cut` and `lean-audit` passed;
  - `lean-agreement` was skipped: no bundle.

  The run was unrecorded (the local tree, not `--record`), so the pipeline's recorded run is the one of record.

## (b) #193, right after

- **The PR:** [#193](https://github.com/danielreuter/verity/pull/193), branch `cursor/flock-m0-glue-4d6a`, head `b7e16c46`,
  stacked on #192.
- **Contents:** the multi-table statement with private glue. Its files are byte-identical to #83's.
- **Status:** its `check` is running now. I'll post the result and mark it ready when it passes.

## Statements

- **`verity/flock-circuit` itself is unchanged.**
- **Every template's pinned circuit changed, only in its unit,** because of train K's lowering. So the Table 1 cells
  (`art:e352f2ad`, `art:a83371c2`), recorded at #83 `855fe81f`, pin #83's circuits, not (a)'s.
- **The red team's list:** `20260928T0125Z-note-to-red-team-m0-prover-pr-statement-changes.md`.

## Other notes

- **The Lean tags:** the request to the verifier lane (bc-8e519ca0) is `20260928T0110Z-note-to-flock-verifier-m0-tags-at-prover-pr.md`.
  (a)'s statement is its `circuit967b8d06` tag set, so the lane's change lands after (a) and needn't block it.
- **Heads posted to** the backend GPU sweep (bc-ea1c2c4f) and the constant-API rollout (bc-613ddf45):
  `20260928T0100Z-note-to-backend-stress-and-constant-api-m0-prover-head.md`.
- **Superseded:** #83 and #184 (the inline-reads draft) are superseded by #192. I've left both open for you to close.

Next from me: the GEMM cell's `commit.seconds`, and the attention input set re-registered with its meta. Both are done: see
`20260928T0205Z-answer-flock-netlist-m0-input-set-and-gemm-commit.md`.

## Update 02:55Z: #193 is ready too, and both are granted

- **#192 `adcf38bf`:** the red team **granted** it (`private/red-team-reviews/m0-statement/split-192-193-195.md`). The
  statement is byte-identical, and inline reads meet all three conditions. Its non-blocking recommendation (row-order
  checking) is superseded by phase 1, so it isn't acted on.
- **#193 is marked ready,** at head **`b47f8009de8b3b0d86f3d9225e5bbcbecd9bcd0b`**, stacked on #192. Please merge it right
  after #192.
  - **The only change since `b7e16c46`:** its test is renamed to `test_flock_tables.py`. `main` has another
    `test_tables.py`, and pytest refused to collect both.
  - **`check` on `b47f8009`:** passed in 39 min.
    - `pytest`: 3,167 passed, 42 skipped;
    - `circuit-check`: 811 targets, 0 new failures;
    - the Lean steps passed; `lean-agreement` was skipped.

    One earlier run hit `tools/research`'s known lock-file race, which passes 3 of 3 alone. #193 doesn't touch
    `tools/research`.
  - **The grant is scoped:** the code merges, but no cell or Table 1 row may cite `verity/flock-tables` until that statement
    has its own review. The PR body says so.
- **Also for the queue:** [#198](https://github.com/danielreuter/verity/pull/198), the `serving_commit_cost` tool that both
  re-recorded cells' `commit.seconds` cite (commit `33f057ec`). It's into `main`, independent of #192.
