---
id: 20260930T2158Z-handoff-from-accounting-pearl-c-chain-merge-request
campaign: pouw
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: accounting-merge (worker of bc-e90634dd)
---

# Pearl-C chain: #449 is merge-ready at `135a1123` (check passed); #548 is not (its own test fails under Python 3.14); #534 is untouched (another agent is on it)

This supersedes the old PoUW coordinator's merge requests for #449, #548 and #534 (train order #449, then #548, then #534). All
three had conflicted with `main` in `integrations/vllm/tests/commit/test_native_jit_load.py`.

## How they relate

They're stacked through merges, not independent: #548 merged #449 at `61d0298d`, and #534 merged #548 at `795d65f1`. All three
share merge base `cc0f4688` with `main`. So each updated branch merges its updated predecessor.

## #449: merge-ready

- **PR:** [#449](https://github.com/danielreuter/verity/pull/449), branch `cursor/pearl-c-h100-9ada`.
- **Tip:** `135a1123d490aa6c0e55b24952e1063f0cbcf062`, on main `e15dc1ef` (train TCQ). Merge commits only, no force push.
  - `main` has since moved to `4b6b72e1` (train TLU, 15 files under `backends/flock/` only). That merges cleanly, and none of
    its files are #449's, so the train's check of the merged tree covers it.
- **Conflict resolution:** both sides' tests are kept in `test_native_jit_load.py`.
  - #449 runs every test that calls `jit_load`, forks, signals or locks in a fresh interpreter (`@_isolated`), and its
    docstring says so. So main's four new `jit_load` tests (two trees, a differing staged source, duplicate basenames, local
    headers) get `@_isolated` too.
  - Main's two pure tests (the header-free digest, a header outside the sources) run in-process.
  - A deliberately broken copy of one isolated test fails with the child's traceback, so main's tests really run.
- **Recorded check: passed.** `r20260930-213922-3d25`, `check.py --record --on vy-nebius-2`, on exactly `135a1123` (a clean
  checkout).
  - It finished at 2:57 PM PDT with rc 0.
  - Every step passed: preflight, the Lean build, unit-cut, audit and suites, circuit-check, flock-circuit-build, and pytest.
    Pytest was 18 of 18 suites: vllm 4487, verity 1333, pouw 202, pouw benchmarks 51.
  - `lean-agreement` was skipped by name, since nothing of #449's is under `backends/flock/`.
- **Local suites on the tip:** repository 32, verity 1333, pouw 202, pouw benchmarks 51, and the jit test files 14 (with
  `test_native_jit_isolation.py`).
  - Earlier, on main `b1c77be0`: vllm passed 4479 and failed 1. The failure was
    `test_tp_moe_members[qwen3-30b…tp2]`, OOM-killed twice on a 15 GB VM; it passes alone (927 s) and in node 2's check.
- **Grants: none.** No `.lean` file, `lean-audit.json`, lakefile or manifest changes against `main`, and nothing under
  `backends/flock/`.

## #548: not merge-ready (its own test fails on the check's Python)

- **PR:** [#548](https://github.com/danielreuter/verity/pull/548), branch `cursor/pearl-c-fp4-3084`.
- **Tip:** `b80db70223c0e2ad3deecbee6248615305f48828`. It merges #449 at `135a1123` and so contains main `e15dc1ef`. That merge
  was clean.
- **Recorded check: failed.** `r20260930-211930-3da0` on vy-nebius-2, on exactly `b80db702`.
  - Every step passed except pytest: 17 of 18 suites passed, vllm 4487 among them.
  - `verity-pouw-benchmarks` passed 55 and failed 2: `tests/test_pearl_c4_real.py::test_real_activation_replay` and
    `::test_an_npz_capture_is_read_as_its_linears`, both `BrokenProcessPool`.
- **Cause, which is already in #548 and wasn't made by the merge:**
  - `pearl_c4/real.py` runs its tasks in a default `ProcessPoolExecutor`.
  - The test loads `real.py` through `importlib` under the name `pearl_c4_real`, which exists only in the parent's
    `sys.modules`.
  - Node 2's check runs Python 3.14, where a Linux process pool starts its workers from a `forkserver`, not by `fork`. A worker
    that unpickles `pearl_c4_real.run` raises `ModuleNotFoundError: No module named 'pearl_c4_real'`.
  - On 3.12, which forks, it passes: 57 of 57 on my VM.
  - Running `real.py` as a script is probably unaffected, because the forkserver preloads `__main__`.
- **Fix needed from #548's owner:** either the test loads `real.py` under a name its workers can import, or `real.py` names its
  pool's start method. Then a fresh `check` of #548's tip.
- **Local suites on the tip (Python 3.12):** repository 32, verity 1334, pouw 236, pouw benchmarks 57.
- **Grants: none.** No Lean or `backends/flock/` changes against `main`.
- **Behaviour note, for review rather than a grant:** the chain changes `verity.ml.tc` in core.
  - `BlockScaledAlignAdd` gains `align_add` and `grid`, a refactor of `_transducer`.
  - #534 also makes `models._scale_dyadic` read a UE4M3 scale from its low 7 bits instead of rejecting bit 7.
  - No Lean in the tree transcribes the UE4M3 decode, so no pin reads it.

## #534: not pushed

- **PR:** [#534](https://github.com/danielreuter/verity/pull/534), branch `cursor/pearl-c4-salt-keyed-b-2cf6`.
- Another agent committed to it while I worked: `d4cc0afb` became `170a8e42` (D-NF commits, 20:15–20:50Z), and it is now at
  `e19b783e`. I didn't push over it.
- Its new commits conflict with #548's newer commits in `protocols/pouw/verity_pouw/schemes/pearl_c4.py`. Its owner should
  merge the fixed #548 once #548 lands or is fixed.

## Train order

1. **#449 `135a1123`,** now: a train of its own, or first in any train. The train's check covers `main` `4b6b72e1`.
2. **#548,** after its test is fixed and a check of its new tip passes. It contains #449.
3. **#534,** after its owner merges the updated #548.
