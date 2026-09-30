---
cursor:
  subagentId: "bc-049fc756-e63b-5b43-af14-0e5a94a2422d"
lane: vllm-coordinator
kind: handoff
from: vllm-sm120-tc-gemm
created: 2026-09-30T15:00Z
---

# #557 is the sm_120 biased-linear fix on main (head `9c390086`); CPU checks pass, and the acceptance run is Kueue job 212

This follows my 14:28Z handoff (#483/#501 model `F.linear`, not what vLLM serves).

- **PR:** [#557](https://github.com/danielreuter/verity/pull/557), draft, based on main `8a4e1147`, head `9c390086`. It doesn't need #483, #501 or #535.
  - The manifest names `GemmBias_v1`/`GemmBias_v2` `out` as slot `0`. This also fixes cc 8.x Qwen2 on main.
  - New Definition `GemmBias_v2{K,N,DOT}`: `Gemm_v2`'s coordinate, then `Bf16Add`, with a replay row.
  - `blackwell_consumer`'s record says `gemm_bias_dot`, so `TritonGemmRule` v3 and the fold bind the pair as one Call on cc 12.0.
  - cc 9.0 keeps `Gemm_v2` + `BiasAdd_v1`, and the accepted kinds keep `GemmBias_v1`. No cc 8.x or 9.0 Program digest moves.
- **CPU checks at `9c390086`:**
  - pytest `r20260930-145042-9f30`: rc 0 (lint, the program, observe, query and replay tests, and the gates). The TP-MoE manifest test was left out: it waits on a lock other lanes' checks hold, and it has no biased linear.
  - circuit-check `r20260930-143449-6b0b`: 5 targets, 0 failures.
  - Binding check `r20260930-143503-f42d`: Qwen2.5-0.5B cc 12.0 qkv is `GemmBias_v2`, bound as `qkv_proj/0`; cc 8.9 `GemmBias_v1` is `qkv_proj/0`. Every Linear is bound, with 0 call boundaries and no evaluator gaps.
- **Acceptance:** Qwen2.5-0.5B cc 12.0 B1 config run (`REPLAY_K=460`) on this head, Kueue managed job 212 (`sm120-qwen05-gb2-1`), submitted at 14:58Z. I'll report its verdict.
- **Still your call:**
  1. Pull #483 and #501.
  2. Close #535 as superseded.
  3. Park #539.
  4. Restack #516 and #524 (stacked on #501) onto main.
- **Open question: Hopper.** On main, cc 9.0 Qwen2 has the same split pair, so under `Q_word` its pre-bias word is probably a call boundary with no serving source too. I haven't built cc 9.0 to check. Setting `gemm_bias_dot` on `hopper` would fix it, but it moves the H100 Qwen2 Program digests. I've left it off.
