---
lane: flock-ir-lowering
kind: report
created: 2026-09-26T03:16Z
status: open
---

CHECKPOINT b1e1303f (03:57Z) [open] WAITING r20260926-035651-e6a3 on vy-flock-ir-lowering-h100, check after 04:20Z; agent bc-9916bbb1-de98-5d21-a511-aafa5255c78f; next: RMSNorm MUFU pieces meanwhile. flock-ir-block/v1 CPU selftest all-pass rope+silu (PR #54 @ b1e1303f)
CHECKPOINT 614190b8 (03:41Z) [open] RoPE + SiLU·mul lowered from the IR (fp pieces + ir_lower walker; units read off the IR graph): rope pair unit 5996 ANDs/6401 rows (2^13), silu element 2699 ANDs/3073 rows (2^12), pinned 7156eb27 / f40ec4ad; 0 mismatches on captured #101 rope-head-d64 (1024) + silumul-v1-i8192 (256) and spine synthetic art:02a7e4df / art:13e5b33b; 25 tests incl negatives; commit 614190b8; next: RMSNorm MUFU pieces, then flock-ir-block statement
CHECKPOINT 7289e3ad (03:16Z) [open] started: lane flock-ir-lowering (agent bc-9916bbb1), branch cursor/flock-ir-lowering-c78f off origin/main 7289e3ad (the spine's templates/ are on main); step 1 = gadget-library design note
