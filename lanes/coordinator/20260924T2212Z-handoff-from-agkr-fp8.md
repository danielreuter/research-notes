# A-GKR H100 FP8 (fp8-hopper) Table 2 cell: independently verify art:2e7baba7 (3 byte-identical proofs, Rust verity-gkr-verify, ~1-2 s each)

From lane agkr-fp8, 22:12Z. New row and new relation: the H100 FP8 (E4M3) row, A-GKR column. This is not the 4090 fp8-ada
handoff (`20260924T2129Z-…`; that cell is in Table 2 as of 22:10Z), so the proof bytes and expected verifier output differ.
The Table 2 predicate's ONLY rejection reason for this result is `not independently verified` (laptop, 22:10Z, after
`research data reindex --remote`, `python -m verity_numerical.bench.tables --format json`, `rejected[]`).

**Result**
- bench-result/v1 `art:2e7baba76e89f789646de954bf63e21b6fa28df8065d45b34cf3836148997780` (attempt r20260924-215501-f96b,
  PRESERVED, validation passed, contract_problems []; source lane/agkr-fp8 @ 891572a0, clean). NVIDIA H100 80GB HBM3 (reference
  part, host Xeon Platinum 8480+); profile `fp8-hopper-wgmma-draft/2026-09-22`, relation `fp8-hopper` (instances manifest
  0ff75002…, the frozen fp8-hopper set); K=1536, B=4096; NON_ZK_PROOF_DIAGNOSTIC; soundness 2^-130.19 (interactive model, SHA-512
  Merkle). t.total median 0.688 s (reps 0.686 / 0.688 / 0.687).
- run-files/v1 `art:438ada92e2328866c4028d74ccd55bf74ef2b09cd26555618f06f21a551dff5e`: `proofs/rep{0,1,2}.bin` (17251312 B each; all
  three sha256 `f80ecc5321264d57d7b6036747503dbd5e10bb2e06a63f69b27a5ef6758159ab`), `statement/{circuit.txt, epilogue.txt, chain.txt,
  manifest.json, public.bin}` (model `hopper_e4m3_wgmma_k32`, groups [32], 48 steps of 32 products, 448 unit columns; the epilogue is
  the 22-bit packed public word), plus this lane's own `verify_rep*.json` / `verify_independent.json`, which do not count.

**Verifier**: unchanged since base main ab9573fd (`git diff ab9573fd lane/agkr-fp8 -- backends/gkr/verifier` is empty); your binary
(sha256 ee899383c03cfac3) is the right one.

**Command** (per rep; `DIR` = `research data fetch art:438ada92 --to DIR`):

~~~bash
verity-gkr-verify verify --dir DIR/statement --proof DIR/proofs/rep0.bin --vus 4096 --threads 15 --json out_rep0.json
~~~

**Expected**: exit 0, accepted, vus 4096, units 196608, steps 48, slots 2711, msgs 8912, bytes_read 17251312,
ligero_rows 21576, committed_elements 88375120. 0.64 s at 22 threads on the producer's Xeon 8480+.

**Negatives** (this lane's own, so not independent; dev run r20260924-214248-558a, same code at 4096 VUs): public word +1, -1,
sign bit (bit 21) flipped and exponent +1 (bit 13), each on a different VU, are rejected by both the Python and the Rust verifier at
`epilogue/assertions: phase-1 round 0 sum mismatch`; the honest proof is accepted by both. Tree: `art:cdaabf41f3b825ffd040fe7a60e96b1623bd8dd96cf6da1310e728984ec5d5dd`
(PRESERVED; ref result = art:2e7baba7); `verity-gkr-verify verify --dir DIR/neg/word_plus --proof DIR/neg/word_plus/proof.bin
--vus 4096 --threads 15` should exit non-zero.
