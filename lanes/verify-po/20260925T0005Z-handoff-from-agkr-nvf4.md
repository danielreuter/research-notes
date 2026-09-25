# A-GKR RTX 5090 NVFP4 (fp4-nvf4) Table 2 cell, best so far: independently verify art:49757870 — SAME statement and proof bytes as art:5adf62eb (23:50Z handoff); only the prover got faster

From lane agkr-nvf4, 00:05Z. This supersedes the 23:50Z handoff (art:5adf62eb, 0.245 s). The circuit is unchanged since 2b25df7f.
The changes up to 716ea008 are prover-only (agkr-fp8's shared prover commits and a compiled witness step), and the proof bytes
are byte-identical: sha256 `091fecadbd39ecca…` in both runs. So verifying either run's rep0 covers both, and the 23:50Z command,
expected stats and verifier build are all unchanged.

**Result**
- bench-result/v1 `art:49757870c9720787072c8593cf8a448b59d0d35e34e0e1a2021a4020ab2c4f15` (attempt r20260924-235457-ff98,
  PRESERVED, validation passed, contract_problems none; source lane/agkr-nvf4 @ 716ea008, clean). NVIDIA GeForce RTX 5090, fp4-nvf4,
  frozen NVFP4 set (`bench-instances-nvfp4-sm120/v1`, `vu-k1536-nvfp4-sm120`, seed 20260922), K=1536, B=4096,
  NON_ZK_PROOF_DIAGNOSTIC, soundness 2^-130.19 (target 2^-128). t.total median 0.1905 s (5 reps: 0.192 / 0.190 / 0.191 / 0.190 /
  0.190).
- run-files/v1 `art:78b3aadf21aabd37f1b104e63dde7d7261266c753d17a27613a3d6bb8f3c9ca0`: `proofs/rep{0..4}.bin` (9467080 B, all sha256
  `091fecadbd39ecca…`) + `statement/`.

**Verifier**: `git diff 3c769c6d 716ea008 -- backends/gkr/verifier` is empty.

**Command** (`DIR` = `research data fetch art:78b3aadf --to DIR`):

~~~bash
verity-gkr-verify verify --dir DIR/statement --proof DIR/proofs/rep0.bin --vus 4096 --threads 15 --json out_rep0.json
~~~

**Expected**: exit 0, accepted, vus 4096, units 98304, steps 24, slots 700, msgs 1689, bytes_read 9467080, ligero_rows 11666,
committed_elements 47782943.

**Negatives** (mine, not independent), re-run with the 716ea008 prover on this circuit: 115/115, Rust 54/54, mutate 148/148.
