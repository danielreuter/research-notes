---
cursor:
  subagentId: "bc-ea1c2c4f-07dd-56b4-afdd-10e38e1a866f"
lane: coordinator
kind: handoff
from: backend GPU sweep (bc-ea1c2c4f)
to: research coordinator (bc-8ece7cde), tonight's merge pipeline
created: 2026-09-28T04:30Z
---

# Merge request: PR #182, the per-shape statement and the sweep's tooling, right after #192

Daniel wants #182 on `main` tonight, right after #192, since collaborators look at the repo tomorrow.

- **The PR:** [#182](https://github.com/danielreuter/verity/pull/182), branch `cursor/class-statements-866f`, head **`8dd350a2`**. It's
  stacked on #192: `adcf38bf` is merged in, and the PR's base is #192's branch.
- **Over #192 it changes 7 files**, and none of them are #193's, #195's, #197's or #198's:
  - `backends/flock/python/verity_flock/class_statement.py` (new): a unit shape of any partition as a `verity/flock-circuit`
    statement, with the per-source row layout and shared rows;
  - `backends/flock/python/verity_flock/class_sweep.py` (new): the sweep's work lists (`plan`) and whole-row figures (`rollup`);
  - `backends/flock/tests/test_class_statement.py` and `test_class_sweep.py` (new);
  - `backends/flock/pod/70-class-sweep.sh` (new): the pod harness;
  - `backends/flock/tool.py`: adds the `FLOCK_CLASS_SWEEP` Tool;
  - `tools/research/src/research/store/tools_registry.py`: adds one line, `flock_class_sweep`.
- **No Lean and no circuit** (a shape's circuit comes from `partition_units.lower_class`, already on `main`), so it needs no
  circuit-check report and no red-team pin. There are no report-genre files: results stay in the evidence store.
- **`check`:** recorded run `r20260928-040715-7615` on `8dd350a2`, running since 04:07Z on the agent VM. I'll post its result
  here. The two test files pass locally; the statement test proves with `FLOCK_CIRCUIT` set and skips proving without it.
- **Order:** in the M0 train with #192 if it hasn't started, else the train right after. Once the M0 train is on `main`, I'll
  merge `main` into #182 and record `check` on that head if you need it to be the exact commit.

The phase-1 and phase-2 sweep launches on #182 merged with the M0 train's commit once that train's `check` passes, under the
`vyb-` guard ($250, 10 $/h, deadline 18:56Z; the plan is in `docs/backend-sweep.md`).

## Update 05:00Z: `check` passed on `8dd350a2`

`r20260928-040715-7615`, recorded on the agent VM and preserved on the store's remote:
- pytest: 3,171 passed, 42 skipped;
- `circuit-check --all`, `lean-build`, `lean-unit-cut` and `lean-audit` passed;
- `lean-agreement` was skipped: no bundle.

Also checked: #182 with `main` (train M), #192, #193, #195, #197 and #198 merged in merges cleanly, and both of #182's test files
pass on that tree. So #182 can ride the M0 train as it is.

A follow-up, [PR #212](https://github.com/danielreuter/verity/pull/212) (draft, stacked on #182), holds the re-aggregation for the
re-baseline's new digests. It isn't part of tonight's request.
