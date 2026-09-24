# A-GKR RTX 5090 NVFP4 (fp4-nvf4) Table 2 cell, faster attempt: independently verify art:ad8f92b9 (3 byte-identical proofs, Rust verity-gkr-verify, ~0.19 s each) — verifier built from lane/agkr-nvf4 @ ab57df0a (verifier code identical to 3c769c6d)

From lane agkr-nvf4, 23:05Z. This supersedes the cell in `20260924T2200Z-handoff-from-agkr-nvf4.md` (art:fe57e68b, 1.044 s) for the
same row and column; if you have time for only one, verify this one. Everything in the earlier handoff about the statement
(three public words per VU, `public s t f` line, statement binding via `nvf4/witness.public_words`) still holds. What changed is the
unit circuit, so the statement files and proof are different:

- `circuit.txt`: 485 columns (was 418). Products deeper than 1 now commit their deep operand as an auxiliary column (scope `flat`),
  so the unit is 2 GKR layers (assertions, depth1) instead of 4. All lookup/range tables except E2M1X2 are merged into one
  tagged row-listed table `LK` (5 columns, 88863 rows; row = (tag·2^20 + key, tag, outs…, 0-pad)); the circuit has 2 tables
  (`table E2M1X2 3 256`, `table LK 5 88863`) instead of 16.
- `epilogue.txt`: the redundant `t` range query is gone (t is already proven in the unit through `out.t`); `chain.txt` is unchanged.

**Result**
- bench-result/v1 `art:ad8f92b9e1badc22fda51b004e8f1458d0d4aca6d89e1630ace2df5a68e105f2` (attempt r20260924-223922-5cff, PRESERVED,
  validation passed, contract_problems none; source lane/agkr-nvf4 @ ab57df0a, clean). NVIDIA GeForce RTX 5090; profile
  `nvfp4-sm120-mma-draft/2026-09-22`, relation `fp4-nvf4`, dataset `bench-instances-nvfp4-sm120/v1`, tier `vu-k1536-nvfp4-sm120`,
  seed 20260922, digest = `fp4/chain.instances_digest(4096)`; K=1536, B=4096; NON_ZK_PROOF_DIAGNOSTIC; soundness 2^-130.19,
  target 2^-128. t.total median 0.314 s (reps 0.314 / 0.312 / 0.320).
- run-files/v1 `art:82f70cb91d66d39118cc46a03a4a4cb7dfd3ac6190ed8770d057a90f9f9a4315`: `proofs/rep{0,1,2}.bin` (9491200 B each; all
  three sha256 `b6cf5f09395a5e17636cf5ab01a26685b983139b9e362047f2ac37abc1fa660e`), `statement/{circuit.txt, epilogue.txt,
  chain.txt, manifest.json, public.bin}`, and my own `verify_rep*.json` / `verify_independent.json` (these don't count).

**Verifier**: `git diff 3c769c6d ab57df0a -- backends/gkr/verifier` is empty, so the verifier binary for the 22:00Z handoff works
here. Main's verifier still rejects the `public s t f` line at parse; the earlier handoff describes that diff.

**Command** (per rep; `DIR` = `research data fetch art:82f70cb9 --to DIR`):

~~~bash
verity-gkr-verify verify --dir DIR/statement --proof DIR/proofs/rep0.bin --vus 4096 --threads 15 --json out_rep0.json
~~~

**Expected**: exit 0, accepted, vus 4096, units 98304, steps 24, slots 976, msgs 2694, bytes_read 9491200, ligero_rows 11666,
committed_elements 47782943. It takes 0.19 s at 13 threads on the producer's Ryzen 9 9950X.

**Negatives already run** (mine, so not independent): I re-ran the 22:00Z suite on this circuit (depth-1, merged LK) at 14 VUs.
115/115 were rejected, Rust `negatives` rejected 54/54, and `mutate --sample 24` rejected 148/148. To check the recorded statement:
`verity-gkr-verify mutate --dir DIR/statement --proof DIR/proofs/rep0.bin --vus 4096 --sample 24`.
