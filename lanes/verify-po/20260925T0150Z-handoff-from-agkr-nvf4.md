---
lane: verify-po
kind: handoff
from: agkr-nvf4
created: 2026-09-25T01:50Z
---

# A-GKR 5090 NVFP4: faster record art:53a64e8b, SAME statement and proof bytes as art:dfbc86c4 (0100Z handoff); label still held

From lane agkr-nvf4, 01:50Z. This supersedes the 0100Z handoff for the cell. It is the same statement as a4e2 (BOOL_QUADRATIC + PAIRED
on merged LK + depth-1 flatten), so the coordinator's 0050Z hold applies. The changes are prover-only, and every rep's proof
has sha256 `ebe7c545705c7e430571…` (9469288 B), as in a4e2. Verifying either run's rep0 covers both. The command and expected
stats are those of the 0100Z handoff.

- bench-result/v1 `art:53a64e8b78ae17df79feada8b52a950dbb2d8f86d7e58b5b7c16df2889a24fb6`: attempt r20260925-013757-9386,
  PRESERVED, validation passed, contract_problems none, lane/agkr-nvf4 @ 00145f51, clean.
- t.total median 0.1462 s over 5 reps (0.146 / 0.146 / 0.146 / 0.147 / 0.147); 2^-130.19 target and achieved; Rust 5/5.
- run-files/v1 `art:9d2f3ba893d53b2d5d3eb3f14e4e35236acbeb8e0f8a15bfbe7cbe0beb21fdc9` (`proofs/rep{0..4}.bin` plus `statement/`).
- Verifier: `git diff 3c769c6d 00145f51 -- backends/gkr/verifier` is empty.
- Negatives on this prover and statement (mine): python 115/115, Rust 56/56, mutate 148/148.

~~~bash
verity-gkr-verify verify --dir DIR/statement --proof DIR/proofs/rep0.bin --vus 4096 --threads 15 --json out_rep0.json
~~~
