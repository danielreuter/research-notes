---
id: vllm-rf-a4/state
lane: vllm-rf-a4
kind: state
updated: 2026-09-25T12:03Z
---
# a4 (re-home into the §5.1 tree): state

> **a4, 12:03Z: READY.** `READY.md` in this directory. Branch `lane/vllm-rf-a4` @ `10996616` (pushed). All gates pass.
> Every pod is terminated and unregistered. Evidence is preserved as
> `art:a7d652556f976541977458fda01ba123b2050b1a8025e096043c8ed44c770f29`.

> **Coordinator, 06:35Z: owner-approved naming. The evaluator implementations are "kernels": use `program/kernels/`, not `program/backends/`,** wherever SYNTHESIS 5.1/5.2 say `program/backends/`. Details: `20260925T0635Z-handoff-from-vllm-coordinator.md`.
> **a4, 07:12Z: done** in `22f5bc58`.

Coordinator: vLLM coordinator bc-ba6cec03. Worktree `/Users/danielreuter/projects/verity-wt/rf-a4`, branch
`lane/vllm-rf-a4`, head **`10996616`**, on origin/main `00ffe398`. origin/main is now `c09d74e6` (backends/,
benchmarks/, tools/research/ and tests/ only, no overlap with this branch). `git merge-tree` is clean. Not rebased.

## Done (evidence under `evidence/`)
- All moves committed and pushed (16 commits; table in READY.md).
- Lints 45/45 at head and at base.
- Gate (b) xdist, same pod: no new error, skip or skip reason. The one new failure (test_twins 'openmp') depends on
  the build dir and reproduces at base with an empty one (`evidence/twins/`). 942 renamed test ids.
- Gate (a) T0+T1 at head: 158 tests, 73 passed, 85 skipped, identical to a23b's base test by test. Two skip-reason texts
  (#70 and #75 manifest_digest, "row_pod_tp2.sh" -> "tp_stage.sh") come from main's `5cc0506e`, already in base
  `00ffe398`. Peak 130.8 GB, 3 h 14 min.
- GPU smoke #101 at head and base: root `7adcef49…`, program `ccc21347…`, manifest `90f81868…`, commit PASS.
  All 33 `python -m` targets in ops/*.sh resolve.
- Pods: cpu (terminated 08:42Z), g1 (09:07Z) and reg (11:54Z) are all terminated and unregistered. Spend is about $9.4
  of the $45 budget.

## Found, not fixed
- Listed in READY.md.
