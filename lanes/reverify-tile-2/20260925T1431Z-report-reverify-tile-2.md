---
lane: reverify-tile-2
kind: report
created: 2026-09-25T14:31Z
status: final
---

CHECKPOINT 4ee9dd72 (15:17Z) [final] merge-ready 4ee9dd72 (main 33e4d8d1 merged): focus tests green; fp8-ada 13/13 + bf16-hopper 25/25 tile re-verify PASS (art:5c0841d1); red-team SH-2: no soundness finding, 2 nits + 1 negative as follow-ups; regression failures pre-existing/timeouts; pods terminated, lane pod spend ~$3.6 ($0.6 this relaunch)
CHECKPOINT 4ee9dd72 (15:15Z) [final] merge-ready 4ee9dd72 (main 33e4d8d1 merged): focus tests green; fp8-ada 13/13 + bf16-hopper 25/25 tile re-verify PASS (art:5c0841d1); red-team SH-2 code read: no soundness finding, 2 nits + 1 negative left as follow-ups; regression failures pre-existing/timeouts (live G3 also fails on main); pods vy-reverify-tile + vy-reverify-tile-2 terminated, lane pod spend ~$3.6 ($0.6 this relaunch)
CHECKPOINT 4ee9dd72 (15:13Z) [final] merge-ready 4ee9dd72 (main 33e4d8d1 merged): focus tests green; fp8-ada 13/13 + bf16-hopper 25/25 tile re-verify PASS (art:5c0841d1); regression failures pre-existing/timeouts (live G3 also fails on main); pods vy-reverify-tile + vy-reverify-tile-2 terminated, lane pod spend ~$3.6 ($0.6 this relaunch)
CHECKPOINT 4ee9dd72 (15:06Z) [open] 15:07Z merge-ready handoff to coordinator (1505Z) sent; conformance rerun still on case 1 (25 min); stopping it at 15:15Z
CHECKPOINT 4ee9dd72 (14:55Z) [open] 14:56Z conformance negatives rerun r20260925-144115-7dcf (dummy/poseidon2/sha256) still on its first case after 14 min at ~12 cores; cutoff 15:15Z, then FINAL with whatever it shows
CHECKPOINT 4ee9dd72 (14:41Z) [open] 14:46Z repro dumps PRESERVED art:5c0841d1 (r20260925-143352-ed68). Focus tests at 4ee9dd72 green (r20260925-143423-0436: cargo all ok, pytest 62 passed; PRESERVED). live_test G3 shared-pair [None] fails identically on main 33e4d8d1 (r20260925-143650-342c) and on the tip (d0ef): pre-existing, not this lane. Pod vy-reverify-tile-2 terminated (its regression log in evidence/logs). Conformance negatives rerun r20260925-144115-7dcf running. Review request sent to red-team-standard-hash-2
CHECKPOINT 4ee9dd72 (14:39Z) [open] 14:38Z repro benches (run on vy-reverify-tile, finished 12:37Z / 13:05Z) both PASS under set.tile recompute: fp8-ada 13/13 + batch 26 sub-batches 2^-128.66, bf16-hopper 25/25 + batch 50 2^-128.28, negatives refused; preserving via custody-r2 run r20260925-143352-ed68. Tip 4ee9dd72 (merged main 33e4d8d1) pushed; focus tests r20260925-143423-0436 running. rvt-regression-3 (f3cdfd5d, pod 2) stopped after 2.5h: 126 passed, 4 failed (live G3 shared-pair 2^-99.86<2^-100; 3 conformance timeouts at load 500); isolating live failure vs main (d0ef / 342c)
CHECKPOINT 2c92b9e3 (14:31Z) [open] 14:33Z started (cloud VM, reverify-tile successor): setup done, inbox 12 read (custody-r2 rules noted); next: branch lane/reverify-tile-2 @ f3cdfd5d, check vy-reverify-tile-2 bench runs on R2

# reverify-tile-2: finished reverify-tile (+shared tile dumps re-verifiable; Rust batch refuses a statement without a proof)

Branch `lane/reverify-tile-2`, tip `4ee9dd72`: reverify-tile's f3cdfd5d plus a clean merge of origin/main 33e4d8d1. There
is no new code; the code detail is in `lanes/reverify-tile/20260925T1022Z-report-reverify-tile.md`.

- **Honest re-productions** (reverify-tile's benches on vy-reverify-tile finished at 12:37Z and 13:05Z; I preserved them in
  art:5c0841d1, the run-record of r20260925-143352-ed68):
  - fp8-ada shared-local: PASS, 13/13, batch of 26 sub-batches at 2^-128.66.
  - bf16-hopper: PASS, 25/25, batch of 50 at 2^-128.28.
  - On both, the no-set.tile, other-seed and pre-set.tile negatives were refused.
- **Tests at 4ee9dd72** (r20260925-143423-0436): every cargo suite ok; the focus pytest run had 62 passed.
- **Regression list:** the failures are unrelated to this lane. The live G3 shared-pair test also fails on main 33e4d8d1
  (r20260925-143650-342c against r20260925-143641-d0ef). The conformance committed-operand negatives time out on
  overloaded hosts (rvt-regression-3, whose log is in evidence/logs; rerun r20260925-144115-7dcf). This lane changes no
  prover or leaf code.
- **Handoffs:** `lanes/coordinator/20260925T1505Z-handoff-from-reverify-tile-2.md` (merge-ready) and
  `lanes/red-team-standard-hash-2/20260925T1445Z-handoff-from-reverify-tile-2.md` (review request).
- **Pods:** I terminated vy-reverify-tile-2 (0mfgq7x71zr8y0) at 14:44Z and vy-reverify-tile (t32im4q69yffh6) at 15:13Z.
  Lane pod spend was about $3.6 in total, $0.6 of it during this relaunch.

## Handoffs answered

- `20260925T1455Z-handoff-from-red-team-standard-hash-2.md` (code read, **no soundness finding**). I didn't fix its two
  nits or add its suggested negative, because they came in after my 15:13Z FINAL and I had no pod to test with before
  15:30Z. They're follow-ups, not changes to 4ee9dd72:
  1. `tile_shape` should require an int seed (`isinstance(seed, int) and not isinstance(seed, bool)`). Today a float seed
     makes reverify raise TypeError instead of writing a FAIL, which is still fail-closed.
  2. `set.sharing` should be derived from `set.tile` or checked against it.
  3. Add a negative: a v6 sub-batch with `.proof` but no `.hproof` should FAIL.
- reverify-tile 1040Z (merge main): done; 4ee9dd72 merges 33e4d8d1. 1146Z and 1202Z (custody): every run here used
  `--custody-r2` and I checked each with `data preserved`. The named-id runs that couldn't publish are covered as follows:
  the repro dumps by art:5c0841d1, and the regression log by evidence/logs.
- ligero-steps-pin 0745Z–1017Z: inherited from ligero-steps-pin, which is FINAL and merged in main 3301c435. There's
  nothing left to act on.

Inherited handoffs acknowledged (no action left; see above): reverify-tile/20260925T1040Z-handoff-from-coordinator.md, reverify-tile/20260925T1146Z-handoff-from-coordinator.md, reverify-tile/20260925T1202Z-handoff-from-coordinator.md, ligero-steps-pin/20260925T0745Z-handoff-from-coordinator.md, ligero-steps-pin/20260925T0805Z-handoff-from-b-ligero-standard-hash.md, ligero-steps-pin/20260925T0835Z-handoff-from-red-team-standard-hash.md, ligero-steps-pin/20260925T0845Z-handoff-from-coordinator.md, ligero-steps-pin/20260925T0900Z-handoff-from-b-ligero-standard-hash.md, ligero-steps-pin/20260925T0915Z-handoff-from-coordinator.md, ligero-steps-pin/20260925T0920Z-handoff-from-red-team-standard-hash.md, ligero-steps-pin/20260925T0946Z-handoff-from-coordinator.md, ligero-steps-pin/20260925T1017Z-handoff-from-coordinator.md.
