# A-GKR RTX 4090 FP8 (fp8-ada) Table 2 cell: independently verify art:1b4fd4a1 (3 byte-identical proofs, Rust verity-gkr-verify, ~1-3 s each)

From lane agkr-fp8, 21:29Z. New row and new relation: the RTX 4090 FP8 (E4M3) row, A-GKR column. The Table 2 predicate's ONLY
rejection reason for this result is `not independently verified` (checked 21:29Z with `python -m verity_numerical.bench.tables
--format json`, `rejected[]`; I ran the laptop catalog after `research data reindex --remote`).

**Result**
- bench-result/v1 `art:1b4fd4a17e9023258e502169b2ec156dc084393cddf284616a0642a3e645d6e2` (attempt r20260924-211113-5f9e,
  PRESERVED, validation passed, contract_problems []; source lane/agkr-fp8 @ 07a8edd6, clean). NVIDIA GeForce RTX 4090 (24 GB);
  profile `fp8-ada-mma-draft/2026-09-22`, relation `fp8-ada` (instances manifest e66ff0f2…, the frozen fp8-ada set);
  K=1536, B=4096; NON_ZK_PROOF_DIAGNOSTIC; soundness 2^-130.19 (interactive model, SHA-512 Merkle; same Ligero term as the BF16
  cells). t.total median 1.130 s (reps 1.124 / 1.130 / 1.132).
- run-files/v1 `art:89a2ce85c4550ca004c76bcc9ba82eb4edb182f4d6961b459c252eb16c9f406c`: `proofs/rep{0,1,2}.bin` (18152824 B each; all
  three sha256 `b5ef0238ed5f46b025a51875caa9e0f43c72fec4fe43629bb44468d6bdc2f28f`), `statement/{circuit.txt, epilogue.txt,
  chain.txt, manifest.json, public.bin}` (model `ada_e4m3_m16n8k32`, 48 steps of 32 products; the FP8 epilogue is the 22-bit
  packed public word), and the producer's own `verify_rep{0,1,2}.json` / `verify_independent.json` (run by this lane, so they
  do not count).

**Verifier**: unchanged since base main ab9573fd (`git diff ab9573fd lane/agkr-fp8 -- backends/gkr/verifier` is empty), so your
binary (sha256 ee899383c03cfac3) is the right one. It reads Params from `statement/`; the FP8 path is new statement files, not
new verifier code. (The producer's copy on the pod hashed 8878830e… only because it was built there.)

**Command** (per rep; `DIR` = `research data fetch art:89a2ce85 --to DIR`):

~~~bash
verity-gkr-verify verify --dir DIR/statement --proof DIR/proofs/rep0.bin --vus 4096 --threads 15 --json out_rep0.json
~~~

**Expected**: exit 0, accepted, vus 4096, units 196608, steps 48, slots 2881, msgs 9547, bytes_read 18152824,
ligero_rows 22730, committed_elements 93101755. 0.97 s at 16 threads on the producer's EPYC 7702.

**Negatives already run by this lane** (dev run r20260924-210424-0471, same code at 4096 VUs; my own, so not independent): public
word +1, -1, sign bit (bit 21) flipped and exponent +1 (bit 13), each on a different VU, are rejected by both the Python and the Rust
verifier at `epilogue/assertions: phase-1 round 0 sum mismatch`; the honest proof is accepted by both.

**Known metadata slip (not a validity issue)**: this result's descriptive strings came from the BF16 path: `software.backend.version`
says "limb epilogue", `.model` says "checker Params.from_model", and `note` says "96 chained units". The FP8 path actually uses
fp8.adder_params, a packed-word epilogue and 48 units, and `steps`/`units` in the same fingerprint say 48 / 196608. It is fixed
at 40069d44 for later runs. If you prefer a clean one, the next recorded 4090 run supersedes this one.
