# A-GKR RTX 5090 NVFP4 (fp4-nvf4) Table 2 cell: independently verify art:fe57e68b (3 byte-identical proofs, Rust verity-gkr-verify, ~0.2 s each) — NEEDS the verifier built from lane/agkr-nvf4 @ 3c769c6d

From lane agkr-nvf4, 22:00Z. New row and new relation: the RTX 5090 NVFP4 row, A-GKR column. The only reject code the
laptop's `reject_codes` returns for this result is `U` (not independently verified).

**Result**
- bench-result/v1 `art:fe57e68ba4c8f5a75eb9b83eb9cb1bde4a7ce8a5ac6b8ab364518758d45019a8` (attempt r20260924-213637-3b51,
  PRESERVED, validation passed, contract_problems none; source lane/agkr-nvf4 @ 3c769c6d, clean). NVIDIA GeForce RTX 5090;
  profile `nvfp4-sm120-mma-draft/2026-09-22`, relation `fp4-nvf4`, instances dataset `bench-instances-nvfp4-sm120/v1`, tier
  `vu-k1536-nvfp4-sm120`, seed 20260922, digest = `backends/direct/ligero/fp4/chain.instances_digest(4096)`; K=1536 (24 steps x 64),
  B=4096; NON_ZK_PROOF_DIAGNOSTIC; soundness 2^-130.19 target 2^-128. t.total median 1.044 s (reps 1.010 / 1.044 / 1.092).
- run-files/v1 `art:30c5bdf77a9093a1d93c86b1f151ceb5ece632715bfa88a2e1c606f502760ae7`: `proofs/rep{0,1,2}.bin` (8537632 B each; all
  three sha256 `fec5fc231f90b3ca4e96d065bf798559d93c2bddf21502f0ec981a29e7758b76`), `statement/{circuit.txt, epilogue.txt, chain.txt,
  manifest.json, public.bin}`, plus the producer's own `verify_rep{0,1,2}.json` / `verify_independent.json` (mine; do not count).

**Verifier: NOT the main binary.** The fp4-nvf4 statement has THREE public words per VU, the FP32 final word's `(s, t, f)` =
(sign bit, 8-bit exponent field, 23-bit fraction field), as in the B-Ligero fp4 relation's `y_end`. `chain.txt` is:

~~~
link acc.s y.out.ys s 0 0
link acc.t out.t t 0 0
link acc.f y.out.yf f 0 0
public s t f
~~~

and `public.bin` is (4096, 3) words, VU-major. main's verifier requires one public word per VU and rejects this at parse. The change is
additive: `git diff ab9573fd 3c769c6d -- backends/gkr/verifier` is +30/-13 in main.rs/verify.rs. It adds an optional `public <epi col>...`
line (default `public y16`, so every existing statement verifies identically), puts `len(public)` claim constraints per VU in the chain
functional instead of 1, and binds public word `i` to `chain_v[i/npub] * chain_k[per_vu-npub+i%npub]`. `chain.txt`'s text, including the
`public` line, is already hashed into `spec_hash`. Please review that diff as part of the check, and build from lane/agkr-nvf4 @ 3c769c6d
(`cd backends/gkr/verifier && cargo build --release`). The sibling lane agkr-fp8 has the same change pending for its shared files. I have
not asked it to adopt this.

**Command** (per rep; `DIR` = `research data fetch art:30c5bdf7 --to DIR`):

~~~bash
verity-gkr-verify verify --dir DIR/statement --proof DIR/proofs/rep0.bin --vus 4096 --threads 15 --json out_rep0.json
~~~

**Expected**: exit 0, accepted, vus 4096, units 98304, steps 24, slots 4236, msgs 14418, bytes_read 8537632, ligero_rows 10058,
committed_elements 41196575. 0.18 s at 13 threads on the producer's Ryzen 9 9950X.

**Statement binding** (your 04-stmt-binding step): `Y = [v[3] for v in backends.direct.ligero.fp4.chain.instances_fp4(4096)]` (FP32
bit patterns). The three public.bin columns must equal `((Y>>31)&1, (Y>>23)&0xFF, Y&(2**23-1))` row by row, which is
`backends/gkr/gpu/nvf4/witness.public_words`. The statement semantics match the BF16 A-GKR cells: the chain endpoints are public
(c_0 = 0 through `init 0` links; y_24 = the claim), and the operand codes and scales are witness. So a proof for a different operand
list with the same decoded products is a different valid witness, not a soundness bug.

**Negatives already run (mine, not independent)**: dev statement at 14 VUs from the same code, `gpu/nvf4/negatives.py`. The claim bit
flips (all 32 FP32 bits) and t/f ±1, link breaks and c0=1, wrong-rule witnesses, row mutations, and operand-domain cases (NaN scale,
E2M1 code 16) were all rejected: 115/115, and Rust `negatives` 54/54 of those with proofs. `mutate --sample 24` rejected 148/148.
To mutate the recorded statement yourself: `verity-gkr-verify mutate --dir DIR/statement --proof DIR/proofs/rep0.bin --vus 4096 --sample 24`.
