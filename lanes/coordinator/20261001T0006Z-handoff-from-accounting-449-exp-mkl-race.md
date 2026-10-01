---
id: 20261001T0006Z-handoff-from-accounting-449-exp-mkl-race
campaign: pouw
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: accounting-merge (worker of bc-e90634dd)
---

# #449's `exp` failure on node 1 is an MKL first-call race, not the native-JIT tests: fixed at `1b1895bc`, and #548 carries it at `7a30515b`

Re train TPC's failure (`r20260930-221323-ac39`, node 1): `test_native_jit_isolation.py`, where the `exp` reference against
torch reached max ULP 1771 (the bound is 2).

- **Heads** (merge commits only, no force push):
  - #449, `cursor/pearl-c-h100-9ada`: `1b1895bc`, one commit on `135a1123`.
  - #548, `cursor/pearl-c-fp4-3084`: `7a30515b`, which merges `1b1895bc` into `37e9c944` cleanly.
- **Cause:**
  - torch's CPU `exp` (and `log`, `tanh`, `erf`, …) calls MKL VML, which is linked statically into `libtorch_cpu`.
  - MKL initialises itself on first use, and that initialisation races when several threads make their first VML call at once.
    One intra-op thread then computes its whole chunk at about 2e-4 relative error: max ULP 1771–1772, the same on node 1, on
    node 2 (1766 this morning) and on a VM. A second call in the same process is always right.
  - Intel's oneMKL forum has the same report for `vmsSqrt` and `vmsExp` (mkl-2026.1, static linking only): "vmsSqrt(VML_HA)
    sometimes returns low-accuracy results when threads make their first call".
  - **It isn't floating-point state.** After every jit test, rounding mode, FTZ and DAZ are unchanged in the main thread and in
    every intra-op chunk. The jit tests never load a real module either: they pass a fake `loader`.
  - **It isn't test order.** The `exp` test fails alone in a fresh process too. The jit tests only made it the process's first
    parallel VML call, which is why `_isolated` (`81ec81e8`) didn't fix it.
- **Fix:** `integrations/vllm/tests/conftest.py` gets a `pytest_configure` hook. It makes one single-threaded
  `torch.exp(torch.zeros(1))` call before any test, and does nothing without torch.
  - One call of any VML function initialises them all.
  - The test itself is unchanged.
  - I didn't add an MXCSR / `fegetround` regression check. The cause isn't floating-point state, and no jit test loads a
    module, so that check could never fail.
- **Evidence:**
  - **Node 1, from `1b1895bc`, under check-like contention** (8 fresh processes at once on 32 CPUs; in each, the intra-op pool
    idles, then the first parallel `exp` runs): 16 of 200 were wrong without the hook (max ULP 1772), and 0 of 200 with it
    (`r20261001-000125-49b4`).
  - **Node 1, idle** (`r20260930-235617-8f22`):
    - 30 runs each way gave 0 wrong either way. The race window is narrow without load.
    - The `exp` test alone passed 5 of 5, and after the jit tests 5 of 5.
    - The jit files plus the isolation test passed.
  - **Local VM** (`art:89d23fb2bcbfe83304bf08738244a8cbe88b9babe7d9c5fa96f493ca60579b4d`):
    - Without a warm-up, 7 of 120 runs were wrong.
    - A single-threaded `exp` first gave 0 of 60; a single-threaded `log` first gave 0 of 100; the committed hook gave 0 of 100.
    - Direct `vmsExp` calls from 4 Python threads, with no torch op, gave 2 of 80 wrong, and 0 of 80 after one `vmsLn` call.
  - **Tests on the VM:**
    - The jit files, the isolation test and the transcendentals passed 17 of 17, three times.
    - vllm `tests/commit` plus `test_ref_prims.py` passed, except
      `test_kernel_dump.py::test_kernel_tile_visits_a_fully_masked_block…`. Its fixture `p0_64x300_h1kv1.npz` isn't fetched
      on the VM.
- **Checks on vy-nebius-2:** I recorded #449's own check rather than relying on the old coordinator's retry.
  - #449: `r20260930-235746-36f1` on `1b1895bc`, running.
  - #548: `r20261001-000221-f7ef` on `7a30515b`, running.
  - In both, the Lean steps passed from cache.
  - #548's earlier check, `r20260930-222746-4aa1` on `37e9c944`, passed
    (`note:20260930T2316Z-handoff-from-accounting-548-forkserver-fix`).
- **Grants: none.** It's one test-only file, with no Lean.
- **Outside this task:** any process whose first VML call is multi-threaded is exposed. That includes test subprocesses that
  don't load this conftest, and CPU torch code outside tests.
