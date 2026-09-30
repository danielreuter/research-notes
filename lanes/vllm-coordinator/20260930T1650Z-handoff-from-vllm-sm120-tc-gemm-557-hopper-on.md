---
cursor:
  subagentId: "bc-049fc756-e63b-5b43-af14-0e5a94a2422d"
lane: vllm-coordinator
kind: handoff
from: vllm-sm120-tc-gemm
created: 2026-09-30T16:50Z
---

# #557 head is now `470cf59d`: Hopper fused as you decided at 16:15Z, the B8 workload is added, and tests pass

(Your 16:15Z note arrived after my 16:22Z handoff was drafted.)

- **`9d5049e3`: `gemm_bias_dot` is on for `hopper`.** The cc 9.0 (FA2) Qwen2.5-0.5B request Build is now 96 × `GemmBias_v2{DOT=Hopper}`, with 0 call boundaries and qkv named `0`.
  - The Program digest moves from `5fbb6fee…` to `3973345c…` (`r20260930-163600-dba2`).
  - #557's body says that H100 Qwen2/2.5 Program digests change and that no expected record binds them. The two-Call fallback stays tested, for a family whose record lacks the flag.
- **`470cf59d`:** `workloads/qwen25-05b__bf16__rtxpro6000__tp1__b8__i256__o32__mixed__greedy__bi-eager.json`, the B8 acceptance workload.
- **Tests at `470cf59d`** pass (`r20260930-163544-3dd7`, rc 0). The set is wider than before: it adds the engine, pipeline and check tests that touch biased linears or workloads.
- **The regression suite's `manifest_digest` check:**
  - Row #101 (Llama-3.2-1B B1 stoch) reproduces its expected record on `470cf59d`: manifest `368283ad…`, Program `079ee0a8…`, 7,043 identities, 0 problems (`r20260930-163630-fbc8`).
  - Row #39's i4096 rebuild needs over 20 minutes of the shared short slot, and there's no CPU-only Kueue template. Its stored Program has no `GemmBias`, so it can't move. Tell me if you want it recomputed anyway and where.
- **The acceptance runs (227 B1, 229 B8) were at `ad6ed12a`.** The two later commits don't change a cc 12.0 Program. Say if you want them rerun on `470cf59d`.
- **The FP8 CUTLASS capture is Kueue job 273** (`sm120-fp8blk-cutlass-2`; job 271 lacked `PYTHONPATH`). It records:
  - Qwen3-4B-Instruct-2507-FP8 under `VLLM_USE_DEEP_GEMM=0`;
  - the kernel class vLLM selects and the kernels a served step launches;
  - the engine path against `quant_method.apply`;
  - the served quantizer and GEMM words for layer 0's four linears, across the three sm120 blockwise dispatch regimes (M ≤ 64 swap_ab, ≤ 256 pingpong, above that the 128×128 tile).

  The same job then runs the CPU check against `Fp8GroupQuant_v1` and the blockwise schedule, with the sm_120 e4m3 step against Hopper's and FFMA promotion against mul+add. The check's model reproduces the existing Hopper twin exactly (`r20260930-163005-f22c`).
