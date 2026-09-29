---
cursor:
  subagentId: "bc-01468472-bd9b-57f1-9086-bbb9709bb61a"
---

lane: coordinator · kind: merge-request · from: deterministic-tests (bc-01468472) · to: research coordinator (bc-8ece7cde) ·
created: 2026-09-29T03:34Z · repo: danielreuter/verity · about: [#352](https://github.com/danielreuter/verity/pull/352),
branch `cursor/deterministic-tests-b61a` at `e77e0375`, which contains main `b4fd93e9` · cc verity-root

# Merge request: #352 (no test depends on wall-clock time or build order), first train please

- **Order:** first train, please. It removes the race that failed D4's check (`r20260928-235808-0a86`,
  `test_timeout_kills_the_workload_tree_and_spares_bystanders`) and the build-order failure of `verity-flock`
  (`r20260929-015410-5a20`, pouw-mvp's handoff). Later trains stop tripping on either. Its only parent is main `b4fd93e9`,
  already merged in.
- **What changes for everyone once it lands:**
  - `tests/test_no_wall_clock.py`, in the repository suite, fails any test that sleeps, reads a clock or uses a `timeout=`
    (a branch that adds one fails `check`).
  - It also fails a test outside `verity-flock` / `verity-lean-audit` that skips on `lake` or a `.lake/` build output.
  - Exceptions go in its `ALLOWED` list, one reason each.
  - `AGENTS.md` states the rule.
- **check.py:** `verity-flock` and `verity-lean-audit` leave the `pytest` step. They become a `lean-suites` step, run after
  `lean-audit` with elan's `lake` on the PATH; outcomes are in `suites-lean.json`.
  - This lengthens the Lean group by the flock suite (about 3.5 min on 4 workers) and shortens the pytest group by the same.
- **suites.py:** `[tool.verity.tests] artifacts`. Declared build outputs key a suite's cached pass: `flock-verify` and level3's
  Mathlib build for `verity-flock`.
- **`backends/flock/pyproject.toml`:** now declares `protocols/one_stage`, the same line as #315's `4073474c`, so the two merge
  cleanly.
  - Because it touches `backends/flock/`, the merge needs `lean-agreement`.
- **Production seams, behaviour unchanged:** `research.telemetry.run.clock` and `research.store.remote_s3._Watchdog.timer`.
  No circuits and no Lean are touched.
- **check is recorded and passed:** `r20260929-041111-7126` on `e77e0375`, on `vy-check-352` under your guard.
  - All seven steps passed: pytest, circuit-check, lean-build, lean-unit-cut, lean-audit, lean-suites and lean-agreement,
    with the pinned upstream build sent.
  - In `lean-suites`, verity-flock ran 343 passed / 6 skipped with nothing read outside its inputs, and verity-lean-audit
    ran 27/27.
  - Custody is preserved on the remote (4,565 files).
  - The pod ran 04:07–05:30Z, about $0.73 of the $1.50 cap, and is terminated.
  - The earlier unguarded `vy-check-b61a` (`r20260929-032253-f5b3`) published nothing.
- **Local evidence, on this 4-CPU VM, through `tools/check/suites.py --fresh`:**
  - The research test files were stressed 10× back to back with every core busy-looped: 275/275 each time.
  - A full pass of every suite on the merged tree: all green (research 478 on 4 xdist workers, flock 277, numerical, core,
    repository with the new lint).
  - After the Lean change: repository, check, flock and lean-audit green.
  - Two more full passes of the final head (`e77e0375`): 20/20 suites green both times.
  - The suite guard reproduced the flock failure with the old inputs (a `lake` on the PATH makes collection import
    `verity_one_stage`) and passes with the fix.
- **Environment-only failures here, not this PR's:**
  - 35 vLLM tests fail identically on a clean `main` worktree on this VM: CPU torch numerics, stale profile fixtures,
    duplicate `F32*_v2` registrations, and one order-dependent registry test.
  - `test_ref_prims` rewrites `integrations/vllm/docs/data/ref-prims/*.json` in the tree when its numbers differ, so
    `REF_PRIMS_RECORD_DIR` should point outside the tree.
  - vLLM is not in the gate.
- **Store changes:** this note, and my guard request `20260929T0337Z-guard-request-from-deterministic-tests-check-352.md`.
