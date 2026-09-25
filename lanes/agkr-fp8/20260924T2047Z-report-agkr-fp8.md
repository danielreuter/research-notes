---
lane: agkr-fp8
kind: report
created: 2026-09-24T20:47Z
status: open
---

CHECKPOINT a97576b5 (01:31Z) [open] H100 merged fp8-hopper 0.328s recorded: art:3ae971dd (run-files art:0c23dfc9, r20260925-010941-b9eb @3be6a35f), Rust 3/3, 2^-130.19, negatives art:70bbba68; handoff 0132Z (held). 10 nvf4 picks -> a97576b5, bytes same (fp8 + bf16). Unmerged H100 dev @a97576b5 running.
CHECKPOINT 3be6a35f (01:11Z) [open] H100 pod 28sqi5rstcudhk (00:50Z): fp8-hopper MERGED dev @3be6a35f t.total 0.330-0.335s (cell 0.482), Rust 2/2, negatives OK. Recorded run r20260925-010941-b9eb running; then push, lookup negatives, handoff.
CHECKPOINT 3be6a35f (00:43Z) [open] 4090 fp8-ada on MERGED LK statement: 0.490s (art:45c5be4a, run-files art:979e37aa, r20260925-002240-8ed3 @3be6a35f), Rust 3/3, 2^-130.19, dev+lookup negatives art:f01f7196; handoff 0045Z. Next: drain 4090, H100 fp8-hopper merged re-record.
CHECKPOINT f2363663 (00:05Z) [open] 4090 fp8-ada cell re-recorded 0.666s (was 1.130): art:ecd96143, run-files art:0667ed46, r20260924-234932-5828 @f2363663, proofs b5ef0238 unchanged, Rust 3/3, 2^-130.19; negatives art:9398f028; handoff 0006Z. Merged LK table dev pass r20260925-000446-6b38 running.
CHECKPOINT bb859220 (23:46Z) [open] 4090 dev @bb859220 fp8-ada: warm t.total 0.692s (cell was 1.130), proofs sha b5ef0238 unchanged, Rust 2/2, negatives OK. A/B int32 Acc running r20260924-234548-cd34; then recorded 4090 run. Considering merged tagged LogUp table for FP8 unit.
CHECKPOINT bb859220 (23:35Z) [open] H100 cell re-recorded 0.482s (was 0.688; art:b1010ac8, proofs identical; handoff 2326Z). H100 terminated 23:26Z (~$7.2 total). 4090 pod 5vnbd6rfwm3wmd bootstrapped; fp8-ada dev pass running, then int32 Acc test and recorded run.
CHECKPOINT ab57df0a (23:10Z) [open] H100 hill-climb: prove 0.626->0.432s byte-identical (11 commits to bb859220). Recording improved fp8-hopper cell r20260924-230813-9198 now; next push+handoff, then 4090 fp8-ada re-record on a new pod.
CHECKPOINT ab57df0a (22:39Z) [open] Both FP8 cells recorded (4090 in Table 2; H100 0.688s handed off). Hill-climb on H100: eq_table one-launch + numpy ext serialization committed (048e6a41, 8670d0f7), prove 0.599->0.537s, bytes identical. Testing query-value caching; then re-record H100.
CHECKPOINT 891572a0 (22:10Z) [open] H100 FP8 cell recorded: art:2e7baba7 (run-files art:438ada92, r20260924-215501-f96b @891572a0) t.total 0.688s med, Rust 3/3, 2^-130.19, only rejection=indep. verif.; negatives art:cdaabf41; handoff coordinator/20260924T2212Z. 4090 cell art:1b4fd4a1 now IN Table 2. next: profile + hill-climb
CHECKPOINT 891572a0 (21:57Z) [open] H100 pod ac0m34rqaw3hti (guard 90): fp8-hopper dev 4096 VUs t.total 0.683s, Rust 2/2, negatives 4/4 both verifiers, predicate: only indep. verification. Recorded run r20260924-215501-f96b @891572a0 running; next: push+handoff, then profile lookup/open_acc
CHECKPOINT 40069d44 (21:34Z) [open] 4090 FP8 cell recorded: art:1b4fd4a1 (run-files art:89a2ce85, r20260924-211113-5f9e @07a8edd6) t.total 1.130s med, Rust 3/3, 2^-130.19, only rejection=indep. verification; negatives art:edfbca4d; handoff coordinator/20260924T2129Z. next: H100 fp8-hopper
CHECKPOINT 07a8edd6 (21:07Z) [open] 07a8edd6: fp8-ada 4096 VUs on 4090 passes (t.total ~1.11s, Rust 2/2, 2^-130.19, negatives 4/4 both verifiers); next: recorded 3-rep run + data put --preserve + coordinator handoff, then H100
CHECKPOINT 4e26d864 (20:47Z) [open] 66841d43: A-GKR FP8 circuits (checker v2 adder-side view, packed-word epilogue), BF16 statements byte-identical, 600 random VUs match silicon; 4090 pod vy-agkr-fp8 bootstrapped; dev run fp8-ada 256 VUs running. next: 4096 + negatives

## Design (commit 66841d43, 07a8edd6)

A-GKR at the E4M3 relations reuses lane agkr-table's GPU path (gpu.v2 export / witness / bench_result, prover,
Rust verifier) with checker v2 on the pipeline's **adder-side view**:
`Params(sig=4, exp=4, acc_sig=14, width=14, floor=-139, groups=model.groups, acc_exp=8, op_nan_rule="e4m3")`
(`backends/gkr/gpu/v2/fp8.py::adder_params`). The chained state (s, e_hat, M, z) is the 14-bit adder magnitude; the
FP32 word is `M << 10`. Silicon's lossy rescale of the incoming FP32 word (`M24 >> 10`, zero flag on all 24 bits) is
the identity on every chained state (low 10 bits zero), so no rescale gadget is needed; `check_widths` still refuses a
lossy view. Units are `sum(groups) = 32` products: 48 per VU (ada: 2 groups of 16; hopper: 1 group of 32).

Checker v2 edits (BF16 byte-identical: REAL and hopper-bf16 circuit/epilogue/chain/manifest sha256 unchanged vs
ab9573fd): accumulator-named bounds where the accumulator is meant (LEADNORM clamp/overflow `acc_e_min/acc_e_max`,
Pack `acc_bias/acc_e_min/acc_t_finite`, T_HDR `acc_exp`), T_OP honours the e4m3 NaN rule (only 0x7f/0xff lack rows),
`vb = max(ceil(s_bits/2), -k_lo)` (FP8: s_bits 20, k_lo -13 from the floor clamp -> vb 13; REAL unchanged at 15).

Epilogue (FP8): one row per VU `one, s, e, M, z, ovf[g], sgn[g], y16` with `y16 == Pack.check(state, flags)` at the
adder-side params = the 22-bit packed word `s 2^21 + t 2^13 + (f >> 10)` = `fp8/relation.pack_public(y)` (public
word, < 2^22 < p, every linked component table-determined in the last unit). Column keeps the name `y16` because the
chain binds the public word by that name in `gpu/run.read_chain` and `verifier/src/main.rs`.

Unit sizes: ada 472 columns / 150 queries per unit, epilogue 10 columns; hopper 448 / 139, epilogue 8. Tables tiny
(T_OP 254, SHIFT 8192, TNORM 229376 the largest) vs BF16's 5.1M implicit rows.

Cross-checks: laptop, 612 random VUs x 2 models (zeros, subnormals, max exponents, cancellation) through
`vu_rows_fp8`: every unit's packed state == silicon `tc_dot` accumulator >> 10, every row satisfies its circuit mod p.
Pod: `gpu.v2.witness recipe --relation fp8-ada --vus 64` byte-exact (device generator vs export rows). 256-VU
bench_result (4090): Python 2/2, Rust 2/2 accept, 2^-130.19, contract clean, t.total 0.73 s.

4096 VUs on the 4090 first OOMed in the Ligero opening (a 6.7 GB cupy buffer); 07a8edd6 runs `open_w_qc_eval` in
row blocks of 4096 on < 40 GB parts (block sums mod p: q unchanged; 80 GB parts keep the one-shot path).

## RTX 4090 FP8 (fp8-ada) cell, recorded 21:21Z
- `research run --on vy-agkr-fp8 --project verity --source . --stage gkr.gpu.v2.table2.fp8-ada --timeout 2400 --cwd source/backends/gkr
  --tool a_gpu_prove --scratch triton --env PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True -- /workspace/venv312/bin/python bench_result.py
  /workspace/agkr-fp8/fp8-ada/stmt --relation fp8-ada --vus 4096 --reps 3 --warmup 1 --verifier /workspace/bin/verity-gkr-verify --threads 16`
- r20260924-211113-5f9e @ 07a8edd6 (clean): result art:1b4fd4a1, run-files art:89a2ce85; PRESERVED (pod-side push, `data preserved` rc 0);
  laptop `reindex --remote` ok (5198 artifacts / 1126 attempts / 11208 labels after).
- t.total median 1.130 s (1.124 / 1.130 / 1.132); buckets (median rep): witness 0.047, commit 0.013, lookup 0.316, arithmetic 0.673
  (arith 0.370 + open 0.303: acc 0.224, wq 0.079), serialization 0.080. Rust 3/3 accept (0.97 s at 16 threads, EPYC 7702), proofs
  byte-identical b5ef0238…, 18152824 B. Soundness 2^-130.19 (encoding_opening dominant), NON_ZK_PROOF_DIAGNOSTIC, instances e66ff0f2… (frozen).
  Warm-up (Triton compile into the fresh scratch cache) 512 s. Overhead vs native peak (330.3 TFLOP/s): 2.97e7x.
- Table 2 predicate: only `not independently verified` (laptop tables --format json, rejected[]). Handoff:
  lanes/coordinator/20260924T2129Z-handoff-from-agkr-fp8.md. Negatives tree art:edfbca4d (dev run r20260924-210424-0471, same code).
- Descriptive strings in this result's fingerprint still say limb epilogue / Params.from_model / 96 units (BF16 text); fixed at 40069d44.
- 4090 pod tnfwhbryf1mdnr drained + terminated 21:34Z (20:37-21:34, $0.74/h, ~$0.70).

## H100 FP8 (fp8-hopper) cell, recorded 21:55Z
- New pod vy-agkr-fp8 = H100 80GB HBM3 ac0m34rqaw3hti (reference part, Xeon 8480+, $3.49/h, created 21:35Z). Same recipe as the 4090
  cell with `fp8-hopper` and `--threads 22`.
- r20260924-215501-f96b @ 891572a0 (clean): result art:2e7baba7, run-files art:438ada92; PRESERVED; reindex ok.
- t.total median 0.688 s (0.686 / 0.688 / 0.687); buckets: witness 0.036, commit 0.010, lookup 0.258, arithmetic 0.320, serialization
  0.063. Rust 3/3 accept (0.62 s at 22 threads), proofs byte-identical f80ecc53…, 17251312 B, 2^-130.19, instances 0ff75002… (frozen).
  Warm-up 438 s. Overhead vs native peak (1978.9 TFLOP/s): 1.08e8x.
- Predicate: only `not independently verified`. Handoff lanes/coordinator/20260924T2212Z-handoff-from-agkr-fp8.md. Negatives art:cdaabf41.

## Hill-climb on the H100 (22:15Z-), every step byte-identical (fp8-hopper proof sha f80ecc53…; bf16-hopper 4a05ada6… checked once)
Median warm prove (06_ab.sh, 4 timed proves at 4096 VUs), start 0.626 s:
- bba64ea1 (cherry-pick of agkr-nvf4 a8d471ba, `eq_rows_dot` for phase-2 vf) + 097a1e61 (cached lookup-claim plan) -> 0.599
- 048e6a41 eq_table as one `eq_table_vars` launch on CUDA (was a doubling loop of ext_mul_chunked launches; exact n=0..20) -> 0.537
- 8670d0f7 numpy serialization of ext vectors in Proof.to_bytes / Transcript.absorb_exts (t.serialization; transcript unchanged)
- 1e21cd26 keep the query tuples from the multiplicity pass for the lookup pass on >= 48 GB parts (0.7 GiB) -> 0.507
- c6aadfdf query tuples from a cached per-table linear-form plan (mults 28 -> 11 ms) + 01ee07f0 tolist tuples -> 0.470
- 6517652d incremental eq prefix in packed phase 1 + 2dacc949 depth-batched eval_wires (12 -> 4.7 ms) -> 0.459
Remaining profile: lookup 0.196 (graphed LogUp: ~18.6k tiny kernels ~7.7 us each, fs_step SHA-256 14 us; latency-bound, fusing
kernels is the only lever, transcript fixed), arith 0.115 (phase-1 per-round host/sync), open_acc 0.073, open_wq 0.038.
- 10b726f9 host numpy for phase-2 sumcheck_prod (<= 4096 rows), e8503e2d both input claims of a segment as one rank-1 update,
  bb859220 skip the int8 fold matrices in packed phase 1 -> 0.432 s.

## H100 FP8 (fp8-hopper) improved cell, recorded 23:08Z @ bb859220
- r20260924-230813-9198 (clean): result art:b1010ac8, run-files art:ec01de08; PRESERVED (pod push, `data preserved` ok); reindex ok.
- t.total median 0.482 s (0.490 / 0.480 / 0.482), was 0.688; buckets witness 0.026, commit 0.010, lookup 0.200, arithmetic 0.200,
  serialization 0.044. Proofs byte-identical to the 21:55Z cell (f80ecc53…), Rust 3/3 (0.63 s at 22 threads), 2^-130.19,
  contract clean. Warm-up 436 s. Overhead 7.57e7x.
- Negatives on bb859220: dev run r20260924-232156-7658, NEGATIVES OK, tree art:9eee02c9 (ref result art:b1010ac8).
- Predicate: only `not independently verified`. Handoff lanes/coordinator/20260924T2326Z-handoff-from-agkr-fp8.md.
- H100 pod ac0m34rqaw3hti drained + terminated 23:26Z (21:35-23:26, $3.49/h, ~$6.46).

## RTX 4090 re-record
- New pod vy-agkr-fp8 = RTX 4090 5vnbd6rfwm3wmd (reference part, EPYC 7532, 12 vCPU, created 23:27Z); sync 226 s, bootstrap
  RELS=fp8-ada 4 min (BOOTSTRAP_OK). Dev pass at bb859220: r20260924-233453-ee05 (bench_result 0.692 s, proofs b5ef0238… unchanged,
  Rust 2/2, NEGATIVES OK).
- f2363663: `Acc.a` in int32 on CUDA (06_ab r20260924-234548-cd34: same sha, t_open_acc 113 -> 85 ms, median prove 0.594 s).
- Recorded r20260924-234932-5828 @ f2363663 (clean; recipe as above with `--threads 10` and
  `--env OMP_NUM_THREADS=10 MKL_NUM_THREADS=10 OPENBLAS_NUM_THREADS=10 VY_CPU_THREADS=10`): result art:ecd96143, run-files art:0667ed46,
  PRESERVED, reindex ok. t.total median 0.666 s (0.667 / 0.666 / 0.665), was 1.130; buckets witness 0.038, commit 0.014, lookup 0.249,
  arithmetic 0.309, serialization 0.055. Proofs b5ef0238… (as the 21:21Z cell), Rust 3/3 (1.37 s at 10 threads), 2^-130.19, status
  passed. Overhead ~1.75e7x (the 1.130 s cell's 2.97e7x scaled). Negatives art:9398f028 (dev run ee05). Predicate: only
  `not independently verified`. Handoff lanes/coordinator/20260925T0006Z-handoff-from-agkr-fp8.md.

## Merged tagged LogUp table (statement change, FP8 unit circuit only)
- `gpu/v2/export.py::merge_tables`: every table of the FP8 unit circuit (ALIGN4, LEAD, LEADNORM, R5, R7, SHIFT, SSHIFT_HI/LO, TNORM,
  T_OP) becomes one row-listed `LK` (8 columns, 261819 rows: `(tag 2^20 + key, tag, outs.., 0..)`); the 150 queries per unit are
  rewritten into it. It is the default in `circuits()` for E4M3 models; `--no-merge` gives the old statement. The epilogue queries none.
  chain.txt unchanged. It is a new statement, so it needs new negatives and a new independent verification.
- Dev pass r20260925-000446-6b38 (H=/workspace/agkr-fp8/fp8-ada-m, f2363663 + the merge): bench 0.620 / 0.631 s, t_lookup 0.187
  (was 0.224), t_mults 0.040 (was 0.024, searchsorted on the listed table), slots 2881 -> 727, proof 17966656 B sha c31c1cd8…,
  soundness 2^-130.19 (recomputed live, -130.1898057610 vs -130.1898057657), Python + Rust 2/2, NEGATIVES OK. Committed d5d80e0b.
- Cherry-picked from agkr-nvf4: 605b1bbb leaf_q (c94df52a), 285c32cc gate_eval query values (dfe89c36), the Merkle.path part of
  2b25df7f (5ce007ea). Plus 5034767f (a key -> row map for listed-table multiplicities) and 3be6a35f (hold the query tuples on
  < 48 GB parts while they total at most a tenth of the device). 06_ab on the merged statement: every step gives the same sha c31c1cd8;
  median prove 0.447 s (leaf_q + gate_eval: t_lookup 0.187 -> 0.083 s), then 0.427 s (held tuples: t_lookup 0.060 s).
- t_mults split (11_mults_prof.sh): query values 24 ms (gate_eval, 29.5M x 8 int64), multiplicities 14 ms.

## RTX 4090 FP8 (fp8-ada) cell on the merged statement, recorded 00:38Z @ 3be6a35f
- Dev pass on the final code r20260925-002010-55ea (H=/workspace/agkr-fp8/fp8-ada-m): bench 0.483 / 0.491 s, Rust 2/2, NEGATIVES OK.
- Recorded r20260925-002240-8ed3 (clean, `/workspace/agkr-fp8/fp8-ada-m/stmt`, thread caps 10): result art:45c5be4a, run-files
  art:979e37aa; PRESERVED; reindex ok. t.total median 0.490 s (0.490 / 0.482 / 0.495), was 0.666 s (00:06Z, old statement) and
  1.130 s (21:21Z). Buckets: witness 0.038, commit 0.014, lookup 0.100, arithmetic 0.291, serialization 0.044. Proofs c31c1cd8…,
  17966656 B, Rust 3/3 (1.34 s at 10 threads; slots 727, msgs 1790), 2^-130.19, status passed. Overhead ~1.29e7x (2.97e7x scaled).
- Lookup negatives r20260925-004029-acbd (12_lookup_neg.sh): one unit column read by LK +1 (T_OP out, SHIFT out, TNORM out, R5 key
  term), honest multiplicities, from a prover copy with the LogUp self-check turned off: Python and Rust reject all four at
  `LogUp LK level 0: final check`. The negatives tree (dev + lookup) is art:f01f7196.
- Predicate: only `not independently verified`. Handoff lanes/coordinator/20260925T0045Z-handoff-from-agkr-fp8.md (supersedes 0006Z).
- 4090 pod 5vnbd6rfwm3wmd drained + terminated 00:48Z (23:27-00:48, $0.74/h, ~$1.00). verify-po verified art:45c5be4a (verdict
  art:df4d2c3c) and HELD the label per the coordinator's 0050Z rule (rewritten statements wait for red-team-lk). The unchanged-statement
  4090 cell art:ecd96143 (0.666 s) has been in Table 2 since about 01:20Z. Note 0115Z to the coordinator.

## H100 FP8 (fp8-hopper) on the merged statement, recorded 01:21Z @ 3be6a35f
- New pod vy-agkr-fp8 = H100 80GB HBM3 28sqi5rstcudhk (reference part, Xeon 8480+, quota 23.8 cores, $3.49/h, created 00:50Z);
  sync 157 s, bootstrap r20260925-005609-c18d (RELS=fp8-hopper,bf16-hopper) BOOTSTRAP_OK.
- Dev r20260925-005858-6faf (H=/workspace/agkr-fp8/fp8-hopper-m): bench 0.335 / 0.330 s, Rust 2/2, NEGATIVES OK; slots 703.
- Recorded r20260925-010941-b9eb (clean, thread caps 23, --threads 22): result art:3ae971dd, run-files art:0c23dfc9; PRESERVED;
  reindex ok. t.total median 0.328 s (0.322 / 0.328 / 0.328), was 0.482; buckets witness 0.025, commit 0.010, lookup 0.073,
  arithmetic 0.177, serialization 0.041. Proofs 0021aa91…, 17078296 B, Rust 3/3 (0.58 s at 22 threads), 2^-130.19. Overhead
  ~5.2e7x (1.08e8x of the 0.688 s cell, scaled).
- Lookup negatives r20260925-012601-e354: 4/4 rejected by both verifiers (T_OP out, SHIFT out, TNORM out, R6 key term). Negatives
  tree art:70bbba68. Predicate: only `not independently verified`. Handoff 0132Z (the label is held for red-team-lk).
- Cherry-picked agkr-nvf4's 10 same-bytes prover commits (e1bcf472 … 79f00fd3 -> 7f58961f..a97576b5; clean picks). 06_ab
  r20260925-012247-e20f: fp8-hopper merged sha 0021aa91 unchanged, bf16-hopper sha 4a05ada6 unchanged. Median prove 0.235 s (bench
  prove at 3be6a35f was 0.281): mults 23.5 -> 12.5 ms, open_acc 42 -> 28, arith 96 -> 88, open_cols 15 -> 4.
