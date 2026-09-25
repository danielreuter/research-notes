# A-GKR H100 FP8 (fp8-hopper) cell 0.328 s on the merged-LK statement: verify art:3ae971dd (label HELD for red-team-lk, per your 0050Z)

From lane agkr-fp8, 01:32Z. The statement rewrite is the same as the 4090 cell art:45c5be4a (handoff 0045Z; verify-po checked it
structurally in 0104Z). `gpu/v2/export.py::merge_tables` @ d5d80e0b, here at model `hopper_e4m3_wgmma_k32`: the ten tables ALIGN4,
LEAD, LEADNORM, **R6**, R7, SHIFT, SSHIFT_HI, SSHIFT_LO, TNORM, T_OP become one `LK`, with 139 queries per unit. hopper has R6 where ada
has R5. `--no-merge` reproduces the statement of art:2e7baba7 / art:b1010ac8. Soundness is recomputed live: 2^-130.19
(-130.1898057623).

**Result**
- bench-result/v1 `art:3ae971dd97799d842007bae866a735cd1324b50aba8e0af408b36b278172213b` (attempt r20260925-010941-b9eb, PRESERVED,
  validation passed; source lane/agkr-fp8 @ 3be6a35f, clean). H100 80GB HBM3 reference part 28sqi5rstcudhk (Xeon 8480+, quota 23.8
  cores, thread caps 23), profile `fp8-hopper-wgmma-draft/2026-09-22`, relation `fp8-hopper`, frozen instances 0ff75002…; K=1536,
  B=4096; NON_ZK_PROOF_DIAGNOSTIC. t.total median 0.328 s (reps 0.322 / 0.328 / 0.328); buckets witness 0.025, commit 0.010, lookup
  0.073, arithmetic 0.177, serialization 0.041. It was 0.482 s (art:b1010ac8) and 0.688 s (art:2e7baba7, in Table 2).
- run-files/v1 `art:0c23dfc94b3a0651d74e57c220ae5b9c632c56661eb79ad918a2f5e46b8ed1bb`: `proofs/rep{0,1,2}.bin` (17078296 B each, sha256
  `0021aa914caac40cf60da363620d571dcbeb11af8603aeebcc20ddd1fef587d3`) + `statement/` (the merged circuit.txt).

**Verifier**: unchanged since base main ab9573fd.

**Command** (per rep; `DIR` = `research data fetch art:0c23dfc9 --to DIR`):

~~~bash
verity-gkr-verify verify --dir DIR/statement --proof DIR/proofs/rep0.bin --vus 4096 --threads 15 --json out_rep0.json
~~~

**Expected**: exit 0, accepted, vus 4096, units 196608, steps 48, slots 703, msgs 1703, bytes_read 17078296, ligero_rows 21576,
committed_elements 88375120 (pod rep0, 0.58 s at 22 threads).

**Negatives**: tree `art:70bbba68931935ef16b4ce31b159cf868f7dfa82ec63aabf7c57fcae01c45ad2` (ref result = art:3ae971dd).
- Dev run r20260925-005858-6faf @ 3be6a35f: public word +1 / -1 / sign bit / exponent +1 are rejected by both verifiers; honest
  is accepted.
- r20260925-012601-e354, aimed at LK (`12_lookup_neg.sh`, prover a97576b5, whose proof bytes equal 3be6a35f's on this statement,
  sha 0021aa91): one unit column read by LK +1 (a T_OP output, a SHIFT output, a TNORM output, an R6 key term), with the honest
  multiplicities, from a prover copy whose LogUp self-check is a no-op. Python and Rust reject all four at `LogUp LK level 0:
  final check`.
