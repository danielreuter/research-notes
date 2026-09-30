---
id: 20260930T2316Z-handoff-from-accounting-548-forkserver-fix
campaign: pouw
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: accounting-merge (worker of bc-e90634dd)
---

# #548 is merge-ready at `37e9c944`: the forkserver fix is in, and its recorded check passed on vy-nebius-2

This updates `note:20260930T2158Z-handoff-from-accounting-pearl-c-chain-merge-request`, whose #548 entry failed its check.

- **PR:** [#548](https://github.com/danielreuter/verity/pull/548), branch `cursor/pearl-c-fp4-3084`.
- **Tip:** `37e9c944b570316c0cb8512f8d310419f2986b24`.
  - It contains #449 at `135a1123` and main `984cd238`, as merge commits with no force push.
  - `main` has since moved to `ce30e9b6` (train TQS), which merges cleanly.
- **The fix,** one commit that changes only `benchmarks/pouw/tests/test_pearl_c4_real.py` (+12):
  - An autouse fixture `monkeypatch`es the test module's `real.py` so its `ProcessPoolExecutor` uses a `fork` context.
  - Forked workers inherit the test's `importlib`-loaded `pearl_c4_real` module. Python 3.14's default `forkserver` workers
    import the pool's callable by module name, and only the test process has that name, which is why the check failed with
    `BrokenProcessPool`.
  - `real.py` is unchanged. Run as a script under Python 3.14's `forkserver`, it completes on the test's capture: exit 99 out
    of budget, then 0 with its summary.
  - Why not put `pearl_c4` on `sys.path`? Other tests in the suite start process pools, so a forkserver could already be running
    with the old `sys.path`. Also, the testing skill allows `sys.path` changes only through `monkeypatch`.
- **Recorded check: passed.** `r20260930-222746-4aa1`, `check.py --record --on vy-nebius-2`, on exactly `37e9c944` (a clean
  checkout).
  - It finished at 4:02 PM PDT with rc 0.
  - Every step passed: preflight, lean-build, lean-unit-cut, circuit-check, flock-circuit-build, and pytest (18 of 18 suites,
    pouw benchmarks 57).
  - `lean-audit` passed after 1,709 s, because it re-audited `soundness` for main's Lean changes. `lean-suites` passed.
  - `lean-agreement` was skipped by name: nothing of #548's is under `backends/flock/`.
  - On node 2, under the pytest group's load, `test_real_activation_replay` took 232 s (about 20 s on a 4-core VM). It is not
    marked slow.
- **Local suites on the tip, under Python 3.12.3 and 3.14.7 (the check's):** pouw benchmarks 57, pouw 236, repository 32.
  - Under 3.14.7, both tests failed before the fix with the same `ModuleNotFoundError: No module named 'pearl_c4_real'`.
- **Grants: none.** No `.lean` file, `lean-audit.json`, lakefile or manifest changes against `main`, and nothing under
  `backends/flock/`.
- **Order:** after #449 (train TPC). #534, #556 and #602 belong to bc-a8466279, who carries this head up through them.
