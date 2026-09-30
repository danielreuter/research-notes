---
cursor:
  subagentId: "bc-049fc756-e63b-5b43-af14-0e5a94a2422d"
lane: vllm-coordinator
kind: finding
from: vllm-sm120-tc-gemm
created: 2026-09-30T16:23Z
---

# Finding: H100 Qwen2/2.5 has sm_120's call-boundary gap on main; `gemm_bias_dot` on `hopper` closes it, and moves the Program digest

For the H100 re-baseline epoch. Nothing is changed; `hopper` stays off in #557.

**The gap is real on main `8a4e1147`.** Qwen2.5-0.5B request Build, cc 9.0, 132 SMs, FA2 declared, LP 16, T 3, CPU only (`r20260930-150743-0c7e`):
- qkv is `Gemm_v2{DOT=Hopper}` followed by a separate `BiasAdd_v1`.
- The manifest requires 96 `call_boundaries` identities, `qkv_proj/triton_launch_N/out`: the pre-bias word, which serving has no source for.
- It names the post-bias value `qkv_proj/bias`, while the collector binds a Linear's value as `0`.
- So an H100 Qwen2/2.5 Commit fails identity coverage, as sm_120 did.
- The replay side isn't the problem: it composes the interior `Gemm_v2` (`test_hopper_biased_linear_composes_the_interior_gemm_v2`).

**Native FA3 fails earlier.** On main, cc 9.0 without FA2 declared refuses Qwen2.5-0.5B and 1.5B at `fa3_masked_from`: 7 or 6 query heads per KV head don't divide kBlockM 192 or 128 (`r20260930-145700-c3ae`, `-150302-a10a`). So on main only FA2-declared H100 Qwen2 rows reach the manifest at all.

**What `gemm_bias_dot: True` on `hopper` does** (#557 plus that one line, scratch tree, never pushed; `r20260930-161722-faa2`):

| | main / #557 | with `gemm_bias_dot` on `hopper` |
|---|---|---|
| Program digest (this Build) | `5fbb6fee44785228…` | `3973345cabe7f4dd…` |
| qkv | `Gemm_v2` + `BiasAdd_v1` | 96 × `GemmBias_v2{K=896,N=1152,DOT=Hopper}` |
| call boundaries | 96 | 0 |
| qkv member | `bias` | `0` |
| manifest | 1,827 identities | 1,731 identities, `4c025d38…` |

**What would move in the re-baseline:** every H100 Qwen2/2.5 Program with a biased linear.
- In the tree those are the `qwen25-15b__bf16__h100__…` workloads (B1 i1024, B8 eager, compiled, stoch).
- None is in `tests/regression/expected/`.
- Their digests move the way this Build's does. I have not built each of them.
