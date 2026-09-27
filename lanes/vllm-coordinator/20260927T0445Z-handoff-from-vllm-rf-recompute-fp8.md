---
cursor:
  subagentId: "bc-06147ba0-d1ae-5ddc-84d6-00cb2d93cbba"
---

lane: vllm-rf-recompute · kind: handoff · from: vllm-rf-recompute (bc-06147ba0) · created: 2026-09-27T04:45Z

# PR #106 merge-ready: #74's FP8 block scale products computed once (`ScaledMmFp8BlockSharedScale_v1`, opt-in)

[PR #106](https://github.com/danielreuter/verity/pull/106), branch `cursor/vllm-rf-recompute-fp8-cbba` @ `df13126f`, base `main` `3040ac1f`, one commit. It merges cleanly with #98 (`d7f76916`): the diff touches only `registry/fp8.py`, where it adds code, and one new test file.

## What it adds
- **New Definitions** in `registry/fp8.py`:
  - `ScaledMmFp8BlockSharedScale_v1{K,N,G}` has `ScaledMmFp8Block_v1`'s signature. It is one batch over the N/G weight blocks.
  - `ScaledMmFp8BlockSharedScaleTile_v1{K,G}` is one weight block: a batch of `F32Mul(sx[kb], sw[kb])` over kb, then its G coordinates reading those products.
  - `ScaledMmFp8BlockCoordinateGivenScale_v1{K,G}` is the coordinate with `s[kb]` read instead of computed.
- **The selector:** `SHARED_SCALE = {"ScaledMmFp8Block_v1": ScaledMmFp8BlockSharedScale}`, in #101's style. Nothing binds the new Definitions, so the default Program is unchanged.

## Partition checker, #74 with the selector on
`Q_word_v1{X=16,W=32,R=no-recompute}` with #98's `unit_rule` member check, over #74's 580 groups (program graphs `art:c74deac4…`):
- The four FP8 specializations were cut fresh, both before and after.
- Every other group's summary is the graph's own (the same Definition).
- Script: `evidence/word_row.py`. Output: `evidence/word_row74.jsonl`. Both are under the notes repo's `lanes/vllm-rf-recompute/`.

| | violations | recomputed gates | units | committed interior words |
|---|---|---|---|---|
| recorded (`ScaledMmFp8Block_v1`) | 4 (`cut` / `gate-recomputed`) | 113,639,803,200 | 16,269,049,573 | 5,328,722,811 |
| `SHARED_SCALE` applied | **0** | **0** | 17,163,851,173 | 6,223,524,411 |

Per Call, with the selector on:

| linear | specialization | Calls | committed words / Call | gates / Call (old → new) |
|---|---|---|---|---|
| qkv | K=2560 N=6144 | 145,260 | 960 | 872,448 → 750,528 |
| o | K=4096 N=2560 | 145,260 | 640 | 578,560 → 497,280 |
| gate_up | K=2560 N=19456 | 145,260 | 3,040 | 2,762,752 → 2,376,672 |
| down | K=9728 N=2560 | 145,260 | 1,520 | 1,367,040 → 1,174,000 |

- The committed words are the products, N/G × K/G per Call: all `F32Mul_v1` heads in the tile. That is 6,160 f32 words per token per layer and **894,801,600 more for the row** (3.58 GB).
- Widths: every committed unit is one value of 32 bits (W = 32), and every output unit is 16 bits.
- The strict partition and committed-boundaries checks pass: `validate_unit_cut` inside `unit_rule` reports 0 violations and 0 redundant gates.
- **`query.cross_call`** (#98): 0 recomputes on `build_request_LP73_T1`, both as recorded and with every `ScaledMmFp8Block_v1` Call rewritten to the new id (`evidence/cross_sub.py`). This finding is inside the Call, so it is the member check's to catch.

## Digest A/B, selector off
- The diff only adds code.
- The 229 Definition specializations that #74's and #57's request Programs call (`build_request_LP73_T1`, `LP11_T94` and #57's `LP31_T52`) encode byte-identically on `3040ac1f` and `df13126f`. The encoding is the `definitions` closure `encode_program` writes (`evidence/def_digests.py`, `evidence/def_digests_main_3040ac1f.json`).
- The frontend, the fold and the manifest code are untouched, and `registry_version` covers only `prims.py` / `b1.py`. So every Program digest, manifest and verdict of record is unchanged.

## Tests
`tests/program/test_fp8_shared_scale.py` (8 tests, all pass in gate (b)):
- the same circuit after interning both gate DAGs in one table, at 3 shapes;
- (G−1)·N/G·K/G fewer `F32Mul`;
- bit-equal under the reference evaluator on 32 edge vectors covering e4m3 ±0, subnormals, ±448 and NaN bytes, and f32 ±0, subnormals, ±max, ±inf, NaNs, overflowing and underflowing products. Every bf16 output class occurs. The lane run used 96 vectors (`evidence/fp8_edges.py`).
- the partition: `by_kind` = N outputs + N/G·K/G committed, 0 violations, no recomputed gate in the tile. This holds on main and on main + #98;
- names without versions.

## Gate (b)
Both sides ran on `vyv-rf-recompute-cpu` (cpu3g, 16 vCPU), using `gate_b2.sh` in git clones (tree check 0 differing entries, `verity_sampled_proofs` importable).

| side | run | lints | gate (b) |
|---|---|---|---|
| base `3040ac1f` | `r20260927-035144-299a` | rc 0 | 40 F / 3,996 P / 286 S / 6 xf / 11 E (4,339) |
| head `df13126f` | `r20260927-035231-167a` | rc 0 | 39 F / 4,005 P / 286 S / 6 xf / 11 E (4,347) |

- **jdiff rc 0:** 8 new tests, all pass; 0 new failures; 0 new skips.
- 1 test is fixed on head: `test_twins::test_check_writes_the_evidence_schema`. An extra `openmp` key appears depending on whether the IR's C++ build exists on the pod, so this is unrelated to the change.
- Evidence: `evidence/gate-b/jdiff-3040ac1f-vs-df13126f.txt`. Both runs are preserved on R2.

## Serving: where the committed products come from
They come from a host-side computation: `F32Mul_v1(x_s[kb], weight_scale_inv[nb][kb])` over the committed `x_s` (`Fp8GroupQuant_v1` port 1, already a required value) and the checkpoint's block scales (under the weights root), in the IR's F32 semantics (numpy float32), as `vocab_range_source` does.
- **Kernel source:** vLLM `d9105ea80` with CUTLASS v4.7.1, `sm90_mma_tma_gmma_ss_warpspecialized_fp8_blockwise_scaling.hpp`. Both dispatch variants form the product in registers: `tCrSFA_local(i) * scale_b` for Cooperative, and `tCrSFB_local(i) * scale_a` for swap_ab Pingpong. That is one FMUL, never stored, then `accum += accum_temp * scale` (`fp8_accumulation.hpp`). A kernel store would need a modified mainloop.
- **No fast-math:** `scaled_mm_blockwise_sm90_fp8.cu` is not in vLLM's `--use_fast_math` set, so that FMUL is IEEE round-to-nearest with subnormals. It equals `F32Mul_v1` on every non-NaN pair.
- **NaN:** the GPU writes canonical `0x7FFFFFFF`, while `F32Mul_v1` keeps numpy's payload. The host-side value is the Program's, and both NaNs give bf16 `0x7FFF` at the coordinate.

## Not changed, and the switch points for the re-baseline
These are listed in the PR:
- vocabulary kind `scaled_mm_fp8_block`
- fold pattern `CutlassScaledMmFp8Block`
- `required.NAMED_RESIDUALS`
- `kernels/rows.py` (the same twin)
- `vu_export`
- the products source and its identity: `<linear>/scale_products` f32 [rows, N/G, K/G], one per (step, FP8 linear site)

Switching the record is root's re-baseline item. No Program, manifest, root, leaf id or verdict moves, and no allowlist grows.

## Found, not fixed
- The committed-word cost is real: +17% of #74's committed interior words. It is the price of the no-recompute rule for this kernel's scale layout.
