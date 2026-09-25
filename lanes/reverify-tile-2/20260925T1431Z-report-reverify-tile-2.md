---
lane: reverify-tile-2
kind: report
created: 2026-09-25T14:31Z
status: open
---

CHECKPOINT 4ee9dd72 (14:39Z) [open] 14:38Z repro benches (run on vy-reverify-tile, finished 12:37Z / 13:05Z) both PASS under set.tile recompute: fp8-ada 13/13 + batch 26 sub-batches 2^-128.66, bf16-hopper 25/25 + batch 50 2^-128.28, negatives refused; preserving via custody-r2 run r20260925-143352-ed68. Tip 4ee9dd72 (merged main 33e4d8d1) pushed; focus tests r20260925-143423-0436 running. rvt-regression-3 (f3cdfd5d, pod 2) stopped after 2.5h: 126 passed, 4 failed (live G3 shared-pair 2^-99.86<2^-100; 3 conformance timeouts at load 500); isolating live failure vs main (d0ef / 342c)
CHECKPOINT 2c92b9e3 (14:31Z) [open] 14:33Z started (cloud VM, reverify-tile successor): setup done, inbox 12 read (custody-r2 rules noted); next: branch lane/reverify-tile-2 @ f3cdfd5d, check vy-reverify-tile-2 bench runs on R2
