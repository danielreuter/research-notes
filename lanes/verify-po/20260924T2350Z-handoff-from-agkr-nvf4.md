# A-GKR RTX 5090 NVFP4 (fp4-nvf4) Table 2 cell, best so far: independently verify art:5adf62eb (3 byte-identical proofs, Rust verity-gkr-verify, ~0.19 s each) — verifier built from lane/agkr-nvf4 @ 2b25df7f (verifier code identical to 3c769c6d)

From lane agkr-nvf4, 23:50Z. This supersedes both `20260924T2200Z-handoff-from-agkr-nvf4.md` (art:fe57e68b, 1.044 s) and
`20260924T2305Z-handoff-from-agkr-nvf4.md` (art:ad8f92b9, 0.314 s) for the same row and column; if you verify one, verify
this one. The 22:00Z handoff describes the statement: three public words per VU, the `public s t f` line, and statement binding via
`nvf4/witness.public_words`. The unit circuit differs from 23:05Z in one respect: E2M1X2 is merged into LK as well, so
`circuit.txt` has exactly one table, `table LK 5 89119` (485 columns, depth 1, 226 LK queries per unit). `chain.txt` and
`epilogue.txt` are the same as at 23:05Z.

**Result**
- bench-result/v1 `art:5adf62eb53700c38b7338b83065d8d7985fa48543be4ee78cb38b073c3f08f31` (attempt r20260924-233405-1b1d,
  PRESERVED, validation passed, contract_problems none; source lane/agkr-nvf4 @ 2b25df7f, clean). NVIDIA GeForce RTX 5090;
  profile `nvfp4-sm120-mma-draft/2026-09-22`, relation `fp4-nvf4`, dataset `bench-instances-nvfp4-sm120/v1`, tier
  `vu-k1536-nvfp4-sm120`, seed 20260922, digest = `fp4/chain.instances_digest(4096)`; K=1536, B=4096; NON_ZK_PROOF_DIAGNOSTIC;
  soundness 2^-130.19, target 2^-128. t.total median 0.245 s (reps 0.245 / 0.240 / 0.278).
- run-files/v1 `art:d6673af2e8c8052514347dae74e1cafc07ad105e79c130dc28dead30d5d94c28`: `proofs/rep{0,1,2}.bin` (9467080 B each; all
  three sha256 start `091fecadbd39ecca`), `statement/{circuit.txt, epilogue.txt, chain.txt, manifest.json, public.bin}`, and my own
  `verify_rep*.json` / `verify_independent.json` (these don't count).

**Verifier**: `git diff 3c769c6d 2b25df7f -- backends/gkr/verifier` is empty, so a verifier built for either earlier handoff works
unchanged.

**Command** (per rep; `DIR` = `research data fetch art:d6673af2 --to DIR`):

~~~bash
verity-gkr-verify verify --dir DIR/statement --proof DIR/proofs/rep0.bin --vus 4096 --threads 15 --json out_rep0.json
~~~

**Expected**: exit 0, accepted, vus 4096, units 98304, steps 24, slots 700, msgs 1689, bytes_read 9467080, ligero_rows 11666,
committed_elements 47782943.

**Negatives already run** (mine, so not independent) on this exact circuit, with the dev statement at 14 VUs: 115/115 rejected,
Rust `negatives` 54/54, `mutate --sample 24` 148/148. For the recorded statement:
`verity-gkr-verify mutate --dir DIR/statement --proof DIR/proofs/rep0.bin --vus 4096 --sample 24`.
