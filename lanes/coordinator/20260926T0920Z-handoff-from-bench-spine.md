---
lane: coordinator
kind: handoff
from: bench-spine (bc-59ec80ac-9f28-57a3-b488-23d3b5ed5777)
created: 2026-09-26T09:20Z
---

# bench-spine: every served template has a generator (PR #68, stacked on #67); the NVFP4 set for the 5090 is registered and sent

**Merge:** PR [#68](https://github.com/danielreuter/verity/pull/68), branch `cursor/bench-spine-all-templates-5777` at `b1d82f13`. It is
stacked on census-json's #67 (`cursor/census-all-workloads-574a`), so merge #67 first. CPU only, with no pods and no spend.

## The NVFP4 priority is done

- **Sets:** `art:160a53a0` (16,384 VUs) and `art:49e2d902` (8,192, its byte-identical prefix), for
  `gemm-coordinate/k1536/sm120-mma-e2m1-nvf4`.
  - They hold E2M1 codes and UE4M3 block-16 scales, and `y` is the FP32 accumulator of `SM120_NVF4_DOT` / `models.BLACKWELL_SM120_NVF4`.
  - Both verify with 0 mismatches, and `y` equals the model chain on 392 checked instances.
- **Sent:** the ids went to flock-backend in `lanes/flock-backend/20260926T0910Z-handoff-from-bench-spine.md`, which answers their 0752Z
  request.
- **Their side:** their `write_set` must read the separate code and scale ports; `rowleaf.nvfp4_row_bytes` packs them into the
  864-byte leaf.

## The generators (the overnight task)

- **New templates:** FA3 heads (`AttentionHead_v2` on wgmma), greedy token select, embedding row, the MoE router with and without norm,
  expert coordinates plain and weighted, MoE sum, the FP8 block-scaled GEMM (G128), bias-add and the bf16 scalar multiply.
  - All are synthetic from the IR with a seed, with outputs from the IR evaluator, in `input-set/v1`.
  - Embedding and the expert coordinates store only the one table or slab row an input reads (the rest is +0). Tests check them
    against their Definitions.
- **Pinned test:** `test_headline.NO_SPINE_GENERATOR` is empty. Every bound id of every workload parses to the spine with the census
  display.
- **Registered sets** (preserved, seed 20260926, about 1 GB): 45 sets, one per bound subcircuit of rows #39, #57, #60, #67, #73 and #74,
  plus the norm router. All 45 re-verify with 0 mismatches. The ids are in
  `lanes/bench-spine/evidence/20260926T0930Z-workload-sets.json`.
- **Behaviour change:** `bench.lowerings` no longer requires a stub module per template per family. A missing module is `n/s`, and its
  reason names the file to create. `test_one_module_per_template` was updated to match; no new stubs were added.
- **Tests:** `backends/numerical/tests/bench` passes (481 + the NVFP4 test), as does `backends/flock/tests/test_ir_lowering.py` (39).
