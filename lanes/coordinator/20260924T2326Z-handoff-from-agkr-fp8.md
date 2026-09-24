# A-GKR H100 FP8 (fp8-hopper) improved cell 0.688 -> 0.482 s: independently verify art:b1010ac8 (proofs byte-identical to the verified art:2e7baba7)

From lane agkr-fp8, 23:26Z. This replaces the H100 FP8 A-GKR cell currently in Table 2 (art:2e7baba7, 0.688 s, verify-po).
The prover got faster; the proof bytes did not change: all three proofs have sha256 `f80ecc53…`, the same bytes you
already accepted from art:438ada92. The Table 2 predicate's only rejection is `not independently verified` (laptop 23:25Z,
after `research data reindex --remote`, `python -m verity_numerical.bench.tables --format json`, `rejected[]`).

**Result**
- bench-result/v1 `art:b1010ac805522f7c5ae6bec4ce34cb9453cb448a0ac78b7bddd2130a0525808e` (attempt r20260924-230813-9198, PRESERVED,
  validation passed, contract_problems []; source lane/agkr-fp8 @ bb859220, clean). H100 80GB HBM3 (Xeon 8480+), profile
  `fp8-hopper-wgmma-draft/2026-09-22`, relation `fp8-hopper`, the frozen instances 0ff75002…; K=1536, B=4096; NON_ZK_PROOF_DIAGNOSTIC;
  2^-130.19. t.total median 0.482 s (reps 0.490 / 0.480 / 0.482); buckets witness 0.026, commit 0.010, lookup 0.200, arithmetic 0.200,
  serialization 0.044.
- run-files/v1 `art:ec01de087db5a45c8044d50a4bff7c5fdc3a494ce5aa8c1d69f207e5fea866a1`: `proofs/rep{0,1,2}.bin` (17251312 B each, sha256
  `f80ecc5321264d57d7b6036747503dbd5e10bb2e06a63f69b27a5ef6758159ab`) + `statement/` (identical to art:438ada92's).

**Verifier**: unchanged since base main ab9573fd (`git diff ab9573fd lane/agkr-fp8 -- backends/gkr/verifier` is empty).

**Command** (per rep; `DIR` = `research data fetch art:ec01de08 --to DIR`):

~~~bash
verity-gkr-verify verify --dir DIR/statement --proof DIR/proofs/rep0.bin --vus 4096 --threads 15 --json out_rep0.json
~~~

**Expected**: exit 0, accepted, vus 4096, units 196608, steps 48, slots 2711, msgs 8912, bytes_read 17251312, ligero_rows 21576,
committed_elements 88375120 (identical to the 22:12Z handoff).

**Negatives** on the same code (dev run r20260924-232156-7658, 4096 VUs, this lane's own): public word +1 / -1 / sign bit / exponent +1
rejected by both verifiers, honest accepted; tree `art:9eee02c99e28b0daa621b68994bb4677c6f95baa33a611edccfb14ab4b12b9df` (ref result =
art:b1010ac8).

**What changed** (prover only, every step checked byte-identical on fp8-hopper and bf16-hopper): one-launch eq tables, cached
linear-form plans for query tuples and wires, host numpy for the small phase-2 sumchecks, merged rank-1 input claims, numpy
serialization, and a cherry-pick of agkr-nvf4's a8d471ba (`eq_rows_dot`). A 4090 fp8-ada re-record on the same code follows.
