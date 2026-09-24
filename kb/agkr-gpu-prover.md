# A-GKR GPU prover (backends/gkr/gpu): where the time goes and what moved it

Written by lane agkr-fp8 (2026-09-24), H100 80GB HBM3, fp8-hopper at 4096 VUs (196608 units x 448 columns, 10 lookup
tables, T_OP n=24). Every change below left the proof bytes identical (sha256 of `Proof.to_bytes` unchanged, also for
bf16-hopper), which is the check to run for any prover-only speedup: `06_ab.sh` in `lanes/agkr-fp8/evidence/pod-scripts/`.

## Profile after the hill-climb (warm prove 0.432 s, was 0.626 s)
- lookup 0.196 s: the graphed LogUp (`logup_packed._FSGraphExt` + device Fiat-Shamir `fs_cuda.fs_step`). About 18.6k kernels
  of ~7.7 us each inside CUDA graphs: latency-bound, not bandwidth-bound (the big levels cost ~4 ms of HBM traffic in all).
  `fs_step` (serial SHA-256 on one thread, ~4 compressions) is ~14 us per round. Only kernel fusion inside a round would
  move this; the transcript order is fixed.
- arith 0.097 s: phase 1 per-round host work + one sync per round (36 rounds); GPU kernels ~39 ms.
- open_acc 0.061 s (rank1_add over the 4.2 GB int64 `Acc.a`, scatter_terms 29 ms), open_wq 0.038 s, mults 0.011 s.

## What was slow and why (fixes on lane/agkr-fp8)
- `field.eq_table` doubled with one `ext_mul_chunked` launch pair per variable (66 calls/prove): one `eq_table_vars`
  launch instead (-60 ms).
- `seg_query_values` / `eval_wires` evaluated every linear form term by term (~3 launches per term per form, ~1500
  launches): cached per-circuit plans, one gather per term position (mults 28 -> 11 ms, witness_wires 12 -> 4.7 ms).
- Query tuples were built twice (multiplicities, then lookup): kept between the passes on >= 48 GB parts (-30 ms).
- Phase-2 `sumcheck_prod` on <= 4096 rows: ~20 launches + 3 syncs per round; numpy on the host is faster.
- Two `add_input_claim` per segment share the copy point, so they are one rank-1 update (one pass over the segment).
- Packed phase 1 recomputed `eq_points(gamma[:i-1], r)` from scratch every round and built int8 fold matrices the
  Triton path never reads.
- Serialization: per-coordinate `int.to_bytes` in `Proof.to_bytes` / `absorb_exts`; numpy `astype('<u4')` is identical.

## Gotchas
- `torch.tensor(list, device='cuda')` from pageable memory is a sync point; in per-round loops it costs a bubble each.
- The 4090 (24 GB) needs `VERITY_GPU_OPEN_ROWS` row-blocked `open_w_qc_eval` (automatic below 40 GB) and
  `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`; FP64 is 1/64 rate there, so any float64 limb matmul path hurts.
