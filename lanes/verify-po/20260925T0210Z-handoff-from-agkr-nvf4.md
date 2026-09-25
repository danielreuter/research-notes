---
lane: verify-po
kind: handoff
from: agkr-nvf4
created: 2026-09-25T02:10Z
---

# A-GKR 5090 NVFP4: final best art:f277786d, SAME statement and proof bytes as art:dfbc86c4 / art:53a64e8b; label still held

From lane agkr-nvf4, 02:10Z. This supersedes the 0100Z and 0150Z handoffs; it is my last record. It is the same statement as
a4e2 and 9386 (BOOL_QUADRATIC + PAIRED on merged LK + depth-1 flatten), so the coordinator's 0050Z hold applies: verdict yes,
`verified=accepted` label only after red-team-lk passes. The changes are prover-only, and every rep's proof has sha256
`ebe7c545705c7e430571…` (9469288 B), as in a4e2 and 9386. So one verification of rep0 covers all three runs.

- bench-result/v1 `art:f277786dadaebbffc3fe01f02e0d49452a7dfc5fceed359cb746588b79eac63c`: attempt r20260925-015152-d098,
  PRESERVED, validation passed, contract_problems none, lane/agkr-nvf4 @ c97d2ad2, clean.
- t.total median 0.1388 s over 5 reps (0.143 / 0.139 / 0.139 / 0.138 / 0.137); 2^-130.19 target and achieved; python 5/5;
  Rust 5/5 (0.152–0.156 s).
- run-files/v1 `art:1f0b0b60645c02e158c1c8fda975ad04e76e3e18782ee92ee8c26a7247941cad` (`proofs/rep{0..4}.bin` plus `statement/`).
- Verifier: `git diff 3c769c6d c97d2ad2 -- backends/gkr/verifier` is empty.
- Negatives on this prover and statement (mine, not independent): python 115/115 (56 at the verifier, 59 at the prover),
  Rust 56/56, mutate 148/148.

**Update 02:16Z**: red-team-lk PASSED BOOL_QUADRATIC + PAIRED on this statement (the b7cec878 export, art:319062b4) together
with the merged LK and flatten: `lanes/agkr-nvf4/20260925T0200Z-handoff-from-red-team-lk.md`. Under the 0050Z rule your
verdict is then the only thing left before the label. Build the verifier from lane/agkr-nvf4, where it is identical to
3c769c6d. Main's verifier predates 679697a4 and cannot parse `public s t f` in chain.txt.

**Command** (`DIR` = `research data fetch art:1f0b0b60 --to DIR`):

~~~bash
verity-gkr-verify verify --dir DIR/statement --proof DIR/proofs/rep0.bin --vus 4096 --threads 15 --json out_rep0.json
~~~

**Expected**: exit 0, accepted, vus 4096, units 98304, steps 24, slots 673, msgs 1589, bytes_read 9469288, ligero_rows 11672,
committed_elements 47804437.
