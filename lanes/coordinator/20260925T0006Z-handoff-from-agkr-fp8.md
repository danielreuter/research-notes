# A-GKR RTX 4090 FP8 (fp8-ada) improved cell 1.130 -> 0.666 s: independently verify art:ecd96143 (proofs byte-identical to the verified art:1b4fd4a1)

From lane agkr-fp8, 00:06Z. This replaces the RTX 4090 FP8 A-GKR cell currently in Table 2 (art:1b4fd4a1, 1.130 s, verify-po).
Only the prover changed, and the proof bytes are the same: all three proofs have sha256 `b5ef0238…`, the same bytes you
already accepted from art:89a2ce85. The Table 2 predicate's only rejection is `not independently verified` (laptop 00:04Z,
after `research data reindex --remote`, `python -m verity_numerical.bench.tables --format json`, `rejected[]`).

**Result**
- bench-result/v1 `art:ecd961433c94c2b49b06d722b0d349a73d8bb89fb1858ce1b167e18836576d61` (attempt r20260924-234932-5828, PRESERVED,
  validation passed; source lane/agkr-fp8 @ f2363663, clean). RTX 4090 (reference part 5vnbd6rfwm3wmd, EPYC 7532, cgroup quota 10.2
  cores, thread caps 10), profile `fp8-ada-mma-draft/2026-09-22`, relation `fp8-ada`, the frozen instances e66ff0f2…; K=1536, B=4096;
  NON_ZK_PROOF_DIAGNOSTIC; 2^-130.19. t.total median 0.666 s (reps 0.667 / 0.666 / 0.665); buckets witness 0.038, commit 0.014,
  lookup 0.249, arithmetic 0.309, serialization 0.055.
- run-files/v1 `art:0667ed4684083a8bb2893f31a00140fea374ffb85a43973420dcd62118c1b6d7`: `proofs/rep{0,1,2}.bin` (18152824 B each, sha256
  `b5ef0238ed5f46b025a51875caa9e0f43c72fec4fe43629bb44468d6bdc2f28f`) + `statement/` (the same as art:89a2ce85's).

**Verifier**: unchanged since base main ab9573fd (`git diff ab9573fd lane/agkr-fp8 -- backends/gkr/verifier` is empty).

**Command** (per rep; `DIR` = `research data fetch art:0667ed46 --to DIR`):

~~~bash
verity-gkr-verify verify --dir DIR/statement --proof DIR/proofs/rep0.bin --vus 4096 --threads 15 --json out_rep0.json
~~~

**Expected**: exit 0, accepted, vus 4096, units 196608, steps 48, slots 2881, msgs 9547, bytes_read 18152824, ligero_rows 22730,
committed_elements 93101755 (the same as the 21:29Z handoff; confirmed on the pod's rep0).

**Negatives** (dev run r20260924-233453-ee05 @ bb859220, 4096 VUs, this lane's own; proofs identical to f2363663's): public word +1 / -1 /
sign bit / exponent +1 were rejected by both verifiers and the honest proof was accepted. Tree
`art:9398f0289a5050f76f78b6f425fbc3ffe90073d52d6738116adf69959ed3c3b0` (ref result = art:ecd96143).

**What changed**: the H100 hill-climb of the 23:26Z handoff, plus f2363663 (the opening accumulator in int32 on CUDA, t_open_acc
113 -> 85 ms).
