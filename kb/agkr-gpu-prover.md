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

## One merged lookup table (statement change; agkr-nvf4 18ab232e for NVFP4, lane/agkr-fp8 d5d80e0b for E4M3)
- The LogUp cost was ten trees' round latencies. `gpu/v2/export.py::merge_tables` rewrites circuit.txt: every table becomes one
  row-listed `LK` with rows `(tag 2^20 + key, tag, outs.., 0..)`, and every query becomes `(key + tag 2^20, tag, outs.., 0..)`. That is
  sound because the tag column pins the match, and the keys stay unique because every source key is below 2^20. The Rust verifier
  needs no change. The soundness bound did not move (2^-130.19, encoding_opening dominant). FP8 ada: 261819 rows x 8 columns, 150
  queries/unit, slots 2881 -> 727.
- After the merge the lookup is bandwidth-bound, and the query-tuple work dominates: 29.5M x 8 int64 tuples = 1.8 GiB.
  agkr-nvf4's `leaf_q` (one Triton pass for `z - Σ β^k v_k`) plus the gate_eval query values took 4090 t_lookup 0.187 -> 0.083 s.
  Holding the tuples for the lookup pass when they fit in a tenth of the device took it to 0.060 s.
- Row-listed tables used argsort + searchsorted multiplicities; a cached key -> row map (keys < 2^26) replaces them.
- The standard negatives (public word +-1, sign, exponent) all fail at the epilogue assertions, so they never exercise the lookup.
  For a lookup statement change, use `12_lookup_neg.sh`: tamper one unit column read by a query, patch in the honest
  multiplicities, and run a prover copy whose "fractional sum is not zero" self-check is a no-op. Both verifiers must reject at
  `LogUp LK level 0: final check`.
- 4090 fp8-ada at 4096 VUs, t.total 1.130 -> 0.666 s (prover only, same bytes) -> 0.490 s (merged statement).
- Red-team (red-team-lk, 2026-09-25, art:ca49b2f8 art:9a6280c5 art:319062b4 art:5419ef15): the merge, the nvf4 depth-1 flatten, the
  epilogue t drop, BOOL_QUADRATIC and PAIRED all PASS. Soundness holds for any key: the tag is its own constant column and the shift
  is injective mod p. The 2^20 bound only matters to the prover's first-column multiplicity search. The harness is
  `backends/gkr/tools/red_team_lk.py` (lane/red-team-lk), with subcommands `static-merge`, `static-nvf4`, `selftest`,
  `forge [--control]` and `audit`. Its evidence kind is `redteam-findings/v1`.
- Tag-collision forgeries need the cheating prover (no self-check, first-column multiplicities). On nvf4, a tag-stripped LK moves
  the rejection from LogUp to assertions. On fp8, every range-checked column also feeds another query (ALIGN4, a second R5), so
  no single-cell forgery isolates the tag; `audit` lists each forgery's LK misses with and without the tag.
- Gotcha: tree 3be6a35f (fp8) under Triton 3.4 (5090 image) raises a CompilationError in `packed/kernels_triton.py` until it
  gets b7cec878's 5-line constexpr-global fix.
